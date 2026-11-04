"""Pass 2, Track 6: Evals and observability."""
from ease.kit import arrow, box, compare, esc, fan, flow, lines, path_arrow, raw, rect, svg, text, wrap


def split_where(n):
    """Pass-1 analogies in this section end with "Where it breaks: ...", which ease_pass2.split_breaks
    does not recognise. Split it here so the picture and the break are shown once each."""
    import re
    import lesson_shape
    a = lesson_shape.load_data()[n]["analogy"]
    m = re.search(r"\s*Where it breaks:\s*", a)
    pic, br = a[:m.start()].strip(), a[m.end():].strip()
    return dict(pic=pic, breaks=br[0].upper() + br[1:])


def two(fn, label):
    return raw(svg(*fn(760), label, "ez-wide"), svg(*fn(360), label, "ez-tall"))


def seg_bar(x, y, w, h, parts, total):
    """Stacked bar. parts = [(label, n, cls_fill)] ; returns svg."""
    out, cx = "", x
    for lab, n, cls in parts:
        sw = w * n / total
        out += f'<rect x="{cx:.1f}" y="{y}" width="{sw-3:.1f}" height="{h}" rx="5" class="{cls}"/>'
        cx += sw
    return out


# ---------- 6.2 what goes into the 400-case golden set (the page's worked example)
def golden_fig(W):
    nw = W < 400
    x0 = 12 if nw else 20
    bw = W - 2 * x0
    if nw:
        body = text(x0, 20, "The 400-case golden set from", "b", "start", 14) + text(x0, 38, "this page's telecom example", "b", "start", 14)
        y = 56
    else:
        body = text(x0, 20, "The 400-case golden set from this page's telecom example", "b", "start")
        y = 40
    rows = [("What goes in", [("360 real tickets", "sampled by intent share, at least 20 per intent", 360, "fill-a"),
                               ("40 edge cases", "out-of-scope, abusive, should refuse; 10 from past incidents", 40, "fill-k")]),
            ("How it is used", [("300 dev cases", "you look at these while you iterate", 300, "fill-c"),
                                 ("100 locked", "run only before a release", 100, "fill-p")])]
    for title, parts in rows:
        body += text(x0, y + 14, title, "s b", "start")
        y += 24
        body += seg_bar(x0, y, bw, 30, [(a, n, c) for a, _, n, c in parts], 400)
        cx = x0
        for a, d, n, c in parts:
            sw = bw * n / 400
            if sw > 90:
                body += text(cx + (sw - 3) / 2, y + 20, a, "b", size=13)
            cx += sw
        y += 40
        for a, d, n, c in parts:
            body += f'<rect x="{x0}" y="{y}" width="12" height="12" rx="3" class="{c}"/>'
            dl = wrap(f"{a}: {d}", bw - 24, 13)
            body += lines(x0 + 20, y + 11, dl, "s", "start", 13, 17)
            y += 17 * len(dl) + 6
        y += 14
    if nw:
        body += text(x0, y + 6, "Every production incident becomes a new", "s ac-t", "start") + text(x0, y + 24, "case, so the set keeps growing.", "s ac-t", "start")
        return W, y + 38, body
    body += text(x0, y + 6, "Every production incident becomes a new case, so the set keeps growing.", "s ac-t", "start")
    return W, y + 20, body


