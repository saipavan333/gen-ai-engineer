"""Lab 09 - Text-to-SQL you can put in front of a database: grounding, a parser-based gate, self-correction, scoring.

Lessons: 9.1-9.4 (why text-to-SQL, schema-aware prompting, safe SQL, self-correcting agent).
Run:   python labs/09_text_to_sql_duckdb.py

DuckDB stands in for your warehouse (BigQuery / Snowflake / Databricks SQL). The safety ideas carry over
directly: parse, allow only SELECT, run as a read-only principal, cap rows and time.
"""
import atexit
import random
import re
import shutil
import tempfile
from pathlib import Path

import duckdb

from common import ask, check_ollama, header

check_ollama()

# ------------------------------------------------------------ build a small, realistic warehouse
random.seed(11)
_tmp = tempfile.mkdtemp(prefix="lab09-")
atexit.register(shutil.rmtree, _tmp, True)  # remove the scratch database when the lab ends
db_path = Path(_tmp) / "shop.duckdb"
w = duckdb.connect(str(db_path))
cities = ["Bengaluru", "Hyderabad", "Chennai", "Mumbai", "Pune", "Delhi", "Kolkata", "Jaipur"]
w.execute("CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, name VARCHAR, city VARCHAR, signup_date DATE, is_plus BOOLEAN)")
w.execute("CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date DATE, status VARCHAR, amount_rs DECIMAL(10,2))")
w.executemany("INSERT INTO customers VALUES (?, ?, ?, DATE '2024-01-01' + CAST(? AS INTEGER), ?)",
              [(i, f"cust_{i}", random.choice(cities), random.randint(0, 600), random.random() < 0.3) for i in range(1, 501)])
w.executemany("INSERT INTO orders VALUES (?, ?, DATE '2025-01-01' + CAST(? AS INTEGER), ?, ?)",
              [(i, random.randint(1, 450), random.randint(0, 540), random.choices(["delivered", "returned", "cancelled"], [85, 10, 5])[0],
                round(random.uniform(149, 9999), 2)) for i in range(1, 6001)])
w.close()
ro = duckdb.connect(str(db_path), read_only=True)  # the app's connection can't write, whatever SQL arrives

SCHEMA = """Tables (DuckDB SQL):
customers(customer_id INTEGER, name VARCHAR, city VARCHAR, signup_date DATE, is_plus BOOLEAN)  -- is_plus = paid Plus member
orders(order_id INTEGER, customer_id INTEGER -> customers.customer_id, order_date DATE,
       status VARCHAR  -- one of 'delivered','returned','cancelled'
       , amount_rs DECIMAL(10,2))  -- order value in rupees
Revenue means SUM(amount_rs) over orders with status = 'delivered'."""

SYSTEM = ("You write one DuckDB SQL SELECT query that answers the question using only the given schema. "
          "Return only the SQL, no explanation, no markdown fences.\n" + SCHEMA)


def gate(sql: str):
    """Parser-based allowlist: exactly one statement and it must be a SELECT (CTEs parse as SELECT)."""
    try:
        stmts = ro.extract_statements(sql)
    except Exception as e:
        return False, f"parse error: {e}"
    if len(stmts) != 1:
        return False, f"{len(stmts)} statements; exactly one is allowed"
    if stmts[0].type != duckdb.StatementType.SELECT:
        return False, f"{stmts[0].type.name} is not allowed (SELECT only)"
    return True, "ok"


def run_sql(sql: str, limit: int = 1000):
    ok, why = gate(sql)
    if not ok:
        raise PermissionError(why)
    body = sql.strip().rstrip(";")
    # newlines matter: a trailing "-- comment" in model SQL would otherwise swallow ") AS q LIMIT ..."
    return ro.execute(f"SELECT * FROM (\n{body}\n) AS q LIMIT {limit}").fetchall()


def clean(sql: str) -> str:
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.M).strip()


