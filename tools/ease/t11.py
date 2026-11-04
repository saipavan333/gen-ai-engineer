"""Pass 2, Section 11: Going deeper (folder track12/). Numbers are computed from the inputs the
lesson pages state in their "At real scale" boxes."""
from ease.kit import arrow, box, flow, lines, raw, rect, svg, text, wrap
from ease.t08 import bar, fold_where, label_lines


# ---------- 11.2 small per-step error rates compound over a 10-step task
def compound_svg():
    steps = list(range(1, 11))
    lo = [0.95 ** n for n in steps]
    hi = [(0.95 + 0.05 * 0.6) ** n for n in steps]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "Chance the whole task succeeds, by number of steps" if not nw else "Chance the whole task succeeds", "b", "start")
        lx, rx = (44, W - 14) if nw else (60, W - 150)
        top, bot = 44, 44 + (190 if nw else 210)
        sy = lambda p: bot - (bot - top) * p
        # gridlines
        for p in (0, 0.25, 0.5, 0.75, 1.0):
            body += f'<line x1="{lx}" y1="{sy(p):g}" x2="{rx}" y2="{sy(p):g}" class="grid"/>' + text(lx - 6, sy(p) + 4, f"{p:.0%}", "s m", "end")
        gw = (rx - lx) / len(steps)
        bw = gw * 0.36
        for i, n in enumerate(steps):
            x = lx + i * gw + gw * 0.12
            body += bar(x, sy(lo[i]), bw, bot - sy(lo[i]), "fill-w", 2)
            body += bar(x + bw + 2, sy(hi[i]), bw, bot - sy(hi[i]), "fill-g", 2)
            body += text(lx + i * gw + gw / 2, bot + 16, str(n), "s m")
        body += text((lx + rx) / 2, bot + 34, "steps in the task", "s m")
        # end labels
        ex = lx + 9 * gw + gw * 0.12
        if nw:
            body += text(rx, sy(lo[-1]) - 8, f"{lo[-1]:.0%}", "s b wn-t", "end")
            body += text(rx, sy(hi[-1]) - 8, f"{hi[-1]:.0%}", "s b ok-t", "end")
            y = bot + 56
            body += bar(14, y - 11, 14, 14, "fill-w") + text(34, y + 1, "95% per step", "s", "start")
            body += bar(150, y - 11, 14, 14, "fill-g") + text(170, y + 1, "98% (errors recovered)", "s", "start")
            y += 26
        else:
            body += text(rx + 12, sy(lo[-1]) + 4, f"{lo[-1]:.0%} at 95% a step", "s b wn-t", "start")
            body += text(rx + 12, sy(hi[-1]) + 4, f"{hi[-1]:.0%} at 98% a step", "s b ok-t", "start")
            y = bot + 58
        tail = "Every step multiplies in its own chance of failing. Validating tool results, retrying and escalating are what lift the per-step rate."
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Bar chart: success of a multi-step task falls fast as steps add up", cls))
    return raw(*out)


# ---------- 11.3 the judge-vs-human agreement table and Cohen's kappa (the page's 50 labels)
def kappa_numbers():
    yy, yn, ny, nn = 27, 3, 5, 15          # human yes/judge yes, human yes/judge no, human no/judge yes, both no
    n = yy + yn + ny + nn
    po = (yy + nn) / n
    ph, pj = (yy + yn) / n, (yy + ny) / n
    pe = ph * pj + (1 - ph) * (1 - pj)
    return dict(c=(yy, yn, ny, nn), n=n, po=po, pe=pe, k=(po - pe) / (1 - pe), ph=ph, pj=pj)


def kappa_svg():
    k = kappa_numbers()
    yy, yn, ny, nn = k["c"]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "50 answers labelled by humans and by the LLM judge" if not nw else "50 answers: humans vs the judge", "b", "start")
        gx, gy, cw, ch = (110, 70, 100, 66) if nw else (150, 70, 120, 70)
        body += text(gx + cw, gy - 26, "judge says", "s b")
        body += text(gx + cw / 2, gy - 8, "faithful", "s") + text(gx + cw * 1.5, gy - 8, "not", "s")
        body += text(gx - 10, gy + ch / 2 - 4, "human:", "s b", "end") + text(gx - 10, gy + ch / 2 + 13, "faithful", "s", "end")
        body += text(gx - 10, gy + ch * 1.5 + 4, "human: not", "s b", "end")
        cells = [(0, 0, yy, "g", "agree"), (1, 0, yn, "k", "too strict"), (0, 1, ny, "w", "too lenient"), (1, 1, nn, "g", "agree")]
        for c, r, v, tone, lab in cells:
            x, y = gx + c * cw, gy + r * ch
            body += rect(x + 2, y + 2, cw - 4, ch - 4, tone, rx=6)
            body += text(x + cw / 2, y + 32, str(v), "b", size=20)
            body += text(x + cw / 2, y + 52, lab, "s", size=12)
        if nw:
            x0, y = 14, gy + 2 * ch + 30
        else:
            x0, y = gx + 2 * cw + 50, 52
        rows = [("Raw agreement", f"({yy} + {nn}) / {k['n']} = {k['po']:.2f}"),
                ("Chance agreement", f"{k['ph']:.2f} x {k['pj']:.2f} + {1 - k['ph']:.2f} x {1 - k['pj']:.2f} = {k['pe']:.3f}"),
                ("Cohen's kappa", f"({k['po']:.2f} - {k['pe']:.3f}) / (1 - {k['pe']:.3f}) = {k['k']:.2f}")]
        for i, (a, b) in enumerate(rows):
            body += text(x0, y, a, "s b" + (" ac-t" if i == 2 else ""), "start")
            body += text(x0, y + 18, b, "s mono" if not nw else "s", "start")
            y += 46
        tail = (f"Kappa {k['k']:.2f} means usable, but the {ny} answers the judge passed and humans failed are the dangerous ones for a faithfulness gate: tighten the rubric and re-measure.")
        ty = max(y, gy + 2 * ch + 24) if not nw else y + 2
        tl, th = label_lines(14, ty, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, ty + th + 4, body, "Agreement table between human labels and an LLM judge, and the kappa calculation", cls))
    return raw(*out)


