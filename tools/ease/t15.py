"""Pass 2, Section 15 (folder track9/): Interview bank.

These are Q&A pages with no pass-1 analogy, so every lesson writes its own pic + breaks.
Each diagram shows the reasoning shape an interviewer wants to hear, filled in with the page's own example.
All wording inside the figures is taken from the lesson pages (answers, narration, practice solutions).
"""
from ease.kit import arrow, box, box_h, esc, flow, lines, path_arrow, raw, rect, stack, svg, text, wrap


# ---------- shared helpers (local to this module)
def tbox(x, y, w, body, tone="b", size=14, anchor="start", bold_first=None, minh=0):
    """A box of wrapped sentence text (left-aligned by default). Returns (svg, height).
    Text sits in <g class="vzb"> right after its rect, so the QA script checks it stays inside."""
    rows = wrap(body, w - 28, size)
    lh = round(size * 1.32)
    head = wrap(bold_first, w - 28, size, bold=True) if bold_first else []
    h = max(minh, 18 + (len(head) + len(rows)) * lh + 4)
    tx = x + 14 if anchor == "start" else x + w / 2
    y0 = y + (h - (len(head) + len(rows)) * lh) / 2 + size * 0.95
    out = rect(x, y, w, h, tone) + '<g class="vzb">'
    if head:
        out += lines(tx, y0, head, "b", anchor, size, lh)
    out += lines(tx, y0 + len(head) * lh, rows, "", anchor, size, lh) + "</g>"
    return out, h


def tbox_h(w, body, size=14, bold_first=None, minh=0):
    rows = wrap(body, w - 28, size)
    head = wrap(bold_first, w - 28, size, bold=True) if bold_first else []
    return max(minh, 18 + (len(head) + len(rows)) * round(size * 1.32) + 4)


def pill(x, y, w, h, label, tone="a", num=None):
    out = rect(x, y, w, h, tone, rx=h / 2 if h < 40 else 12)
    rows = wrap(label, w - 20, 14, bold=True)
    y0 = y + (h - len(rows) * 18) / 2 + 13.5
    out += '<g class="vzb">' + lines(x + w / 2, y0, rows, "b", size=14, lh=18) + "</g>"
    if num is not None:
        out += f'<circle cx="{x+2:g}" cy="{y+2:g}" r="11" class="badge"/>' + text(x + 2, y + 6.5, num, "badge-t")
    return out


def ladder(question, rungs, foot, label):
    """Tag column + content boxes, read top to bottom. rungs: [(tag, text, tone)]."""
    # wide
    W, tx, tw, cx, cw = 760, 20, 170, 214, 526
    body = text(20, 24, question, "b", "start")
    y = 42
    for i, (tag, t, tone) in enumerate(rungs):
        h = max(54, tbox_h(cw, t))
        body += pill(tx, y, tw, h, tag, tone, num=i + 1)
        b, _ = tbox(cx, y, cw, t, tone, minh=h)
        body += b + arrow(tx + tw + 4, y + h / 2, cx - 4, y + h / 2, "thin")
        if i < len(rungs) - 1:
            body += arrow(tx + tw / 2, y + h + 3, tx + tw / 2, y + h + 23)
        y += h + 26
    fl = wrap(foot, W - 40, 13)
    body += lines(20, y + 8, fl, "s ac-t", "start", 13, 17)
    wide = svg(W, y + 8 + len(fl) * 17, body, label, "ez-wide")
    # tall
    W2 = 360
    ql = wrap(question, W2 - 24, 15, bold=True)
    body = lines(12, 22, ql, "b", "start", 15, 20)
    y = 22 + len(ql) * 20 + 6
    for i, (tag, t, tone) in enumerate(rungs):
        body += pill(12, y, 200, 32, tag, tone, num=i + 1)
        y += 40
        b, h = tbox(12, y, W2 - 24, t, tone)
        body += b
        y += h
        if i < len(rungs) - 1:
            body += arrow(W2 / 2, y + 3, W2 / 2, y + 23)
        y += 28
    fl = wrap(foot, W2 - 24, 13)
    body += lines(12, y + 4, fl, "s ac-t", "start", 13, 17)
    tall = svg(W2, y + 4 + len(fl) * 17, body, label, "ez-tall")
    return raw(wide, tall)


