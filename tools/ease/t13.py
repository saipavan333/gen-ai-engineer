"""Pass 2, Section 13: Frontier & responsible AI (pages in track16/)."""
from ease.kit import arrow, box, box_h, esc, lines, path_arrow, raw, rect, svg, text, wrap

# ---------- 13.1 the same answer with and without thinking (token counts from the page's worked example)
OUT_PRICE = 10.0   # Claude Sonnet 5.5, $ per million output tokens (thinking is billed as output)
TPS = 80           # the page's assumed output speed, tokens per second
ANSWER, THINK = 300, 4000


def think_svg():
    rows = [("Easy input, low effort", "the model may skip thinking", 0),
            ("Hard problem, high effort", "adaptive thinking runs long first", THINK)]
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        tall = W < 400
        x0 = 12 if tall else 230
        span = W - x0 - 16
        sc = (span - 100) / (THINK + ANSWER)
        body = text(12, 22, "Tokens the model writes for one answer (illustrative sizes from the page's example)", "s m", "start") if not tall else \
            text(12, 20, "Tokens written for one answer", "b", "start") + text(12, 38, "(sizes from the page's example)", "s m", "start")
        y = 72 if tall else 50
        for name, sub, th in rows:
            if tall:
                body += text(12, y, name, "b", "start") + text(12, y + 18, sub, "s m", "start")
                by = y + 28
            else:
                body += text(12, y + 18, name, "b", "start") + text(12, y + 36, sub, "s m", "start")
                by = y + 6
            x = x0
            if th:
                w = th * sc
                body += f'<rect x="{x:g}" y="{by+6:g}" width="{w:g}" height="22" rx="4" class="fill-k"/>' + text(x + 4, by + 2, f"thinking {th:,} tokens (often hidden)", "s b k-t", "start")
                x += w + 3
            w = max(ANSWER * sc, 30)
            body += f'<rect x="{x:g}" y="{by+6:g}" width="{w:g}" height="22" rx="4" class="fill-g"/>' + text(x + w + 6, by + 22, f"answer {ANSWER}", "s b ok-t", "start")
            tot = th + ANSWER
            if tall:
                body += text(x0, by + 50, f"billed output {tot:,} tokens = ${tot * OUT_PRICE / 1e6:.3f}", "s", "start")
                body += text(x0, by + 68, f"about {tot / TPS:.0f} s at {TPS} tokens/s", "s m", "start")
                by += 18
            else:
                body += text(x0, by + 50, f"billed output {tot:,} tokens = ${tot * OUT_PRICE / 1e6:.3f}, about {tot / TPS:.0f} s at {TPS} tokens/s", "s", "start")
            y = by + (86 if tall else 78)
        # effort dial
        levels = ["low", "medium", "high", "xhigh", "max"]
        body += text(12, y + 4, "You steer it with output_config.effort:" if not tall else "Steer it with output_config.effort:", "s ac-t", "start")
        y += 18
        lw = (W - 24 - 4 * 6) / 5
        for i, lv in enumerate(levels):
            lx = 12 + i * (lw + 6)
            body += rect(lx, y, lw, 30, "a" if lv == "high" else "b", rx=6) + text(lx + lw / 2, y + 20, lv, "s b mono")
        hx = 12 + 2 * (lw + 6) + lw / 2
        body += text(hx, y + 46, "default on Sonnet 5.5", "s ac-t", size=12)
        y += 12
        body += arrow(14, y + 46, W - 14, y + 46, "ac")
        body += text(12, y + 66, "more thinking, slower, more billed output →" if tall else
                     "more thinking allowed → slower and more billed output, better on hard multi-step problems", "s", "start")
        body += text(12, y + 86, "budget_tokens is rejected (400) on Claude 4.7 and later.", "s wn-t", "start")
        out.append(svg(W, y + 98, body, "Thinking tokens before the answer, billed as output, steered by effort level", cls))
    return raw(*out)


