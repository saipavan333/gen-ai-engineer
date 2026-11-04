"""Pass 2, Section 12: Productionization & LLMOps (pages in track14/)."""
from ease.kit import arrow, box, box_h, esc, flow, lines, path_arrow, raw, rect, svg, text, wrap

import lesson_shape

_SHAPE = lesson_shape.load_data()


def p1(n):
    """Pass-1 analogies in this section say 'Where it breaks:', which the injector does not split, so split here."""
    a = _SHAPE[n]["analogy"]
    i = a.index("Where it breaks:")
    b = a[i + len("Where it breaks:"):].strip()
    return esc(a[:i].strip()), esc(b[0].upper() + b[1:])


# ---------- 12.1 one request in time: client -> FastAPI -> model, plus the 422 path
def seq_svg():
    out = []
    for W, cls, lanes, hw, gap in ((760, "ez-wide", (110, 380, 650), 180, 50), (360, "ez-tall", (52, 180, 308), 96, 58)):
        tall = W < 400
        names = [("Client", "app, website, curl"), ("FastAPI service", "POST /ask endpoint"), ("Ollama model", "qwen2.5:7b, local")]
        if tall:
            names = [("Client", ""), ("FastAPI", ""), ("Model", "")]
        hh = max(box_h(hw, t, s) for t, s in names)
        body = ""
        for (t, s), cx, tone in zip(names, lanes, ("c", "a", "k")):
            b, _ = box(cx - hw / 2, 12, hw, t, s, tone, h=hh)
            body += b
        y = 12 + hh + 40
        rows = [
            ("msg", 0, 1, ['POST /ask  {"question": "What is RAG?"}'], ["POST /ask", '{"question": …}'], ""),
            ("note", 1, ["pydantic checks the body has a question"], ["pydantic checks", "the body"]),
            ("msg", 1, 2, ["ollama.chat(model, messages)"], ["ollama.chat(…)"], ""),
            ("msg", 2, 1, ["reply text, a few seconds later"], ["reply text"], "dash"),
            ("msg", 1, 0, ['200 OK  {"answer": "RAG retrieves…"}'], ["200 OK", '{"answer": …}'], "ok"),
            ("sep", "A bad request: the body has no question" if not tall else "Bad request: no question"),
            ("msg", 0, 1, ["POST /ask  {}"], ["POST /ask {}"], ""),
            ("msg", 1, 0, ["422 error: field 'question' is missing"], ["422 error:", "question missing"], "wn"),
            ("end", "The model is never called, and nothing crashes." if not tall else "The model is never called."),
        ]
        for r in rows:
            if r[0] == "msg":
                _, a, b, lw, lt, c = r
                lab = lt if tall else lw
                y += 14 * (len(lab) - 1)
                x1, x2 = lanes[a], lanes[b]
                d = 1 if x2 > x1 else -1
                body += arrow(x1 + d * 4, y, x2 - d * 4, y, c)
                tc = {"ok": "s ok-t", "wn": "s wn-t"}.get(c, "s")
                body += lines((x1 + x2) / 2, y - 8 - 16 * (len(lab) - 1), lab, tc, size=13, lh=16)
                y += gap
            elif r[0] == "note":
                _, a, lw, lt = r
                lab = lt if tall else lw
                bw = 150 if tall else 300
                bh = 14 + 17 * len(lab)
                y -= 22
                body += rect(lanes[a] - bw / 2, y, bw, bh, "b", rx=6)
                body += lines(lanes[a], y + 20, lab, "s", size=13, lh=17)
                y += bh + gap - 4
            elif r[0] == "sep":
                y -= 18
                body += f'<line x1="10" y1="{y}" x2="{W-10}" y2="{y}" class="grid dash"/>'
                tw = len(r[1]) * 6.6 + 16
                body += rect(10, y + 6, tw, 22, "b", rx=6) + text(18, y + 22, r[1], "s m", "start")
                y += 34 + 28
            else:
                body += text(lanes[1], y - 16, r[1], "s m")
                y += 2
        H = y - 10
        for cx in lanes:
            body = f'<line x1="{cx}" y1="{12+hh}" x2="{cx}" y2="{H-30}" class="ln thin dash"/>' + body
        body += text(W - 10, H + 14, "time runs downward ↓", "s m", "end")
        out.append(svg(W, H + 24, body, "One request through a FastAPI model service, and a bad request rejected with 422", cls))
    return raw(*out)


