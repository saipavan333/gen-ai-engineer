"""Pass 2, Track 3: RAG."""
from ease.kit import arrow, box, box_h, compare, flow, lines, path_arrow, raw, rect, stack, svg, text, wrap


def _lane(body, x0, y, bw, G, steps, size=14, h=None):
    """Boxes left to right with arrows. Returns (body, height, centres)."""
    h = h or max(box_h(bw, t, s, size) for t, s, _ in steps)
    cs = []
    for i, (t, s, tone) in enumerate(steps):
        x = x0 + i * (bw + G)
        b, _ = box(x, y, bw, t, s, tone, h=h, size=size)
        body += b
        cs.append(x + bw / 2)
        if i < len(steps) - 1:
            body += arrow(x + bw + 3, y + h / 2, x + bw + G - 3, y + h / 2)
    return body, h, cs


def _col(body, x, y, w, steps, size=13, G=22):
    """Boxes top to bottom with arrows. Returns (body, end_y, [(top, h)])."""
    pos = []
    for i, (t, s, tone) in enumerate(steps):
        b, hh = box(x, y, w, t, s, tone, size=size)
        body += b
        pos.append((y, hh))
        if i < len(steps) - 1:
            body += arrow(x + w / 2, y + hh + 2, x + w / 2, y + hh + G - 2)
        y += hh + G
    return body, y - G, pos


# ---------- 3.1 the RAG pipeline: offline indexing lane and online query lane
OFF = [("Your documents", "manuals, policies, tickets", "b"), ("Chunk", "cut into short passages", "c"),
       ("Embed", "each chunk becomes a vector", "c"), ("Vector index", "vectors + text + source, stored", "d")]
ON = [("Question", "“How long is the warranty?”", "b"), ("Embed", "same model as the chunks", "a"),
      ("Retrieve top-k", "the k nearest chunks", "a"), ("Build the prompt", "rules + chunks [1] [2] + question", "a"),
      ("Generate", "“3 years [1]”, cited", "g")]


def rag_svg():
    out = []
    W = 760
    body = text(14, 20, "Offline: indexing (run once, and again when documents change)", "b", "start")
    body, h1, c1 = _lane(body, 14, 32, (W - 28 - 3 * 40) / 4, 40, OFF)
    ysep = 32 + h1 + 26
    body += f'<line x1="10" y1="{ysep}" x2="{W-10}" y2="{ysep}" class="grid dash"/>'
    yon = ysep + 42
    body += text(14, yon - 12, "Online: every question (milliseconds)", "b ac-t", "start")
    body, h2, c2 = _lane(body, 14, yon, (W - 28 - 4 * 24) / 5, 24, ON)
    # index -> retrieve
    xm = (c1[3] + c2[2]) / 2
    body += path_arrow([(c1[3], 32 + h1 + 2), (c1[3], ysep + 10), (c2[2] + 30, ysep + 10), (c2[2] + 30, yon - 3)], "ac")
    body += text(c1[3] - 8, ysep + 28, "search the index", "s ac-t", "end")
    out.append(svg(W, yon + h2 + 14, body, "RAG: an offline indexing lane and an online question lane", "ez-wide"))
    # tall: two columns
    W2, cw = 360, 150
    xl, xr = 12, W2 - 12 - cw
    body = text(xl, 18, "Offline: indexing", "b", "start") + text(xr, 18, "Online: each question", "b ac-t", "start")
    body, yl, pl = _col(body, xl, 30, cw, OFF)
    body, yr, pr = _col(body, xr, 30, cw, ON)
    ti, hi = pl[3]
    tr, hr = pr[2]
    gx = xl + cw + (xr - xl - cw) / 2
    body += path_arrow([(xl + cw + 2, ti + hi / 2), (gx, ti + hi / 2), (gx, tr + hr / 2), (xr - 3, tr + hr / 2)], "ac")
    nl = wrap("The arrow from the index into “Retrieve” is the only link between the two lanes.", cw - 6, 13)
    body += lines(xl, yl + 26, nl, "s ac-t", "start", 13, 17)
    out.append(svg(W2, max(yl + 26 + len(nl) * 17, yr) + 14, body, "RAG: an offline indexing lane and an online question lane", "ez-tall"))
    return raw(*out)


