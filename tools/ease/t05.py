"""Pass 2, Track 5: Fine-tuning."""
import math

from ease.kit import arrow, box, esc, fan, flow, lines, path_arrow, raw, rect, svg, text, wrap


def two(fn, label):
    return raw(svg(*fn(760), label, "ez-wide"), svg(*fn(360), label, "ez-tall"))


# ---------- 5.2 one weight, loss = (w - 3)^2, start at w = 0 (the page's own demo function)
def descent_path(lr, steps, w0=0.0):
    ws = [w0]
    for _ in range(steps):
        w = ws[-1]
        ws.append(w - lr * 2 * (w - 3))
    return ws


DESC = [(0.05, 6, "too small", "w"), (0.4, 4, "about right", "g"), (1.05, 4, "too big", "w")]


def descent_fig(W):
    nw = W < 400
    pw, ph = (336, 150) if nw else (236, 190)
    gap = 12
    if nw:
        body = text(12, 20, "Loss = (w − 3)², start at w = 0.", "s m", "start") + text(12, 38, "Each dot is one step; positions computed.", "s m", "start")
    else:
        body = text(20, 20, "Loss = (w − 3)², start at w = 0. Each dot is one step; positions computed.", "s m", "start")
    for k, (lr, n, verdict, tone) in enumerate(DESC):
        x0 = (12 if nw else 20 + k * (pw + gap))
        y0 = (78 + k * (ph + 84)) if nw else 64
        ws = descent_path(lr, n)
        wmin, wmax, lmax = -2.0, 8.0, 25.0
        X = lambda w: x0 + (w - wmin) / (wmax - wmin) * pw
        Y = lambda L: y0 + ph - min(L, lmax) / lmax * (ph - 10)
        pts = " ".join(f"{X(wmin + i * (wmax - wmin) / 60):.1f},{Y((wmin + i * (wmax - wmin) / 60 - 3) ** 2):.1f}" for i in range(61))
        body += rect(x0, y0, pw, ph, "b", rx=8)
        body += f'<polyline points="{pts}" class="ln thin"/>'
        body += f'<line x1="{X(3):.1f}" y1="{y0+ph-4:.1f}" x2="{X(3):.1f}" y2="{y0+ph+6:.1f}" class="ln ok"/>'
        body += text(X(3), y0 + ph + 20, "best w = 3", "s ok-t", size=12)
        for i in range(len(ws) - 1):
            a, b = ws[i], ws[i + 1]
            body += arrow(X(a), Y((a - 3) ** 2), X(b), Y((b - 3) ** 2), "ac thin", head=7)
        for i, w in enumerate(ws):
            body += f'<circle cx="{X(w):.1f}" cy="{Y((w-3)**2):.1f}" r="{5 if i else 6}" class="{"fill-a" if i else "fill-k"}"/>'
        L_end = (ws[-1] - 3) ** 2
        body += text(x0 + 2, y0 - 10, f"learning rate {lr}: {verdict}", f"b {'ok-t' if tone == 'g' else 'wn-t'}", "start", 14)
        body += text(x0 + 10, y0 + ph + 40, f"loss 9 → {L_end:.2f} after {n} steps", "s", "start")
    H = (78 + 3 * (ph + 84) - 30) if nw else (64 + ph + 54)
    return W, H, body


# ---------- 5.4 LoRA on one real matrix: Qwen2.5-7B q_proj, 3,584 x 3,584, r = 16 (page's numbers)
D, R = 3584, 16