# ---------- 12.2 one image, many environments; config and secrets come from outside
LAYERS = [("CMD uvicorn main:app", "starts the API on port 8000", "a"),
          ("COPY . .", "your code: main.py, config.py, prompts", "c"),
          ("pip install -r requirements.txt", "pinned versions, so every build is the same", "p"),
          ("FROM python:3.11-slim", "a known, fixed base", "b")]
ENVS = [("dev", "MODEL=qwen2.5:7b\nDB_URL=sqlite:///local.db", "g"),
        ("staging", "PROMPT_VERSION=v15\nDB_URL=staging database", "k"),
        ("prod", "PROMPT_VERSION=v14\nAPI_KEY from the secret store", "a")]


def image_svg():
    # wide
    W = 760
    body = text(20, 22, "Image my-llm-app:3f9c2a1 (about 200 MB), built once", "b", "start")
    y, lw = 34, 330
    for t, s, tone in LAYERS:
        b, h = box(20, y, lw, t, s, tone, h=58, size=14)
        body += b
        y += 58 + 6
    img_bot = y - 6
    body += text(20 + lw / 2, img_bot + 22, "↑ built from the Dockerfile, bottom layer first", "s m")
    ex, ew = 470, 270
    body += text(ex, 22, "docker run, same image, different env vars", "s ac-t", "start")
    ey = 34
    mids = []
    for name, vars_, tone in ENVS:
        vl = vars_.split("\n")
        h = 38 + 18 * len(vl)
        body += rect(ex, ey, ew, h, tone)
        body += text(ex + 12, ey + 22, name, "b", "start")
        body += lines(ex + 12, ey + 42, vl, "s mono", anchor="start", size=12, lh=18)
        mids.append(ey + h / 2)
        ey += h + 12
    for m in mids:
        body += path_arrow([(20 + lw + 4, 34 + (img_bot - 34) / 2), (410, 34 + (img_bot - 34) / 2), (410, m), (ex - 4, m)], "ac")
    wy = max(img_bot + 44, ey + 6)
    body += rect(20, wy, W - 40, 62, "w")
    body += text(36, wy + 24, "Never inside the image", "b wn-t", "start")
    body += text(36, wy + 46, "API keys (secret store, injected at run time) · .env (listed in .gitignore) · 4.7 GB model weights (run as their own service)", "s", "start")
    wide = svg(W, wy + 72, body, "One Docker image runs in dev, staging and prod; config and secrets come from the environment", "ez-wide")
    # tall
    W2 = 360
    body = text(12, 20, "Image my-llm-app:3f9c2a1", "b", "start") + text(12, 38, "about 200 MB, built once", "s m", "start")
    y = 50
    for t, s, tone in LAYERS:
        b, h = box(12, y, W2 - 24, t, s, tone, size=14)
        body += b
        y += h + 5
    body += text(W2 / 2, y + 14, "↑ built bottom layer first", "s m")
    y += 26
    body += arrow(W2 / 2, y, W2 / 2, y + 28, "ac")
    body += text(W2 / 2 + 10, y + 19, "docker run, same image", "s ac-t", "start")
    y += 38
    for name, vars_, tone in ENVS:
        vl = vars_.split("\n")
        h = 38 + 18 * len(vl)
        body += rect(12, y, W2 - 24, h, tone)
        body += text(24, y + 22, name, "b", "start")
        body += lines(24, y + 42, vl, "s mono", anchor="start", size=12, lh=18)
        y += h + 8
    y += 6
    nl = ["API keys: secret store, at run time", ".env: listed in .gitignore", "4.7 GB model weights: own service"]
    body += rect(12, y, W2 - 24, 36 + 18 * len(nl), "w")
    body += text(24, y + 22, "Never inside the image", "b wn-t", "start")
    body += lines(24, y + 44, nl, "s", anchor="start", size=13, lh=18)
    y += 36 + 18 * len(nl)
    tall = svg(W2, y + 10, body, "One Docker image runs in dev, staging and prod; config and secrets come from the environment", "ez-tall")
    return raw(wide, tall)


# ---------- 12.3 the gate as a decision, with the fix loop
def diamond(cx, cy, hw, hh, rows):
    pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
    return f'<polygon points="{pts}" class="bx tn-k"/>' + lines(cx, cy - 8 * (len(rows) - 1) + 5, rows, "b", size=14, lh=17)


