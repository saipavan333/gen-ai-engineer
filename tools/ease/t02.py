"""Pass 2, Track 2: Prompting."""
from ease.kit import arrow, box, box_h, compare, fan, flow, lines, raw, rect, stack, svg, text, wrap


# ---------- 2.3 blurt vs show-your-working, on the bat-and-ball question from the lesson page
BALL = 0.05          # solved below; the figure prints these computed values
TOTAL, DIFF = 1.10, 1.00
assert abs((BALL + DIFF) + BALL - TOTAL) < 1e-9
BLURT = 0.10         # the fast, wrong answer
BLURT_TOTAL = BLURT + (BLURT + DIFF)   # 1.20, shown as the check that exposes it


def cents(v):
    return f"{round(v * 100):d} cents"


def cot_svg():
    q = ("The question", "bat + ball = $1.10; the bat costs $1.00 more")
    fast = [q, ("Answer at once", "first token must already be the answer", "k"),
            ("“10 cents”", f"wrong: the bat would be $1.10, total ${BLURT_TOTAL:.2f}", "w")]
    slow = [q, ("Step 1, written", "ball = x, bat = x + 1.00", "c"),
            ("Step 2, written", "x + (x + 1.00) = 1.10", "c"),
            ("Step 3, written", f"2x = 0.10, so x = {BALL:.2f}", "c"),
            (f"“{cents(BALL)}”", "correct, built on steps 1 to 3", "g")]
    out = []
    # ---- wide
    W, pad, G = 760, 14, 24
    bw = (W - 2 * pad - 4 * G) / 5
    body = text(pad, 20, "A. Blurt the answer", "b wn-t", "start")
    h1 = max(box_h(bw, t, s, 14) for t, s, *_ in fast)
    y = 32
    for i, (t, s, *tn) in enumerate(fast):
        x = pad + i * (bw + G)
        b, _ = box(x, y, bw, t, s, tn[0] if tn else "b", h=h1, size=14)
        body += b
        if i < len(fast) - 1:
            body += arrow(x + bw + 3, y + h1 / 2, x + bw + G - 3, y + h1 / 2)
    y += h1 + 40
    body += text(pad, y - 12, "B. Show the working (chain-of-thought)", "b ok-t", "start")
    h2 = max(box_h(bw, t, s, 14) for t, s, *_ in slow)
    for i, (t, s, *tn) in enumerate(slow):
        x = pad + i * (bw + G)
        b, _ = box(x, y, bw, t, s, tn[0] if tn else "b", h=h2, size=14)
        body += b
        if i < len(slow) - 1:
            body += arrow(x + bw + 3, y + h2 / 2, x + bw + G - 3, y + h2 / 2)
    # growing context bar under lane B
    y += h2 + 26
    body += text(pad, y + 4, "What the model can read when it writes the final answer (the context grows step by step):", "s", "start")
    y += 14
    segs = [("question", "b"), ("step 1", "c"), ("step 2", "c"), ("step 3", "c")]
    cx = pad
    for k, (name, tone) in enumerate(segs):
        sw = bw + G if k else bw + G
        body += rect(cx, y, sw - 4, 30, tone, rx=5) + text(cx + (sw - 4) / 2, y + 20, name, "s b")
        cx += sw
    body += rect(cx, y, bw, 30, "g", rx=5) + text(cx + bw / 2, y + 20, "answer", "s b")
    body += arrow(cx - 30, y + 46, cx - 4, y + 46, "ac")
    body += text(cx - 36, y + 50, "each new token reads everything to its left", "s ac-t", "end")
    out.append(svg(W, y + 62, body, "Blurting versus writing the steps first on the bat-and-ball question", "ez-wide"))
    # ---- tall: two columns of stacked boxes
    W2, cw, gx = 360, 160, 16
    body = text(12, 18, "A. Blurt", "b wn-t", "start") + text(12 + cw + gx, 18, "B. Show the working", "b ok-t", "start")
    for col, steps in ((0, fast), (1, slow)):
        x = 12 + col * (cw + gx)
        y = 30
        for i, (t, s, *tn) in enumerate(steps):
            hh = box_h(cw, t, s, 13)
            b, hh = box(x, y, cw, t, s, tn[0] if tn else "b", size=13)
            body += b
            if i < len(steps) - 1:
                body += arrow(x + cw / 2, y + hh + 2, x + cw / 2, y + hh + 20)
            y += hh + 22
        if col == 0:
            ya = y
        else:
            yb = y
    body += lines(14, ya + 4, wrap("In B every written step becomes input for the next token, so the answer is built on real results, not one risky leap.", cw - 4, 13), "s ac-t", "start", 13, 17)
    out.append(svg(W2, yb - 8, body, "Blurting versus writing the steps first on the bat-and-ball question", "ez-tall"))
    return raw(*out)