# ---------- 6.3 the swap test for position bias
def judge_fig(W):
    nw = W < 400
    body = ""
    runs = [("Run 1", "A", "B", "slot 1 wins", "A"), ("Run 2", "B", "A", "slot 1 wins", "B")]
    if not nw:
        body += text(20, 22, "Same question, rubric and two answers. Only the order changes.", "s m", "start")
        y = 40
        for name, s1, s2, v, who in runs:
            body += text(20, y + 40, name, "b", "start")
            body += rect(80, y + 10, 92, 50, "a" if s1 == "A" else "k") + text(126, y + 32, "slot 1", "s", size=12) + text(126, y + 50, f"answer {s1}", "b", size=14)
            body += rect(182, y + 10, 92, 50, "a" if s2 == "A" else "k") + text(228, y + 32, "slot 2", "s", size=12) + text(228, y + 50, f"answer {s2}", "b", size=14)
            body += arrow(278, y + 35, 316, y + 35)
            body += rect(320, y + 4, 130, 62, "c") + text(385, y + 30, "LLM judge", "b") + text(385, y + 50, "+ rubric", "s")
            body += arrow(454, y + 35, 492, y + 35)
            body += rect(496, y + 10, 110, 50, "b") + text(551, y + 32, v, "s", size=12) + text(551, y + 50, f"→ {who} wins", "b", size=14)
            y += 84
        # decision
        body += path_arrow([(608, 75), (640, 75), (640, 112), (650, 112)])
        body += path_arrow([(608, 159), (640, 159), (640, 122), (650, 122)])
        body += rect(652, 70, 96, 94, "w") + text(700, 96, "Orders", "b", size=14) + text(700, 114, "disagree:", "b", size=14) + text(700, 136, "a flip, so", "s", size=13) + text(700, 152, "count a tie", "s", size=13)
        body += text(20, y + 14, "Count a win only when both orders pick the same answer. A flip means the judge is", "s", "start")
        body += text(20, y + 32, "rewarding the slot, not the answer (position bias). Check judges against human labels too.", "s", "start")
        return W, y + 44, body
    body += text(12, 20, "Same question, rubric and answers.", "s m", "start") + text(12, 38, "Only the order changes.", "s m", "start")
    y = 52
    for name, s1, s2, v, who in runs:
        body += text(12, y + 14, name, "b", "start")
        y += 22
        body += rect(12, y, 104, 46, "a" if s1 == "A" else "k") + text(64, y + 19, "slot 1", "s", size=12) + text(64, y + 37, f"answer {s1}", "b", size=14)
        body += rect(124, y, 104, 46, "a" if s2 == "A" else "k") + text(176, y + 19, "slot 2", "s", size=12) + text(176, y + 37, f"answer {s2}", "b", size=14)
        body += arrow(232, y + 23, 252, y + 23)
        body += rect(256, y - 4, 92, 54, "c") + text(302, y + 19, "LLM judge", "b", size=13) + text(302, y + 37, "+ rubric", "s", size=12)
        y += 56
        body += arrow(302, y - 6, 302, y + 10)
        body += rect(196, y + 12, 152, 40, "b") + text(272, y + 37, f"{v} → {who}", "b", size=13)
        y += 66
    body += rect(12, y, 336, 56, "w") + text(180, y + 22, "Orders disagree: a flip", "b", size=14) + text(180, y + 42, "→ count it as a tie, not a win", "s")
    y += 74
    for i, t in enumerate(["Count a win only when both orders agree.", "A flip means the judge rewards the slot,", "not the answer: position bias."]):
        body += text(12, y + i * 18, t, "s", "start")
    return W, y + 3 * 18, body


# ---------- 6.5 one request as a trace (illustrative timings; span sizes from the page)
SPANS = [("input guard", 0, 40, "2 KB"), ("embed", 40, 70, "2 KB"), ("retrieve", 70, 150, "2 KB"),
         ("rerank", 150, 230, "2 KB"), ("LLM call", 230, 1830, "12 KB"), ("output guard", 1830, 1870, "2 KB")]


