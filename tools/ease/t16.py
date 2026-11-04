"""Pass 2, Section 16 (folder track11/): Get hired.

No pass-1 analogy on these pages, so each lesson writes its own pic + breaks.
Numbers come from the pages: 6-8 hours a week for about ten weeks, five two-week phases (16.1); the
before/after resume bullets (16.3); a 45-minute mock in three ~15-minute blocks scored 1-3 on four axes (16.4).
"""
from ease.kit import arrow, box, flow, lines, path_arrow, raw, rect, svg, text, wrap

# ---------- 16.1 the ten-week plan as a timeline
PHASES = [("Foundations", "Start Here + Tracks 1–2", "Checkpoint: explain tokens, embeddings and sampling to a friend", "k", False),
          ("RAG", "Track 3, the most-tested topic", "Build capstone 14.1, your flagship RAG assistant", "c", True),
          ("Agents + tuning", "Tracks 4–5", "Build capstone 14.2: a second repo exists", "p", True),
          ("Eval · safety · serving", "Tracks 6–8", "Build capstone 14.3, the eval harness, and point it at 14.1", "g", True),
          ("Interview + apply", "Track 15, then 16.2–16.4", "Polish repos, write STAR stories, run the mock, apply", "a", False)]
H_LO, H_HI, WEEKS = 6, 8, 10


def plan_svg():
    tot_lo, tot_hi = H_LO * WEEKS, H_HI * WEEKS
    # wide: gantt
    W, gx, gw = 760, 190, 550
    wk = gw / WEEKS
    body = text(20, 22, f"Ten weeks at {H_LO}–{H_HI} hours a week = {tot_lo}–{tot_hi} hours in all", "b", "start")
    for k in range(WEEKS):
        x = gx + k * wk
        body += f'<line x1="{x:g}" y1="40" x2="{x:g}" y2="350" class="grid"/>' + text(x + wk / 2, 52, f"Wk {k+1}", "s m")
    body += f'<line x1="{gx+gw:g}" y1="40" x2="{gx+gw:g}" y2="350" class="grid"/>'
    y = 64
    for i, (name, study, build, tone, is_build) in enumerate(PHASES):
        x0 = gx + 2 * i * wk
        body += text(20, y + 18, name, "b", "start", 14) + text(20, y + 36, study, "s", "start", 12)
        body += f'<rect x="{x0+2:g}" y="{y+4:g}" width="{2*wk-4:g}" height="22" rx="5" class="fill-{tone}"/>'
        dot = "fill-g" if is_build else "fill-m"
        late = x0 > gx + gw / 2
        tx = x0 + 2 * wk - 2 if late else x0 + 2
        body += f'<circle cx="{tx + (-8 if late else 8):g}" cy="{y+42:g}" r="5" class="{dot}"/>'
        body += text(tx + (-18 if late else 18), y + 46, build, "s ok-t" if is_build else "s", "end" if late else "start", 12)
        y += 56
    # weekly review ticks
    for k in range(WEEKS):
        x = gx + (k + 1) * wk - 6
        body += f'<polygon points="{x-5:g},{y+2:g} {x+5:g},{y+2:g} {x:g},{y+11:g}" class="hd ac"/>'
    body += text(gx - 10, y + 12, "20-min review, every week", "s ac-t", "end", 12)
    body += f'<circle cx="26" cy="{y+40:g}" r="5" class="fill-g"/>' + text(38, y + 44, "= a build lands in this phase (from Week 3, not Week 10)", "s", "start")
    wide = svg(W, y + 56, body, "The ten-week study plan: five phases with a build attached", "ez-wide")
    # tall: one card per phase with a ten-square week strip
    W2 = 360
    body = text(12, 20, f"10 weeks × {H_LO}–{H_HI} h = {tot_lo}–{tot_hi} hours", "b", "start")
    y = 36
    for i, (name, study, build, tone, is_build) in enumerate(PHASES):
        bl = wrap(build, W2 - 58, 12)
        h = 80 + len(bl) * 16 + 4
        body += rect(12, y, W2 - 24, h, tone, rx=10)
        body += text(24, y + 22, f"Wk {2*i+1}–{2*i+2} · {name}", "b", "start", 14)
        body += text(24, y + 40, study, "s", "start", 12)
        for k in range(WEEKS):
            body += f'<rect x="{24 + k*18:g}" y="{y+50:g}" width="14" height="10" rx="2" class="{"fill-a" if k // 2 == i else "bx"}"/>'
        body += text(212, y + 59, f"weeks {2*i+1}–{2*i+2} of 10", "s m", "start", 12)
        body += f'<circle cx="30" cy="{y+76:g}" r="5" class="{"fill-g" if is_build else "fill-m"}"/>'
        body += lines(42, y + 80, bl, "s ok-t" if is_build else "s", "start", 12, 16)
        y += h + 10
    body += text(12, y + 10, "Plus a 20-minute review every week.", "s ac-t", "start")
    tall = svg(W2, y + 22, body, "The ten-week study plan: five phases with a build attached", "ez-tall")
    return raw(wide, tall)