# ---------- 15.2 debugging a wrong RAG answer: which half failed?
def rag_tree():
    root = "A user reports a wrong answer"
    qn = "Open the trace. Was the relevant chunk in the top-k?"
    no_t, no_s = "No: retrieval failed", "Fix chunking, the embedding model, hybrid search, query transformation, or fetch more then rerank."
    yes_t, yes_s = "Yes, but the answer ignored it: generation failed", "Check grounding and faithfulness and the prompt. Reproduce with the exact retrieved context."
    # wide
    W = 760
    body = ""
    b, h1 = box(230, 14, 300, root, "", "b")
    body += b
    b, h2 = box(180, 14 + h1 + 30, 400, qn, "recall@k for this query says which half to fix", "k")
    body += b + arrow(380, 14 + h1 + 3, 380, 14 + h1 + 27)
    y2 = 14 + h1 + 30 + h2
    bw = 340
    hb = max(box_h(bw, no_t, no_s), box_h(bw, yes_t, yes_s))
    yb = y2 + 56
    b, _ = box(20, yb, bw, no_t, no_s, "w", h=hb)
    body += b
    b, _ = box(W - 20 - bw, yb, bw, yes_t, yes_s, "c", h=hb)
    body += b
    body += path_arrow([(300, y2 + 2), (300, y2 + 22), (190, y2 + 22), (190, yb - 3)], "wn")
    body += path_arrow([(460, y2 + 2), (460, y2 + 22), (570, y2 + 22), (570, yb - 3)], "ac")
    body += text(180, y2 + 44, "no", "b wn-t", "end") + text(580, y2 + 44, "yes", "b ac-t", "start")
    yf = yb + hb + 26
    body += text(20, yf, "Interview example: recall@10 = 0.97 but users still get wrong answers → the right-hand branch.", "s", "start")
    body += text(20, yf + 20, "Retrieval is healthy, so fix grounding. Don't re-chunk or swap the embedder.", "s", "start")
    wide = svg(W, yf + 30, body, "Debugging a wrong RAG answer: split retrieval failures from generation failures", "ez-wide")
    # tall
    W2 = 360
    b, h1 = box(12, 12, W2 - 24, root, "", "b")
    body = b
    y = 12 + h1 + 30
    body += arrow(W2 / 2, 12 + h1 + 3, W2 / 2, y - 3)
    b, h2 = box(12, y, W2 - 24, qn, "recall@k for this query says which half", "k")
    body += b
    y += h2
    sx = 26
    for t, s, tone, lab, cls in ((no_t, no_s, "w", "no", "wn"), (yes_t, yes_s, "c", "yes", "ac")):
        hh = box_h(W2 - 70, t, s)
        y += 40
        b, _ = box(56, y, W2 - 68, t, s, tone, h=hh)
        body += b + f'<line x1="{sx}" y1="{y-40:g}" x2="{sx}" y2="{y+hh/2:g}" class="ln {cls}"/>' + arrow(sx, y + hh / 2, 53, y + hh / 2, cls)
        body += text(sx + 8, y - 8, lab, f"b {cls}-t" if cls == "wn" else "b ac-t", "start")
        y += hh
    body += text(12, y + 26, "recall@10 = 0.97, answers still wrong:", "s", "start")
    body += text(12, y + 44, "take the yes branch and fix grounding.", "s", "start")
    tall = svg(W2, y + 54, body, "Debugging a wrong RAG answer: split retrieval failures from generation failures", "ez-tall")
    return raw(wide, tall)


# ---------- 15.4 the seven-step framework, filled in for the page's worked example
STEPS = ["Clarify", "Data & knowledge", "Core design", "Evaluation", "Safety", "Cost & latency", "Iterate"]
SUPPORT = ["Answers from our help docs, about 50k questions a day, under 2 s perceived, no money-moving actions in v1.",
           "Private, changing product and policy docs, so RAG: chunk with overlap + metadata, embed, vector DB, re-index on doc changes.",
           "Input moderation → hybrid retrieve + rerank → grounded prompt (answer only from context, cite) → LLM. Small model for easy queries, bigger for hard.",
           "Golden set of real questions: recall@k and MRR for retrieval, faithfulness via LLM judge; gate changes in CI; A/B online.",
           "Fence user input as data, moderate in and out, validate output, redact PII in logs. No actions, so the blast radius is small.",
           "Cache repeats (a big win), stream the answer, cap output, trim retrieved context.",
           "Trace every request, mine failures into the golden set, escalate low-confidence answers to a human."]


