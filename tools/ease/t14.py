"""Pass 2, Section 14: Capstones (pages in track10/). Each figure is the architecture of the project the page builds,
labelled with the page's own file names and settings."""
from ease.kit import arrow, box, box_h, esc, flow, lines, path_arrow, raw, rect, svg, text, wrap


def diamond(cx, cy, hw, hh, rows, size=14):
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    return f'<polygon points="{pts}" class="bx tn-k"/>' + lines(cx, cy - 8.5 * (len(rows) - 1) + 5, rows, "b", size=size, lh=17)


def column(items, x, y, w, gap=28, size=14):
    """Boxes stacked top to bottom with down arrows. Returns (svg, [(y, h)], next_y)."""
    body, pos = "", []
    for i, (t, s, tone) in enumerate(items):
        b, h = box(x, y, w, t, s, tone, size=size)
        body += b
        pos.append((y, h))
        if i < len(items) - 1:
            body += arrow(x + w / 2, y + h + 3, x + w / 2, y + h + gap - 3)
        y += h + gap
    return body, pos, y - gap


def row(items, x0, y, w, gap, h, size=14):
    body = ""
    for i, (t, s, tone) in enumerate(items):
        x = x0 + i * (w + gap)
        b, _ = box(x, y, w, t, s, tone, h=h, size=size)
        body += b
        if i < len(items) - 1:
            body += arrow(x + w + 3, y + h / 2, x + w + gap - 3, y + h / 2)
    return body


# ---------- 14.1 RAG assistant: ingest once, answer every question, measure
INGEST = [("docs/ folder", ".txt and .md files", "b"), ("Chunk", "120 words, 20 overlap", "c"),
          ("Embed", "all-MiniLM-L6-v2", "p"), ("Chroma store", "./store, with source + chunk no.", "d")]
ANSWER = [("Question", "from the user", "b"), ("Embed it", "same embedder", "p"), ("Top k = 4", "nearest chunks", "d"),
          ("Grounded prompt", "ONLY the context, cite [n]", "a"), ("qwen2.5:7b", "local, via Ollama", "k")]