K = kappa_numbers()

LESSONS = {
    "11.1": dict(
        plain=["Basic RAG (retrieval-augmented generation) embeds the question and grabs the closest few chunks.",
               "It stalls when the question is worded differently from the documents, or the right chunk is buried.",
               "Advanced RAG adds fixes: rewrite the question, search with several versions, then rerank the results carefully.",
               "Then it trims the context so only the useful sentences reach the model.",
               "Each fix is a knob, and an evaluation tells you which knob actually helped."],
        map=[("Trying a few phrasings", "Query rewriting and multi-query: several versions, results merged with RRF (reciprocal rank fusion)"),
             ("Guessing the title", "HyDE: embed a made-up ideal answer instead of the short question"),
             ("Checking two shelves, then picking the best", "Retrieve 25 cheaply (bi-encoder), rerank with a cross-encoder, keep 5"),
             ("Handing over only the two pages that matter", "Context compression and ordering, against “lost in the middle”")],
        fig=flow([("Fix the query", "rewrite, multi-query, HyDE", "c"),
                  ("Retrieve wide", "bi-encoder top 25 per query, fused with RRF", "b"),
                  ("Rerank", "cross-encoder reads query + chunk, keeps 5", "p"),
                  ("Curate", "dedupe, trim to relevant sentences, best first and last", "k"),
                  ("Generate", "grounded answer with citations", "g")],
                 "Advanced RAG pipeline", loop=(4, 0, "measure on the golden set, then change one knob at a time")),
        cap="Each box is a knob you can turn on its own. The loop is the discipline: turn one knob, rerun the eval, keep it only if the numbers moved the right way.",
        play=("rrf", "Switch the query versions on and off. Each list is a ranked search result (illustrative); the fused score uses the page's formula, 1 / (60 + rank), added across lists."),
        line="Better RAG means a better question, a wider search, a careful re-sort and a tidy context, each checked by an eval."),
    "11.2": dict(
        plain=["An agent is a model that takes many steps: think, call a tool, read the result, repeat.",
               "Small mistakes add up: if each step is right 95% of the time, a 10-step task works only about 60% of the time.",
               "Reliable agents make a plan first, check their own work and check every tool result.",
               "They also have hard limits on steps, time and money, and hand over to a person when stuck.",
               "To test an agent, grade the whole journey, not just the final answer."],
        map=[("The intern's checklist", "Plan-then-execute: a plan you can validate before any action runs"),
             ("Checking the receipts", "Validating tool results and reviewing the trajectory (every step in the trace)"),
             ("A spending limit", "Caps on steps, wall-clock time and tokens per task"),
             ("A phone to call when stuck", "Escalating to a human instead of looping")],
        fig=compound_svg(),
        cap="Computed from the page: 0.95 to the power of the step count, and 0.98 once tool-error recovery rescues 60% of failed steps. At 10 steps that is 60% versus 82%.",
        line="An agent is only as reliable as all its steps multiplied together, so check each step and cap the loop."),
    "11.3": dict(
        plain=["An LLM judge is a model that grades other models' answers.",
               "A judge can be wrong or biased too, so you test the judge before you trust it.",
               "First compare its grades with human grades on 30 to 50 examples.",
               "Then cancel its known habits, such as liking the first answer shown or the longer one.",
               "Finally, only call a new version better when the gap is bigger than the noise."],
        map=[("Watching the new referee call 50 recorded plays", "Calibrating the judge against hand labels"),
             ("Agreeing more often than chance", "Cohen's kappa: agreement corrected for luck"),
             ("Swapping the teams' sides of the screen", "Position swapping: judge A-then-B and B-then-A"),
             ("One lucky call in a close game", "Noise: a small score change can be random, so test significance")],
        fig=kappa_svg(),
        cap=f"The counts are the page's example. Raw agreement looks high at {K['po']:.0%}, but some of it would happen by luck; kappa removes that and lands at {K['k']:.2f}.",
        line="Before a judge grades your system, grade the judge."),
}
fold_where(LESSONS)
