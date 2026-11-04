"""Small, readable RAG building blocks shared by labs 03, 06, 07 and 08.

Nothing here is a framework: each function is a few lines so you can see the mechanism.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from common import embed

DATA = Path(__file__).parent / "data"


def load_kb():
    return json.loads((DATA / "kb.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- chunking
def split_sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def chunk_fixed(text: str, size_words: int = 25):
    """Naive fixed-size chunks: cuts wherever the word count says, even mid-sentence."""
    w = text.split()
    return [" ".join(w[i:i + size_words]) for i in range(0, len(w), size_words)]


def chunk_sentences(text: str, max_words: int = 45, overlap_sentences: int = 1):
    """Sentence-aware chunks with a sentence of overlap so facts are not cut in half."""
    sents, chunks, cur = split_sentences(text), [], []
    for s in sents:
        if cur and len(" ".join(cur + [s]).split()) > max_words:
            chunks.append(" ".join(cur))
            cur = cur[-overlap_sentences:] if overlap_sentences else []
        cur.append(s)
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def build_chunks(kb, max_words: int = 45):
    out = []
    for d in kb:
        for j, c in enumerate(chunk_sentences(d["text"], max_words=max_words)):
            out.append({"cid": f"{d['id']}#{j}", "doc": d["id"], "title": d["title"],
                        "text": f"{d['title']}. {c}"})
    return out


# ---------------------------------------------------------------- lexical: BM25
TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def tokens(s: str):
    return TOKEN.findall(s.lower())


class BM25:
    def __init__(self, docs, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.toks = [tokens(d) for d in docs]
        self.avg = sum(map(len, self.toks)) / len(self.toks)
        df = Counter(t for ts in self.toks for t in set(ts))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, q: str):
        qt = tokens(q)
        out = np.zeros(len(self.toks), dtype="float32")
        for i, ts in enumerate(self.toks):
            tf = Counter(ts)
            for t in qt:
                if t in tf:
                    f = tf[t]
                    out[i] += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(ts) / self.avg))
        return out


# ---------------------------------------------------------------- dense index
class Index:
    """Dense vectors in DuckDB (SQL) and FAISS (library), plus BM25 for hybrid."""

    def __init__(self, chunks):
        import duckdb
        import faiss

        self.chunks = chunks
        self.vecs = embed([c["text"] for c in chunks])
        dim = self.vecs.shape[1]
        self.con = duckdb.connect()
        self.con.execute(f"CREATE TABLE chunks(i INTEGER, cid VARCHAR, text VARCHAR, v FLOAT[{dim}])")
        self.con.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?)",
                             [(i, c["cid"], c["text"], self.vecs[i].tolist()) for i, c in enumerate(chunks)])
        self.faiss = faiss.IndexFlatIP(dim)  # inner product on unit vectors == cosine
        self.faiss.add(self.vecs)
        self.bm25 = BM25([c["text"] for c in chunks])
        self.dim = dim

    def dense_duckdb(self, q: str, k: int = 3):
        qv = embed([q])[0].tolist()
        rows = self.con.execute(
            f"SELECT i, array_cosine_similarity(v, ?::FLOAT[{self.dim}]) AS s FROM chunks ORDER BY s DESC LIMIT ?",
            [qv, k]).fetchall()
        return [(int(i), float(s)) for i, s in rows]

    def dense_faiss(self, q: str, k: int = 3):
        s, i = self.faiss.search(embed([q]), k)
        return [(int(a), float(b)) for a, b in zip(i[0], s[0])]

    def lexical(self, q: str, k: int = 3):
        sc = self.bm25.scores(q)
        order = np.argsort(-sc)[:k]
        return [(int(i), float(sc[i])) for i in order]

    def hybrid(self, q: str, k: int = 3, rrf_k: int = 60, depth: int = 10):
        """Reciprocal rank fusion (Cormack et al., 2009): score = sum 1/(rrf_k + rank), rank from 1."""
        fused = Counter()
        for ranked in (self.dense_faiss(q, depth), self.lexical(q, depth)):
            for rank, (i, _) in enumerate(ranked, start=1):
                fused[i] += 1.0 / (rrf_k + rank)
        return fused.most_common(k)


GROUNDED_SYSTEM = (
    "You answer customer questions using ONLY the numbered context passages. "
    "Cite the passage id in square brackets after each fact, like [ref-01#0]. "
    "If the context does not contain the answer, reply exactly: I don't know based on our policies."
)


def grounded_prompt(question: str, passages):
    ctx = "\n".join(f"[{p['cid']}] {p['text']}" for p in passages)
    return f"Context:\n{ctx}\n\nQuestion: {question}"
