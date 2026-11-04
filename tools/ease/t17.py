"""Pass 2, Section 17 (folder track17/): GenAI on your data platform.

These lessons have concrete pass-1 analogies, so `pic` is omitted and the old box is folded in.
Every number below is either the page's own scenario arithmetic, recomputed here from its stated inputs,
or labelled. Function names and arguments are exactly as the pages state them (docs read 2026-11-03).
"""
import math

from ease.kit import arrow, box, box_h, lines, path_arrow, raw, rect, svg, text, wrap

# ---------- 17.1 the row funnel and what placement costs (page scenario: 12 M reviews, 25% duplicates)
ROWS, DUP, NEW_DAY, NEW_DISTINCT = 12_000_000, 0.25, 60_000, 45_000
TOK_IN, TOK_OUT, P_IN, P_OUT = 120, 5, 0.10, 0.50  # Claude Haiku 5.5 list price per million tokens, checked 2026-11-03
DASHBOARDS, SCANS = 40, 5


def cost(calls):
    return calls * TOK_IN * P_IN / 1e6 + calls * TOK_OUT * P_OUT / 1e6


def money(v):
    return f"${v:,.2f}" if v < 1000 else f"${v:,.0f}"


def funnel_svg():
    distinct = int(ROWS * (1 - DUP))
    naive, dd = cost(ROWS), cost(distinct)
    view = DASHBOARDS * SCANS * naive
    daily = cost(NEW_DISTINCT)
    designs = [("A view: 40 dashboards × 5 scans a day", view, "per day", "w"),
               ("Back-fill, no dedupe", naive, "once", "k"),
               ("Back-fill after SELECT DISTINCT", dd, "once", "c"),
               ("Daily incremental, 45,000 new distinct texts", daily, "per day", "g")]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        x0, bw = (12, W - 24) if nw else (20, W - 40)
        body = text(x0, 20, "Rows reaching the AI function decide the bill", "b", "start", 14 if nw else 15)
        y = 34
        stages = [("reviews table", ROWS, "rows", "fill-m"), ("after SELECT DISTINCT", distinct, "rows", "fill-c"),
                  ("AI function: one model call per row", distinct, "calls", "fill-a")]
        for i, (lab, n, unit, fc) in enumerate(stages):
            w = bw * n / ROWS
            body += f'<rect x="{x0:g}" y="{y:g}" width="{w:g}" height="26" rx="5" class="{fc}"/>'
            body += text(x0 + 10, y + 18, f"{n:,} {unit}", "badge-t", "start", 13)
            if not nw:
                body += text(x0 + w - 10, y + 18, lab, "badge-t", "end", 13)
            if nw:
                body += text(x0, y + 42, lab, "s", "start", 12)
                y += 16
            y += 36
        b, h = box(x0, y, bw, "Map the answer onto the label set, else ‘unknown’, then write a table", "positive / negative / mixed / unknown, materialised once", "g", size=13 if nw else 14)
        if nw:
            y += 6
            b, h = box(x0, y, bw, "Map the answer onto the label set, else ‘unknown’, then write a table", "positive / negative / mixed / unknown, materialised once", "g", size=13)
        body += ("" if nw else arrow(x0 + 20, y - 8, x0 + 20, y - 1)) + b
        y += h + 28
        # log-scale cost bars
        body += text(x0, y, "Cost of each design at the reference price (log scale)", "b", "start", 13 if nw else 14)
        y += 10
        lab_w = 0 if nw else 300
        bx0, bww = x0 + lab_w, bw - lab_w - (0 if nw else 4)
        lo, hi = -1, 5  # $0.10 .. $100,000
        for k in range(lo, hi + 1):
            gx = bx0 + bww * (k - lo) / (hi - lo)
            body += f'<line x1="{gx:g}" y1="{y+6:g}" x2="{gx:g}" y2="{y + 14 + len(designs) * (48 if nw else 34):g}" class="grid"/>'
        y += 14
        for lab, v, per, tone in designs:
            if nw:
                body += text(x0, y + 12, lab, "s", "start", 12)
                y += 16
            else:
                body += text(x0 + lab_w - 10, y + 17, lab, "s", "end", 13)
            w = max(4, bww * (math.log10(v) - lo) / (hi - lo))
            body += f'<rect x="{bx0:g}" y="{y+3:g}" width="{w:g}" height="20" rx="4" class="fill-{tone}"/>'
            vt = f"{money(v)} {per}"
            inside = w > len(vt) * 7.2 + 16
            body += text(bx0 + (w - 8 if inside else w + 6), y + 18, vt, "badge-t" if inside else "s b", "end" if inside else "start", 13)
            y += 32
        for k in (lo, 1, 3, hi):
            gx = bx0 + bww * (k - lo) / (hi - lo)
            body += text(gx, y + 12, money(10 ** k).replace(".00", "") if k >= 0 else "$0.10", "s m", "start" if k == lo else "end" if k == hi else "middle", 12)
        y += 26
        note = (f"{TOK_IN} input + {TOK_OUT} output tokens a call at Claude Haiku 5.5 list price (${P_IN:.2f} / ${P_OUT:.2f} per million, "
                "checked 2026-11-03). Your warehouse's model price differs; the ratios don't.")
        nl = wrap(note, bw, 12)
        body += lines(x0, y + 6, nl, "s m", "start", 12, 16)
        out.append(svg(W, y + 10 + len(nl) * 16, body, "SELECT DISTINCT shrinks the calls; where the AI column lives moves cost by thousands", cls))
    return raw(*out)