# ---------- 16.3 the bridge from data-engineering bullets to GenAI language
BRIDGE = [("Built ETL pipelines ingesting 2 TB/day into Snowflake", "ingestion", "Large-scale ingestion: the same chunking, dedupe and metadata tagging that powers RAG"),
          ("Owned data-quality monitoring across 40+ tables", "quality gates", "LLM evaluation: golden datasets, automated quality metrics, catching regressions"),
          ("Optimized Spark jobs to cut cloud spend 35%", "batching, caching", "The same levers that control LLM serving cost and latency"),
          ("Batch reporting to streaming: 6 hours → 5 minutes", "latency work", "The latency engineering that makes LLM apps feel responsive")]


def bridge_svg():
    W, bw = 760, 290
    lx, rx = 20, W - 20 - bw
    body = text(lx, 22, "What your résumé says now", "b", "start") + text(rx, 22, "How a GenAI team reads it", "b", "start")
    y = 36
    for before, skill, after in BRIDGE:
        hb = max(box_hh(bw, before), box_hh(bw, after))
        b, _ = box(lx, y, bw, before, "", "b", h=hb, size=14)
        body += b
        b, _ = box(rx, y, bw, after, "", "g", h=hb, size=14)
        body += b
        body += arrow(lx + bw + 6, y + hb / 2, rx - 6, y + hb / 2, "ac")
        body += text(W / 2, y + hb / 2 - 8, skill, "s ac-t", size=12)
        y += hb + 14
    body += text(20, y + 10, "Keep the real metric (2 TB/day, 35%, 6 h → 5 min). Change only the framing, so the skill that carries over is obvious.", "s", "start")
    wide = svg(W, y + 22, body, "Rewriting data-engineering bullets so the GenAI skill is visible", "ez-wide")
    W2 = 360
    body = text(12, 20, "Before → after, same metric", "b", "start")
    y = 34
    for before, skill, after in BRIDGE:
        b, h = box(12, y, W2 - 24, before, "", "b", size=14)
        body += b
        y += h
        body += arrow(40, y + 3, 40, y + 25, "ac") + text(52, y + 19, skill, "s ac-t", "start", 12)
        y += 28
        b, h = box(12, y, W2 - 24, after, "", "g", size=14)
        body += b
        y += h + 18
    tall = svg(W2, y, body, "Rewriting data-engineering bullets so the GenAI skill is visible", "ez-tall")
    return raw(wide, tall)


def box_hh(w, title, size=14):
    tl = wrap(title, w - 18, size, bold=True)
    return 16 + len(tl) * round(size * 1.3) + 6


# ---------- 16.4 one mock: 45 minutes, then score, then the study list
BLOCKS = [("Technical Q&A", "fundamentals, RAG, agents", "c"), ("System design", "one prompt, as at a whiteboard", "k"), ("Behavioral", "your STAR stories", "p")]
AXES = [("Correctness", 3), ("Structure", 2), ("Trade-offs", 1), ("Delivery", 3)]  # example scores (illustrative)


