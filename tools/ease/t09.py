"""Pass 2, Section 9: Text-to-SQL (folder track13/). Numbers come from the lesson pages' own
"At real scale" boxes and are recomputed here; the safety-gate play mirrors safe_run.py on 9.3."""
from ease.kit import arrow, box, flow, lines, path_arrow, raw, rect, stack, svg, text, wrap
from ease.t08 import SONNET, bar, fold_where, label_lines, usd


# ---------- 9.2 retrieve the schema, don't dump it (400-table example from the page)
def schema_numbers():
    per_table = 20 + 25 * 12
    full = 400 * per_table
    parts = [("6 table cards", 6 * per_table, "fill-c"), ("sample rows + value notes", 1000, "fill-k"),
             ("2 few-shot examples", 600, "fill-p"), ("instructions", 200, "fill-a")]
    small = sum(p[1] for p in parts)
    return dict(per=per_table, full=full, parts=parts, small=small,
                c_full=full * SONNET[0] / 1e6, c_small=small * SONNET[0] / 1e6)


def schema_svg():
    n = schema_numbers()
    pick = {23, 57, 61, 140, 262, 333}       # which squares light up (positions are arbitrary)
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "Question: “Which refunds came from Canada last month?”", "s b", "start") if not nw else \
            text(14, 20, "“Which refunds came from Canada?”", "s b", "start")
        y = 36
        # 400 table cards as a 25 x 16 grid
        cols, sq, gap = (25, 9, 2) if nw else (20, 11, 3)
        rows = 400 // cols
        gx = 14
        for i in range(400):
            r, c = divmod(i, cols)
            body += bar(gx + c * (sq + gap), y + 22 + r * (sq + gap), sq, sq, "fill-a" if i in pick else "fill-m", 2).replace('class="fill-m"', 'class="fill-m" opacity=".35"')
        gw = cols * (sq + gap)
        gh = rows * (sq + gap)
        body += text(gx, y + 12, "400 table cards, embedded once", "s", "start")
        body += text(gx, y + 22 + gh + 16, "6 nearest to the question light up", "s ac-t", "start")
        if nw:
            y2 = y + 22 + gh + 40
            body += arrow(W / 2, y2 - 14, W / 2, y2 + 8)
            px, pw, y = 14, W - 28, y2 + 16
        else:
            px, pw = gx + gw + 70, W - (gx + gw + 70) - 16
            body += arrow(gx + gw + 14, y + 22 + gh / 2, px - 10, y + 22 + gh / 2)
            y = y + 22
        body += text(px, y + 4, f"The prompt: about {n['small']:,} tokens", "b", "start")
        y += 16
        x = px
        for name, v, f in n["parts"]:
            w = pw * v / n["small"]
            body += bar(x, y, w - 2, 30, f, 3)
            x += w
        y += 46
        for name, v, f in n["parts"]:
            body += bar(px, y - 11, 14, 14, f) + text(px + 20, y + 1, f"{name}: {v:,}", "s", "start")
            y += 21
        y += 14
        # dump vs retrieve
        body += text(px, y, "Dump everything vs retrieve 6 tables (input tokens)", "s b", "start") if not nw else text(px, y, "Dump all vs retrieve 6 (tokens)", "s b", "start")
        y += 12
        body += bar(px, y, pw - 70, 18, "fill-w") + text(px + pw - 64, y + 14, f"{n['full']:,}", "s", "start")
        body += bar(px, y + 26, max(2, (pw - 70) * n["small"] / n["full"]), 18, "fill-g") + text(px + (pw - 70) * n["small"] / n["full"] + 8, y + 40, f"{n['small']:,}", "s", "start")
        y += 62
        tl, th = label_lines(px, y, f"At $2 per million input tokens: {usd(n['c_full'], 3)} vs {usd(n['c_small'])} a question. Miss a needed table and the SQL quietly answers a different question, so measure table recall.", pw, 13, "s")
        body += tl
        H = max(y + th, 36 + 22 + gh + 30) + 6
        out.append(svg(W, H, body, "Schema retrieval: pick the few relevant tables, then build a small prompt", cls))
    return raw(*out)


