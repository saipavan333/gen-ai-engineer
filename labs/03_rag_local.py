"""Lab 03 - A complete local RAG pipeline you can read in one sitting.

Lessons: 3.1-3.7 (why RAG, chunking, embeddings, vector DBs, reranking, hybrid, grounding), 11.1 advanced RAG.
Run:   python labs/03_rag_local.py

The corpus is 14 short policy pages for a made-up Indian e-commerce store (a toy on purpose,
so every number below is checkable by eye). The mechanics are the same at 10 M chunks;
what changes at scale is the index type (HNSW/IVF instead of exact search) and the eval set size.
"""
import re

from common import Timer, ask, check_ollama, header
from raglib import GROUNDED_SYSTEM, Index, build_chunks, chunk_fixed, chunk_sentences, grounded_prompt, load_kb

check_ollama()
kb = load_kb()

header("1) Chunking: fixed-size cuts facts in half, sentence-aware chunks keep them whole")
doc = next(d for d in kb if d["id"] == "ref-01")["text"]
for name, chunks in (("fixed 12 words", chunk_fixed(doc, 12)), ("sentence-aware", chunk_sentences(doc, 30))):
    print(f"  {name}:")
    for c in chunks:
        print(f"    | {c}")
print("  Look: the fixed chunker splits 'Card refunds take 5 to 7 business days' across two chunks,")
print("  so neither chunk answers 'how long do card refunds take' on its own.")

header("2) Index: MiniLM embeddings stored in DuckDB and FAISS")
with Timer() as t:
    chunks = build_chunks(kb)
    idx = Index(chunks)
print(f"  {len(kb)} docs -> {len(chunks)} chunks, dim={idx.dim}, built in {t.s:.1f}s")

header("3) Dense retrieval: DuckDB SQL and FAISS must agree (same cosine, two engines)")
q = "How long does a refund to my credit card take?"
d1, d2 = idx.dense_duckdb(q, 3), idx.dense_faiss(q, 3)
for (i1, s1), (i2, s2) in zip(d1, d2):
    print(f"  duckdb {chunks[i1]['cid']:9s} {s1:.3f}   faiss {chunks[i2]['cid']:9s} {s2:.3f}")
print(f"  same top-3: {[a for a, _ in d1] == [b for b, _ in d2]}")

header("4) Dense vs BM25 vs hybrid (RRF), scored against the doc a human says is right")
CASES = [("what does RF-BANK mean", "ref-02"), ("warranty on MX-750", "sell-01"),
         ("can I pay in instalments", "pay-02"), ("my parcel came broken, what do I do", "ret-02"),
         ("is there a fee if my cart is small", "ship-01"), ("someone on the phone asked for my OTP", "acc-01")]
tally = {"dense": 0, "bm25": 0, "hybrid": 0}
for q, gold in CASES:
    row = {"dense": idx.dense_faiss(q, 3), "bm25": idx.lexical(q, 3), "hybrid": idx.hybrid(q, 3)}
    marks = []
    for name, ranked in row.items():
        docs = [chunks[i]["doc"] for i, _ in ranked]
        hit = gold in docs
        tally[name] += hit
        marks.append(f"{name}={'#' + str(docs.index(gold) + 1) if hit else 'miss'}")
    print(f"  {q!r:45s} gold={gold:8s} " + "  ".join(marks))
print(f"  hit@3 over {len(CASES)} queries: " + ", ".join(f"{k}={v}/{len(CASES)}" for k, v in tally.items()))
print("  Look: BM25 misses the paraphrase ('instalments' never appears; the doc says 'EMI'). Fusion is not free:")
print("  RRF gives a noisy BM25 list the same vote as a good dense list, so it can push a right answer")
print("  out of the top 3. On this tiny corpus dense already wins; hybrid earns its keep on big corpora full of")
print("  near-identical codes (SKUs, error ids) that embeddings blur. Never assume: measure hit@k (lab 06).")

header("5) Grounded answers with citations, and a refusal when retrieval is weak")
THRESHOLD = 0.35  # cosine below this = 'nothing relevant'; tune it on your golden set (lab 06)
QUESTIONS = [
    "I was charged twice for one order. What happens now?",
    "Can I change my delivery address after the order has shipped?",
    "Do you deliver to Antarctica by drone?",
]
for q in QUESTIONS:
    hits = idx.hybrid(q, 3)
    best_cos = idx.dense_faiss(q, 1)[0][1]
    passages = [chunks[i] for i, _ in hits]
    if best_cos < THRESHOLD:
        ans = "I don't know based on our policies. (refused before calling the LLM: best cosine "
        ans += f"{best_cos:.2f} < {THRESHOLD})"
    else:
        ans = ask(grounded_prompt(q, passages), system=GROUNDED_SYSTEM, num_predict=120)
    cites = re.findall(r"\[([a-z]+-\d+#\d+)\]", ans)
    valid = all(c in {p["cid"] for p in passages} for c in cites)
    print(f"  Q: {q}\n  A: {ans.strip()}\n     citations={cites} all-cited-ids-were-retrieved={valid}\n")
print("  Look: every factual sentence carries an id you can check; the off-topic question is refused")
print("  cheaply by the retrieval threshold, so the model never gets a chance to make something up.")