def design_svg():
    tones = ["k", "c", "a", "g", "w", "p", "d"]
    # wide
    W, tw, cx = 760, 150, 200
    cw = W - cx - 60
    body = text(20, 22, "“Design a customer-support assistant”, answered layer by layer", "b", "start")
    y, ys = 38, []
    for i, (st, t) in enumerate(zip(STEPS, SUPPORT)):
        h = max(46, tbox_h(cw, t, 13))
        body += pill(20, y, tw, h, st, tones[i], num=i + 1)
        b, _ = tbox(cx, y, cw, t, tones[i], 13, minh=h)
        body += b + arrow(20 + tw + 3, y + h / 2, cx - 3, y + h / 2, "thin")
        ys.append((y, h))
        if i < len(STEPS) - 1:
            body += arrow(20 + tw / 2, y + h + 2, 20 + tw / 2, y + h + 16)
        y += h + 18
    # feedback loop: iterate → evaluation (failures join the golden set)
    xr = cx + cw + 22
    (ye, he), (yi, hi) = ys[3], ys[6]
    body += path_arrow([(cx + cw + 3, yi + hi / 2), (xr, yi + hi / 2), (xr, ye + he / 2), (cx + cw + 4, ye + he / 2)], "ac")
    cy = (ye + he / 2 + yi + hi / 2) / 2
    body += (f'<text x="{xr+14:g}" y="{cy:g}" text-anchor="middle" class="s ac-t" '
             f'transform="rotate(-90 {xr+14:g} {cy:g})">failures feed the golden set</text>')
    body += text(20, y + 6, "Step 1 sets the budget every later step must meet. Raise steps 4 and 5 (evals, failure modes) unprompted.", "s m", "start")
    wide = svg(W, y + 16, body, "A system-design answer as seven layers, filled in for a support assistant", "ez-wide")
    # tall
    W2 = 360
    body = text(12, 20, "“Design a customer-support", "b", "start") + text(12, 40, "assistant”, step by step", "b", "start")
    y = 54
    for i, (st, t) in enumerate(zip(STEPS, SUPPORT)):
        body += pill(12, y, 190, 30, st, tones[i], num=i + 1)
        y += 36
        b, h = tbox(12, y, W2 - 24, t, tones[i], 13)
        body += b
        y += h
        if i < len(STEPS) - 1:
            body += arrow(W2 / 2, y + 2, W2 / 2, y + 16)
        y += 20
    body += text(12, y + 4, "Then loop: production failures go back", "s ac-t", "start")
    body += text(12, y + 22, "into the golden set (step 7 → step 4).", "s ac-t", "start")
    tall = svg(W2, y + 32, body, "A system-design answer as seven layers, filled in for a support assistant", "ez-tall")
    return raw(wide, tall)


# ---------- 15.5 what each file of a take-home proves to the grader
FILES = [("ingest.py", "chunk, embed, store in Chroma"), ("rag.py", "retrieve → grounded prompt → Ollama; cites, abstains"),
         ("tests/", "regression tests at temperature 0"), ("README.md", "setup, run, decisions, trade-offs, what next"),
         ("eval.py + golden.jsonl", "~25 questions → recall@k + faithfulness")]
SCORES = [("It runs (the floor)", "g"), ("Handles failures", "k"), ("Runs from a clean clone", "c"), ("Justified architecture", "c"),
          ("Cost and latency notes", "c"), ("Has an evaluation: the #1 differentiator", "a")]
LINKS = [(0, 0), (1, 0), (1, 1), (2, 1), (3, 2), (3, 3), (3, 4), (4, 5)]