def trace_fig(W):
    nw = W < 400
    x0 = 12 if nw else 20
    lab = 0 if nw else 120
    gx = x0 + lab
    gw = W - gx - (12 if nw else 90)
    end = SPANS[-1][2]
    X = lambda t: gx + t / end * gw
    body = text(x0, 20, "One request = one trace; each step = one span", "b", "start", 14 if nw else 15)
    body += text(x0, 38, "(illustrative timings; stored size per span from this page)", "s m", "start", 12)
    y = 54
    for t in (0, 500, 1000, 1500):
        body += f'<line x1="{X(t):.1f}" y1="{y}" x2="{X(t):.1f}" y2="{y + len(SPANS) * (46 if nw else 34)}" class="grid"/>'
        body += text(X(t), y + len(SPANS) * (46 if nw else 34) + 16, f"{t} ms", "s m", size=12)
    for name, a, b, kb in SPANS:
        bad = name == "retrieve"
        if nw:
            body += text(x0, y + 12, f"{name}  {b-a} ms · {kb}", "s " + ("wn-t b" if bad else ""), "start", 12)
            body += f'<rect x="{X(a):.1f}" y="{y+18}" width="{max(4, X(b)-X(a)):.1f}" height="16" rx="3" class="{"fill-w" if bad else "fill-a"}"/>'
            y += 46
        else:
            body += text(gx - 10, y + 19, name, "s " + ("wn-t b" if bad else ""), "end")
            body += f'<rect x="{X(a):.1f}" y="{y+6}" width="{max(4, X(b)-X(a)):.1f}" height="20" rx="3" class="{"fill-w" if bad else "fill-a"}"/>'
            body += text(X(b) + 6, y + 21, f"{b-a} ms · {kb}" + ("  · returned the old doc v3" if bad else ""), "s wn-t" if bad else "s", "start", 12)
            y += 34
    y += 30
    msg = ["The retrieve span shows it returned last year's policy (doc v3, not v4).",
           "Fast, no error, wrong data: an indexing bug, not a model bug."]
    if nw:
        msg = ["The retrieve span returned last year's", "policy (doc v3, not v4). Fast, no error,", "wrong data: an indexing bug, not a model bug."]
    for i, m in enumerate(msg):
        body += text(x0, y + 8 + i * 18, m, "s wn-t" if i == 0 else "s", "start", 13)
    return W, y + 8 + len(msg) * 18, body


# ---------- 6.6 a regression gate: the total goes up, one case breaks (illustrative)
BASE = [1, 1, 1, 1, 0, 1, 1, 0, 1, 1]
CAND = [1, 1, 1, 0, 1, 1, 1, 1, 1, 1]


def gate_fig(W):
    nw = W < 400
    x0 = 12 if nw else 20
    n = len(BASE)
    lab = 96 if nw else 150
    cw = (W - x0 - lab - (12 if nw else 200)) / n
    body = text(x0, 20, "10 golden cases, old prompt vs new (illustrative)", "b", "start", 14 if nw else 15)
    y = 40
    for i in range(n):
        body += text(x0 + lab + i * cw + cw / 2, y + 12, f"#{i+1}", "s m", size=12)
    y += 20
    for name, row in (("old prompt", BASE), ("new prompt", CAND)):
        body += text(x0 + lab - 10, y + 22, name, "s b", "end")
        for i, v in enumerate(row):
            reg = name == "new prompt" and BASE[i] == 1 and v == 0
            cls = "fill-g" if v else "fill-w"
            body += f'<rect x="{x0+lab+i*cw+3:.1f}" y="{y}" width="{cw-6:.1f}" height="32" rx="5" class="{cls}"/>'
            body += text(x0 + lab + i * cw + cw / 2, y + 21, "✓" if v else "✗", "b", size=14)
            if reg:
                body += f'<rect x="{x0+lab+i*cw:.1f}" y="{y-3}" width="{cw:.1f}" height="38" rx="7" class="ring"/>'
        if not nw:
            body += text(x0 + lab + n * cw + 14, y + 22, f"{sum(row)}/10 pass", "b", "start")
        y += 42
    regressed = [i + 1 for i in range(n) if BASE[i] == 1 and CAND[i] == 0]
    if nw:
        body += text(x0, y + 12, f"old {sum(BASE)}/10 → new {sum(CAND)}/10: the total went up", "s", "start")
        y += 22
    else:
        body += text(x0, y + 12, f"The total went up, {sum(BASE)}/10 → {sum(CAND)}/10, but case #{regressed[0]} went from pass to fail.", "s", "start")
        y += 22
    body += rect(x0, y + 4, W - 2 * x0, 44, "w") + text(W / 2, y + 32, f"Gate: no case may regress → BLOCKED (case #{regressed[0]})", "b wn-t", size=14 if nw else 15)
    return W, y + 60, body