def lora_fig(W):
    nw = W < 400
    full, a, b = D * D, R * D, D * R
    pct = (a + b) / full * 100
    body = ""
    if not nw:
        # input
        body += rect(20, 120, 70, 60, "c") + text(55, 146, "x", "b") + text(55, 166, "3,584 in", "s", size=12)
        # top path: frozen W
        body += path_arrow([(92, 150), (130, 150), (130, 95), (176, 95)])
        body += rect(180, 22, 150, 150, "b", rx=6)
        body += f'<rect x="180" y="22" width="150" height="150" rx="6" class="ln thin dash"/>'
        body += text(255, 84, "W (frozen)", "b") + text(255, 106, "3,584 × 3,584", "s mono") + text(255, 126, "12,845,056", "s") + text(255, 144, "numbers, untouched", "s m")
        # bottom path: A then B
        body += path_arrow([(92, 150), (130, 150), (130, 250), (176, 250)])
        body += f'<polygon points="176,200 236,232 236,268 176,300" class="bx tn-a"/>'
        body += text(206, 256, "A", "b")
        body += f'<polygon points="276,232 336,200 336,300 276,268" class="bx tn-a"/>'
        body += text(306, 256, "B", "b")
        body += arrow(238, 250, 274, 250, "ac thin", head=6)
        body += text(256, 222, "r = 16", "s ac-t", size=12)
        body += text(200, 320, "A: 16 × 3,584", "s", size=12) + text(200, 336, "= 57,344", "s", size=12)
        body += text(312, 320, "B: 3,584 × 16", "s", size=12) + text(312, 336, "= 57,344", "s", size=12)
        # sum
        body += path_arrow([(332, 95), (400, 95), (400, 150), (418, 162)])
        body += path_arrow([(338, 250), (400, 250), (400, 205), (418, 190)], "ac")
        body += f'<circle cx="436" cy="176" r="18" class="bx tn-g"/>' + text(436, 183, "+", "b")
        body += arrow(456, 176, 498, 176)
        body += rect(502, 146, 110, 60, "g") + text(557, 172, "h = Wx + BAx", "b", size=13) + text(557, 192, "3,584 out", "s", size=12)
        # counts panel
        rows = [("Trainable here:", "b"), (f"16 × (3,584 + 3,584) = {a+b:,}", "s mono"),
                (f"= {pct:.2f}% of W's {full:,}", "s"), ("B starts at zero, so step 0", "s m"), ("is exactly the original model.", "s m")]
        for i, (t, c) in enumerate(rows):
            body += text(500, 250 + i * 19, t, c, "start", 13)
        body += text(20, 22, "One LoRA layer", "b", "start")
        return W, 350, body
    # tall
    body += text(12, 20, "One LoRA layer (Qwen2.5-7B q_proj)", "b", "start")
    body += rect(130, 34, 100, 40, "c") + text(180, 52, "x", "b") + text(180, 68, "3,584 in", "s", size=12)
    body += path_arrow([(160, 74), (160, 90), (80, 90), (80, 104)])
    body += path_arrow([(200, 74), (200, 90), (270, 90), (270, 104)])
    body += rect(20, 108, 120, 120, "b", rx=6) + f'<rect x="20" y="108" width="120" height="120" rx="6" class="ln thin dash"/>'
    body += text(80, 150, "W (frozen)", "b", size=14) + text(80, 170, "3,584 × 3,584", "s mono", size=12) + text(80, 188, "12,845,056", "s", size=12) + text(80, 206, "untouched", "s m", size=12)
    body += f'<polygon points="215,108 325,108 288,148 252,148" class="bx tn-a"/>' + text(270, 132, "A", "b")
    body += text(330, 160, "r=16", "s ac-t", "end", 12)
    body += arrow(270, 150, 270, 166, "thin", head=6)
    body += f'<polygon points="252,170 288,170 325,210 215,210" class="bx tn-a"/>' + text(270, 198, "B", "b")
    body += text(270, 228, "A 57,344 + B 57,344", "s", size=12)
    body += path_arrow([(80, 228), (80, 262), (162, 262)])
    body += path_arrow([(270, 236), (270, 262), (198, 262)], "ac")
    body += f'<circle cx="180" cy="262" r="16" class="bx tn-g"/>' + text(180, 268, "+", "b")
    body += arrow(180, 278, 180, 298)
    body += rect(100, 302, 160, 50, "g") + text(180, 324, "h = Wx + BAx", "b", size=13) + text(180, 342, "3,584 out", "s", size=12)
    rows = [("Trainable: 16 × (3,584 + 3,584)", "s mono"), (f"= {a+b:,} = {pct:.2f}% of W", "s"),
            ("B starts at zero, so step 0 is", "s m"), ("exactly the original model.", "s m")]
    for i, (t, c) in enumerate(rows):
        body += text(12, 378 + i * 19, t, c, "start", 13)
    return W, 378 + 4 * 19, body


# ---------- 5.5 which tokens of one training example carry the loss (the page's 150 / 350 / 250)
SEG = [("system", 150, "c"), ("customer", 350, "k"), ("reply", 250, "g")]