# ---------- 13.2 where your data and your money go: closed API vs open weights
def openclosed_svg():
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        tall = W < 400
        body = ""
        if not tall:
            edge = 410
            body += text(edge - 8, 22, "your network", "s m", "end") + text(edge + 8, 22, "outside", "s m", "start")
            for k, (lab, tone) in enumerate((("Closed API model", "c"), ("Open-weight model", "g"))):
                y = 50 + k * 140
                body += f'<line x1="{edge}" y1="{y-20 if k else 30}" x2="{edge}" y2="{y+82}" class="ln wn dash"/>'
                body += text(20, y - 6, lab, "b", "start")
                b, h = box(20, y + 4, 160, "Your app", "prompt with user data", "b", h=70, size=14)
                body += b
                if k == 0:
                    b2, _ = box(470, y + 4, 270, "Provider's model", "their GPUs; they choose when versions change", "c", h=70, size=14)
                    body += b2 + arrow(184, y + 30, 466, y + 30, "wn") + arrow(466, y + 54, 184, y + 54)
                    body += text(296, y + 22, "prompt leaves your network", "s wn-t")
                    body += text(296, y + 72, "answer comes back", "s m")
                    body += text(20, y + 104, "Pay per token (Sonnet 5.5: $2 in / $10 out per million). No servers to run. Needs a data processing agreement.", "s", "start")
                else:
                    b2, _ = box(240, y + 4, 150, "Your GPUs", "open weights you downloaded", "g", h=70, size=14)
                    body += b2 + arrow(184, y + 30, 236, y + 30) + arrow(236, y + 54, 184, y + 54)
                    body += text(edge + 14, y + 44, "nothing crosses the line", "s ok-t", "start")
                    body += text(20, y + 104, "Pay for GPUs and engineers, busy or idle. You pick the versions. Data never leaves.", "s", "start")
            out.append(svg(W, 310, body, "Closed API sends prompts outside your network; open weights run inside it", cls))
        else:
            y = 14
            for k, (lab, tone) in enumerate((("Closed API model", "c"), ("Open-weight model", "g"))):
                body += text(12, y + 8, lab, "b", "start")
                y += 20
                b, h = box(12, y, 150, "Your app", "prompt + user data", "b", h=62, size=14)
                body += b
                if k == 0:
                    b2, _ = box(198, y, 150, "Provider's model", "their GPUs", "c", h=62, size=14)
                    body += f'<line x1="180" y1="{y-14}" x2="180" y2="{y+76}" class="ln wn dash"/>'
                    body += arrow(165, y + 22, 195, y + 22, "wn") + arrow(195, y + 42, 165, y + 42)
                    ln = ["Prompt leaves your network.", "Pay per token ($2 / $10 per million", "on Sonnet 5.5). No servers to run."]
                else:
                    b2, _ = box(198, y, 150, "Your GPUs", "open weights", "g", h=62, size=14)
                    body += arrow(165, y + 22, 195, y + 22) + arrow(195, y + 42, 165, y + 42)
                    body += f'<rect x="5" y="{y-6}" width="350" height="74" rx="12" class="ln wn dash"/>'
                    ln = ["Everything stays inside.", "Pay for GPUs and engineers,", "busy or idle. You pick versions."]
                body += b2
                body += lines(12, y + 88, ln, "s", anchor="start", size=13, lh=18)
                y += 88 + 18 * len(ln) + 14
            out.append(svg(W, y, body, "Closed API sends prompts outside your network; open weights run inside it", cls))
    return raw(*out)


# ---------- 13.3 matched-pair audit, computed from the page's illustrative rates
RATES = [("Group A", 32), ("Group B", 31), ("Group C", 30), ("Group D", 23)]


def audit_svg():
    top = max(r for _, r in RATES)
    line = 0.8 * top
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        tall = W < 400
        x0, bw = (90, W - 260) if not tall else (78, W - 190)
        sc = bw / 40
        body = text(12, 20, "Same 500 resumes, only the name changed (rates from the page, illustrative)" if not tall
                    else "Same 500 resumes, only the name changed", "s m", "start")
        y = 42
        for name, r in RATES:
            ratio = r / top
            bad = ratio < 0.8
            body += text(x0 - 10, y + 20, name, "s b", "end")
            body += f'<rect x="{x0}" y="{y+4}" width="{r*sc:g}" height="24" rx="4" class="{"fill-w" if bad else "fill-g"}"/>'
            body += text(x0 + 34 * sc, y + 21, f"{r}%  ratio {ratio:.2f}", "s " + ("wn-t b" if bad else ""), "start")
            y += 38
        lx = x0 + line * sc
        body += f'<line x1="{lx:g}" y1="34" x2="{lx:g}" y2="{y+4}" class="ln wn dash"/>'
        body += text(lx, y + 22, f"four-fifths line: 0.8 x {top}% = {line:.1f}%", "s wn-t")
        body += text(12, y + 48, "Below the line is evidence of adverse impact." if tall else
                     f"Group D advances at {RATES[-1][1]}%, ratio {RATES[-1][1]/top:.2f} < 0.8: evidence of adverse impact on identical qualifications.", "s", "start")
        avg = sum(r for _, r in RATES) / len(RATES)
        body += text(12, y + 68, f"The average advance rate is {avg:.0f}%. It hides the gap.", "s m", "start")
        out.append(svg(W, y + 80, body, "Per-group advance rates against the four-fifths line", cls))
    return raw(*out)