def gate_svg():
    W = 760
    b1, h = box(20, 20, 200, "Pull request", "the prompt change is a diff in git", "c", h=92)
    b2, _ = box(280, 20, 200, "pytest", "valid JSON? right chunk retrieved?", "b", h=92)
    b3, _ = box(540, 20, 200, "eval.py", "scores the golden set, e.g. 0.83 (illustrative)", "a", h=92)
    body = b1 + b2 + b3 + arrow(224, 66, 276, 66) + arrow(484, 66, 536, 66)
    body += arrow(640, 116, 640, 150)
    body += diamond(640, 200, 92, 48, ["score ≥", "--min-score 0.85?"])
    rb, _ = box(290, 176, 200, "Merge blocked", "eval.py exits 1, so the build goes red", "w", h=92)
    gb, _ = box(540, 290, 200, "Merge allowed", "exit 0, build green, deploy", "g", h=72)
    body += rb + gb
    body += arrow(548, 200, 494, 200, "wn") + text(521, 192, "no", "s wn-t")
    body += arrow(640, 248, 640, 286, "ok") + text(652, 272, "yes", "s ok-t", "start")
    body += arrow(380, 116, 380, 172, "wn") + text(388, 150, "a test fails", "s wn-t", "start")
    fb, _ = box(20, 176, 200, "Fix and push again", "add the broken case to the golden set too", "p", h=92)
    body += fb + arrow(286, 222, 224, 222, "wn") + arrow(120, 172, 120, 120, "ac")
    body += text(128, 150, "new commit", "s ac-t", "start")
    wide = svg(W, 372, body, "The eval gate: tests and the golden-set score decide whether a pull request can merge", "ez-wide")
    # tall
    W2, bw = 360, 336
    body, y = "", 12
    for t, s, tone in (("Pull request", "the prompt change is a diff in git", "c"),
                       ("pytest", "valid JSON? right chunk retrieved?", "b"),
                       ("eval.py", "scores the golden set, e.g. 0.83 (illustrative)", "a")):
        b, hh = box(12, y, bw, t, s, tone)
        body += b + arrow(180, y + hh + 3, 180, y + hh + 27)
        y += hh + 30
    body += diamond(180, y + 46, 110, 46, ["score ≥", "--min-score 0.85?"])
    y += 92
    body += path_arrow([(70, y - 46), (40, y - 46), (40, y + 26)], "wn") + text(48, y - 54, "no", "s wn-t", "start")
    body += path_arrow([(290, y - 46), (320, y - 46), (320, y + 26)], "ok") + text(312, y - 54, "yes", "s ok-t", "end")
    rb, rh = box(12, y + 30, 160, "Merge blocked", "eval.py exits 1: build red", "w", h=96)
    gb, _ = box(188, y + 30, 160, "Merge allowed", "exit 0: build green, deploy", "g", h=96)
    body += rb + gb
    y += 30 + 96 + 22
    body += text(12, y, "A failing pytest blocks the merge too.", "s m", "start")
    body += text(12, y + 20, "Fix it, add the case to the golden set, push again.", "s m", "start")
    tall = svg(W2, y + 32, body, "The eval gate: tests and the golden-set score decide whether a pull request can merge", "ez-tall")
    return raw(wide, tall)