# ---------- 9.4 what a 3-try loop buys on 1,000 questions (the page's assumptions)
def loop_numbers():
    runs, fail = [820.0], 180.0
    for _ in range(2):
        fixed = fail * 0.7
        runs.append(runs[-1] + fixed)
        fail -= fixed
    calls = 1 + 0.18 + 0.054
    first = 4000 * SONNET[0] / 1e6 + 200 * SONNET[1] / 1e6
    retry = 4400 * SONNET[0] / 1e6 + 200 * SONNET[1] / 1e6
    avg = first + (calls - 1) * retry
    return dict(runs=runs, left=fail, calls=calls, avg=avg, correct=860)


def loop_svg():
    n = loop_numbers()
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "1,000 questions, up to 3 tries each (the page's assumptions)" if not nw else "1,000 questions, up to 3 tries", "b", "start")
        lx = 70 if nw else 150
        bw = W - lx - (60 if nw else 120)
        sc = bw / 1000
        y = 44
        labels = ["try 1", "try 2", "try 3"] if nw else ["try 1", "try 2 (+ error)", "try 3 (+ error)"]
        for i, r in enumerate(n["runs"]):
            body += text(lx - 8, y + 20, labels[i], "s", "end")
            body += f'<rect x="{lx}" y="{y}" width="{bw:g}" height="28" rx="4" class="bx tn-w"/>'
            prev = n["runs"][i - 1] if i else 0
            body += bar(lx, y, prev * sc, 28, "fill-c", 4)
            if i:
                body += bar(lx + prev * sc, y, (r - prev) * sc, 28, "fill-g", 0)
            body += text(lx + bw + 8, y + 19, f"{r:.0f} run", "s b", "start")
            y += 52
        # ceiling: correct answers
        cx = lx + n["correct"] * sc
        body += f'<line x1="{cx:g}" y1="34" x2="{cx:g}" y2="{y-14:g}" class="ln ac dash"/>'
        body += text(cx - 6, y + 2, f"only {n['correct']} are correct", "s ac-t", "end")
        y += 26
        legend = [("fill-c", "ran on an earlier try"), ("fill-g", "fixed by feeding the error back"), ("bx tn-w", "still failing")]
        if nw:
            for f, t in legend:
                body += f'<rect x="14" y="{y-11}" width="14" height="14" rx="3" class="{f}"/>' + text(34, y + 1, t, "s", "start")
                y += 20
        else:
            x = 14
            for f, t in legend:
                body += f'<rect x="{x}" y="{y-11}" width="14" height="14" rx="3" class="{f}"/>' + text(x + 20, y + 1, t, "s", "start")
                x += 20 + len(t) * 7 + 28
            y += 22
        y += 6
        wrong = n["runs"][-1] - n["correct"]
        tail = (f"The loop lifts “runs” from 82% to {n['runs'][-1] / 10:.1f}% for about {usd(n['avg'], 4)} a question "
                f"({n['calls']:.3f} calls on average). But about {wrong:.0f} queries ran fine and gave the wrong answer: no error, so the loop never sees them.")
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Bars: each retry with the error message fixes most failures, but not wrong answers", cls))
    return raw(*out)


N = loop_numbers()
S = schema_numbers()