# ---------- 3.2 chunk size and overlap, computed on the lesson's real-scale numbers
ART, SIZE, OVER = 1800, 240, 40   # tokens per article, chunk size, overlap (lesson 3.2 "At real scale")


def chunk_spans(n, size, overlap):
    step, spans = size - overlap, []
    for i in range(0, n, step):
        spans.append((i, min(i + size, n)))
        if i + size >= n:
            break
    return spans


SPANS = chunk_spans(ART, SIZE, OVER)
EMBEDDED = sum(b - a for a, b in SPANS)


def chunk_svg():
    out = []
    for W, cls, narrow in ((760, "ez-wide", False), (360, "ez-tall", True)):
        x0, sw = (20, W - 40) if not narrow else (12, W - 24)
        s = sw / ART
        body = text(x0, 20, f"One {ART:,}-token article, chunk size {SIZE}, overlap {OVER}" if not narrow else f"{ART:,} tokens, size {SIZE}, overlap {OVER}", "b", "start")
        y = 34
        body += rect(x0, y, sw, 26, "b", rx=4) + text(x0 + sw / 2, y + 18, "the article as one strip of tokens", "s")
        for t in (0, 600, 1200, 1800):
            body += f'<line x1="{x0+t*s:g}" y1="{y+26}" x2="{x0+t*s:g}" y2="{y+32}" class="ln thin"/>' + text(x0 + t * s, y + 46, f"{t:,}", "s m", "start" if t == 0 else ("end" if t == ART else "middle"))
        y += 60
        labs = ""
        for i, (a, b) in enumerate(SPANS):
            ry = y + (i % 2) * 34
            body += rect(x0 + a * s, ry, (b - a) * s, 26, "c" if i % 2 == 0 else "a", rx=4)
            labs += text(x0 + (a + b) / 2 * s, ry + 18, (str(i + 1) if narrow else f"chunk {i+1}"), "s b")
        # overlap bands, under the labels
        for (a, b), (a2, _) in zip(SPANS, SPANS[1:]):
            body += f'<rect x="{x0+a2*s:g}" y="{y-4}" width="{(b-a2)*s:g}" height="72" class="fill-k" opacity=".4"/>'
        body += labs
        y += 82
        # zoom on the first boundary
        za, zb = 160, 280
        zs = sw / (zb - za)
        if narrow:
            body += lines(x0, y + 4, [f"Zoom on tokens {za} to {zb}:", "where chunk 1 meets chunk 2"], "s b", "start", 13, 17)
        else:
            body += text(x0, y + 4, f"Zoom on tokens {za} to {zb}: the boundary between chunk 1 and chunk 2", "s b", "start")
        y += 14 if not narrow else 30
        a1, b1 = SPANS[0]
        a2, b2 = SPANS[1]
        body += rect(x0, y, (b1 - za) * zs, 28, "c", rx=4) + rect(x0 + (a2 - za) * zs, y + 36, (zb - a2) * zs, 28, "a", rx=4)
        body += f'<rect x="{x0+(a2-za)*zs:g}" y="{y-4}" width="{(b1-a2)*zs:g}" height="72" class="fill-k" opacity=".4"/>'
        body += text(x0 + 6, y + 19, "end of chunk 1 (stops at 240)", "s", "start", 12 if narrow else None)
        body += text(x0 + sw - 6, y + 55, "chunk 2 starts at 200", "s", "end", 12 if narrow else None)
        body += text(x0 + ((a2 + b1) / 2 - za) * zs, y + 86, f"{b1-a2} tokens in both chunks", "s b k-t")
        y += 108
        pct = round((EMBEDDED / ART - 1) * 100)
        msg = f"Step = {SIZE} − {OVER} = {SIZE-OVER}. Result: {len(SPANS)} chunks, {EMBEDDED:,} tokens embedded, about {pct}% more than the article itself."
        for k, ln in enumerate(wrap(msg, sw, 13)):
            body += text(x0, y + k * 18, ln, "s", "start")
        y += len(wrap(msg, sw, 13)) * 18
        out.append(svg(W, y + 4, body, "An article cut into overlapping chunks, with the overlaps shaded", cls))
    return raw(*out)