def rag_svg():
    W = 760
    body = text(20, 20, "Once: ingest.py", "b ac-t", "start")
    h1 = max(66, max(box_h(160, t, d, 14) for t, d, _ in INGEST))
    body += row(INGEST, 20, 30, 160, 33, h1)
    w2, g2 = 124, 30
    r2 = 30 + h1 + 52
    body += text(20, r2 - 10, "Every question: rag.py", "b ac-t", "start")
    h2 = max(box_h(w2, t, d, 14) for t, d, _ in ANSWER)
    body += row(ANSWER, 20, r2, w2, g2, h2)
    sx = 20 + 3 * 193 + 80
    tkx = 20 + 2 * (w2 + g2) + w2 / 2
    mid = 30 + h1 + 22
    body += path_arrow([(sx, 30 + h1 + 2), (sx, mid), (tkx + 20, mid), (tkx + 20, r2 - 3)], "ac")
    body += text(sx + 8, mid + 18, "search by similarity", "s ac-t", "end")
    lx = 20 + 4 * (w2 + g2) + w2 / 2
    bot = r2 + h2
    oy = bot + 44
    gb, _ = box(400, oy, 170, "Answer + sources", "every claim cites [1], [2]…", "g", h=66, size=14)
    ab, _ = box(590, oy, 150, "Abstain", "\"I don't know based on the documents.\"", "w", h=66, size=14)
    body += gb + ab
    body += path_arrow([(lx, bot + 3), (lx, bot + 22), (485, bot + 22), (485, oy - 3)], "ok") + arrow(lx, bot + 3, lx, oy - 3, "wn")
    eb, _ = box(20, oy, 340, "eval.py: golden set of ~20 questions", "retrieval hit-rate + answer correctness", "p", h=66, size=14)
    body += eb + arrow(396, oy + 33, 364, oy + 33, "ac")
    body += arrow(82, oy - 3, 82, bot + 4, "ac") + text(92, bot + 28, "asks each golden question", "s ac-t", "start")
    wide = svg(W, oy + 78, body, "RAG assistant architecture: ingest documents once, answer each question with retrieval and citations, measure with an eval", "ez-wide")
    # tall
    W2, bw = 360, 290
    body = text(12, 18, "Once: ingest.py", "b ac-t", "start")
    c1, p1, y = column(INGEST, 12, 28, bw, gap=24)
    body += c1
    y += 40
    body += text(12, y, "Every question: rag.py", "b ac-t", "start")
    c2, p2, y = column(ANSWER, 12, y + 10, bw, gap=24)
    body += c2
    sy = p1[-1][0] + p1[-1][1] / 2
    ty = p2[2][0] + p2[2][1] / 2
    body += path_arrow([(12 + bw + 2, sy), (340, sy), (340, ty), (12 + bw + 4, ty)], "ac")
    body += (f'<text x="352" y="{(sy+ty)/2:g}" text-anchor="middle" class="s ac-t" '
             f'transform="rotate(-90 352 {(sy+ty)/2:g})">search by similarity</text>')
    y += 40
    cx = 12 + bw / 2
    body += path_arrow([(cx, y - 37), (cx, y - 20), (95, y - 20), (95, y - 3)], "ok") + path_arrow([(cx, y - 37), (cx, y - 20), (266, y - 20), (266, y - 3)], "wn")
    gb, gh = box(12, y, 165, "Answer + sources", "cites [1], [2]…", "g", h=70, size=14)
    ab, _ = box(185, y, 163, "Abstain", '"I don\'t know…"', "w", h=70, size=14)
    body += gb + ab
    y += 70 + 16
    eb, eh = box(12, y, 336, "eval.py: golden set", "retrieval hit-rate + answer correctness", "p", size=14)
    body += eb
    tall = svg(W2, y + eh + 10, body, "RAG assistant architecture: ingest documents once, answer each question with retrieval and citations, measure with an eval", "ez-tall")
    return raw(wide, tall)