def mock_svg():
    total, n = 45, len(BLOCKS)
    per = total / n
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        x0, bw = (12, W - 24) if nw else (20, W - 40)
        body = text(x0, 20, f"One {total}-minute mock: out loud, no notes, recorded", "b", "start", 14 if nw else 15)
        y = 34
        if nw:
            for i, (t, s, tone) in enumerate(BLOCKS):
                b, h = box(x0, y, bw, f"{per*i:g}–{per*(i+1):g} min · {t}", s, tone, size=14)
                body += b
                y += h + 6
        else:
            seg = bw / n
            for k in range(n + 1):
                body += text(x0 + k * seg, y + 10, f"{per*k:g} min", "s m", "start" if k == 0 else "end" if k == n else "middle")
            y += 18
            for i, (t, s, tone) in enumerate(BLOCKS):
                b, _ = box(x0 + i * seg + (0 if i == 0 else 3), y, seg - 3, t, s, tone, h=58, size=14)
                body += b
            y += 58
        body += arrow(x0 + 30, y + 4, x0 + 30, y + 30)
        body += text(x0 + 42, y + 22, "replay the recording, score every answer 1–3", "s", "start")
        y += 40
        # score grid
        lab_w = 104 if nw else 130
        cw = 40 if nw else 56
        gx = x0 + lab_w
        for c in range(3):
            body += text(gx + c * cw + cw / 2, y + 12, str(c + 1), "s b")
        body += text(gx + 3 * cw + 8, y + 12, "(example)", "s m", "start", 12)
        y += 20
        flagged = []
        for name, sc in AXES:
            body += text(x0, y + 19, name, "b", "start", 14)
            for c in range(3):
                body += rect(gx + c * cw + 3, y + 3, cw - 6, 24, "b", rx=5)
            body += f'<circle cx="{gx + (sc-1)*cw + cw/2:g}" cy="{y+15:g}" r="7" class="{"fill-g" if sc == 3 else "fill-w"}"/>'
            if sc < 3:
                flagged.append(name)
                body += arrow(gx + 3 * cw + 6, y + 15, gx + 3 * cw + (30 if nw else 46), y + 15, "wn")
            y += 30
        sx = gx + 3 * cw + (34 if nw else 52)
        tw = x0 + bw - sx
        ty = y - 30 * len(AXES) + 6
        b, _ = box(sx, ty, tw, "Next week's study list", ", ".join(flagged), "w", h=30 * len(AXES) - 12, size=13 if nw else 14)
        body += b
        y += 8
        body += text(x0, y + 12, "Anything below a 3 goes on the list. Run the next mock against it.", "s ac-t", "start", 12 if nw else 13)
        out.append(svg(W, y + 22, body, "A 45-minute mock interview, then a 1 to 3 score on four axes", cls))
    return raw(*out)