# ---------- 17.2 BigQuery: two lifecycles, batch embedding vs per-question RAG
BATCH = [("kb.chunks", "3 M chunks; alias text AS content", "b"),
         ("AI.GENERATE_EMBEDDING", "remote embedding model; 900 M tokens, run once", "c"),
         ("kb.chunk_emb", "adds embedding ARRAY<FLOAT64>; other columns kept", "c"),
         ("CREATE VECTOR INDEX", "for millions of rows: approximate, fast", "k")]
ASK = [("The question", "embedded with AI.GENERATE_EMBEDDING, same model", "a"),
       ("VECTOR_SEARCH", "top_k => 3, distance_type => 'COSINE'; returns query, base, distance", "a"),
       ("Grounded prompt", "answer only from these chunks, cite chunk_id", "a"),
       ("AI.GENERATE", "the answer; NULL means failed or blocked: log it, retry", "g")]


def lanes_svg():
    # wide
    W, n = 760, 4
    BW = [162, 188, 166, 146]
    G = (W - 40 - sum(BW)) / (n - 1)
    XS = [20 + sum(BW[:i]) + i * G for i in range(n)]
    body = ""
    y = 14
    hs = []
    for title, steps, tone in (("Scheduled batch job: embed once, refresh weekly", BATCH, "b"), ("Per question (20,000 a day)", ASK, "a")):
        h = max(box_h(BW[i], t, s, 14) for i, (t, s, _) in enumerate(steps))
        body += rect(10, y, W - 20, h + 46, "b", rx=14) + text(24, y + 22, title, "b ac-t" if tone == "a" else "b", "start", 14)
        yb = y + 34
        for i, (t, s, tn) in enumerate(steps):
            x, bw = XS[i], BW[i]
            b, _ = box(x, yb, bw, t, s, tn, h=h, size=14)
            body += b
            if i < n - 1:
                body += arrow(x + bw + 3, yb + h / 2, x + bw + G - 3, yb + h / 2)
        hs.append((yb, h))
        y += h + 46 + 40
    # cross-lane: chunk_emb feeds VECTOR_SEARCH
    (y1, h1), (y2, _h2) = hs
    xa = XS[2] + BW[2] / 2
    xb = XS[1] + BW[1] / 2
    ym = y1 + h1 + 30
    body += path_arrow([(xa, y1 + h1 + 2), (xa, ym), (xb, ym), (xb, y2 - 3)], "ac")
    body += text(xa + 8, ym - 6, "searched by", "s ac-t", "start", 13)
    yf = y - 30
    body += text(20, yf + 8, "Weekly refresh: 2% of 150,000 documents change, so re-embed only about 60,000 chunks, keyed on a content hash.", "s", "start", 13)
    wide = svg(W, yf + 20, body, "BigQuery RAG as two lifecycles: a batch embedding job and a per-question path", "ez-wide")
    # tall
    W2 = 360
    body = ""
    y = 10
    for title, steps, tone in (("Batch job: embed once, refresh weekly", BATCH, "b"), ("Per question (20,000 a day)", ASK, "a")):
        top = y
        y += 30
        inner = ""
        for i, (t, s, tn) in enumerate(steps):
            b, h = box(24, y, W2 - 48, t, s, tn, size=14)
            inner += b
            y += h
            if i < len(steps) - 1:
                inner += arrow(W2 / 2, y + 3, W2 / 2, y + 19)
            y += 22
        body += rect(10, top, W2 - 20, y - top - 8, "b", rx=14) + text(22, top + 21, title, "b ac-t" if tone == "a" else "b", "start", 14) + inner
        if tone == "b":
            body += arrow(40, y - 6, 40, y + 20, "ac") + text(52, y + 12, "VECTOR_SEARCH reads kb.chunk_emb", "s ac-t", "start", 12)
            y += 28
    body += text(12, y + 6, "Weekly: re-embed only ~60,000 changed", "s", "start") + text(12, y + 24, "chunks (2%), keyed on a content hash.", "s", "start")
    tall = svg(W2, y + 34, body, "BigQuery RAG as two lifecycles: a batch embedding job and a per-question path", "ez-tall")
    return raw(wide, tall)