# ---------- 14.2 the guarded agent loop
def agent_svg():
    W = 760
    body = ""
    gb, _ = box(20, 34, 140, "Goal", "from the user", "b", h=78, size=14)
    mb, _ = box(200, 34, 180, "qwen2.5:7b", "sees the tool schemas, proposes an answer or a tool call", "a", h=78, size=14)
    fb, _ = box(610, 34, 130, "Final answer", "returned to the user", "g", h=78, size=14)
    body += gb + mb + fb + arrow(164, 73, 196, 73) + arrow(384, 73, 416, 73)
    body += diamond(500, 73, 80, 46, ["tool call", "proposed?"])
    body += arrow(582, 73, 606, 73, "ok") + text(594, 64, "no", "s ok-t")
    body += text(510, 150, "yes", "s", "start")
    a1, _ = box(560, 200, 180, "Allowlist + argument check", "unknown tool → error message", "c", h=84, size=14)
    a2, _ = box(380, 200, 150, "Risky tool?", "send_email waits for a human: Approve? [y/N]", "w", h=84, size=14)
    a3, _ = box(200, 200, 150, "Run the tool", "print the call: the trace", "g", h=84, size=14)
    body += a1 + a2 + a3
    body += path_arrow([(500, 120), (500, 176), (650, 176), (650, 197)])
    body += arrow(556, 242, 534, 242) + arrow(376, 242, 354, 242)
    body += path_arrow([(260, 198), (260, 115)], "ac")
    body += text(254, 160, "observation", "s ac-t", "end") + text(254, 176, "goes back in", "s ac-t", "end")
    sb, _ = box(20, 200, 150, "max_steps = 6", 'then stop: "Stopped: hit max steps."', "w", h=84, size=14)
    body += sb + f'<line x1="174" y1="242" x2="196" y2="242" class="ln wn dash"/>'
    body += text(20, 316, "Every pass round the loop is one step. The model only proposes; your code decides what actually runs.", "s m", "start")
    wide = svg(W, 328, body, "Guarded agent loop: the model proposes tool calls, code checks and runs them, results go back in, at most 6 steps", "ez-wide")
    # tall
    W2, x, bw = 360, 48, 300
    body = ""
    items = [("Goal", "from the user", "b"), ("qwen2.5:7b", "proposes an answer or a tool call", "a")]
    c, pos, y = column(items, x, 12, bw, gap=26)
    body += c
    my = pos[1][0] + pos[1][1] / 2
    body += arrow(x + bw / 2, y + 3, x + bw / 2, y + 23)
    cy = y + 26 + 44
    body += diamond(x + bw / 2 - 40, cy, 100, 44, ["tool call", "proposed?"])
    body += path_arrow([(x + bw / 2 + 60, cy), (x + bw - 10, cy), (x + bw - 10, cy + 56)], "ok") + text(x + bw - 18, cy - 8, "no", "s ok-t", "end")
    fb, fh = box(x + bw - 110, cy + 60, 110, "Final answer", "", "g", size=14)
    body += fb
    y = cy + 44
    body += arrow(x + bw / 2 - 40, y + 2, x + bw / 2 - 40, y + 24) + text(x + bw / 2 - 30, y + 18, "yes", "s", "start")
    gl = [("Allowlist + argument check", "unknown tool → error", "c"),
          ("Risky tool?", "send_email waits for a human: Approve? [y/N]", "w"),
          ("Run the tool", "print the call: the trace", "g")]
    c, gpos, y = column(gl, x, y + 28, 190, gap=24)
    body += c
    ry = gpos[-1][0] + gpos[-1][1] / 2
    body += path_arrow([(x - 2, ry), (22, ry), (22, my), (x - 4, my)], "ac")
    body += (f'<text x="12" y="{(ry+my)/2:g}" text-anchor="middle" class="s ac-t" '
             f'transform="rotate(-90 12 {(ry+my)/2:g})">observation goes back in</text>')
    y += 18
    sb, sh = box(x, y, bw, "max_steps = 6", 'then stop: "Stopped: hit max steps."', "w", size=14)
    body += sb
    tall = svg(W2, y + sh + 10, body, "Guarded agent loop: the model proposes tool calls, code checks and runs them, results go back in, at most 6 steps", "ez-tall")
    return raw(wide, tall)


# ---------- 14.3 eval harness: pipeline + why per-category gating matters (illustrative scores, computed overall)
CATS = [("billing", 20, 4.2, 4.6), ("technical", 20, 3.8, 4.1), ("edge", 10, 4.5, 3.9)]
TOL = 0.3