# ---------- 3.5 top-k with a similarity threshold (illustrative scores)
CH5 = ["The X200 has a 3-year limited warranty.", "Warranty claims need the order number.", "Returns are free within 30 days.",
       "The X200 motor is rated at 1200 watts.", "Cancel under Settings > Billing."]
Q5 = [("“How long is the X200 warranty?”", [0.82, 0.71, 0.46, 0.39, 0.12]),
      ("“Who won the 2022 World Cup?”", [0.21, 0.18, 0.15, 0.11, 0.09])]
K5, TH5 = 3, 0.50


def topk_panel(x0, y, pw, q, scores):
    body = text(x0, y, q, "s b", "start")
    y += 14
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    bw = pw - 50
    used = []
    for r, i in enumerate(order):
        yy = y + r * 44
        intop, above = r < K5, scores[i] >= TH5
        cls = "fill-g" if intop and above else ("fill-w" if intop else "fill-m")
        if intop and above:
            used.append(i)
        body += text(x0, yy + 14, f"{r+1}. {CH5[i]}", "s" if intop else "s m", "start")
        body += f'<rect x="{x0}" y="{yy+20}" width="{max(2, bw*scores[i]):g}" height="14" rx="3" class="{cls}"/>'
        lx, tx = x0 + bw * scores[i] + 6, x0 + bw * TH5
        if lx - 8 < tx < lx + 36:
            lx = tx + 6
        body += text(lx, yy + 32, f"{scores[i]:.2f}", "s", "start")
        if r == K5 - 1:
            body += f'<line x1="{x0-4}" y1="{yy+40}" x2="{x0+pw}" y2="{yy+40}" class="ln thin dash"/>'
            body += text(x0 + pw, yy + 37, f"top-{K5} cut", "s m", "end")
    tx = x0 + bw * TH5
    for r in range(len(scores)):
        body += f'<line x1="{tx:g}" y1="{y+r*44+17}" x2="{tx:g}" y2="{y+r*44+37}" class="ln wn"/>'
    body += f'<line x1="{tx:g}" y1="{y+(len(scores)-1)*44+37}" x2="{tx:g}" y2="{y+len(scores)*44}" class="ln wn dash"/>'
    body += text(tx + 4, y + len(scores) * 44 + 14, f"threshold {TH5:.2f}", "s wn-t", "start")
    yb = y + len(scores) * 44 + 40
    if used:
        verdict = f"→ prompt gets chunks {', '.join(str(order.index(i) + 1) for i in used)}; rank 3 is in the top {K5} but below the threshold, so it stays out"
        cls = "s ok-t"
    else:
        verdict = f"→ refuse: best score {max(scores):.2f} is under {TH5:.2f}, so no chunk is good enough and the model is never called"
        cls = "s wn-t"
    vl = wrap(verdict, pw, 13)
    body += lines(x0, yb, vl, cls, "start", 13, 17)
    return body, yb + len(vl) * 17


def topk_svg():
    out = []
    W = 760
    pw = 345
    b1, e1 = topk_panel(20, 22, pw, *Q5[0])
    b2, e2 = topk_panel(20 + pw + 50, 22, pw, *Q5[1])
    out.append(svg(W, max(e1, e2) + 8, b1 + b2, "Top-k retrieval with a similarity threshold, for an answerable and an off-topic question", "ez-wide"))
    W2 = 360
    b1, e1 = topk_panel(12, 20, W2 - 24, *Q5[0])
    b2, e2 = topk_panel(12, e1 + 34, W2 - 24, *Q5[1])
    out.append(svg(W2, e2 + 8, b1 + b2, "Top-k retrieval with a similarity threshold, for an answerable and an off-topic question", "ez-tall"))
    return raw(*out)


# ---------- 3.6 reciprocal rank fusion on the lesson's own three chunks (k = 60, ranks from 1)
RRF_K = 60
RRF = {"A": (1, 4), "B": (2, None), "C": (30, 1)}   # (dense rank, BM25 rank); None = not in BM25's top 100


def rrf_score(ranks):
    return sum(1 / (RRF_K + r) for r in ranks if r)