# ---------- 17.3 failOnError: one bad row costs the night, or one row (page scenario: 800,000 tickets, 0.1% time out)
TICKETS, FAIL_RATE, FAIL_AT = 800_000, 0.001, 612_004
TK_IN, TK_OUT = 240, 25  # 180 tokens of ticket + 60 of instruction; 25-token JSON answer


def failonerror_svg():
    failed = round(TICKETS * FAIL_RATE)
    night = TICKETS * TK_IN * P_IN / 1e6 + TICKETS * TK_OUT * P_OUT / 1e6
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        pw = W - 24 if nw else (W - 60) / 2
        panels = [("failOnError true (the default)", "w"), ("failOnError => false", "g")]
        body = ""
        y0 = 12
        for k, (title, tone) in enumerate(panels):
            px = 12 if nw else 20 + k * (pw + 20)
            py = y0 if not nw else y0 + k * 236
            body += rect(px, py, pw, 222, tone, rx=14)
            body += text(px + 16, py + 26, title, "b mono", "start", 14)
            bx, bwid, by = px + 16, pw - 32, py + 50
            body += text(bx, by - 6, f"{TICKETS:,} ai_query calls, one per ticket", "s", "start", 12)
            if k == 0:
                done = bwid * FAIL_AT / TICKETS
                body += f'<rect x="{bx:g}" y="{by:g}" width="{bwid:g}" height="26" rx="4" class="bx"/>'
                body += f'<rect x="{bx:g}" y="{by:g}" width="{done:g}" height="26" rx="4" class="fill-m"/>'
                body += f'<line x1="{bx+done:g}" y1="{by-4:g}" x2="{bx+done:g}" y2="{by+32:g}" class="ln wn" style="stroke-width:3"/>'
                body += text(bx + done, by + 48, f"row {FAIL_AT:,} times out", "s wn-t b", "end" if nw else "middle", 13)
                rows = ["The whole statement fails.", "Rows written: 0.",
                        f"A retry pays again for {FAIL_AT // 1000} K rows,", "and at this scale some row always fails."]
            else:
                body += f'<rect x="{bx:g}" y="{by:g}" width="{bwid:g}" height="26" rx="4" class="fill-g"/>'
                for j in range(8):  # where the failures fall is illustrative
                    tx = bx + bwid * (0.07 + 0.12 * j + 0.03 * (j % 3))
                    body += f'<line x1="{tx:g}" y1="{by-3:g}" x2="{tx:g}" y2="{by+29:g}" class="ln wn" style="stroke-width:2"/>'
                body += text(bx, by + 48, f"{failed:,} rows (0.1%) return an error", "s wn-t b", "start", 13)
                rows = ["Each row returns a struct: response + error.", f"Rows written: {TICKETS - failed:,}.",
                        f"Then retry only the {failed:,} failed rows.", "One bad row costs one row, not the night."]
            body += lines(bx, by + 78, rows, "", "start", 14, 20)
        H = (y0 + 2 * 236) if nw else (y0 + 222 + 14)
        nt = f"Same {TICKETS:,} tickets either way: {TK_IN} input + {TK_OUT} output tokens each, about ${night:,.0f} a night at the page's reference price."
        nl = wrap(nt, W - 40, 12)
        body += lines(12 if nw else 20, H + 12, nl, "s m", "start", 12, 16)
        out.append(svg(W, H + 18 + len(nl) * 16, body, "ai_query with failOnError true versus false on a nightly batch", cls))
    return raw(*out)