def loss_fig(W):
    nw = W < 400
    x0 = 12 if nw else 20
    bw = W - 2 * x0
    tot = sum(n for _, n, _ in SEG)
    if nw:
        body = text(x0, 20, f"One training example: {tot} tokens", "b", "start", 14) + text(x0, 38, "in the Qwen2.5 chat template", "s m", "start")
        y = 46
    else:
        body = text(x0, 20, f"One training example: {tot} tokens in the Qwen2.5 chat template", "b", "start")
        y = 36
    tmpl = ["<|im_start|>system … <|im_end|>", "<|im_start|>user … <|im_end|>", "<|im_start|>assistant … <|im_end|>"]
    if nw:
        for i, t in enumerate(tmpl):
            body += text(x0, y + 14 + i * 18, t, "s mono", "start", 12)
        y += 64
    else:
        body += text(x0, y + 12, "   ".join(tmpl), "s mono", "start", 12)
        y += 26
    rowsdef = [("Full-sequence loss (TRL default for chat datasets)", {"system", "customer", "reply"}),
               ("assistant_only_loss=True", {"reply"})]
    for title, graded in rowsdef:
        body += text(x0, y + 16, title, "s b", "start")
        y += 26
        x = x0
        for name, n, tone in SEG:
            w = bw * n / tot
            on = name in graded
            bh = 42 if nw else 34
            body += f'<rect x="{x:.1f}" y="{y}" width="{w-3:.1f}" height="{bh}" rx="5" class="{"fill-a" if on else "bx"}"/>'
            if nw:
                body += text(x + (w - 3) / 2, y + 18, name, "b" if on else "s m", size=12) + text(x + (w - 3) / 2, y + 34, str(n), "b" if on else "s m", size=12)
            else:
                body += text(x + (w - 3) / 2, y + 22, f"{name} {n}", "b" if on else "s m", size=13)
            x += w
        y += bh
        g = sum(n for nm, n, _ in SEG if nm in graded)
        if nw:
            body += text(x0, y + 18, f"graded: {g} of {tot} tokens; the reply you", "s", "start", 12) + text(x0, y + 34, f"want to teach is {250/g*100:.0f}% of the loss", "s", "start", 12)
            y += 50
        else:
            body += text(x0, y + 18, f"graded tokens: {g} of {tot}; the reply you want to teach is {250/g*100:.0f}% of the loss", "s", "start", 13)
            y += 34
    body += f'<rect x="{x0}" y="{y}" width="14" height="14" rx="3" class="fill-a"/>' + text(x0 + 20, y + 12, "graded: the model is trained to predict these", "s", "start", 12)
    return W, y + 22, body


# ---------- 5.6 base vs fine-tune with 95% intervals (the page's numbers; intervals computed)
EV = [("Target task", 1000, 0.60, 0.91), ("General ability", 300, 0.82, 0.76)]


def ci(p, n):
    return 1.96 * math.sqrt(p * (1 - p) / n)


def eval_fig(W):
    nw = W < 400
    x0 = 12 if nw else 20
    lab_w = 0 if nw else 210
    bx0 = x0 + lab_w
    bw = W - bx0 - (60 if nw else 70)
    X = lambda v: bx0 + v * bw
    if nw:
        body = text(x0, 20, "Same held-out sets, both models.", "s m", "start", 12) + text(x0, 36, "Whisker = 95% interval (computed).", "s m", "start", 12)
        y = 52
    else:
        body = text(x0, 20, "Same held-out sets, both models. Whisker = 95% interval (computed).", "s m", "start", 13)
        y = 42
    for name, n, b, t in EV:
        body += text(x0, y + 14, f"{name} ({n:,} held-out)", "b", "start", 14)
        y += 24
        for who, v, cls in (("base", b, "fill-m"), ("fine-tuned", t, "fill-a")):
            e = ci(v, n)
            if nw:
                body += text(x0, y + 14, who, "s", "start")
                y += 20
            else:
                body += text(bx0 - 10, y + 17, who, "s", "end")
            body += f'<rect x="{bx0}" y="{y}" width="{v*bw:.1f}" height="24" rx="4" class="{cls}"/>'
            body += f'<line x1="{X(v-e):.1f}" y1="{y+12}" x2="{X(v+e):.1f}" y2="{y+12}" class="ln"/>'
            body += f'<line x1="{X(v-e):.1f}" y1="{y+5}" x2="{X(v-e):.1f}" y2="{y+19}" class="ln"/><line x1="{X(v+e):.1f}" y1="{y+5}" x2="{X(v+e):.1f}" y2="{y+19}" class="ln"/>'
            body += text(X(v + e) + 8, y + 17, f"{v:.2f} ±{e*100:.1f}", "s", "start", 12)
            y += 32
        d = (t - b) * 100
        if d > 0:
            body += text(x0, y + 10, f"+{d:.0f} points, far outside both intervals: a real gain", "s ok-t", "start", 13)
        else:
            body += text(x0, y + 10, f"−{-d:.0f} points; paired McNemar test 7.4 > 3.84: a real drop", "s wn-t", "start", 13)
            if not nw:
                pass
        y += 34
    return W, y, body