LESSONS = {
    "12.1": dict(
        plain=["Code in a notebook only helps the person running it.",
               "A web service is a program that waits for requests over the network and sends back answers.",
               "Its address and the shape of each request together are called an API (application programming interface).",
               "Wrap your model code in one, and any app, website or teammate can ask it a question.",
               "In Python, FastAPI does this in about 15 lines."],
        pic=p1("12.1")[0], breaks=p1("12.1")[1],
        map=[("The kitchen where you cook", "Your Python logic: RAG, an agent, a plain model call"),
             ("The counter customers order at", "The endpoint: a URL path such as <code>POST /ask</code>"),
             ("The menu", "The request schema (a pydantic model) that says which fields are allowed"),
             ("Sending back an order that makes no sense", "A <code>422</code> error for a bad request, before your code runs"),
             ("The queue at the door", "Requests in flight; you plan for peak load on purpose")],
        fig=seq_svg(),
        cap="Read it top to bottom: time runs down the page. A good request goes all the way to the model and back. A request with no <code>question</code> is turned away by the schema check with a 422, so the model is never called.",
        line="A service puts a counter and a menu in front of your code, so other programs can order from it."),
    "12.2": dict(
        plain=["Your service needs the right Python, the right libraries and the right versions to run.",
               "Copy it to another computer and one small mismatch can break it.",
               "A container packs your code together with everything it needs into one sealed image.",
               "Docker is the usual tool for building and running these images.",
               "Settings and secrets, like API keys, stay out of the image and are handed in when it starts."],
        pic=p1("12.2")[0], breaks=p1("12.2")[1],
        map=[("The packed lunchbox", "The Docker image: code plus Python plus pinned libraries"),
             ("The packing list", "The Dockerfile, read from the base layer up"),
             ("The allergy note handed to the teacher", "Environment variables and secrets, given at run time"),
             ("Eating the same lunch at school or at home", "The same image running in dev, staging and prod"),
             ("Trying to pack the whole fridge", "Baking 4.7 GB of model weights into the image")],
        fig=image_svg(),
        cap="The image is built once and tagged by commit. Only the environment variables change between dev, staging and prod. The red box is what must never be built in. Image size, tag and prompt versions follow the page's worked example.",
        line="Pack the code and its tools into one box, and hand the settings and secrets in from outside."),
    "12.3": dict(
        plain=["CI (continuous integration) runs your tests on every change and blocks the change if they fail.",
               "Normal bugs announce themselves: something crashes or a test goes red.",
               "A worse prompt crashes nothing. The answers are still fluent, just wrong more often.",
               "So CI also scores your golden set: fixed questions with known good answers.",
               "If the score falls below a bar you set, the change cannot merge."],
        pic=p1("12.3")[0], breaks=p1("12.3")[1],
        map=[("The same 50 words every week", "The golden set: fixed questions with expected answers"),
             ("Your score on the test", "The eval score, for example the share of cases that pass"),
             ("The pass mark", "<code>--min-score 0.85</code> in the CI workflow"),
             ("Failing the test before report-card day", "<code>eval.py</code> exits with code 1, the build goes red, the merge is blocked"),
             ("Forgetting 'separate' while learning 'necessary'", "A regression: a case that passed before now fails")],
        fig=gate_svg(),
        cap="The whole trick is the exit code. <code>eval.py</code> returns 1 when the score is below the bar, and CI treats that like any failed test. The score shown is illustrative.",
        play=("evalgate", "Pick a candidate prompt and move the pass mark. Each square is one golden-set case. Watch which cases flip, and whether the gate catches them."),
        line="Every prompt change has to pass the whole test, not just the question you were fixing."),
    "12.4": dict(
        plain=["Your tests only cover the questions you thought of. Real users ask everything else.",
               "Monitoring means recording what the live service does on every request.",
               "Each request leaves a trace: the prompt, the retrieved text, tool calls, tokens and time taken.",
               "Traces roll up into charts, and an alarm goes off when a number goes out of range.",
               "The failures you find become new test cases, so the system gets better the longer it runs."],
        pic=p1("12.4")[0], breaks=p1("12.4")[1],
        map=[("The patient's file", "Traces: one full record per request"),
             ("Pulse, temperature, blood pressure", "p95 latency, cost per request, error rate, thumbs-down share"),
             ("The alarm when a reading is out of range", "Alerts on p95 and error rate, not on the average"),
             ("Asking how the patient actually feels", "Quality signals: user feedback and an LLM judge on a sample of live traffic"),
             ("Changing the treatment next visit", "Fixing the failure and adding it to the golden set")],
        fig=flow([("Live request", "a real user asks", "c"),
                  ("Trace", "prompt, context, tool calls, tokens, timing", "b"),
                  ("Metrics", "p95 latency, cost, errors, thumbs-down", "a"),
                  ("Alert and triage", "read the traces of the bad answers", "w"),
                  ("Fix and add to the golden set", "the eval gate now blocks it", "g")],
                 "The monitoring loop: traces become metrics, alerts lead to fixes, fixes become test cases",
                 loop=(4, 0, "monitor again: that failure can no longer ship")),
        cap="Monitoring is a loop, not a wall of charts. Each real failure ends up in the golden set from Lesson 12.3, so the eval gate stops it from ever coming back.",
        line="Watch what real users get, and turn every failure you find into a test."),
}
