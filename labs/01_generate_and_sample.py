"""Lab 01 - Generation, sampling, tokens and timing on a real local LLM.

Lessons: 1.1 what an LLM is, 1.2 tokens, 1.4 context, 1.5 sampling, 8.1 cost/latency, 8.2 streaming.
Run:   python labs/01_generate_and_sample.py
"""
from common import MODEL, Timer, chat, check_ollama, header

import ollama

check_ollama()
PROMPT = "Write one short sentence describing the weather in Bengaluru in July."

header(f"1) Same prompt, temperature 0, three different seeds  (model: {MODEL})")
outs0 = []
for seed in (1, 2, 3):
    r = chat([{"role": "user", "content": PROMPT}], temperature=0.0, seed=seed, num_predict=40)
    outs0.append(r.message.content.strip())
    print(f"  seed={seed}: {outs0[-1]}")
print(f"  distinct outputs at T=0: {len(set(outs0))}")
print("  Look: T=0 is close to greedy but NOT a determinism guarantee. In one of our runs only 2 of 3 seeds")
print("  matched, in another all 3 did: GPU kernels, batching and tie-breaking can still change a token.")
print("  Never build a test on exact text.")
print("  Also check the FACT: Bengaluru in July is monsoon season (mild and wet). A fluent, confident")
print("  'hot and dry' answer is a hallucination - fluency is not accuracy (Lesson 1.6).")

header("2) Same prompt, temperature 1.0, three different seeds")
outs1 = []
for seed in (1, 2, 3):
    r = chat([{"role": "user", "content": PROMPT}], temperature=1.0, seed=seed, num_predict=40)
    outs1.append(r.message.content.strip())
    print(f"  seed={seed}: {outs1[-1]}")
print(f"  distinct outputs at T=1.0: {len(set(outs1))}  (sampling -> usually 2-3)")

header("3) Same seed twice at T=1.0 -> reproducible on the same machine")
a = chat([{"role": "user", "content": PROMPT}], temperature=1.0, seed=42, num_predict=40).message.content
b = chat([{"role": "user", "content": PROMPT}], temperature=1.0, seed=42, num_predict=40).message.content
print(f"  identical: {a == b}")

header("4) Tokens are what you pay for: prompt vs output token counts")
short = chat([{"role": "user", "content": "Capital of France? One word."}], num_predict=10)
long_ctx = "Background notes. " * 200 + "\nQuestion: capital of France? One word."
long = chat([{"role": "user", "content": long_ctx}], num_predict=10)
for name, r in (("short prompt", short), ("long prompt ", long)):
    print(f"  {name}: prompt_tokens={r.prompt_eval_count:5d}  output_tokens={r.eval_count:3d}  "
          f"prefill_s={r.prompt_eval_duration/1e9:6.2f}  answer={r.message.content.strip()!r}")
print("  Look: the long prompt costs many more input tokens and more prefill time for the same answer.")

header("5) Streaming: time-to-first-token (TTFT) vs total time")
with Timer() as t:
    first = None
    n_chunks = 0
    for chunk in ollama.chat(model=MODEL, stream=True,
                             messages=[{"role": "user", "content": "List five Indian rivers, comma separated."}],
                             options={"temperature": 0, "num_predict": 40}):
        if first is None and chunk.message.content:
            import time as _t
            first = _t.perf_counter() - t.t0
        n_chunks += 1
        last = chunk
print(f"  TTFT={first:.2f}s  total={t.s:.2f}s  chunks={n_chunks}  "
      f"decode_tokens_per_s={last.eval_count/(last.eval_duration/1e9):.1f}")
print("  Look: streaming does not make generation faster; it shows the first words sooner.")