def rrf_svg():
    fused = sorted(RRF, key=lambda c: -rrf_score(RRF[c]))
    desc = {"A": "on topic, shares some words", "B": "a close paraphrase", "C": "contains the exact error code"}
    out = []
    for W, cls, narrow in ((760, "ez-wide", False), (360, "ez-tall", True)):
        x0 = 20 if not narrow else 12
        cw = (W - 2 * x0 - 20) / 2
        body = text(x0, 20, "Two ranked lists for one query", "b", "start")
        y = 34
        for col, (title, idx, tone) in enumerate((("Dense (meaning)", 0, "c"), ("BM25 (exact words)", 1, "k"))):
            x = x0 + col * (cw + 20)
            rows = sorted([(RRF[c][idx], c) for c in RRF if RRF[c][idx]])
            body += rect(x, y, cw, 44 + 26 * 3, tone) + text(x + 10, y + 22, title, "s b", "start")
            for k, (r, c) in enumerate(rows):
                body += text(x + 10, y + 46 + k * 26, f"rank {r}: chunk {c}", "s", "start")
            missing = [c for c in RRF if not RRF[c][idx]]
            for k, c in enumerate(missing):
                body += text(x + 10, y + 46 + (len(rows) + k) * 26, f"{c}: not in top 100" if narrow else f"chunk {c}: not in its top 100", "s m", "start")
            body += arrow(x + cw / 2, y + 44 + 26 * 3 + 2, W / 2 + (-30 if col == 0 else 30), y + 44 + 26 * 3 + 34, "ac")
        y += 44 + 26 * 3 + 38
        fh = 44 + 3 * (46 if narrow else 30)
        body += rect(x0, y, W - 2 * x0, fh, "g") + text(x0 + 10, y + 22, f"Fused by RRF: score = sum of 1 / ({RRF_K} + rank) over the lists" if not narrow else f"RRF: sum of 1 / ({RRF_K} + rank)", "s b", "start")
        for k, c in enumerate(fused):
            parts = " + ".join(f"1/{RRF_K + r}" for r in RRF[c] if r)
            line = f"{k+1}. chunk {c} = {parts} = {rrf_score(RRF[c]):.4f}"
            if narrow:
                body += text(x0 + 10, y + 46 + k * 46, line, "s", "start") + text(x0 + 24, y + 64 + k * 46, f"({desc[c]})", "s m", "start")
            else:
                body += text(x0 + 10, y + 48 + k * 30, line, "s", "start") + text(W - x0 - 10, y + 48 + k * 30, desc[c], "s m", "end")
        y += fh
        out.append(svg(W, y + 8, body, "Reciprocal rank fusion combines a dense and a BM25 ranking by rank", cls))
    return raw(*out), fused


RRF_FIG, RRF_ORDER = rrf_svg()


# ---------- 3.8 hit rate@5 and MRR on a three-query golden set (one relevant chunk each)
GOLD = [("how long is the warranty?", 2), ("can I return it?", 1), ("how do I cancel billing?", None)]  # rank of the relevant chunk in the top 5


def eval_svg():
    hits = sum(1 for _, r in GOLD if r)
    mrr = sum((1 / r) if r else 0 for _, r in GOLD) / len(GOLD)
    out = []
    for W, cls, narrow in ((760, "ez-wide", False), (360, "ez-tall", True)):
        x0 = 20 if not narrow else 12
        qw = 0 if narrow else 230
        cell = 52 if not narrow else 44
        body = text(x0, 20, "Top 5 results per query: green = the chunk your label says is right", "s b", "start") if not narrow else lines(x0, 20, ["Top 5 results per query", "green = the labelled right chunk"], "s b", "start", 13, 17)
        y = 36 if not narrow else 48
        gx = x0 + qw
        for k in range(5):
            body += text(gx + k * (cell + 6) + cell / 2, y + 4, f"#{k+1}", "s m")
        body += text(gx + 5 * (cell + 6) + 12, y + 4, "RR" if narrow else "reciprocal rank (RR)", "s m", "start")
        y += 14
        for q, r in GOLD:
            if narrow:
                body += text(x0, y + 12, f"“{q}”", "s", "start")
                y += 20
            else:
                body += text(x0, y + 25, f"“{q}”", "s", "start")
            for k in range(5):
                hit = r == k + 1
                body += f'<rect x="{gx + k*(cell+6):g}" y="{y+4}" width="{cell}" height="30" rx="5" class="{"fill-g" if hit else "bx"}"/>'
                if hit:
                    body += text(gx + k * (cell + 6) + cell / 2, y + 24, "✓", "b")
            rr = f"1/{r} = {1/r:.2f}" if r else "0 (missed)"
            body += text(gx + 5 * (cell + 6) + 12, y + 24, rr, "s ok-t" if r else "s wn-t", "start")
            y += 44
        msg = [f"hit rate@5 = {hits} of {len(GOLD)} queries found it = {hits/len(GOLD):.2f}",
               f"MRR = mean reciprocal rank = ({' + '.join(f'{1/r:.2f}' if r else '0' for _, r in GOLD)}) / {len(GOLD)} = {mrr:.2f}",
               "precision@5 for query 1 = 1 relevant of 5 shown = 0.20"]
        for k, m in enumerate(msg):
            for j, ln in enumerate(wrap(m, W - 2 * x0, 13)):
                body += text(x0, y + 14 + j * 17, ln, "s b" if k < 2 else "s", "start")
            y += len(wrap(m, W - 2 * x0, 13)) * 17 + 6
        out.append(svg(W, y + 10, body, "Scoring a small golden set: hit rate at 5 and mean reciprocal rank", cls))
    return raw(*out), hits, mrr