def takehome_svg():
    W, lw, rw = 760, 280, 280
    lx, rx = 20, W - 20 - rw
    body = text(lx, 22, "Files in my-rag-takehome/", "b", "start") + text(rx, 22, "What the grader scores", "b", "start")
    ly, lpos = 40, []
    for name, sub in FILES:
        b, h = box(lx, ly, lw, name, sub, "b", size=14)
        body += b
        lpos.append(ly + h / 2)
        ly += h + 12
    ry, rpos = 40, []
    rh = (ly - 12 - 40 - 12 * (len(SCORES) - 1)) / len(SCORES)
    for i, (name, tone) in enumerate(SCORES):
        b, _ = box(rx, ry, rw, name, "", tone, h=rh, size=14)
        body += b
        rpos.append(ry + rh / 2)
        if i == 0:
            body += f'<line x1="{rx-8:g}" y1="{ry+rh+6:g}" x2="{rx+rw:g}" y2="{ry+rh+6:g}" class="ln wn dash"/>'
            body += text(rx + rw, ry + rh + 22, "above this line is what gets offers", "s wn-t", "end")
            ry += 16
        ry += rh + 12
    for a, b2 in LINKS:
        cls = "ac" if b2 == 5 else "thin"
        body += path_arrow([(lx + lw + 3, lpos[a]), (lx + lw + 40, lpos[a]), (rx - 40, rpos[b2]), (rx - 4, rpos[b2])], cls)
    H = max(ly, ry) + 6
    body += text(20, H + 8, "Anyone can wire an LLM to a vector store. The eval files are the ones that show you can measure it.", "s ac-t", "start")
    wide = svg(W, H + 20, body, "Each file of a RAG take-home and the rubric line it proves", "ez-wide")
    # tall: file, then what it proves
    proves = ["it runs (the floor)", "it runs, and it handles failures", "it handles failures",
              "clean clone, justified architecture, cost notes", "an evaluation: the #1 differentiator"]
    W2 = 360
    body = text(12, 20, "Each file and what it proves", "b", "start")
    y = 34
    for (name, sub), pv in zip(FILES, proves):
        tone = "a" if "eval" in name else "b"
        b, h = box(12, y, W2 - 24, name, sub, tone, size=14)
        body += b + arrow(30, y + h + 2, 30, y + h + 20, "ac" if tone == "a" else "thin")
        pl = wrap("proves: " + pv, W2 - 70, 13)
        body += lines(44, y + h + 18, pl, "s ac-t" if tone == "a" else "s", "start", 13, 17)
        y += h + 26 + len(pl) * 17
    body += text(12, y + 4, "The dashed line in the rubric: “it runs” is", "s wn-t", "start")
    body += text(12, y + 22, "the floor; the rest is what gets offers.", "s wn-t", "start")
    tall = svg(W2, y + 32, body, "Each file of a RAG take-home and the rubric line it proves", "ez-tall")
    return raw(wide, tall)