def harness_chart():
    nb = sum(n for _, n, _, _ in CATS)
    ob = sum(n * b for _, n, b, _ in CATS) / nb
    oc = sum(n * c for _, n, _, c in CATS) / nb
    reg = [k for k, _, b, c in CATS if c < b - TOL]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        tall = W < 400
        x0, L = (110, W - 260) if not tall else (84, W - 150)
        sc = L / 5
        body = text(12, 20, "Judge scores 1-5 per category: baseline.json vs your change (illustrative)" if not tall else
                    "Judge scores 1-5 (illustrative)", "s m", "start")
        y = 40
        for name, n, b, c in CATS + [("overall", nb, ob, oc)]:
            bad = name in reg
            body += text(x0 - 10, y + 16, name, "s b" + (" wn-t" if bad else ""), "end")
            body += text(x0 - 10, y + 32, f"{n} cases", "s m", "end", 12)
            body += f'<rect x="{x0}" y="{y+4}" width="{b*sc:g}" height="12" rx="3" class="fill-m"/>'
            body += f'<rect x="{x0}" y="{y+19}" width="{c*sc:g}" height="14" rx="3" class="{"fill-w" if bad else "fill-a"}"/>'
            body += text(x0 + max(b, c) * sc + 8, y + 22, f"{b:.2f} → {c:.2f}", "s" + (" wn-t b" if bad else ""), "start")
            if name == "overall":
                body += f'<line x1="{x0-80}" y1="{y-4}" x2="{x0+L+90 if not tall else W-12}" y2="{y-4}" class="grid"/>'
            y += 46
        msg = (f"Overall rises {ob:.2f} → {oc:.2f}, but edge falls {CATS[2][2] - CATS[2][3]:.1f} (more than the {TOL} tolerance): gate.py exits 1, BLOCKED."
               if not tall else f"Overall {ob:.2f} → {oc:.2f}, but edge falls")
        body += text(12, y + 8, msg, "s wn-t", "start")
        if tall:
            body += text(12, y + 28, f"{CATS[2][2] - CATS[2][3]:.1f} (> {TOL}): gate.py exits 1.", "s wn-t", "start")
            y += 20
        body += text(12, y + 30, "grey = baseline, blue = candidate", "s m", "start")
        out.append(svg(W, y + 42, body, "Per-category scores: overall rises while the edge category regresses and the gate blocks", cls))
    return raw(*out)


HARNESS_FLOW = flow([("golden.jsonl", "20-50 cases, each with a category", "c"),
                     ("system_fn(q)", "the RAG bot, the agent, or a prompt", "b"),
                     ("LLM judge", "qwen2.5:7b scores 1-5 as JSON", "a"),
                     ("Average per category", "and overall", "p"),
                     ("gate.py", "compare with baseline.json; exit 1 on a regression", "k")],
                    "Eval harness pipeline from golden set to regression gate")