EVAL_FIG, EVAL_HITS, EVAL_MRR = eval_svg()


LESSONS = {
    "3.1": dict(
        plain=["A language model only knows what it read in training, and that stops at a cutoff date.",
               "It has never seen your company's manuals or today's prices.",
               "RAG (retrieval-augmented generation) fixes that by looking things up first.",
               "For each question, the system finds the few most relevant passages in your documents and pastes them into the prompt.",
               "The model then answers from those passages and points to the one it used."],
        map=[("The closed-book exam", "A bare model answering from its training memory"),
             ("The library of books", "Your knowledge base, cut into chunks and indexed"),
             ("The librarian picking three pages", "The retriever: embed the question, take the top-k nearest chunks"),
             ("Handing the pages to the student", "Pasting the chunks into the prompt, numbered [1] [2] [3]"),
             ("Pointing to the line used", "Citations that tie each claim to a chunk")],
        fig=rag_svg(),
        cap="Two lanes. The top one runs ahead of time and builds the index. The bottom one runs per question. The only bridge between them is the search into the index, and both lanes must use the same embedding model.",
        line="RAG looks up the right pages first, then lets the model answer from them with page numbers."),
    "3.2": dict(
        plain=["Retrieval never fetches a whole document, only chunks.",
               "A chunk is a short slice of text that gets its own vector and is found on its own.",
               "Chunk size is how long each slice is, usually counted in tokens.",
               "Overlap repeats the end of one chunk at the start of the next one.",
               "Then an idea cut at the border still sits whole in one chunk.",
               "Too small, and a chunk loses its meaning; too big, and it blurs many topics into one match."],
        map=[("One index card", "One chunk: embedded and stored as a single retrievable unit"),
             ("How much you write per card", "Chunk size, e.g. 240 tokens"),
             ("Copying the last line onto the next card", "Overlap, e.g. 40 tokens shared by neighbouring chunks"),
             ("A card that says “add the eggs” with no dish", "A chunk too small to carry its context"),
             ("Pulling a whole chapter for one step", "A chunk so big that its vector matches many questions weakly")],
        fig=chunk_svg(),
        cap=f"Computed from the lesson's own real-scale example: {ART:,} tokens, size {SIZE}, overlap {OVER}. The shaded bands are the overlaps; each is in two chunks, which is why {len(SPANS)} chunks hold {EMBEDDED:,} tokens.",
        play=("chunker", "Drag chunk size and overlap over a real paragraph. The chunks, their count and the shared words are computed live, the same way as the lesson's chunk_text() function."),
        line="Cut documents into slices that each hold one whole idea, and overlap the edges so nothing is cut in half."),
    "3.3": dict(
        plain=["An embedding model turns text into a vector, a long list of numbers, so similar meanings get similar vectors.",
               "RAG uses it twice. Once to embed every chunk when you build the index, and again for each question.",
               "Then it finds the chunks whose vectors point the same way as the question's.",
               "One hard rule: chunks and questions must go through the same model.",
               "Each model makes its own map, so vectors from two models can't be compared."],
        map=[("A spot on the giant map", "A vector, e.g. 384 numbers from all-MiniLM-L6-v2"),
             ("Neighbours on the same street", "High cosine similarity between two vectors"),
             ("Dropping a pin for the question", "Embedding the query with the same model"),
             ("Looking at the nearest houses", "Ranking chunks by dot product of unit-length vectors (equal to cosine)")],
        fig=compare(("Same model for chunks and question",
                     ["Index time: every chunk goes through all-MiniLM-L6-v2",
                      "Query time: the question goes through the same model",
                      "“how do I stop paying?” lands next to “To cancel your subscription…” (0.62 in the lesson's run) with no shared words"], "g"),
                    ("Different models (the #1 retrieval bug)",
                     ["Chunks indexed with model A, the question embedded with model B",
                      "Each model draws its own map, so the numbers mean different things",
                      "No error is raised: the search just returns the wrong chunks"], "w"),
                    "Why the same embedding model must be used for chunks and queries",
                    verdict="If you switch embedding models, re-embed every chunk before you search again."),
        cap="Left, both sides live on one map and “nearest” means “closest meaning”. Right, the search still runs and still returns k results, which is what makes this bug dangerous.",
        line="Embed the chunks and the question with the same model, then find the closest arrows."),
    "3.4": dict(
        plain=["A vector database stores every chunk as a record: an id, its vector, some metadata and the text.",
               "Comparing a question with a million vectors one by one is too slow for a live app.",
               "So the database builds an index that finds almost the closest vectors while checking only a few.",
               "This is called approximate nearest neighbour (ANN) search. You trade a little accuracy for a lot of speed.",
               "Metadata filters keep each search inside what this user is allowed to see."],
        map=[("Checking every seat in the stadium", "Brute-force (flat) search: compare with every vector"),
             ("Asking the ushers which section", "An ANN index such as HNSW (a graph) or IVF (buckets)"),
             ("Checking two or three sections", "Tuning knobs: ef for HNSW, nprobe for IVF"),
             ("The ticket check at the gate", "Metadata filters: user, product, date"),
             ("Usually finding your friend", "Recall below 100%: measure it on your data")],
        fig=stack([("Metadata filter, applied with the search", "only this user's rows, product = X200", "w"),
                   ("ANN index (HNSW)", "hop along a graph of links toward the query; check a small fraction of vectors", "a"),
                   ("Top-k records", "each one: id, vector, metadata, text", "c"),
                   ("Into the prompt", "the text, plus its id and source for the citation", "g")],
                  "What happens inside a vector database for one query",
                  enter="query vector from the same embedding model", leave="k chunks back in milliseconds",
                  blocked={0: "stops user A reading user B's documents", 1: "can miss the exact best match, silently; that is why you measure recall"}),
        cap="A query passes through these layers in order. Skip the filter and users can read each other's documents; never measure the approximate index and you won't notice when it misses the best chunk (the red notes on wider screens).",
        line="A vector database finds nearly the closest chunks very fast, but only among the ones this user may see."),
    "3.5": dict(
        plain=["Retrieval gives every chunk a similarity score against the question.",
               "Top-k keeps the k highest, for example the best 3.",
               "A similarity threshold also drops any chunk whose score is too low, even if it made the top k.",
               "If nothing passes, the honest answer is “I don't know”, and you never call the model at all.",
               "A reranker can then re-read the shortlist next to the question and put the truly best chunk first."],
        map=[("The recruiter skimming 500 CVs", "Stage 1: fast vector search returns many candidates (e.g. 50)"),
             ("The shortlist size", "k: how many chunks you keep"),
             ("“No one met the bar” for the job", "The threshold: below it, refuse instead of guessing"),
             ("The hiring manager reading each CV", "Stage 2: a cross-encoder reranker scores (query, chunk) pairs")],
        fig=topk_svg(),
        cap=f"Illustrative scores, k = {K5}, threshold {TH5:.2f}. Left, two chunks clear both bars. Right, an off-topic question scores low on everything, so the system refuses before generating.",
        play=("topk", "Move k and the threshold, and switch questions. Green chunks reach the prompt, red ones made the top k but failed the threshold, and grey ones were never in the top k."),
        line="Keep the best few chunks that are actually good enough, and say “I don't know” when none are."),
    "3.6": dict(
        plain=["Dense search compares meaning using embeddings, so it finds “cancel my plan” when you type “stop paying”.",
               "Sparse search compares exact words; the classic method is called BM25.",
               "Dense search blurs exact codes like E-417, while BM25 misses paraphrases.",
               "Hybrid search runs both and merges the two ranked lists into one.",
               "A common merge rule, Reciprocal Rank Fusion (RRF), adds up rank positions instead of raw scores."],
        map=[("The friend who understands vague hums", "Dense retrieval: embeddings and cosine similarity"),
             ("The friend who knows lyrics word for word", "Sparse retrieval: BM25 keyword scoring"),
             ("Combining their two lists", "Fusion: RRF or a weighted mix of scores"),
             ("“A song both put near the top wins”", "RRF: sum of 1 / (60 + rank) over the lists")],
        fig=RRF_FIG,
        cap=f"The lesson's three chunks, computed with k = {RRF_K}. Fused order: {', '.join(RRF_ORDER)}. Chunk C, which only BM25 ranked first, jumps above B, which only dense liked.",
        play=("hybrid", "Pick a query and slide alpha from all-BM25 (0) to all-dense (1). Try to find one alpha that ranks the right chunk first for both queries. RRF gets both right with no weight to tune."),
        line="Run a meaning search and a word search, then merge their rankings so you get both."),
    "3.7": dict(
        plain=["Finding the right text is only half the job.",
               "The model must also answer from it and nothing else: that is grounding.",
               "Each claim gets a citation, like [1], pointing to the chunk it came from.",
               "If the answer isn't in the chunks, the model should say so. That is called abstention, and it is a feature.",
               "Your code then checks the citations, because a model can cite the wrong chunk."],
        map=[("The books on your desk", "The numbered chunks in the context block"),
             ("“Every sentence needs a footnote”", "“Cite the chunk number for each claim”"),
             ("Writing “not in my sources”", "Abstaining: “Not in the provided documents.”"),
             ("A true fact without a footnote still loses marks", "An unsupported claim fails faithfulness, even if true"),
             ("The teacher checking footnotes", "Code that verifies each [n] exists and supports the claim")],
        fig=flow([("Number the chunks", "[1] warranty.md  [2] returns.md", "c"),
                  ("Strict instruction", "only the context; cite [n]; else say you don't know", "k"),
                  ("Question last", "where the model attends well", "b"),
                  ("Model answers", "“The warranty is 3 years [1].”", "a"),
                  ("Verify in code", "every [n] is a real chunk; then check support", "g")],
                 "The grounded-prompt recipe from the lesson, step by step"),
        cap="The lesson's four-part recipe plus the model call. Step 5 is what turns citations from decoration into something you can trust.",
        line="Make the model answer only from the pages you gave it, cite them, and say so when the answer isn't there."),
    "3.8": dict(
        plain=["You can't improve retrieval by feel. You need a score.",
               "Start with a golden set: a few dozen real questions, each labelled with the chunk that should come back.",
               "Hit rate@k asks: did the right chunk show up in the top k at all?",
               "MRR (mean reciprocal rank) asks: how near the top was it?",
               "Change one thing, such as chunk size, re-run, and keep the change only if the numbers go up."],
        map=[("The treasures hidden in the park", "The labelled relevant chunks in the golden set"),
             ("How many treasures came back", "Recall@k (equal to hit rate@k with one relevant chunk per query)"),
             ("Rocks in the bag", "Precision@k: the share of the top k that is relevant"),
             ("Steps until the first treasure", "Reciprocal rank: 1/2 if the first hit is at rank 2"),
             ("Not knowing where every treasure is", "Incomplete labels: a 'miss' may be an unlabelled good chunk")],
        fig=EVAL_FIG,
        cap=f"Three queries from the lesson's golden set, with illustrative results. Computed: hit rate@5 = {EVAL_HITS / len(GOLD):.2f}, MRR = {EVAL_MRR:.2f}. The third query is a recall failure; no prompt fix can repair it.",
        line="Label a few real questions with their right answers, and score every change against them."),
}
