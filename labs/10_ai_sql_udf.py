"""Lab 10 - "LLM inside SQL": a local stand-in for BigQuery AI.GENERATE, Snowflake AI_COMPLETE and Databricks ai_query.

Lessons: 17.1-17.4 (GenAI on your data platform).
Run:   python labs/10_ai_sql_udf.py

All three warehouses now let you call a model from a SELECT, one call per row. DuckDB lets us register a
Python function as a SQL function, so we can feel the same pattern - and its costs - on a laptop.
The real cloud SQL is printed at the end; running it needs your account (free trial / free tier).
"""
import json
import time
from functools import lru_cache

import duckdb

from common import MODEL, ask, check_ollama, embed, header

check_ollama()
CALLS = {"llm": 0, "cache_hits": 0}


@lru_cache(maxsize=10_000)
def _cached(prompt: str) -> str:
    CALLS["llm"] += 1
    return ask(prompt, num_predict=40).strip()


def ai_generate(prompt: str) -> str:
    before = CALLS["llm"]
    out = _cached(prompt)
    CALLS["cache_hits"] += CALLS["llm"] == before
    return out


def ai_classify(text: str, labels: str) -> str:
    out = ai_generate(f"Classify the text into exactly one of [{labels}]. Reply with the label only.\nText: {text}").lower()
    allowed = [l.strip() for l in labels.split(",")]
    return next((l for l in allowed if l in out), "unknown")  # never let free text leak into a label column


def ai_embed(text: str) -> list:
    return embed([text])[0].tolist()


con = duckdb.connect()
con.create_function("ai_generate", ai_generate, ["VARCHAR"], "VARCHAR")
con.create_function("ai_classify", ai_classify, ["VARCHAR", "VARCHAR"], "VARCHAR")
con.create_function("ai_embed", ai_embed, ["VARCHAR"], "FLOAT[384]")

con.execute("""CREATE TABLE reviews AS SELECT * FROM (VALUES
 (1, 'MX-750', 'Grinds idli batter smoothly, motor stays cool. Worth it.'),
 (2, 'MX-750', 'Jar lid cracked in a week, customer care never called back.'),
 (3, 'KT-20',  'Kettle is okay. Boils fast but the handle gets hot.'),
 (4, 'KT-20',  'Stopped working after the warranty ended, exactly one year.'),
 (5, 'MX-750', 'Loud, but does the job for chutneys.'),
 (6, 'MX-750', 'Grinds idli batter smoothly, motor stays cool. Worth it.')
) t(review_id, sku, review)""")

header(f"1) Row-by-row LLM calls from SQL  (model: {MODEL})")
t0 = time.perf_counter()
rows = con.execute("""
  SELECT review_id, sku,
         ai_classify(review, 'positive,negative,mixed') AS sentiment,
         ai_generate('In 6 words or fewer, name the main product issue, or say none: ' || review) AS issue
  FROM reviews ORDER BY review_id""").fetchall()
for r in rows:
    print(f"  {r[0]} {r[1]:7s} {r[2]:9s} {r[3]!r}")
print(f"  rows=6  llm_calls={CALLS['llm']}  cache_hits={CALLS['cache_hits']}  wall={time.perf_counter() - t0:.1f}s")
print("  Look: 6 rows x 2 AI columns = up to 12 model calls. Review 6 duplicates review 1, so the cache saved 2.")
print("  On 10 M rows that is 20 M calls: filter and dedupe BEFORE the AI function, never after.")
print("  Spot-check the issue column against the review text: a small model can add details the review never")
print("  says. An AI column is model output, so it needs the same eval set and spot checks as any other.")

header("2) Aggregate AI output like any other column")
for r in con.execute("""
  WITH s AS (SELECT sku, ai_classify(review, 'positive,negative,mixed') AS sentiment FROM reviews)
  SELECT sku, sentiment, COUNT(*) FROM s GROUP BY ALL ORDER BY sku, sentiment""").fetchall():
    print("  ", r)
print("  (served from cache: identical prompts are not re-sent)")

header("3) Vector search in SQL: embed once into a column, query by cosine")
con.execute("ALTER TABLE reviews ADD COLUMN v FLOAT[384]")
con.execute("UPDATE reviews SET v = ai_embed(review)")
q = "product broke soon after buying"
for r in con.execute("""SELECT review_id, CAST(array_cosine_similarity(v, ai_embed(?)) AS DECIMAL(5,3)) AS sim, review
                        FROM reviews ORDER BY sim DESC LIMIT 3""", [q]).fetchall():
    print("  ", r)

header("4) The same pattern on your platforms  (needs your account - free trial / free tier)")
CLOUD = {
    "BigQuery (AI.GENERATE, docs read 2026-11-03)":
        "SELECT review_id, AI.GENERATE(CONCAT('Classify sentiment as positive, negative or mixed: ', review)).result AS sentiment\n"
        "FROM `my_project.shop.reviews`;",
    "Snowflake Cortex (AI_COMPLETE)":
        "SELECT review_id, AI_COMPLETE('claude-haiku-4-5', 'Classify sentiment as positive, negative or mixed: ' || review) AS sentiment\n"
        "FROM shop.reviews;",
    "Databricks SQL (ai_query)":
        "SELECT review_id, ai_query('system.ai.meta-llama-3-3-70b-instruct', CONCAT('Classify sentiment as positive, negative or mixed: ', review)) AS sentiment\n"
        "FROM shop.reviews;",
}
for k, v in CLOUD.items():
    print(f"  -- {k}\n  " + v.replace("\n", "\n  "))
print("  Model and endpoint names change often: check the current list in each doc page before you run these.")
print(json.dumps(CALLS))