# ---------- 14.4 QLoRA fine-tune: data split, frozen 4-bit base + small adapter, eval vs base
def ft_svg():
    W = 760
    body = text(20, 20, "1. Data", "b ac-t", "start") + text(280, 20, "2. QLoRA training", "b ac-t", "start") + text(560, 20, "3. Prove it", "b ac-t", "start")
    # data bar: 300 examples illustrative, last 40 held out (as data.py does)
    N, HO = 300, 40
    bx, bw = 20, 210
    body += text(20, 46, f"{N} pairs, all in one format (illustrative)", "s", "start")
    tw = bw * (N - HO) / N
    body += f'<rect x="{bx}" y="58" width="{tw:g}" height="34" rx="4" class="fill-c"/><rect x="{bx+tw+2:g}" y="58" width="{bw-tw-2:g}" height="34" rx="4" class="fill-k"/>'
    body += text(bx, 112, f"train: {N-HO}", "s b", "start") + text(bx + bw, 112, f"held out: {HO}", "s b k-t", "end")
    # model
    mx = 280
    body += rect(mx, 34, 180, 190, "b", rx=10)
    body += lines(mx + 90, 70, ["Qwen2.5-0.5B", "base weights"], "b", size=14, lh=18)
    body += lines(mx + 90, 116, ["frozen, loaded in", "4-bit (NF4)"], "s", size=13, lh=17)
    body += lines(mx + 90, 168, ["not changed", "by training"], "s m", size=13, lh=17)
    body += f'<rect x="{mx+190}" y="34" width="34" height="190" rx="6" class="fill-a"/>'
    body += (f'<text x="{mx+207}" y="129" text-anchor="middle" class="s b" style="fill:var(--bg)" '
             f'transform="rotate(-90 {mx+207} 129)">LoRA adapter, r = 16</text>')
    body += path_arrow([(bx + tw / 2, 92), (bx + tw / 2, 246), (mx + 207, 246), (mx + 207, 228)], "ac")
    body += text(250, 262, "only the adapter learns: 3 epochs, lr 2e-4; saved file is a few MB", "s ac-t", "middle")
    # eval
    ex = 560
    body += text(ex, 46, "Format score (40 held out)", "s", "start")
    for k, (lab, v, cls_) in enumerate((("base", 0.40, "fill-m"), ("tuned", 0.92, "fill-g"))):
        yy = 60 + k * 32
        body += text(ex + 40, yy + 17, lab, "s b", "end")
        body += f'<rect x="{ex+46}" y="{yy+3}" width="{110*v:g}" height="18" rx="3" class="{cls_}"/>'
        body += text(ex + 52 + 110 * v, yy + 17, f"{v:.2f}", "s b", "start")
    body += text(ex, 140, "(the page's example numbers)", "s m", "start")
    gb, _ = box(ex, 156, 180, "General ability", "base vs tuned on other tasks: must not drop much", "w", h=68, size=14)
    body += gb
    wide = svg(W, 276, body, "Fine-tuning capstone: data split, a frozen 4-bit base with a small LoRA adapter, and evaluation against the base", "ez-wide")
    # tall
    W2 = 360
    body = text(12, 18, "1. Data", "b ac-t", "start") + text(12, 38, f"{N} pairs (illustrative), last {HO} held out", "s", "start")
    bw2 = 336
    tw2 = bw2 * (N - HO) / N
    body += f'<rect x="12" y="48" width="{tw2:g}" height="28" rx="4" class="fill-c"/><rect x="{12+tw2+2:g}" y="48" width="{bw2-tw2-2:g}" height="28" rx="4" class="fill-k"/>'
    body += text(12, 94, f"train: {N-HO}", "s b", "start") + text(348, 94, f"held out: {HO}", "s b k-t", "end")
    body += text(12, 128, "2. QLoRA training", "b ac-t", "start")
    body += rect(12, 138, 270, 104, "b", rx=10)
    body += lines(147, 164, ["Qwen2.5-0.5B base weights", "frozen, loaded in 4-bit (NF4)", "not changed by training"], "s", size=13, lh=20)
    body += f'<rect x="290" y="138" width="58" height="104" rx="6" class="fill-a"/>'
    body += lines(319, 178, ["LoRA", "r = 16"], "s b", size=13, lh=18).replace('class="s b"', 'class="s b" style="fill:var(--bg)"')
    body += text(12, 262, "Only the adapter learns (3 epochs, lr 2e-4).", "s ac-t", "start")
    body += text(12, 300, "3. Prove it on the 40 held out", "b ac-t", "start")
    for k, (lab, v, cls_) in enumerate((("base", 0.40, "fill-m"), ("tuned", 0.92, "fill-g"))):
        yy = 312 + k * 30
        body += text(56, yy + 16, lab, "s b", "end")
        body += f'<rect x="64" y="{yy+3}" width="{220*v:g}" height="18" rx="3" class="fill-m" />'.replace("fill-m", cls_)
        body += text(70 + 220 * v, yy + 16, f"{v:.2f}", "s b", "start")
    body += text(12, 386, "format score (the page's example numbers)", "s m", "start")
    gb, gh = box(12, 398, 336, "General ability", "base vs tuned on other tasks: must not drop much", "w", size=14)
    body += gb
    tall = svg(W2, 398 + gh + 10, body, "Fine-tuning capstone: data split, a frozen 4-bit base with a small LoRA adapter, and evaluation against the base", "ez-tall")
    return raw(wide, tall)