# ---------- 13.4 the EU AI Act timeline (dates exactly as on the page)
DATES = [("1 Aug 2024", "Act enters into force", "b"),
         ("2 Feb 2025", "prohibited practices apply", "w"),
         ("2 Aug 2025", "general-purpose AI model obligations", "p"),
         ("2 Aug 2026", "Act generally applicable", "c"),
         ("2 Dec 2027", "high-risk rules for Annex III areas (after the 2026 AI Omnibus)", "k")]


def timeline_svg():
    # wide: horizontal axis, labels alternate above and below
    W = 760
    body = ""
    ax, ay, L = 110, 150, 540
    body += arrow(ax - 20, ay, ax + L + 30, ay)
    xs = [ax + i * L / (len(DATES) - 1) for i in range(len(DATES))]
    for i, ((d, what, tone), x) in enumerate(zip(DATES, xs)):
        body += f'<circle cx="{x:g}" cy="{ay}" r="9" class="dot tn-{tone}"/>'
        up = i % 2 == 0
        wl = wrap(what, 190, 13)
        if up:
            body += f'<line x1="{x:g}" y1="{ay-12}" x2="{x:g}" y2="{ay-38}" class="ln thin"/>'
            body += text(x, ay - 48 - 17 * len(wl), d, "b") + lines(x, ay - 44 - 17 * (len(wl) - 1), wl, "s", size=13, lh=17)
        else:
            body += f'<line x1="{x:g}" y1="{ay+12}" x2="{x:g}" y2="{ay+38}" class="ln thin"/>'
            body += text(x, ay + 58, d, "b") + lines(x, ay + 78, wl, "s", size=13, lh=17)
    body += text(W / 2, 272, "A loan-scoring feature is high-risk (Annex III), so 2 December 2027 is the date to plan back from.", "s ac-t")
    wide = svg(W, 286, body, "EU AI Act timeline from entry into force to the Annex III high-risk date", "ez-wide")
    # tall: vertical axis
    W2 = 360
    body, y = "", 20
    ys = []
    for d, what, tone in DATES:
        wl = wrap(what, 250, 13)
        ys.append(y)
        body += f'<circle cx="30" cy="{y+6}" r="9" class="dot tn-{tone}"/>'
        body += text(52, y + 11, d, "b", "start") + lines(52, y + 31, wl, "s", anchor="start", size=13, lh=17)
        y += 34 + 17 * len(wl) + 14
    body = f'<line x1="30" y1="{ys[0]+6}" x2="30" y2="{ys[-1]+6}" class="ln"/>' + body
    body += arrow(30, ys[-1] + 16, 30, ys[-1] + 52) + text(52, ys[-1] + 48, "time", "s m", "start")
    y = ys[-1] + 80
    body += lines(12, y, ["Loan scoring is high-risk (Annex III):", "plan back from 2 December 2027."], "s ac-t", anchor="start", size=13, lh=18)
    tall = svg(W2, y + 30, body, "EU AI Act timeline from entry into force to the Annex III high-risk date", "ez-tall")
    return raw(wide, tall)


