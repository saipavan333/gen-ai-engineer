# Runnable labs (free, local)

Twelve labs that run on your own machine with no API key and no bill. Each one prints what it is doing,
measures something real, and ends with a "Look:" line telling you what the numbers mean.
Every lab was run on 2026-11-03 and its output is saved in [`outputs/`](outputs/) so you can compare.

## Setup (once)

1. Install [Ollama](https://ollama.com) and pull the model (about 4.7 GB):
   ```
   ollama pull qwen2.5:7b
   ```
   Any other local chat model with tool calling works too: `LAB_MODEL=llama3.2 python labs/04_agent_tools.py`.
2. Create a virtual environment and install the packages (torch is the big one; the CPU build is enough):
   ```
   python -m venv .venv
   .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
   pip install -r labs/requirements.txt
   ```
   The first lab that embeds text downloads `sentence-transformers/all-MiniLM-L6-v2` (about 90 MB).
3. Run a lab from the course folder: `python labs/03_rag_local.py`, or all of them: `python labs/run_all.py`.

Our machine: Windows 11, RTX 3050 laptop GPU (4 GB), qwen2.5:7b at about 8 output tokens/s.
A cold start (loading the model into memory) took 3 minutes under load; later calls take seconds.

## The labs

| Lab | What you build and measure | Lessons |
|---|---|---|
| `01_generate_and_sample.py` | temperature and seeds, token counts, prefill time, time-to-first-token | 1.1-1.5, 8.1-8.2 |
| `02_structured_output.py` | vague prompt vs prompt-only JSON vs schema-constrained decoding; content accuracy vs gold | 2.1-2.4 |
| `03_rag_local.py` | chunking, MiniLM embeddings in DuckDB and FAISS, BM25, RRF hybrid, cited answers, refusal | 3.1-3.7, 11.1 |
| `04_agent_tools.py` | tool-calling agent with step budget, repeat guard, tool errors, code-enforced refund limit, claim checks | 4.1-4.8 |
| `05_mcp/client_agent.py` | an MCP server (SDK 2.x) and a client that gives its tools to the local model | 4.6 |
| `06_evals.py` | recall@k, MRR, nDCG; per-case regression gate; LLM judge vs fact checks; judge position bias; error bars | 6.1-6.6, 3.8, 11.3 |
| `07_injection_exfiltration.py` | indirect injection that leaks PII via a markdown image; spotlighting; output filter; attack success rate | 7.1-7.7 |
| `08_llmops.py` | traces (OTel GenAI field names), prompt registry with hashes, exact + semantic cache, cost, guardrails | 6.5, 8.3, 12.x |
| `09_text_to_sql_duckdb.py` | text-to-SQL with a parser-based SELECT-only gate, read-only connection, self-correction, execution accuracy | 9.1-9.4 |
| `10_ai_sql_udf.py` | LLM and embedding functions inside DuckDB SQL: the local stand-in for AI.GENERATE / AI_COMPLETE / ai_query | 17.1-17.4 |
| `11_lora_tiny.py` | LoRA parameter math for Qwen2.5-7B, then a real LoRA fine-tune on a tiny model (forgetting included) | 5.1-5.6 |
| `12_self_consistency.py` | test-time compute: majority vote over N sampled chains, accuracy vs tokens | 13.1, 2.3 |

## What the labs honestly found (our run)

Sample sizes are small on purpose (5-20 cases, so each lab runs in minutes). Every rate below comes with its n
and a 95% Wilson interval (`common.rate()`); read them as demonstrations of a mechanism, not as measured rates.
The runs use temperature 0 and fixed seeds, so re-running reproduces almost exactly: that checks determinism,
it is not an independent replication.

- **01:** in one run temperature 0 gave 2 different outputs across 3 seeds (in the recorded run all 3 matched), and in every run the model said Bengaluru is "hot and dry" in July (it is monsoon season). Fluent is not correct.
- **02:** a vague "extract as JSON" prompt produced 0/4 parseable outputs (markdown fences, invented keys). A clear prompt and the schema-constrained call were both 8/8 (95% CI 68%-100%), so on this model and data the schema showed **no** measurable advantage; one compliment was still filed as "delivery" (content 7/8). The retry loop never had to fire.
- **03:** over n=20 gold queries, hit@3 was dense 20/20 (CI 84%-100%), BM25 18/20 and hybrid 18/20 (CI 70%-97%). The intervals overlap, so this is not evidence that dense beats hybrid; it does show fusion can lose a hit that one retriever had (the "instalments" query).
- **04:** the real model never looped and, in the "needs approval" scenario, never called the refund tool (the crude claim checker flagged its reply). The guards that did not fire on their own are shown with scripted models: a stuck model hits the repeat guard and step budget, and a Rs 1,500 refund returns pending_human_approval. The Rs 25,000 request was blocked by code in every run.
- **06:** a friendlier prompt dropped citations from 100% to 17% of answers, and the gate blocked it. The judge position-bias test is n=5 pairs (consistent 4/5, CI 38%-96%): a demo, not a bias rate.
- **07:** over n=20 questions the poisoned page leaked private data in 20/20 answers (CI 84%-100%); spotlighting gave 17/20 (CI 64%-95%), and the intervals overlap. After the output filter the attacker-URL count is 0/20 **by design** (the filter removes exactly what that check looks for); the independent canary check (any private string anywhere in the text) also found 0/20.
- **08:** a true paraphrase scored 0.657 cosine and a different intent 0.523: too close for a safe semantic-cache threshold.
- **12:** n=5 problems, so accuracy (4/5 at every N) has a very wide interval; the point is the mechanism, and that a vote goes wrong when the most common answer is wrong.

## Cloud steps

Labs never call a paid API. The warehouse versions of lab 10 (BigQuery, Databricks, Snowflake) are printed at the end of
the lab and explained in Track 17; they **need your account (free trial / free tier)** and were not run by us.