LESSONS = {
    "6.1": dict(
        plain=["An eval (evaluation) is a test that scores how good your AI system's answers are.",
               "You keep a fixed list of questions with known good answers, and a rule for scoring each answer.",
               "Every time you change something, you run the same list and compare the score with the old version.",
               "Without this, you look at three answers, decide it “seems better”, and miss what broke.",
               "Evals turn guessing into measuring."],
        map=[("The fixed tasting list of dishes", "The golden set: the same test cases on every run"),
             ("The score the cook writes down", "The metric: exact match, a rule, or an LLM judge"),
             ("Last week's scores", "The baseline: the current version's results"),
             ("Changing the recipe only if the scores hold", "Ship the change only if it measurably helps")],
        fig=flow([("Make a change", "new prompt, model or RAG setting", "c"),
                  ("Run the golden set", "the same fixed cases every time"),
                  ("Score every case", "exact match, a rule, or an LLM judge", "a"),
                  ("Compare to baseline", "per case and per category, not only the total", "k"),
                  ("Keep or revert", "ship only what measurably helps", "g")],
                 "The eval-driven loop", loop=(4, 0, "next change goes through the same loop")),
        cap="The loop that replaces “looks better to me”. The compare step is per case and per category, because a change can lift the total while breaking one kind of question, as the bank example below shows.",
        line="An eval is a fixed test you run after every change, so you know whether you made things better or worse."),
    "6.2": dict(
        plain=["A golden set is a list of real questions, each with a known good answer or a clear pass rule.",
               "It is your team's shared definition of “working”.",
               "It should cover every kind of question, including the tricky ones the system gets wrong.",
               "Keep some cases locked away so nobody tunes the prompt to them.",
               "Every time users find a new failure, add it as a new case."],
        map=[("Questions from every chapter", "Cases from every intent or category of real traffic"),
             ("The tricky questions students always miss", "Edge cases: out-of-scope, ambiguous, should-refuse"),
             ("The answer key", "The expected output or acceptance rule for each case"),
             ("Keeping the exam paper locked", "A held-out set you run only before a release")],
        fig=two(golden_fig, "What goes into a 400-case golden set and how it is split"),
        cap="Real traffic sampled with a floor per intent, plus edge cases on purpose, then split so 100 cases stay unseen while you tune. The numbers are this page's worked example.",
        play=("goldensize", "Move the number of cases and the pass rate. The 95% Wilson interval is computed live: the range where the true pass rate probably sits."),
        line="A golden set is the answer key you test against every time, and it keeps growing."),
    "6.3": dict(
        plain=["Many answers have no single right wording, so a simple text match can't grade them.",
               "LLM-as-judge means asking another model to grade the answer against a written checklist called a rubric.",
               "It can score one answer, or pick the better of two.",
               "Judges have habits: they may favour the first answer shown, or the longest one.",
               "So you swap the order to test for that, and you check the judge against human grades before trusting it."],
        map=[("The judge's scorecard", "The rubric: correct, complete, grounded, concise"),
             ("Liking whoever sang first", "Position bias in pairwise judging"),
             ("Extra points for the longest song", "Verbosity bias: longer answers scored higher"),
             ("Favouring singers from their own school", "Self-preference: rating its own model family higher"),
             ("Checking against expert judges", "Calibrating the judge against human labels (agreement, Cohen's kappa)")],
        fig=two(judge_fig, "The swap test: judge the same pair in both orders"),
        cap="Run each pair twice with the answers swapped. If the judge picks whatever sits in slot 1 both times, its verdict is about position, not quality. The page's worked example counts a win only when both orders agree.",
        play=("judgeswap", "Pick a pair and an order. The judge here is a made-up biased one: it adds a bonus to whatever sits in slot 1. Watch which pairs flip."),
        line="A model can grade answers for you, but test the grader for bias before you trust its marks."),
    "6.4": dict(
        plain=["Offline evals test the system on your golden set before you ship. They are fast, cheap and repeatable.",
               "Online evals watch real users after you ship.",
               "An A/B test sends some users to the new version and compares results, like how many problems get solved.",
               "Offline is a practice test; online is the real thing.",
               "Use both, and turn online failures into new offline cases."],
        map=[("The car park test with the same cones", "Offline eval on a fixed golden set"),
             ("Real roads in rush hour", "Online eval on production traffic"),
             ("A bus cutting in", "Real user queries your golden set never imagined"),
             ("Comparing two learner drivers on the same roads", "An A/B test: two versions, real users, one metric chosen in advance")],
        fig=compare(("Offline: before you ship", ["Fixed golden set, same cases every run", "Minutes to run, cheap, repeatable",
                                                  "Gates every change", "Only as good as the cases you thought of"], "c"),
                    ("Online: after you ship", ["Real users and real traffic", "A/B tests, thumbs up or down, task completion",
                                                "Slow: needs enough traffic to be sure", "Guardrails: latency, cost, error rate"], "g"),
                    "Offline versus online evaluation",
                    verdict="Online failures become new golden cases, so the offline test gets closer to reality."),
        cap="Neither side is enough on its own. Offline catches regressions before users see them; online tells you whether the change helped real people.",
        line="Test on your practice set before shipping, then watch real users to learn what actually works."),
    "6.5": dict(
        plain=["One answer from an AI app often takes several steps: search, build a prompt, call the model, check.",
               "When the answer is wrong, the final text alone doesn't tell you which step failed.",
               "A trace is a record of one request, step by step. Each step is called a span.",
               "A span stores what went in, what came out, how long it took and what it cost.",
               "Monitoring adds these up into charts and alerts, so you hear about problems before users complain."],
        map=[("The parcel's tracking page", "The trace: the whole record of one request"),
             ("Each stop: picked up, sorted, customs", "Each span: guard, embed, retrieve, rerank, LLM call"),
             ("“Stuck at customs for two days”", "A span that is slow, failed, or returned the wrong data"),
             ("What's inside the parcel", "The stored prompt and retrieved text, which may hold private data to redact")],
        fig=two(trace_fig, "A trace as a waterfall of timed spans"),
        cap="A trace drawn as a waterfall. Without it you only see a wrong answer. With it you can see the retrieve step quietly fetched an old document, which is the worked example further down this page.",
        line="A trace is a step-by-step receipt for one request, so you can see exactly where it went wrong."),
    "6.6": dict(
        plain=["A small prompt change that fixes one case can quietly break others.",
               "A regression test checks that something that used to work still works.",
               "Wire your golden set into a test suite that runs on every change, like the tests for normal code.",
               "A gate is the rule that decides if the change may ship, such as “no case may get worse”.",
               "Because answers can vary from run to run, important cases are often run more than once."],
        map=[("The pilot's checklist before every flight", "The eval suite run on every change (CI, continuous integration)"),
             ("Each line exists because something once went wrong", "Each case added after a real failure"),
             ("Any failed line keeps the plane on the ground", "The gate blocks the merge on a regression"),
             ("Checking twice when an instrument flickers", "Running a case 3 times and deciding on the majority")],
        fig=two(gate_fig, "A regression gate blocks a change even though the total score went up"),
        cap="Comparing totals would ship this change. Comparing case by case shows case #4 broke, so the gate blocks it. The pass marks are illustrative.",
        line="Run the same tests on every prompt change and refuse any change that breaks a case that used to pass."),
}
for _n, _e in LESSONS.items():
    _e.update(split_where(_n))
