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

- **01:** in one run temperature 0 gave 2 different outputs across 3 seeds (in the recorded run all 3 matched), and in every run the model said Bengaluru is "hot and dry" in July (it is monsoon season). Fluent is not correct.
- **02:** a vague "extract as JSON" prompt produced 0/4 parseable outputs (markdown fences, invented keys); the schema-constrained call produced 8/8, but one compliment was still filed as "delivery".
- **03:** on this small corpus dense retrieval scored hit@3 = 6/6 and RRF hybrid 5/6: fusion pushed the right EMI page out for "instalments". Hybrid is not automatically better.
- **04:** in an early run the agent told a customer "Rs 300 will be refunded shortly" without calling the refund tool; in the recorded run it ignored the refund request instead, and the checker flags it as IGNORED REQUEST. The Rs 25,000 request was blocked by code in every run.
- **06:** a friendlier prompt dropped citations from 100% to 17% of answers; the LLM judge preferred the same answer position regardless of content on one of five pairs.
- **07:** the poisoned page leaked email and phone in 5/5 answers; spotlighting alone only brought it to 4/5 on a 7B model; the deterministic output filter brought it to 0/5.
- **08:** a true paraphrase scored 0.657 cosine and a different intent 0.523: too close for a safe semantic-cache threshold.
- **12:** majority voting did not help: on one problem the most common answer was wrong.

Your numbers will move a little between runs; the conclusions should not.

## Cloud steps

Labs never call a paid API. The warehouse versions of lab 10 (BigQuery, Databricks, Snowflake) are printed at the end of
the lab and explained in Track 17; they **need your account (free trial / free tier)** and were not run by us.