LESSONS = {
    "16.1": dict(
        plain=["Most people who start a self-paced course don't fail because it is hard. They drift.",
               "Without a schedule, “I'll study GenAI” loses to every busy week.",
               "This plan splits the course into five two-week phases at 6 to 8 hours a week.",
               "Every phase has a build attached, starting in Week 3, so proof grows alongside knowledge.",
               "A 20-minute review each week keeps what you finished from fading."],
        pic="A study plan is like a training plan for a 10 km race. Nobody gets fit by vowing to “run more”. The plan says Tuesday 5 km easy, Sunday a longer run, a practice race every few weeks, and race day is circled on the calendar.",
        breaks="A runner's fitness shows the moment they run. What you learned doesn't show unless you leave something behind, so every phase here ends in a repo, not just finished lessons.",
        map=[("Tuesday and Sunday runs on the calendar", "Two recurring study blocks, each with a named lesson (“Tuesday, Lesson 3.2, 40 minutes”)"),
             ("Each block of weeks builds on the last", "Five phases in order: foundations, RAG, agents, evals and serving, interviews"),
             ("Practice races along the way", "A capstone build in Weeks 3–4, 5–6 and 7–8"),
             ("Race day circled on the calendar", "Polish, mock interview and applications in Weeks 9–10, with a deadline"),
             ("The weekly check-in with your coach", "A 20-minute review: could I explain this, and use it on the job?")],
        fig=plan_svg(),
        cap="Read it left to right. Each phase takes two weeks, and the green dots show where a build lands: from Week 3, not saved for the end. The hour totals are computed from the page's 6–8 hours a week over 10 weeks.",
        play=("studyplan", "Slide to the hours you can really give each week. The plan's 60–80 hours stay the same; watch how long each phase and the whole plan take."),
        line="Put small study blocks on the calendar, build something in every phase, and review once a week."),
    "16.2": dict(
        plain=["A portfolio is a few public projects that show you can build things, not just talk about them.",
               "Thousands of people can say “I've used the API”. Very few can show a working system they measured.",
               "One excellent project beats five half-finished tutorial copies.",
               "It needs a README that explains your decisions, an evaluation with real numbers, and setup steps that work.",
               "A busy reviewer gives it about a minute and a half, so the good parts must be on top."],
        pic="A portfolio repo is like a house for sale. Buyers decide in minutes: the view from the street, the photos, the survey report, a look into one or two rooms, and whether the paperwork is in order.",
        breaks="A buyer can't copy the house to test it. A reviewer can clone your repo, and if it doesn't run from a clean clone the viewing is over on the spot.",
        map=[("The view from the street", "The top of the README: what it does and the headline numbers"),
             ("The photos", "A screenshot or short demo, visible without any setup"),
             ("The survey report", "Key decisions and Results: eval scores and honest limits"),
             ("Looking into one or two rooms", "Opening one or two source files to check they are tidy"),
             ("The paperwork history", "Commit history that grew like real work, not one big dump")],
        fig=flow([("Top of the README", "what it does, that it's evaluated, headline numbers", "c"),
                  ("Screenshot or demo", "visible without setup", "k"),
                  ("Decisions and Results", "reasons, eval scores, limits", "g"),
                  ("One or two source files", "organised, not copy-pasted", "p"),
                  ("Commit history", "grew like real work, not one dump", "d")],
                 "The 90-second review a portfolio repo must survive"),
        cap="This is the order a busy reviewer actually reads a repo, in about 90 seconds. Put the punchline in box 1, because that is often as far as they get.",
        line="Ship one project you can prove works, and put the proof where a reviewer looks first."),
    "16.3": dict(
        plain=["If you come from data engineering, your years of work are an advantage for GenAI roles, not a gap.",
               "Production GenAI is mostly data and systems work.",
               "Retrieval is a data pipeline, evaluation is data quality and testing, and serving is throughput, caching and cost.",
               "The trick is to name that bridge on your résumé, so the hiring manager doesn't have to guess it.",
               "Keep your real numbers and change only the framing."],
        pic="Moving from data engineering into GenAI is like a long-haul lorry driver applying to drive buses. You don't open with “I've never driven a bus”. You open with ten years of heavy vehicles, a clean safety record and night routes, and you mention the bus routes you have already practised.",
        breaks="A bus company can check your licence category. GenAI hiring has no licence, so the bridge exists only if your own words name it.",
        map=[("Ten years of heavy vehicles", "Years of production data systems: pipelines, scale, reliability"),
             ("A clean safety record with numbers", "The real metrics in your bullets: 2 TB/day, 35% cost cut, 6 h → 5 min"),
             ("Bus routes you have already practised", "Your GenAI capstone projects, listed at the top"),
             ("Applying for driving jobs, not pilot jobs", "Applied and platform roles (AI Engineer, RAG/Platform, AI Data Engineer), not research scientist")],
        fig=bridge_svg(),
        cap="Each row is one of the page's before-and-after bullets. The blue label is the skill that carries over; the metric on the left survives into the version on the right.",
        line="Same achievements, same numbers: just say out loud how they map onto GenAI work."),
    "16.4": dict(
        plain=["Knowing an answer and saying it well under pressure are different skills.",
               "A mock interview is a rehearsal you run on yourself.",
               "Set a 45-minute timer, answer out loud with no notes, and record it.",
               "Then score every answer from 1 to 3 on four things: correctness, structure, trade-offs and delivery.",
               "Anything below a 3 becomes next week's study list."],
        pic="A mock interview is like a fire drill. You don't learn the way out by reading the map on the wall. You walk it, with the alarm on and a timer running, and afterwards you note exactly where people got stuck.",
        breaks="A fire drill uses the same route every time. Interviews don't, so you draw questions at random and practise starting to answer within five seconds.",
        map=[("The alarm and the timer", "A 45-minute timer, out loud, no notes"),
             ("Walking the route", "Three blocks of about 15 minutes: technical, system design, behavioral"),
             ("The observer with a clipboard", "Your recording, scored 1–3 on four axes"),
             ("Fixing the door that jammed", "Every score below 3 goes on next week's study list")],
        fig=mock_svg(),
        cap="Top: the 45 minutes split into the page's three blocks. Bottom: the rubric's four axes; the dots are an example score, not real data. The two red rows are what you would study next.",
        line="Rehearse out loud against a clock, score yourself honestly, and study whatever scored below a 3."),
}