LESSONS = {
    "13.1": dict(
        plain=["A normal model starts writing its answer straight away.",
               "A reasoning model first writes out its thinking, step by step, and checks itself before it answers.",
               "That extra work at answer time is called test-time compute.",
               "It makes models much better at maths, code and multi-step planning.",
               "But thinking tokens cost money and time, so you only want it on hard problems."],
        map=[("Hitting the buzzer straight away", "One quick pass: the model writes only the answer"),
             ("Scribbling on the notepad", "Thinking tokens written before the final answer"),
             ("Paying for every page of scribbling", "Thinking tokens are billed as output tokens"),
             ("How long you are allowed to scribble", "The effort level (<code>low</code> to <code>max</code>); the model decides how much to think"),
             ("Not wasting a minute on 'what colour is the sky'", "Routing easy requests to low effort or a cheaper model")],
        fig=think_svg(),
        cap="Thinking happens before the answer and is billed as output. The token counts and the 80 tokens a second are the page's assumptions; cost uses Claude Sonnet 5.5's $10 per million output tokens. Effort is a signal, not a hard cap: <code>max_tokens</code> is the hard limit.",
        breaks="The model's scribbling is not always shown to you, but you are still billed for it. And the scribbles are not a faithful record of how it got the answer: tidy-looking reasoning can sit on top of a wrong answer, so check the answer, not the notepad.",
        line="A reasoning model thinks before it speaks, which helps on hard problems and costs you every word it thinks."),
    "13.2": dict(
        plain=["AI news changes every month, so learn the big directions, not the headlines.",
               "Context windows got huge, agents got more reliable, and small open models got good.",
               "Open-weight models are ones whose numbers (weights) you can download and run on your own machines.",
               "Closed models you only reach through a company's API (application programming interface).",
               "Picking between them is a real design choice about cost, privacy and control."],
        map=[("Eating at the restaurant", "Calling a closed model through its API"),
             ("Paying per plate", "Paying per token, for every call"),
             ("The menu changing when they like", "The provider decides when model versions change"),
             ("Your order leaving the house", "Your prompt, with any user data in it, goes to a third party"),
             ("Owning the kitchen", "Running open weights on your own GPUs, busy or idle")],
        fig=openclosed_svg(),
        cap="The red dashed line is the edge of your network. With a closed API the prompt crosses it on every call; with open weights nothing does, but you pay for the hardware whether it is busy or not.",
        line="Rent the best chef by the plate, or own the kitchen: choose by privacy, volume and how good the answer must be."),
    "13.3": dict(
        plain=["Models learn from text written by people, so they pick up people's biases too.",
               "That matters when a system makes decisions about people, such as who gets a job interview or a loan.",
               "A good overall score can hide a group that is failed again and again.",
               "So you measure results for each group separately, with inputs that differ only in, say, the name.",
               "Then you fix what you find and measure again."],
        map=[("The class average", "Overall accuracy or overall advance rate"),
             ("Results for each group of kids", "Disaggregated evaluation: the same metric per group"),
             ("The same essay in different handwriting", "Matched pairs: the same resume with only the name changed"),
             ("Kids with messy writing marked down", "A group whose rate falls below four-fifths of the top group's"),
             ("A teacher checking the machine's marks", "Human review of rejects and a model card that records the tests")],
        fig=audit_svg(),
        cap="Bars are the advance rates from the page's matched-pair audit (illustrative). Each ratio is the group's rate divided by the highest. US federal guidelines generally treat a ratio below 0.8 as evidence of adverse impact.",
        line="Never trust the class average: check every group, with the same inputs, before the system judges real people."),
    "13.4": dict(
        plain=["Laws now set rules for AI systems. The EU AI Act is the best-known one, and its main idea is spreading.",
               "Its main idea: the more harm a use could do, the more rules it must follow.",
               "A few uses are banned, and hiring and credit scoring are high-risk with strict rules.",
               "Chatbots must say they are AI, while most uses, like spam filters, have no special rules.",
               "This is engineering literacy, not legal advice: check the current law for real decisions."],
        map=[("Banned vehicles", "Unacceptable risk: prohibited, for example government social scoring"),
             ("The school bus with strict inspections", "High risk: hiring, credit, education, healthcare and more"),
             ("A car needs a licence", "Limited risk: tell people they are talking to an AI; AI content may need a label"),
             ("A bicycle needs almost nothing", "Minimal risk: spam filters, recommendations, game AI"),
             ("What the vehicle is used for, not its engine", "The tier follows the use case, not the model")],
        fig=timeline_svg(),
        cap="Dates are from the European Commission's AI Act page as given in this lesson (checked 2026-11-03). Obligations switched on in steps, so the date that matters depends on your tier.",
        play=("riskclass", "Pick a use case. The tier lights up with the obligations this lesson lists for it. The same kind of model lands in different tiers."),
        line="The more harm an AI use can do, the more rules it must follow, and the tier belongs to the use, not the model."),
}
