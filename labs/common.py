"""Shared helpers for the runnable labs.

Everything here is free and local:
  * LLM: Ollama serving qwen2.5:7b  (ollama pull qwen2.5:7b, about 4.7 GB)
  * Embeddings: sentence-transformers all-MiniLM-L6-v2 (about 90 MB, 384-dim)

Set LAB_MODEL to use another local Ollama model, e.g. LAB_MODEL=llama3.2.
"""
from __future__ import annotations

import os
import sys
import time
from functools import lru_cache

MODEL = os.environ.get("LAB_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.environ.get("LAB_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Windows consoles default to cp1252; force UTF-8 so outputs print the same everywhere.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass


def header(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def chat(messages, *, temperature: float = 0.0, seed: int = 7, fmt=None, tools=None,
         num_predict: int = 256, model: str | None = None):
    """One Ollama chat call. Returns the raw response object.

    Local models still accept temperature/seed. (Some hosted APIs no longer do:
    Anthropic API version 2026-10-21 rejects temperature/top_p/top_k with a 400.)
    """
    import ollama

    kwargs = dict(model=model or MODEL, messages=messages,
                  options={"temperature": temperature, "seed": seed, "num_predict": num_predict})
    if fmt is not None:
        kwargs["format"] = fmt
    if tools is not None:
        kwargs["tools"] = tools
    return ollama.chat(**kwargs)


def ask(prompt: str, system: str | None = None, **kw) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    return chat(msgs, **kw).message.content


@lru_cache(maxsize=1)
def embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


def embed(texts):
    """L2-normalised float32 embeddings, shape (n, 384)."""
    import numpy as np

    v = embedder().encode(list(texts), normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(v, dtype="float32")


class Timer:
    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *a):
        self.s = time.perf_counter() - self.t0


def check_ollama() -> None:
    """Fail fast with a clear message if Ollama or the model is missing."""
    try:
        import ollama

        names = [m.model for m in ollama.list().models]
    except Exception as e:  # pragma: no cover
        sys.exit(f"Ollama is not reachable ({e}). Install it from https://ollama.com and run `ollama serve`.")
    if not any(n.split(":")[0] == MODEL.split(":")[0] and (":" not in MODEL or n == MODEL) for n in names):
        sys.exit(f"Model {MODEL} not found locally. Run: ollama pull {MODEL}   (installed: {names})")