LESSONS = {
    "9.1": dict(
        plain=["A lot of company data sits in databases, and you need SQL (Structured Query Language) to ask them questions.",
               "Most people who need answers can't write SQL.",
               "Text-to-SQL lets them type a plain question; a language model writes the SQL, the system runs it and answers in words.",
               "The hard part is not the English. It is knowing the tables well enough to write the right query.",
               "The scary failure is a query that runs fine and returns a confident, wrong number."],
        map=[("The manager's question", "A plain-English question: “How much did Canada spend?”"),
             ("The clerk's filing system", "The database schema: tables, columns and how they join"),
             ("The translator's exact instructions", "The generated SQL: which tables, which join, what to add up"),
             ("The translator who never asks “gross or net?”", "A model that guesses on ambiguous questions instead of asking")],
        fig=flow([("Question", "“How much did customers in Canada spend?”", "c"),
                  ("Schema + question", "the model sees the tables customers and orders", "b"),
                  ("Model writes SQL", "SUM(o.amount), JOIN on customer_id, WHERE country = 'Canada'", "a"),
                  ("Safe run", "read-only, row cap, timeout", "k"),
                  ("Answer in words", "“$48,210.50 in total”, with the SQL shown", "g")],
                 "Text-to-SQL: question, schema, SQL, safe run, answer",
                 loop=(3, 2, "on an error, retry with the message")),
        cap="The model only ever writes the query; your code runs it under strict limits and turns the rows into a sentence. The example question, SQL and $48,210.50 result are the ones on this page.",
        line="Text-to-SQL turns a plain question into a database query, runs it safely and answers in words."),
    "9.2": dict(
        plain=["A model can't query a column it doesn't know exists.",
               "So the most important part of the prompt is the schema: the tables, their columns and how they connect.",
               "Short descriptions, a few sample rows and two or three example questions with their SQL help a lot.",
               "A big company might have 400 tables, far too many to paste in every time.",
               "So you first retrieve the handful of tables that match the question, the same way RAG retrieves documents."],
        map=[("The floor map of the library", "The schema: CREATE TABLE lines for the tables involved"),
             ("The section labels", "One-line descriptions and sample values, e.g. country holds 'Canada', not 'CA'"),
             ("Two example call numbers", "Few-shot pairs of question and correct SQL"),
             ("Only the map of the right floor", "Schema retrieval: embed table cards, take the top few for each question")],
        fig=schema_svg(),
        cap=f"Each table gets a short card that is embedded once. For each question, only the closest cards go into the prompt. Token counts use the page's 400-table estimate: {S['full']:,} tokens to dump everything versus about {S['small']:,} retrieved.",
        line="Give the model a clear map of just the tables it needs, and it stops guessing column names."),
    "9.3": dict(
        plain=["Generated SQL is code you did not write, running on your real database.",
               "A tricked or careless model could write a query that deletes data or scans a billion rows.",
               "Asking nicely in the prompt is not a safety control.",
               "Real safety lives in layers around the model: a read-only account, a check that it is one SELECT, a row cap and a timeout.",
               "If one layer misses something, the next one still holds."],
        map=[("Telling the new driver to drive carefully", "The prompt: “return a single SELECT”; a request, not a guarantee"),
             ("No keys to the truck", "A read-only database user, or SQLite opened with mode=ro"),
             ("A small fuel tank", "The row cap: SELECT * FROM ( ... ) LIMIT 1000"),
             ("A speed limiter", "A statement timeout, e.g. Postgres statement_timeout = 15 s"),
             ("Someone hiding a trick in the map", "Prompt injection through the question, column comments or data values")],
        fig=stack([("Check: one SELECT", "no “;” inside, must start with SELECT or WITH", "k"),
                   ("Parameterize user values", "user text is never pasted into the SQL string", "p"),
                   ("Read-only connection", "the database itself refuses any write (the strongest layer)", "w"),
                   ("Row cap wrapper", "SELECT * FROM ( query ) LIMIT 1000", "c"),
                   ("Timeout", "a runaway scan is stopped, e.g. at 15 s", "d")],
                  "Layers a generated SQL query passes through before rows come back",
                  enter="SQL written by the model", leave="at most 1,000 rows back to your app",
                  blocked={0: "stacked statements; DELETE, DROP", 1: "SQL injection through user text", 2: "any write that slipped past the check",
                           3: "a 10-million-row result", 4: "a 33-minute full scan"}),
        cap="Read it top to bottom as one query's journey. Each layer assumes the others can fail. The read-only permission is the one a prompt injection cannot talk its way past.",
        play=("sqlgate", "Pick a candidate query. The picture runs the same checks as this page's safe_run.py and shows which layer passes it or stops it."),
        line="Never trust the prompt for safety: make the database itself unable to do harm."),
    "9.4": dict(
        plain=["The first query a model writes sometimes fails, for example with a wrong column name.",
               "The database's error message says exactly what went wrong.",
               "A self-correcting agent hands that error back to the model and asks for a fixed query.",
               "Cap the loop at two or three tries so it can't spin forever or run up a bill.",
               "It can only fix errors; a query that runs but answers the wrong question needs other checks."],
        map=[("The teacher circling the wrong letter", "The database error, e.g. “no such column: customer.country”"),
             ("Trying again with the circle in view", "The retry prompt carries the error and the failed SQL"),
             ("Only two more tries", "max_tries = 3, then a polite “could not build a query”"),
             ("A wrong answer with perfect spelling", "Valid SQL that answers a different question: no error, no circle")],
        fig=loop_svg(),
        cap="Each retry fixes most of what is left (70% here, an assumption from the page). The dashed line is the ceiling: queries that run but are wrong never trigger a retry. All counts and costs are computed from the page's assumptions.",
        line="Feed the error back and let the model try again, a few times at most, and check the answers separately."),
}
fold_where(LESSONS)