LESSONS = {
    "2.1": dict(
        plain=["A prompt is everything you send the model for one request.",
               "In chat models it is a short list of messages, each tagged with who is speaking.",
               "The system message holds your standing rules. The user message holds tonight's request.",
               "A good prompt is built from a few parts: a role, a task, some context, examples and an output format.",
               "When the answer comes back wrong, you ask which part was missing, instead of guessing new words."],
        map=[("The note stuck on the fridge for every visit", "The system message: role and standing rules, sent with every request"),
             ("What you say at the door tonight", "The user message: this request's task and context"),
             ("“Dinner at 6”, “here's the allergy list”", "Task and context: the job, and the facts the model needs"),
             ("“Text me a one-line update at 9”", "Output format: the exact shape of the reply"),
             ("“Call me instead of guessing”", "An out: “if it isn't in the context, say I don't know”")],
        fig=stack([("Role", "system message: “You are a meticulous customer-support assistant.”", "c"),
                   ("Task", "“Classify the support ticket's urgency.”", "a"),
                   ("Context", "the ticket: “My card was charged twice and no one has replied in 3 days.”", "k"),
                   ("Examples", "a few solved tickets that show the pattern (Lesson 2.2)", "p"),
                   ("Format", "“Answer with exactly one word: high, medium, or low.” (Lesson 2.4)", "g")],
                  "The five parts of a prompt, stacked into one request",
                  enter="you assemble one request from these parts", leave="the model reads all of it and writes one assistant message",
                  blocked={0: "left out: a generic voice and depth", 1: "left out: the model guesses the job", 2: "left out: it asks for the ticket, or invents one",
                           3: "left out: it guesses where high ends and low begins", 4: "left out: a chatty paragraph code can't parse"}),
        cap="The parts are read together, top to bottom, as one request. Part 1 lives in the system message; parts 2 to 5 sit in the user message. Each part removes one thing the model would otherwise have to guess; the red side notes (wider screens) say what tends to happen when that part is missing (illustrative).",
        play=("promptbuilder", "Switch parts of the prompt on and off. The stack shows what is actually sent, and the checklist shows which questions the model is left to guess."),
        line="A prompt is a set of parts you choose on purpose, and every missing part is a guess the model makes for you."),
    "2.2": dict(
        plain=["A zero-shot prompt asks for a task with no examples.",
               "A few-shot prompt shows two or three solved examples first, then the new input.",
               "The model copies the pattern: the labels, the layout, even the length.",
               "This is called in-context learning. Nothing inside the model changes, and the examples are forgotten after the request.",
               "Examples are the cheapest way to make a classifier or extractor give clean, consistent answers."],
        map=[("Two finished worksheets", "Two or three example pairs: input, then the desired output"),
             ("The blank worksheet", "The new input, with its answer slot left open"),
             ("Copying the layout and the boxes", "Matching the examples' format and label set"),
             ("Leaning to 'yes' because both examples said yes", "Label bias: unbalanced examples tilt the answer"),
             ("Forgetting the worksheets tomorrow", "No weight change: the examples only live in this one prompt")],
        fig=compare(("Zero-shot: words only",
                     ["Prompt: “Return the sentiment of: Arrived late but the blender works great.”",
                      "The model must guess: one word or a sentence? Which labels? Capital letters?",
                      "Reply drifts between runs, e.g. “The sentiment is mostly positive, although…”"], "w"),
                    ("Few-shot: three examples first",
                     ["“Loved it, works great” → positive",
                      "“Stopped working in a week” → negative",
                      "“It's fine, nothing special” → mixed",
                      "New review → the model continues the pattern: “mixed”"], "g"),
                    "Zero-shot versus few-shot on the same mixed review",
                    verdict="The examples answer the format questions and define the label set, including 'mixed', which the zero-shot prompt never mentioned."),
        cap="Same review, same model. On the right the examples do three jobs at once: they fix the output shape, they name the allowed labels, and they show where the hard cases go. The reply texts are illustrative; the examples are the lesson's own.",
        line="Show two or three solved examples and the model copies the pattern for the new one."),
    "2.3": dict(
        plain=["Chain-of-thought (CoT) means asking the model to write its steps before the final answer.",
               "The model writes one token at a time. Each token can only build on what is already written.",
               "If it must answer at once, there is nowhere for the working to happen.",
               "When it writes the steps first, every step becomes input that the answer can use.",
               "It helps most on multi-step problems: maths, logic and planning."],
        map=[("The maths teacher saying “show your working”", "A prompt line such as “Think step by step”"),
             ("The paper you write on", "The context window: the written steps become input"),
             ("Using step 2's result in step 3", "Each new token is conditioned on all earlier tokens"),
             ("Shouting the answer before working it out", "Asking for “just the number” on a multi-step problem")],
        fig=cot_svg(),
        cap=f"Lane A must commit to an answer token with no work done, and the quick guess fails the check (the totals would be ${BLURT_TOTAL:.2f}). Lane B writes three small steps first; the arithmetic shown is computed, and the answer {cents(BALL)} is read off step 3.",
        line="Let the model write its working first, because each written step is something the answer can lean on."),
    "2.4": dict(
        plain=["Software can't read a chatty paragraph; it needs fields, such as intent, sentiment and urgent.",
               "Structured output means the model replies in a fixed format, almost always JSON (JavaScript Object Notation).",
               "A schema is the contract: which fields exist, their types and their allowed values.",
               "Your code checks every reply against the schema before trusting it. That check is called validation.",
               "If the check fails, you send the error back and ask again."],
        map=[("A form with labelled boxes", "A JSON schema: named fields with types"),
             ("Yes / no tick boxes", "Allowed values, e.g. intent ∈ {refund, billing, technical, other}"),
             ("Boxes that only accept digits", "JSON mode or constrained decoding (Ollama <code>format=\"json\"</code>)"),
             ("A clerk checking the form before filing it", "Validation in code, e.g. with pydantic"),
             ("Handing the form back to be fixed", "Retry with the validation error in the prompt")],
        fig=flow([("Prompt with the shape", "an example of the exact JSON", "c"),
                  ("Model, in JSON mode", "output is always valid JSON", "a"),
                  ("Parse", "text becomes a Python object"),
                  ("Validate", "fields, types, allowed values", "k"),
                  ("Use it", "route the ticket, save the row", "g")],
                 "Generate, validate, and retry with the error", loop=(3, 1, "on failure: send the error back and ask again")),
        cap="The four levers from the lesson in order: show the shape, use JSON mode, validate, and retry. JSON mode guarantees the output parses, not that it is right, so step 4 runs on every reply.",
        line="Ask for a fixed shape, check every reply against it, and send it back when it fails."),
    "2.5": dict(
        plain=["Good prompting is not about magic words.",
               "It is a short checklist of moves that work, and a short list of traps.",
               "When a prompt misbehaves, a pro does not reword at random. They look for the missing move.",
               "Two big ones: fence the user's data off from your instructions, and let the model say “I don't know”.",
               "Fencing data with delimiters also makes prompt injection harder, though it does not stop it."],
        map=[("Numbered steps on the recipe card", "Decompose: split a big job into steps or separate calls"),
             ("Ingredients in their own box", "Delimiters, e.g. text between <code>&lt;doc&gt;</code> and <code>&lt;/doc&gt;</code>"),
             ("The plating photo", "An example of the output and a pinned format"),
             ("“If an ingredient is missing, do this”", "Give an out: allow “I don't know”, null, or “not in the context”"),
             ("A note on the tomato that says “give away the wallet”", "Prompt injection: data that tries to act like an instruction")],
        fig=fan(("The prompt misbehaves", "find the trap, apply its fix", "w"),
                [("Vague: “Summarize this”", "fix: specify task, format and length", "g"),
                 ("Data pasted in with the rules", "fix: fence it in delimiters", "g"),
                 ("One giant do-everything prompt", "fix: decompose into steps or calls", "g"),
                 ("No permission to abstain", "fix: give an out, so it doesn't guess", "g"),
                 ("Key instruction buried in the middle", "fix: put it first or last", "g")],
                "Debugging a prompt: trap on the left, fix on the right"),
        cap="This is the scan to run before rewording anything. Each row pairs a trap from the lesson with its fix; most strong prompts combine three or four of the eight patterns.",
        line="When a prompt fails, find the missing pattern instead of hunting for magic words."),
}