# ---------- 14.5 one request through the optimized service
def chat_svg():
    W = 760
    body = ""
    rb, _ = box(20, 40, 130, "Request", "user message", "b", h=72, size=14)
    body += rb + arrow(154, 76, 196, 76)
    body += diamond(270, 76, 70, 44, ["in the", "cache?"])
    hb, _ = box(200, 160, 140, "Return it", "about 0 s, no model call", "g", h=72, size=14)
    body += hb + arrow(270, 120, 270, 156, "ok") + text(280, 144, "hit", "s ok-t", "start")
    body += arrow(340, 76, 386, 76) + text(363, 67, "miss", "s")
    body += diamond(460, 76, 70, 44, ["hard", "message?"])
    sb, _ = box(560, 20, 180, "qwen2.5:1.5b", "small and fast: the cheap path", "c", h=60, size=14)
    bb, _ = box(560, 100, 180, "qwen2.5:7b", "'analyze', 'design', 'prove'… or over 300 characters", "k", h=74, size=14)
    body += sb + bb
    body += path_arrow([(530, 76), (545, 76), (545, 50), (556, 50)]) + text(540, 40, "no", "s", "end")
    body += path_arrow([(530, 76), (545, 76), (545, 137), (556, 137)]) + text(540, 156, "yes", "s", "end")
    steps = [("Trim history", "keep the last 6 messages", "p"), ("Stream", "tokens appear as written; cap 400", "a"),
             ("Save to cache", "for the next identical message", "g"), ("Record metrics", "hit rate, routing split, latency", "d")]
    y = 300
    body += row(steps, 20, y, 160, 33, 70)
    body += f'<polyline points="744,50 752,50 752,258" class="ln"/><line x1="744" y1="137" x2="752" y2="137" class="ln"/>'
    body += path_arrow([(752, 258), (100, 258), (100, 296)])
    body += text(420, 280, "every model call then goes through the same steps", "s m")
    wide = svg(W, 382, body, "One request through the optimized chat service: cache, route, trim, stream, store, measure", "ez-wide")
    # tall
    W2 = 360
    body = ""
    rb, rh = box(12, 12, 336, "Request", "user message", "b", size=14)
    body += rb + arrow(180, 12 + rh + 2, 180, 12 + rh + 22)
    cy = 12 + rh + 24 + 40
    body += diamond(130, cy, 80, 40, ["in the", "cache?"])
    hb, hh = box(228, cy - 34, 120, "Return it", "about 0 s", "g", h=68, size=14)
    body += hb + arrow(212, cy, 224, cy, "ok") + text(214, cy - 44, "hit", "s ok-t", "start")
    body += arrow(130, cy + 42, 130, cy + 70) + text(140, cy + 62, "miss", "s", "start")
    cy2 = cy + 72 + 40
    body += diamond(130, cy2, 80, 40, ["hard", "message?"])
    y = cy2 + 64
    sb, sh = box(12, y, 160, "qwen2.5:1.5b", "small, fast", "c", h=70, size=14)
    bb, _ = box(188, y, 160, "qwen2.5:7b", "hard words or over 300 characters", "k", h=70, size=14)
    body += sb + bb
    body += arrow(90, cy2 + 30, 90, y - 3) + text(80, y - 10, "no", "s", "end")
    body += path_arrow([(210, cy2), (268, cy2), (268, y - 3)]) + text(278, y - 10, "yes", "s", "start")
    y += 70 + 26
    body += text(12, y - 6, "then, for either model:", "s m", "start")
    c, _, y = column([("Trim history", "keep the last 6 messages", "p"), ("Stream", "tokens appear as written; cap 400", "a"),
                      ("Save to cache", "for the next identical message", "g"), ("Record metrics", "hit rate, routing split, latency", "d")],
                     12, y + 6, 336, gap=22)
    body += c
    tall = svg(W2, y + 12, body, "One request through the optimized chat service: cache, route, trim, stream, store, measure", "ez-tall")
    return raw(wide, tall)