# ---------- 17.4 Snowflake: the privilege gate, the search service, and what TARGET_LAG costs
LAGS = [("1 minute", 1), ("1 hour", 60), ("1 day", 1440)]


def cortex_svg():
    steps = [("Role check", "USE AI FUNCTIONS account privilege + CORTEX_USER or AI_FUNCTIONS_USER database role", "w"),
             ("Cortex Search", "filter on ATTRIBUTES region; vector + keyword search, then semantic rerank", "c"),
             ("AI_COMPLETE", "model, prompt (with the retrieved snippets), response_format", "a"),
             ("Grounded answer", "only from transcripts this agent may see", "g")]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = ""
        if nw:
            y = 10
            for i, (t, s, tone) in enumerate(steps):
                b, h = box(12, y, W - 24, t, s, tone, size=14, num=i + 1)
                body += b
                y += h
                if i < len(steps) - 1:
                    body += arrow(W / 2, y + 3, W / 2, y + 21)
                y += 24
        else:
            n, G = len(steps), 30
            bw = (W - 40 - (n - 1) * G) / n
            h = max(box_h(bw, t, s, 14) for t, s, _ in steps)
            for i, (t, s, tone) in enumerate(steps):
                x = 20 + i * (bw + G)
                b, _ = box(x, 14, bw, t, s, tone, h=h, size=14, num=i + 1)
                body += b
                if i < n - 1:
                    body += arrow(x + bw + 3, 14 + h / 2, x + bw + G - 3, 14 + h / 2)
            y = 14 + h + 30
        x0, bw2 = (12, W - 24) if nw else (20, W - 40)
        body += text(x0, y, "TARGET_LAG: how stale search may get, and the refresh work it buys", "b", "start", 13 if nw else 14) if not nw else \
            text(x0, y, "TARGET_LAG sets the refresh work", "b", "start", 14)
        y += 14
        lab_w = 86 if nw else 120
        mx = 1440
        for lab, mins in LAGS:
            per_day = 1440 // mins
            w = max(4, (bw2 - lab_w - 120) * per_day / mx)
            body += text(x0 + lab_w - 10, y + 17, lab, "s b", "end", 13)
            body += f'<rect x="{x0+lab_w:g}" y="{y+3:g}" width="{w:g}" height="20" rx="4" class="fill-{"w" if mins == 1 else "c"}"/>'
            body += text(x0 + lab_w + w + 8, y + 18, f"about {per_day:,} a day", "s", "start", 13)
            y += 30
        tl = wrap("Policy docs that change twice a week: hours to a day is enough. A live support queue may justify minutes. Pick it per corpus.", bw2, 12)
        body += lines(x0, y + 10, tl, "s m", "start", 12, 16)
        out.append(svg(W, y + 14 + len(tl) * 16, body, "A Cortex RAG request through the privilege gate, and refreshes per day for each TARGET_LAG", cls))
    return raw(*out)