def text_to_sql(question: str, max_fixes: int = 1):
    sql = clean(ask(question, system=SYSTEM, num_predict=200))
    for attempt in range(max_fixes + 1):
        try:
            return sql, run_sql(sql), attempt
        except PermissionError:
            raise
        except Exception as e:  # SQL error -> show the model the error once and let it fix the query
            if attempt == max_fixes:
                return sql, f"ERROR: {str(e).splitlines()[0]}", attempt
            sql = clean(ask(f"Question: {question}\nYour SQL:\n{sql}\nfailed with: {str(e).splitlines()[0]}\n"
                            "Return a corrected query.", system=SYSTEM, num_predict=200))


QUESTIONS = [
    ("How many customers live in Hyderabad?", "SELECT COUNT(*) FROM customers WHERE city = 'Hyderabad'"),
    ("What was total revenue in 2025?",
     "SELECT SUM(amount_rs) FROM orders WHERE status = 'delivered' AND order_date >= DATE '2025-01-01' AND order_date < DATE '2026-01-01'"),
    ("Which 3 cities had the most delivered revenue? Return city and revenue.",
     "SELECT c.city, SUM(o.amount_rs) AS rev FROM orders o JOIN customers c USING (customer_id) WHERE o.status = 'delivered' GROUP BY c.city ORDER BY rev DESC LIMIT 3"),
    ("What share of orders were returned? Give a fraction between 0 and 1.",
     "SELECT AVG(CASE WHEN status = 'returned' THEN 1.0 ELSE 0 END) FROM orders"),
    ("Average delivered order value for Plus members vs non-members.",
     "SELECT c.is_plus, AVG(o.amount_rs) FROM orders o JOIN customers c USING (customer_id) WHERE o.status = 'delivered' GROUP BY c.is_plus ORDER BY c.is_plus"),
    ("How many customers placed no orders at all?",
     "SELECT COUNT(*) FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)"),
]


def same(a, b):
    """Execution accuracy: compare result sets, order-insensitive, numbers rounded."""
    norm = lambda rows: sorted(tuple(round(float(x), 2) if isinstance(x, (int, float)) or hasattr(x, "as_integer_ratio") else x for x in r) for r in rows)
    try:
        return norm(a) == norm(b)
    except Exception:
        return False


header("1) The safety gate on hostile or sloppy SQL (no LLM involved)")
print(f"  row cap survives a trailing comment: {len(run_sql('SELECT * FROM orders -- all of them'))} rows (cap 1000)")
for sql in ["SELECT 1", "DELETE FROM orders", "SELECT 1; DROP TABLE orders",
            "WITH x AS (SELECT * FROM orders) SELECT COUNT(*) FROM x", "UPDATE customers SET is_plus = true"]:
    print(f"  {sql[:50]:52s} -> {gate(sql)}")
try:
    ro.execute("CREATE TABLE hack(a INT)")
except Exception as e:
    print(f"  even if the gate missed one, the read-only connection refuses writes: {type(e).__name__}")

header("2) Natural language -> SQL -> result, scored by execution accuracy")
score = 0
for q, gold_sql in QUESTIONS:
    sql, res, fixes = text_to_sql(q)
    gold = ro.execute(gold_sql).fetchall()
    ok = not isinstance(res, str) and same(res, gold)
    score += ok
    print(f"  Q: {q}\n     SQL: {' '.join(sql.split())[:150]}\n     {'PASS' if ok else 'FAIL'} fixes={fixes} got={str(res)[:80]} gold={str(gold)[:80]}")
print(f"\n  execution accuracy: {score}/{len(QUESTIONS)}")

header("3) A user asks for something destructive")
try:
    text_to_sql("Delete all cancelled orders to clean up the table.")
    print("  model produced a SELECT instead (fine: nothing can be deleted either way)")
except PermissionError as e:
    print(f"  blocked by the gate: {e}")
print("  Look: safety comes from the parser + read-only principal + row cap, not from asking the model nicely.")
print("  Wrong-but-valid SQL (a FAIL above) is the harder problem; only an eval set with gold answers catches it.")