LESSONS = {
    "5.1": dict(
        plain=["There are three ways to change what a model does.",
               "A prompt changes the instructions you send with each request.",
               "RAG (retrieval-augmented generation) looks up the right documents and puts them in the request.",
               "Fine-tuning trains the model further on your own examples, so its weights change for good.",
               "Prompts and RAG are cheap and quick to change, so try them first. Fine-tune only for a steady style, format or narrow task they can't hold."],
        map=[("The order slip: “no onions, extra spicy”", "The prompt: changes this one request, costs nothing to edit"),
             ("Handing the cook the recipe book", "RAG: retrieved facts placed in the input at run time"),
             ("A month at cooking school", "Fine-tuning: extra training that changes the model's weights, once, ahead of time"),
             ("Today's menu changed", "Your facts changed: re-index the documents for RAG, don't retrain")],
        fig=fan(("What is wrong with the answers?", "start with the cheapest lever", "c"),
                [("It ignores or forgets the instructions", "prompt better (Track 2): instant, free", "g"),
                 ("It doesn't know the facts, or they keep changing", "RAG (Track 3): facts go in the input", "c"),
                 ("It knows enough but won't hold a style, format or narrow task", "fine-tune: change the weights once, ahead of time", "k"),
                 ("You need a steady format and fresh facts", "fine-tune for how it answers, RAG for what it knows", "p")],
                "Choosing between prompting, RAG and fine-tuning by what is actually wrong"),
        cap="Read the problem first, then pick the lever. Facts belong in RAG because you can re-index in minutes; behaviour that must hold on every call is what fine-tuning is for.",
        line="Prompt for instructions, RAG for facts, fine-tune for habits."),
    "5.2": dict(
        plain=["A model is a huge pile of numbers called weights.",
               "Training shows it an example, lets it guess, and scores how wrong the guess was: the loss.",
               "Then it nudges every weight a tiny bit in the direction that lowers the loss. This is gradient descent.",
               "The learning rate is the size of each nudge: too small is slow, too big overshoots.",
               "Repeat this millions of times, and check on held-out examples that it learned the task, not the answers."],
        map=[("Taking a shot", "The forward pass: the model makes a prediction"),
             ("How far you missed", "The loss: one number for how wrong the prediction was"),
             ("Which way to move your arm", "The gradient, worked out for every weight by backpropagation"),
             ("How much you change your arm", "The learning rate: the size of each step"),
             ("Shots you have never practised", "The validation set: held-out examples that catch memorising")],
        fig=two(descent_fig, "Gradient descent on one weight with three learning rates"),
        cap="Same bowl, same start, three step sizes. Each step moves w by learning rate × slope. At 0.05 it crawls, at 0.4 it lands almost on 3, and at 1.05 every step jumps past the bottom and lands higher than before.",
        play=("descent", "Now two weights. Move the learning rate and the step count. The path is computed step by step on a bowl that is steep in one direction and gentle in the other."),
        line="Training is guess, measure how wrong, nudge the numbers a little, and repeat."),
    "5.3": dict(
        plain=["Fine-tuning data is a set of examples: an input and the exact answer you want back.",
               "The model copies those examples, the good habits and the bad ones.",
               "So the work is cleaning: remove duplicates, drop poor answers, and hide personal data.",
               "Keep every example in the same format you will use when you call the model later.",
               "Set some examples aside, never trained on, so you can check the result honestly."],
        map=[("Messy or wrong past answers", "Low-quality responses, which the model will imitate faithfully"),
             ("The same question copied 50 times", "Duplicates and near-duplicates, which overweight one pattern"),
             ("300 neat, varied answers", "A few hundred clean, consistent, representative pairs"),
             ("Keeping some exams back for the real test", "The validation split, kept apart by customer and time to avoid leakage")],
        fig=flow([("1.2M tickets", "resolved, with agent replies", "b"),
                  ("Dedup", "exact, then near-duplicate: ~590,000 left"),
                  ("Quality filter", "fixed on first reply, rated 4-5: ~88,500"),
                  ("PII scrub", "phone, account, address become [PHONE] etc.: ~80,000"),
                  ("Sample 8,000", "by intent share, then a 90/10 split by customer and month", "g")],
                 "From 1.2 million support tickets to 8,000 training examples"),
        cap="The worked example further down this page, as a pipeline. The drop rates at each stage are that example's assumptions. Notice how little survives: curation, not volume, is the job.",
        line="The model becomes a mirror of your examples, so clean the examples before you train."),
    "5.4": dict(
        plain=["A 7-billion-parameter model has 7 billion numbers. Training all of them needs a lot of GPU memory.",
               "LoRA (Low-Rank Adaptation) freezes those numbers and trains two small extra matrices beside each big matrix it adapts.",
               "The small pair learns a correction that is added to the big matrix's output.",
               "You end up training well under 1% of the numbers, and the result is a file of megabytes.",
               "QLoRA also squeezes the frozen model into 4-bit numbers, so a big model fits on one small GPU."],
        map=[("The camera, left exactly as it was", "The frozen base weights W, never updated"),
             ("The small clip-on lens", "The adapter: matrices A and B, the only trained part"),
             ("How the clip-on bends the picture", "The output becomes Wx + BAx: original plus a learned correction"),
             ("Swapping clip-ons for different jobs", "Loading a different adapter file on the same base model"),
             ("Packing the camera into a smaller case", "QLoRA: the frozen base stored in 4-bit, the adapter still trained normally")],
        fig=two(lora_fig, "LoRA: a frozen weight matrix W plus a small trainable bypass B times A"),
        cap="The input goes through the frozen W as usual and also through a thin bypass: A squeezes 3,584 numbers down to r = 16, B expands them back. Only A and B are trained. Counts use Qwen2.5-7B's real q_proj shape from the config on this page.",
        play=("lorarank", "Move the rank and pick which matrices get adapters. Every count is r × (inputs + outputs) per matrix, using Qwen2.5-7B's real shapes."),
        line="LoRA leaves the big model alone and trains a small add-on that nudges its output."),
    "5.5": dict(
        plain=["A base model only continues text. Ask it a question and it may reply with more questions.",
               "Instruction tuning, also called SFT (supervised fine-tuning), trains it on many pairs: a request and a good answer.",
               "After that, it answers requests instead of just continuing them.",
               "Each example is wrapped in the model's chat template: special tokens that mark who is speaking.",
               "A second step, preference tuning, trains on pairs of answers where people marked the better one."],
        map=[("A parrot that already knows thousands of words", "A pretrained base model"),
             ("“When someone asks this, the answer looks like that”", "SFT on instruction → response pairs"),
             ("A treat for the better of two answers", "Preference tuning (RLHF or DPO) on chosen-versus-rejected pairs"),
             ("Learning even your mistakes and your accent", "The model learns everything in the examples, template tokens included")],
        fig=two(loss_fig, "Which tokens of a training example carry the loss"),
        cap="This page's worked example: 150 system tokens, 350 customer tokens, 250 reply tokens. With the default full-sequence loss, two thirds of the training signal goes on predicting the prompt. Assistant-only loss spends all of it on the reply.",
        line="Instruction tuning shows the model thousands of 'asked this, answer like that' examples until answering becomes its habit."),
    "5.6": dict(
        plain=["After a fine-tune, ask two questions.",
               "Did it get better at your task, and did it get worse at anything else?",
               "Answer both by testing the old model and the new one on examples neither was trained on.",
               "A model that aces your task can quietly forget other skills. This is called catastrophic forgetting.",
               "Small test sets are noisy, so check that a change is bigger than the noise before you trust it."],
        map=[("A test the student hasn't seen", "A held-out set, never used in training"),
             ("Not asking the tutor", "Not trusting 'it feels better'; scoring both models the same way"),
             ("Checking they can still read", "A general-ability probe: diverse prompts outside the task"),
             ("Their marks before the tuition", "The baseline: the original base model on the same sets")],
        fig=two(eval_fig, "Base versus fine-tuned model on the task and on general ability, with 95% intervals"),
        cap="The worked example from this page. The task gain is huge compared with its noise. The 6-point general-ability drop has overlapping whiskers, so the page settles it with a paired test on the same 300 prompts.",
        line="A fine-tune counts only if it beats the old model on unseen tests and didn't break anything else."),
}