LESSONS = {
    "14.1": dict(
        plain=["This project is a question-answering bot for your own documents.",
               "It finds the few passages that match a question, then has a local model answer from those passages only.",
               "Every answer names the document it came from.",
               "If the documents don't cover the question, the bot says \"I don't know\".",
               "The trick has a name: RAG, retrieval-augmented generation.",
               "You also build a small test set, so you can prove with numbers that it works."],
        pic="Think of an open-book exam where you may only use the books on your desk. Before the exam you put sticky tabs on every page by topic. For each question you flip to the few best-tabbed pages, write your answer from them, and note the page numbers. If the books don't cover it, you write \"not in my books\". A teacher with an answer key then marks you.",
        breaks="You understand a page when you read it, but retrieval only finds pages whose meaning looks similar to the question. It can fetch the wrong page for a well-worded question, which is why you measure retrieval on its own.",
        map=[("Sticky tabs on every page", "Ingest: chunk into 120-word pieces, embed, store in Chroma"),
             ("Flipping to the best-tabbed pages", "Retrieve the top k = 4 chunks by similarity"),
             ("Writing only from those pages, with page numbers", "A grounded prompt that demands [n] citations"),
             ("\"Not in my books\"", "The abstain answer: \"I don't know based on the documents.\""),
             ("The teacher's answer key", "<code>eval.py</code>: retrieval hit-rate and answer correctness")],
        fig=rag_svg(),
        cap="The ingest part runs once when you add documents. The answer part runs for every question, pulling chunks from the store. The eval box asks the same golden questions every time you change one thing, such as chunk size or k.",
        line="Look it up in your own documents, answer only from what you found, show where it came from, and measure it."),
    "14.2": dict(
        plain=["An agent is a model that uses tools, like a calculator or Wikipedia, until a job is done.",
               "The model only suggests which tool to call; your code decides whether that call really runs.",
               "Code checks that the tool is on an allowed list and that its inputs make sense.",
               "A human must approve anything risky, like sending an email.",
               "The loop stops after 6 steps, so it can never run forever.",
               "Every action is printed, so you can see exactly what it did."],
        pic="Picture a new intern with a calculator and a reference book. They may suggest any action, but you have rules: only use the tools on this list, show me your sums before you run them, and ask me before you send any email. They get six tries at the task, and they write every step in a notebook.",
        breaks="An intern remembers being told off and gets better. The model does not, and text it reads from a tool (a Wikipedia page, say) can carry instructions of its own. So the rules must live in your code, not in the prompt.",
        map=[("The intern suggesting an action", "The model returns a tool call, not a result"),
             ("Only the tools on the list", "The allowlist: <code>name not in TOOLS</code> → error"),
             ("Ask me before sending email", "<code>RISKY = {\"send_email\"}</code> waits for a human y/N"),
             ("Six tries at the task", "<code>max_steps=6</code>, then \"Stopped: hit max steps.\""),
             ("The notebook of every step", "The printed trace of each tool call")],
        fig=agent_svg(),
        cap="Follow the loop: the model proposes, code checks, the tool runs, and its result goes back into the messages for the next step. Unknown tools and denied actions still return a message, so the model sees what happened.",
        line="The model may suggest anything, but your code decides what runs, and it always stops."),
    "14.3": dict(
        plain=["An eval harness is a reusable test rig for any AI system you build.",
               "It runs the system on a fixed list of questions with known good answers, called a golden set.",
               "Another model acts as the judge and scores each answer from 1 to 5.",
               "Scores are averaged per category, such as billing or edge cases.",
               "If any category drops compared with the last good version, the change is blocked."],
        pic="Think of an exam board. Every class sits the same paper. Essay answers go to a marker with a mark scheme. Results come back per subject, not just one total. If any subject falls clearly below last year's marks, the results are held back until someone looks.",
        breaks="Human markers are trained and fairly steady. An LLM judge can be noisy or biased, so you check it first: hand-mark 10 answers yourself and see if the judge agrees.",
        map=[("The same exam paper for every class", "<code>golden.jsonl</code>: fixed questions, expected answers, a category each"),
             ("The marker with a mark scheme", "The LLM judge: qwen2.5:7b returns a 1-5 score as JSON"),
             ("Results per subject", "Average score per category"),
             ("Last year's marks", "<code>baseline.json</code>, saved from the last good version"),
             ("Results held back", "<code>gate.py</code> exits 1 if a category drops more than 0.3")],
        fig=HARNESS_FLOW + harness_chart(),
        cap="Top: the harness pipeline. Bottom: why it gates per category. The scores and case counts are illustrative; the overall averages are computed from them, weighted by cases. The overall number went up while the edge cases got worse, and only the per-category check catches it.",
        line="Score every change on the same test, subject by subject, and block it if any subject gets worse."),
    "14.4": dict(
        plain=["Fine-tuning means training a model a little more, on your own examples, to change how it behaves.",
               "Here you teach a small open model one habit, such as always replying in a strict support format.",
               "QLoRA (quantized low-rank adaptation) keeps the big model frozen and trains a small add-on called an adapter.",
               "That makes it cheap enough to run on a free Colab GPU.",
               "Then you prove it worked on examples it never saw, and check it didn't get worse at everything else."],
        pic="Think of a skilled new hire learning your company's letter style. You don't send them back to school. You give them a clip-on cheat sheet and a few hundred example letters in the house style. You keep 40 letters aside to test them on, and you also check they can still do the rest of their job.",
        breaks="A person who learns a house style rarely forgets how to do sums. A model can lose general skills when you tune it hard on one thing (catastrophic forgetting), which is why the general-ability check is part of the project.",
        map=[("The skilled new hire", "The base model, Qwen2.5-0.5B, loaded in 4-bit and frozen"),
             ("The clip-on cheat sheet", "The LoRA adapter (r = 16): the only part trained, a few MB"),
             ("Example letters in the house style", "A few hundred instruction → response pairs, all in one format"),
             ("The 40 letters kept aside", "The held-out set, never used for training"),
             ("Checking they can still do the rest of the job", "General-ability prompts, base vs tuned")],
        fig=ft_svg(),
        cap="The base model never changes; only the thin adapter learns. The 300-example size is illustrative (the page says about 200 to 500). The 0.40 and 0.92 format scores are the page's example values, not a measured result.",
        line="Teach one habit with a small add-on, then test on examples it never saw and check nothing else broke."),
    "14.5": dict(
        plain=["This project wraps a model in a chat service that is cheap and fast to run.",
               "Repeated questions are answered from a cache: a store of answers already given.",
               "Easy messages go to a small, fast model and hard ones to a bigger model. That is called routing.",
               "Old chat turns are trimmed, answers stream word by word, and output length is capped.",
               "The service counts cache hits, routing and latency, so you can prove each trick saves something."],
        pic="Picture a busy coffee shop. The most common orders sit ready on the counter. Simple orders go to the junior barista, tricky ones to the head barista. Every customer gets the first sip straight away, cups have a size limit, and at closing time someone counts how many of each happened.",
        breaks="A ready coffee is the same as a fresh one. A cached answer can be out of date, and with a semantic cache (reusing answers for similar questions) it can be wrong for a question that only looks the same.",
        map=[("Orders ready on the counter", "The cache: an identical message returns the saved answer"),
             ("Junior and head barista", "Routing: qwen2.5:1.5b for easy, qwen2.5:7b for hard"),
             ("The first sip straight away", "Streaming tokens as they are written"),
             ("The cup size limit", "<code>num_predict: 400</code> and keeping the last 6 messages"),
             ("Counting at closing time", "<code>report()</code>: hit rate, routing split, average latency")],
        fig=chat_svg(),
        cap="Read left to right. A cache hit skips the model entirely. A miss is routed by a simple rule (hard words or a long message), then trimmed, streamed, saved and measured. The model names and limits are the ones in <code>chat_service.py</code>.",
        play=("chatcost", "If this service ran on the Claude API, what would 1,000 chats cost? Move the prompt-cache hit rate and the share routed to the small model. Prices are real; token counts are illustrative."),
        line="Answer repeats from memory, send easy work to the cheap model, and measure every saving."),
}