LESSONS = {
    "17.1": dict(
        plain=["BigQuery, Databricks and Snowflake all let you call a language model from inside a SQL query.",
               "You pass a prompt built from a row's columns, and the answer comes back as a new column.",
               "On BigQuery the function is AI.GENERATE, on Snowflake AI_COMPLETE, and on Databricks ai_query.",
               "The catch: the model runs once for every row that reaches the function, and you pay per call.",
               "So filter and remove duplicates first, ask for a fixed answer shape, and check the answers."],
        map=[("The reader who charges per page", "The hosted model behind AI.GENERATE, AI_COMPLETE or ai_query"),
             ("Each page you hand over", "Each row that reaches the AI function: one model call"),
             ("Throwing out the duplicate copies", "SELECT DISTINCT on the text before the function runs"),
             ("Skipping pages read last week", "An incremental job: only new or changed rows"),
             ("Keeping the reader's notes in a file", "Materialising the AI column in a table, never a view")],
        fig=funnel_svg(),
        cap="Top: dedupe shrinks the rows before the model sees them. Bottom: the page's four designs, recomputed from its numbers. The model is the same in all four; where the AI function sits moves the bill from cents to tens of thousands of dollars.",
        play=("dedupe", "Set the rows, the share of distinct texts and the number of AI columns. Calls and cost are computed both ways; the Lab 10 preset reproduces the lab's 12 AI cells and 10 calls."),
        line="The model runs once per row it sees, so cut the rows before you call it and store the answer in a table."),
    "17.2": dict(
        plain=["On Google Cloud you can build a whole RAG system in BigQuery SQL. RAG (retrieval-augmented generation) means: find the right passages first, then answer from them.",
               "AI.GENERATE_EMBEDDING turns each chunk of text into an embedding, a list of numbers that captures its meaning.",
               "VECTOR_SEARCH finds the chunks whose embeddings are closest to the question's.",
               "AI.GENERATE sends the question plus those chunks to a Gemini model and returns the answer.",
               "Embedding is a scheduled batch job; searching and answering happen once per question."],
        map=[("A sticky note on every book", "An embedding column, made once by AI.GENERATE_EMBEDDING (the input column must be called content)"),
             ("Writing your question on a sticky note", "Embedding the question with AI.GENERATE_EMBEDDING and the same model"),
             ("Finding the books whose notes look most alike", "VECTOR_SEARCH with top_k and distance_type; it returns query, base and distance"),
             ("The helper who writes using only those pages", "AI.GENERATE with a grounded prompt that cites chunk_id"),
             ("A card catalogue for a huge library", "CREATE VECTOR INDEX, so search over millions of rows is approximate and fast")],
        fig=lanes_svg(),
        cap="Two lifecycles, two lanes. The top lane runs on a schedule and touches every chunk; the bottom lane runs per question and only reads the stored embeddings. Scale figures are the page's scenario (3 M chunks, 20,000 questions a day).",
        line="Embed your table once on a schedule, then for each question search the stored embeddings and answer from what you found."),
    "17.3": dict(
        plain=["On Databricks the same RAG path runs on Delta tables, governed by Unity Catalog.",
               "A Vector Search index is built from a table, and the vector_search() SQL function queries it.",
               "Its HYBRID mode adds keyword matching, which helps with exact codes like part numbers.",
               "ai_query(endpoint, request) calls a model serving endpoint once per row.",
               "For big batch jobs, one setting matters most: failOnError.",
               "Set it to false, so one failing row returns an error instead of failing the whole job."],
        map=[("The library", "Delta tables and the Vector Search index built from them"),
             ("The helper who writes answers", "A model serving endpoint, called once per row by ai_query"),
             ("The rule book", "Unity Catalog grants: the definer needs SELECT on the index"),
             ("The office only enforcing rules it knows about", "Grants protect only the tables, index and endpoints you put under Unity Catalog")],
        fig=failonerror_svg(),
        cap="The page's scenario: 800,000 tickets a night and 0.1% of calls time out. With the default, one timeout throws away the night. With failOnError => false every row is written and only the failures are retried. Where the red ticks fall on the right is illustrative.",
        line="On Databricks, ai_query calls a model per row, so set failOnError => false and retry only the rows that failed."),
    "17.4": dict(
        plain=["Snowflake splits RAG into two pieces that stay inside your account.",
               "Cortex Search is a managed search service: each query mixes vector search, keyword search and a semantic rerank.",
               "AI_COMPLETE is a SQL function that sends a prompt to a model hosted in Snowflake.",
               "TARGET_LAG sets how fresh the search must stay, and fresher costs more refresh work.",
               "To use any of it, a role needs the USE AI FUNCTIONS privilege and the CORTEX_USER or AI_FUNCTIONS_USER database role."],
        map=[("How fresh the shelves must be", "TARGET_LAG on the Cortex Search service"),
             ("The re-shelving work", "Refresh work that keeps the service within TARGET_LAG of the source table"),
             ("Finding the right books", "Hybrid retrieval: vector + keyword search, then semantic reranking"),
             ("The helper who reads and writes the answer", "AI_COMPLETE(model, prompt [, model_parameters, response_format, show_details])"),
             ("Only reading your own region's shelf", "Filtering on an ATTRIBUTES column (region) set by your code")],
        fig=cortex_svg(),
        cap="Top: one request, from the privilege check to a grounded answer. Bottom: refreshes a day for three TARGET_LAG settings (1,440 minutes a day divided by the lag). The page's contact-centre scenario uses 1 hour: about 24 refreshes instead of 1,440.",
        line="Cortex Search finds the passages, AI_COMPLETE writes the answer, and TARGET_LAG is the dial between fresh and cheap."),
}