LESSONS = {
    "15.1": dict(
        plain=["Every GenAI interview starts with the basics: tokens, embeddings, the context window and sampling.",
               "Interviewers aren't checking that you memorised definitions.",
               "They want to hear that you understand the machine: how it works, and what that means in practice.",
               "A good answer has three parts: the mechanism, the consequence, and a bit of judgment.",
               "Keep it to 30 to 45 seconds, then stop and let them ask the follow-up."],
        pic="Think of a driving examiner asking “what does the clutch do?”. A weak answer recites the manual. A strong one says how it works (it disconnects the engine from the wheels), what follows (forget it and you stall when you stop), and a bit of judgment (don't ride it in traffic).",
        breaks="An examiner wants one right answer and moves on. An interviewer uses your answer to pick the next question, so leave a door open for the follow-up instead of saying everything at once.",
        map=[("How the clutch works", "The mechanism: next-token prediction, tokens, embeddings, attention"),
             ("Stalling if you forget it", "The consequence: cost, context limits, latency, failure modes"),
             ("Don't ride it in traffic", "Judgment: when you would not use an LLM, and how you would verify"),
             ("Answer, then wait for the next question", "30 to 45 seconds, then stop and let them follow up")],
        fig=ladder("“What's a token, and why care about counts?”",
                   [("Mechanism", "A chunk of text, often a word-piece, from the model's fixed vocabulary, made by a sub-word tokenizer such as BPE (byte-pair encoding).", "c"),
                    ("Consequence", "Tokens are the unit of cost (billing), of context limits (the window) and of latency. About 4 characters per token in English; code and many languages cost more.", "k"),
                    ("Judgment", "It also explains a classic failure: models miscount letters because they see tokens, not characters.", "g")],
                   "Then stop. 30 to 45 seconds is enough; the interviewer will pick the next thread.",
                   "The shape of a strong foundations answer: mechanism, consequence, judgment"),
        cap="The same three-step shape works for every question in this bank. The words in the boxes are the page's own model answer, split into the three parts an interviewer listens for.",
        line="Say how it works, say what that means in practice, show one bit of judgment, then stop."),
    "15.2": dict(
        plain=["RAG (retrieval-augmented generation) is the most heavily tested topic in GenAI interviews.",
               "RAG means: find the right pieces of your documents first, then let the model answer using only those pieces.",
               "So a RAG system has two halves, retrieval and generation, and either one can fail.",
               "The strongest answers keep the halves apart: measure each one, and debug by asking which half broke.",
               "Interviewers also listen for cost, speed and scale, not just the pipeline steps."],
        pic="Picture a student who gets an open-book exam question wrong. The teacher's first question is: did you open the right page? If not, the index or the search let them down. If they had the right page in front of them and still wrote the wrong thing, the reading and writing let them down.",
        breaks="A student can tell you which page they used. A RAG system can only tell you if you logged the retrieved chunks in a trace, so tracing is not optional.",
        map=[("Opening the right page", "The relevant chunk shows up in the top-k results (measured by recall@k)"),
             ("Couldn't find the page", "Retrieval failure: chunking, embedding model, hybrid search, query transformation"),
             ("Had the page but wrote it wrong", "Generation failure: weak grounding, low faithfulness, a loose prompt"),
             ("Asking which page they opened", "Opening the trace and reproducing with the exact retrieved context")],
        fig=rag_tree(),
        cap="One question splits every RAG failure in two. If the right chunk never arrived, fix retrieval. If it arrived and the answer still went wrong, fix generation. The recall@10 = 0.97 example is the page's own interview question.",
        line="When a RAG answer is wrong, first ask whether the right chunk was retrieved, then fix that half."),
    "15.3": dict(
        plain=["An agent is a language model that runs in a loop and uses tools to take actions.",
               "Agent questions test one thing above all: can you give a model autonomy responsibly?",
               "The senior move is to use the least autonomy that solves the task.",
               "If a plain prompt or RAG works, you don't build an agent.",
               "When you do, you put guards around every tool, and the hard limits live in code, not in the prompt."],
        pic="Giving an agent tools is like giving a new intern a company card. You give them only the cards the job needs. The bank enforces a spending cap, a manager signs off on big purchases, and every purchase leaves a receipt.",
        breaks="An intern won't obey a sticky note on a parcel saying “refund this customer in full”. An agent might, because text inside a ticket or web page can steer it (prompt injection). That is why the cap lives in code, where text can't change it.",
        map=[("Only the cards the job needs", "Least privilege: only the tools this task needs"),
             ("A cap the bank enforces", "Hard limits in code: refund cap, max steps, budgets, timeouts"),
             ("A manager signs off on big purchases", "Human approval for irreversible or high-impact actions"),
             ("A receipt for everything", "Log every step, and evaluate the agent on task suites on every change"),
             ("Don't hire an intern for a vending-machine job", "The least autonomy that solves the task: prompt or RAG first")],
        fig=stack([("Least privilege", "only the tools this task needs; sandbox the dangerous ones", "c"),
                   ("Treat tool and retrieved text as untrusted", "it is data, never instructions", "k"),
                   ("Validate the tool arguments", "types, ranges and ids checked in code", "a"),
                   ("Hard limits in code", "refund cap, max steps, cost budget, timeout", "w"),
                   ("Human approval", "for irreversible or high-impact actions above a threshold", "p"),
                   ("Log every step, evaluate on task suites", "you can't eyeball dozens of autonomous actions", "g")],
                  "Guards around one tool call, in the order the call meets them",
                  enter="model proposes issue_refund(order, amount)", leave="the action runs, or is refused",
                  blocked={0: "a tool this task should never have", 1: "orders hidden in a ticket or web page (injection)",
                           2: "a malformed or out-of-range call", 3: "a refund above the cap, a loop that never stops",
                           4: "a large refund nobody signed off"}),
        cap="Defence in depth: each layer stops a different failure, so one mistake (or one injected instruction) doesn't become a harmful action. The refund agent is the page's own interview question; the senior detail is the cap in code plus a human above a threshold.",
        line="Give an agent the least power that does the job, and put every limit in code where text can't change it."),
    "15.4": dict(
        plain=["A GenAI system-design round asks you to design a whole product, like a support assistant, out loud on a whiteboard.",
               "It differs from classic system design because the model is probabilistic, costs money per token, and can be wrong.",
               "So interviewers listen for evaluation, failure modes, cost, latency and safety, not just boxes and arrows.",
               "A seven-step framework keeps you in order under pressure: clarify, data, core design, evaluation, safety, cost and latency, iterate.",
               "Always clarify first: who uses it, at what scale, and what “good” means."],
        pic="It is like an architect asked to design a house. A good one first asks who will live there and what the budget is. Then the foundations, then the rooms, then the inspection, the fire code and the running costs, and a plan for what to fix after the family moves in.",
        breaks="A house is inspected once and stays the same. An LLM system gives different answers to the same kind of question, so you inspect it on every change and keep inspecting in production.",
        map=[("Who lives there, and the budget", "Clarify: users, scale, latency and cost budget, what “good” means"),
             ("Foundations", "Data and knowledge: private or changing facts mean RAG"),
             ("The rooms", "Core design: prompt, RAG, agent or fine-tune, justified"),
             ("The inspection and the fire code", "Evaluation (golden set + metrics) and safety (injection, PII, output checks)"),
             ("Running costs, and fixing things after move-in", "Cost and latency (caching, routing, streaming), then iterate from traces")],
        fig=design_svg(),
        cap="Read the left column as the order you speak in; the right column is what the page's worked example says at each step. The loop on the right is the part that makes it a system: failures seen in production become new eval cases.",
        play=("designround", "Pick one of the three design prompts this page uses. The same seven layers stay; watch which ones change, and how."),
        line="Clarify first, then walk data, design, evals, safety, cost and iteration, out loud and in order."),
    "15.5": dict(
        plain=["A take-home is a small project a company asks you to build at home, like a RAG app or an eval harness.",
               "Most candidates make it work and stop there.",
               "“It runs” is the floor, not what gets you hired.",
               "The ones who get offers add an evaluation and handle the messy cases.",
               "They also explain each decision, note the cost, and write a README that runs from a clean clone.",
               "This course's free stack lets you ship all of that for $0."],
        pic="A take-home is like a cooking trial at a restaurant. Every candidate puts a plate on the pass. The one who gets hired also wrote the recipe card, tasted and adjusted the dish with notes, planned for the customer with an allergy, and knows the cost per plate.",
        breaks="A chef tastes by feel. Your “tasting” must be a number another person can reproduce from your repo, which is why the eval script and golden set ship with the code.",
        map=[("A plate on the pass", "It runs: ingest.py and rag.py work end to end"),
             ("The recipe card", "A README with exact setup steps and the reasons behind each decision"),
             ("Tasting with notes", "eval.py + golden.jsonl: recall@k and faithfulness you can reproduce"),
             ("The customer with an allergy", "Failure handling: abstain when unsure, validate output, don't crash"),
             ("Cost per plate", "Token counts, where you'd cache, why this model")],
        fig=takehome_svg(),
        cap="The left column is the page's suggested repo layout. Follow the arrows: two files get you to the floor. Everything above the dashed line comes from the tests, the README and the eval files.",
        line="Make it run, then prove it works with an eval: that second part is what gets the offer."),
    "15.6": dict(
        plain=["The behavioral round tests how you think and work, not what you know.",
               "For AI roles it also tests judgment about a powerful technology that is sometimes wrong.",
               "Answer with STAR: the Situation, your Task, the Action you took, and the Result.",
               "Prepare 4 or 5 true stories in advance, with numbers in the results.",
               "Saying “this doesn't need an LLM” when it's true is one of the strongest signals you can give."],
        pic="A STAR answer is like a short match report. Where and when the game was (situation), what your side needed (task), what you did on the pitch (action), and the final score plus what you would change next time (result).",
        breaks="A match report can praise the whole team. In an interview the action has to be clearly yours (your contribution and your reasoning), or the interviewer can't give you credit for it.",
        map=[("Where and when the game was", "Situation: brief context, one or two sentences"),
             ("What your side needed", "Task: your specific goal or challenge"),
             ("What you did on the pitch", "Action: what you did and why, the longest part"),
             ("Final score, and what you'd change", "Result: the outcome with a number, plus what you learned")],
        fig=flow([("Situation", "Our support bot confidently gave a wrong policy", "c"),
                  ("Task", "Find out why, and stop it happening again", "k"),
                  ("Action", "Traced it: retrieval missed the right chunk because of bad chunking. Fixed chunking, added an eval case", "a"),
                  ("Result", "recall@5 and user thumbs-up improved; the new eval case guards against a repeat", "g")],
                 "A STAR answer to: tell me about a time an LLM didn't work as expected"),
        cap="The page's model answer to “tell me about a time an LLM didn't work as expected”, laid out as STAR. Notice the Action shows systematic debugging (retrieval or generation?) and the Result adds a guard, which is the signal interviewers want.",
        line="Tell a true story in four beats (situation, task, action, result) and make the action clearly yours."),
}
