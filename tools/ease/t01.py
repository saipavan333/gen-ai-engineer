"""Pass 2, Track 1: How LLMs work."""
import math

from ease.kit import arrow, box, esc, fan, flow, lines, path_arrow, raw, rect, svg, text, wrap

# ---------- 1.2 BPE, computed for real on a toy corpus (same algorithm as assets/ease/play-t01.js)
CORPUS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}


def bpe_merges(corpus, n):
    words = {w: list(w) for w in corpus}
    merges = []
    for _ in range(n):
        counts, order = {}, []
        for w, f in corpus.items():
            sy = words[w]
            for a, b in zip(sy, sy[1:]):
                if (a, b) not in counts:
                    order.append((a, b))
                counts[(a, b)] = counts.get((a, b), 0) + f
        if not counts:
            break
        best = max(order, key=lambda p: counts[p])  # first-seen wins ties
        merges.append((best, counts[best]))
        for w in words:
            words[w] = apply_one(words[w], best)
    return merges


def apply_one(sy, pair):
    out, i = [], 0
    while i < len(sy):
        if i < len(sy) - 1 and (sy[i], sy[i + 1]) == pair:
            out.append(sy[i] + sy[i + 1]); i += 2
        else:
            out.append(sy[i]); i += 1
    return out


def chips(x, y, toks, cw=17, h=30, tone="a"):
    out, cx = "", x
    for t in toks:
        w = max(28, len(t) * cw + 14)
        out += rect(cx, y, w, h, tone, rx=7) + text(cx + w / 2, y + 20, t, "b mono")
        cx += w + 6
    return out, cx


def bpe_svg():
    merges = bpe_merges(CORPUS, 4)
    word = "lowest"
    states = [list(word)]
    for (p, _c) in merges:
        states.append(apply_one(states[-1], p))
    # wide
    body = text(20, 24, 'Toy training text: "low" x5, "lower" x2, "newest" x6, "widest" x3', "s m", "start")
    y = 44
    for i, st in enumerate(states):
        lab = "Start: single letters" if i == 0 else f"Merge {i}: {merges[i-1][0][0]} + {merges[i-1][0][1]} → {''.join(merges[i-1][0])}  (pair seen {merges[i-1][1]}x)"
        body += text(20, y + 20, lab, "s", "start")
        c, _ = chips(400, y, st, tone="g" if i == len(states) - 1 else "a")
        body += c
        if i < len(states) - 1:
            body += arrow(385, y + 15, 393, y + 15, "thin")
        y += 48
    body += text(20, y + 14, f'New word "{word}" → {len(states[-1])} tokens: ' + " + ".join(states[-1]) + "   (never seen in training, still encoded)", "s ok-t", "start")
    wide = svg(760, y + 28, body, "Byte-pair encoding merges letters into tokens step by step", "ez-wide")
    # tall
    body = text(12, 20, "Toy text: low x5, lower x2,", "s m", "start") + text(12, 38, "newest x6, widest x3", "s m", "start")
    y = 54
    for i, st in enumerate(states):
        lab = "Start: single letters" if i == 0 else f"Merge {i}: {merges[i-1][0][0]} + {merges[i-1][0][1]} → {''.join(merges[i-1][0])} (seen {merges[i-1][1]}x)"
        body += text(12, y + 14, lab, "s", "start")
        c, _ = chips(12, y + 22, st, tone="g" if i == len(states) - 1 else "a")
        body += c
        y += 66
    body += text(12, y + 8, f'"{word}" → ' + " + ".join(states[-1]) + f" ({len(states[-1])} tokens)", "s ok-t", "start")
    tall = svg(360, y + 22, body, "Byte-pair encoding merges letters into tokens step by step", "ez-tall")
    return raw(wide, tall)


# ---------- 1.3 embeddings as points (toy 2-D vectors; origin at the centre)
EMB = [("My flight was cancelled", 0.95, 0.30, "c"), ("The airline scrapped my trip", 0.80, 0.60, "c"),
       ("Train delayed two hours", 0.92, -0.02, "c"), ("I like pizza", -0.62, 0.70, "k"),
       ("Pasta for dinner tonight", -0.75, 0.55, "k"), ("Refund to my card", -0.12, -0.95, "g"),
       ("Where is my money back?", 0.40, -0.85, "g")]


def cos(a, b):
    return (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b))


def emb_svg():
    q = (0.92, 0.22)
    sims = sorted(((cos(q, (x, y)), t) for t, x, y, _ in EMB), reverse=True)
    top = {t for _, t in sims[:3]}
    pizza = dict((t, s) for s, t in sims)["I like pizza"]
    out = []
    for W, H, cx, cy, R, cls in ((660, 360, 305, 180, 150, "ez-wide"), (360, 300, 180, 150, 120, "ez-tall")):
        narrow = W < 400
        body = f'<line x1="{cx-R-20}" y1="{cy}" x2="{cx+R+20}" y2="{cy}" class="grid"/><line x1="{cx}" y1="{cy-R-10}" x2="{cx}" y2="{cy+R+10}" class="grid"/>'
        for k, (t, x, y, tone) in enumerate(EMB):
            px, py = cx + x * R, cy - y * R
            body += f'<line x1="{cx}" y1="{cy}" x2="{px:g}" y2="{py:g}" class="ln thin {"ac" if t in top else ""}" opacity="{1 if t in top else .35}"/>'
            body += f'<circle cx="{px:g}" cy="{py:g}" r="7" class="dot tn-{tone}"/>'
            lab = str(k + 1) if narrow else t
            body += text(px + (-11 if x < 0 else 11), py + 5, lab, "s b" if narrow else "s", "end" if x < 0 else "start")
        qx, qy = cx + q[0] * R * 0.62, cy - q[1] * R * 0.62
        body += f'<circle cx="{qx:g}" cy="{qy:g}" r="9" class="fill-a"/><circle cx="{qx:g}" cy="{qy:g}" r="15" class="ring"/>'
        if narrow:
            body += text(12, 20, "Toy 2-D picture (illustrative)", "s m", "start")
            y = H + 6
            for k, (t, x, yy, tone) in enumerate(EMB):
                body += f'<circle cx="20" cy="{y-5}" r="6" class="dot tn-{tone}"/>' + text(32, y, f"{k+1}  {t}", "s", "start")
                y += 22
            body += text(12, y + 6, "ring = the question", "s ac-t", "start")
            body += text(12, y + 30, "Top 3 cosine: " + ", ".join(f"{s:.2f}" for s, _ in sims[:3]) + f" (travel); pizza {pizza:.2f}", "s", "start")
            out.append(svg(W, y + 44, body, "Texts as points: similar meanings sit close together and point the same way", cls))
        else:
            body += text(20, 24, "Toy 2-D picture (illustrative). Real embeddings have hundreds to thousands of numbers.", "s m", "start")
            body += text(20, 44, "Ringed point = the question “my flight got cancelled, what now?”", "s ac-t", "start")
            body += text(20, H - 10, "Top 3 by cosine similarity: " + ", ".join(f"{s:.2f}" for s, _ in sims[:3]) + f" (all travel). “I like pizza”: {pizza:.2f}", "s", "start")
            out.append(svg(W, H, body, "Texts as points: similar meanings sit close together and point the same way", cls))
    return raw(*out)


# ---------- 1.4 the context window budget (illustrative numbers)
def ctx_svg():
    W = 760
    segs = [("system prompt", 2000, "c"), ("chat history", 30000, "p"), ("pasted documents", 150000, "k"), ("question", 500, "a"), ("room for the answer", 8000, "g")]
    total, win = sum(s for _, s, _ in segs), 200000
    x0, bw = 20, W - 40
    body = text(20, 22, "One shared budget: a 200,000-token window (illustrative numbers)", "b", "start")
    x = x0
    for name, n, tone in segs:
        w = bw * n / win
        body += rect(x, 40, w, 46, tone, rx=4)
        x += w
    body += f'<line x1="{x0+bw}" y1="30" x2="{x0+bw}" y2="96" class="ln wn"/>' + text(x0 + bw - 4, 112, "window limit: 200,000", "s wn-t", "end")
    # legend
    lx, ly = 20, 136
    for name, n, tone in segs:
        lab = f"{name} {n:,}"
        body += rect(lx, ly - 11, 14, 14, tone, rx=3) + text(lx + 20, ly + 1, lab, "s", "start")
        lx += 20 + len(lab) * 7 + 22
        if lx > 600:
            lx, ly = 20, ly + 24
    body += text(20, ly + 30, f"Used {total:,} of 200,000. Add 10,000 more tokens of history and something gets cut.", "s", "start")
    # attention arcs
    words = ["The", "dog", "chased", "the", "ball", "because", "it", "was", "bored"]
    y = ly + 118
    xs = []
    cx = 30
    for w_ in words:
        ww = len(w_) * 9 + 18
        xs.append(cx + ww / 2)
        body += rect(cx, y, ww, 30, "a" if w_ in ("dog", "it") else "b", rx=6) + text(cx + ww / 2, y + 20, w_)
        cx += ww + 8
    i, j = words.index("it"), words.index("dog")
    body += f'<path d="M{xs[i]:g},{y} C{xs[i]:g},{y-48} {xs[j]:g},{y-48} {xs[j]:g},{y-2}" class="ln ac"/>'
    body += f'<polygon points="{xs[j]:g},{y-1} {xs[j]-5:g},{y-10} {xs[j]+5:g},{y-10}" class="hd ac"/>'
    k = words.index("ball")
    body += f'<path d="M{xs[i]:g},{y} C{xs[i]:g},{y-26} {xs[k]:g},{y-26} {xs[k]:g},{y-2}" class="ln thin dash"/>'
    body += text(20, y - 58, "Attention: “it” looks back at every earlier token and weighs “dog” highest", "s ac-t", "start")
    body += text(20, y + 52, "Thick arrow = high attention weight, dashed = low (illustrative)", "s m", "start")
    wide = svg(W, y + 64, body, "The context window as one shared token budget, and attention linking it to dog", "ez-wide")
    # tall: vertical stack bar + short sentence
    W2 = 360
    body = text(12, 20, "A 200,000-token window", "b", "start") + text(12, 38, "(illustrative numbers)", "s m", "start")
    y = 50
    hmax = 300
    for name, n, tone in segs:
        h = max(16, hmax * n / win)
        body += rect(12, y, 120, h, tone, rx=3) + text(142, y + min(h, 30) / 2 + 5, f"{name} {n:,}", "s", "start")
        y += h + 2
    body += f'<line x1="6" y1="{y+4}" x2="200" y2="{y+4}" class="ln wn"/>' + text(12, y + 22, "limit: everything must fit above", "s wn-t", "start")
    y += 60
    sw = ["dog", "chased", "the", "ball", "…", "it"]
    xs = []
    cx = 12
    for w_ in sw:
        ww = len(w_) * 9 + 16
        xs.append(cx + ww / 2)
        body += rect(cx, y, ww, 30, "a" if w_ in ("dog", "it") else "b", rx=6) + text(cx + ww / 2, y + 20, w_)
        cx += ww + 6
    body += f'<path d="M{xs[-1]:g},{y} C{xs[-1]:g},{y-44} {xs[0]:g},{y-44} {xs[0]:g},{y-2}" class="ln ac"/>'
    body += f'<polygon points="{xs[0]:g},{y-1} {xs[0]-5:g},{y-10} {xs[0]+5:g},{y-10}" class="hd ac"/>'
    body += text(12, y + 52, "Attention links “it” back to “dog”", "s ac-t", "start")
    tall = svg(W2, y + 64, body, "The context window as one shared token budget, and attention linking it to dog", "ez-tall")
    return raw(wide, tall)


# ---------- 1.5 temperature and top-p reshape one distribution (illustrative scores)
CANDS = [("sunny", 3.0), ("cloudy", 2.2), ("rainy", 1.8), ("nice", 1.5), ("humid", 0.9), ("purple", -1.0)]


def softmax(scores, T):
    m = max(scores)
    e = [math.exp((s - m) / T) for s in scores]
    z = sum(e)
    return [v / z for v in e]


def nucleus(p, top_p):
    order = sorted(range(len(p)), key=lambda i: -p[i])
    keep, cum = set(), 0.0
    for i in order:
        keep.add(i)
        cum += p[i]
        if cum >= top_p:
            break
    return keep


def samp_svg():
    panels = [(0.3, 1.0), (1.0, 1.0), (1.0, 0.8), (1.6, 1.0)]
    W, pw = 760, 178
    body = text(20, 22, 'Next token after "The weather today is" (illustrative scores)', "b", "start")
    for k, (T, tp) in enumerate(panels):
        x0 = 20 + k * (pw + 8)
        p = softmax([s for _, s in CANDS], T)
        keep = nucleus(p, tp)
        body += text(x0 + pw / 2, 50, f"T = {T}" + (f", top-p = {tp}" if tp < 1 else ""), "b ac-t")
        for i, (name, _) in enumerate(CANDS):
            y = 64 + i * 30
            w = (pw - 70) * p[i]
            body += text(x0 + 52, y + 15, name, "s", "end")
            body += f'<rect x="{x0+56:g}" y="{y+2:g}" width="{max(2, w):g}" height="18" rx="3" class="{"fill-a" if i in keep else "fill-w"}"/>'
            body += text(x0 + 60 + w, y + 16, f"{p[i]*100:.0f}%", "s m" if i in keep else "s wn-t", "start", 12)
        if tp < 1:
            body += text(x0 + pw / 2, 64 + len(CANDS) * 30 + 14, "red = cut before the draw", "s wn-t", size=12)
    body += text(20, 64 + len(CANDS) * 30 + 40, "Low T sharpens the favourite. High T flattens the odds. Top-p drops the unlikely tail, then the rest is rescaled.", "s", "start")
    wide = svg(W, 64 + len(CANDS) * 30 + 56, body, "Temperature and top-p reshape the next-token probabilities", "ez-wide")
    # tall: 2 x 2 grid
    W2, pw = 360, 168
    body = text(12, 20, 'After "The weather today is"', "b", "start") + text(12, 38, "(illustrative scores)", "s m", "start")
    for k, (T, tp) in enumerate(panels):
        x0 = 8 + (k % 2) * (pw + 12)
        y0 = 52 + (k // 2) * 250
        p = softmax([s for _, s in CANDS], T)
        keep = nucleus(p, tp)
        body += text(x0 + pw / 2, y0 + 14, f"T={T}" + (f", top-p {tp}" if tp < 1 else ""), "b ac-t")
        for i, (name, _) in enumerate(CANDS):
            y = y0 + 26 + i * 34
            w = (pw - 40) * p[i]
            body += text(x0, y + 12, name, "s", "start")
            body += f'<rect x="{x0:g}" y="{y+16:g}" width="{max(2, w):g}" height="12" rx="3" class="{"fill-a" if i in keep else "fill-w"}"/>'
            body += text(x0 + w + 4, y + 27, f"{p[i]*100:.0f}%", "s m" if i in keep else "s wn-t", "start", 12)
    tall = svg(W2, 52 + 2 * 250, body, "Temperature and top-p reshape the next-token probabilities", "ez-tall")
    return raw(wide, tall)


LESSONS = {
    "1.1": dict(
        plain=["A language model is a program that guesses what comes next in a piece of text.",
               "You give it some words. It scores every possible next piece, picks one, and adds it on.",
               "Then it does the same again, one small piece at a time, until the answer is done.",
               "Those pieces are called tokens: a whole word or part of a word.",
               "Chat apps such as ChatGPT and Claude run this same guessing game, trained on a huge amount of text."],
        map=[("The suggestion bar above your phone keyboard", "The model's probability for every possible next token"),
             ("Tapping one suggestion", "Picking (sampling) one token and adding it to the text"),
             ("Tapping again and again to finish a message", "The generation loop: one token per step"),
             ("What the keyboard learned about your writing", "The weights learned in pre-training on trillions of words")],
        fig=flow([("Your text so far", '"The cat sat on the"', "c"), ("Split into tokens", "text becomes token ids"),
                  ("Model scores every token", "mat 41%, sofa 22%, … (illustrative)", "a"), ("Pick one", '"mat"', "k"),
                  ("Add it to the text", '"The cat sat on the mat"', "g")],
                 "The generation loop of a language model", loop=(4, 0, "repeat until a stop token or the length limit")),
        cap="The whole trick is this loop. The model never writes the answer in one go. It runs once per token, and each new token joins the input for the next run.",
        line="A language model is a very well-read guesser that writes one small piece of text at a time."),
    "1.2": dict(
        plain=["Language models don't read letters or whole words. They read tokens.",
               'A token is a small chunk of text, such as "the", "ing" or " cat" (with its space).',
               "A tool called a tokenizer cuts your text into tokens and swaps each one for a number.",
               "The model only ever sees those numbers.",
               "You pay per token, and the model's memory limit is counted in tokens too."],
        map=[("A big ready-made brick", 'A common word that is one token, like "the"'),
             ("Building a rare word from small bricks", 'A rare word split into pieces, like "Token" + "izing"'),
             ("The full brick catalogue", "The vocabulary: about 50,000 to 200,000 tokens"),
             ("Each brick's catalogue number", "The token id, which is all the model reads")],
        fig=bpe_svg(),
        cap="How a tokenizer learns its bricks (byte-pair encoding, BPE): count which neighbouring pieces appear together most, merge that pair into a new token, repeat. This toy run is computed from the four words shown; real tokenizers do tens of thousands of merges on terabytes of text.",
        play=("bpe", "Pick a word and drag the slider to learn more merges. Watch the word shrink from letters to a few tokens. The merges are computed live on the same toy text."),
        line="Text is cut into tokens, tokens become numbers, and everything (cost, limits, speed) is counted in tokens."),
    "1.3": dict(
        plain=["An embedding turns a piece of text into a long list of numbers.",
               "Texts with similar meaning get similar lists.",
               "So you can treat every text as a point on a map, where close points mean similar meaning.",
               "To search, you turn the question into a point too and look at what is nearby.",
               "Search, recommendations and RAG (retrieval-augmented generation, Track 3) all start here."],
        map=[("A student standing somewhere in the hall", "One text turned into a vector (a point in meaning space)"),
             ("Standing shoulder to shoulder", "High cosine similarity: the vectors point the same way"),
             ("Walking to where the question stands", "Embedding the question with the same embedding model"),
             ("Looking at who is nearby", "Nearest-neighbour search: return the top few closest texts")],
        fig=emb_svg(),
        cap="Each text is an arrow from the centre. Cosine similarity measures how closely two arrows point the same way (1.0 = same direction, 0 = unrelated). The coordinates here are made up for a 2-D picture; the similarity numbers are computed from them.",
        play=("embed", "Pick a question. The three closest texts light up, with their cosine similarity computed from the toy vectors."),
        line="An embedding is a meaning-to-numbers map, so 'similar meaning' becomes 'nearby points'."),
    "1.4": dict(
        plain=["The context window is everything the model can see at one time.",
               "Your instructions, the chat so far, any pasted documents and the model's own answer all share it.",
               "It is measured in tokens: from about 8,000 on small models up to 1 million on today's largest.",
               "Anything outside the window does not exist for the model.",
               'Attention is how the model picks which earlier tokens matter, such as linking "it" back to "the dog".'],
        map=[("The desk surface", "The context window: a fixed number of tokens"),
             ("Pages spread on the desk", "System prompt, chat history, documents, and the answer being written"),
             ("The cupboard", "Everything not in the prompt; the model cannot see it"),
             ("Your eyes jumping between pages", "Attention weights linking each token to earlier ones")],
        fig=ctx_svg(),
        cap="Top: every part of a request spends the same token budget, including the reply. Bottom: attention lets the token “it” draw on “dog” more than on “ball”. Both pictures use illustrative numbers.",
        line="The model sees only what fits on its desk, and attention decides which parts of the desk it looks at."),
    "1.5": dict(
        plain=["For every next token, the model gives a probability to every option.",
               "Sampling is the step that picks one option from that list.",
               "Temperature sets how bold the pick is: low almost always takes the favourite, high gives long shots a chance.",
               "Top-p throws away the unlikely tail before the pick.",
               "On local models you set these knobs yourself; some hosted APIs now fix them for you."],
        map=[("How many marbles of each colour", "The probability of each candidate token"),
             ("Shaking the odds (temperature)", "Dividing the model's scores by T before turning them into probabilities"),
             ("Throwing the rarest colours out (top-k, top-p)", "Cutting the tail, then rescaling what is left"),
             ("Drawing one marble", "Sampling one token"),
             ("Refilling the bag after every draw", "New probabilities after every token, based on the text so far")],
        fig=samp_svg(),
        cap="Same scores, four settings. The percentages are computed from the illustrative scores with softmax. Temperature changes the shape; top-p (nucleus sampling) keeps the smallest set of tokens whose probabilities add up to p.",
        play=("sampling", "Move temperature and top-p. The bars are recomputed with softmax; red bars are cut before the draw. Press Draw to sample one token."),
        line="The model gives the odds; temperature and top-p decide how adventurous the pick is."),
    "1.6": dict(
        plain=["LLMs are great at working with text you hand them: rewriting, summarising, pulling out facts.",
               "They are weak when they must recall something exactly, like a date, a price or last week's news.",
               "When they don't know, they still answer in the same confident voice.",
               "A made-up answer like that is called a hallucination.",
               "The fix is engineering: put the facts in the prompt, give the model tools, and check what comes back."],
        map=[("Rewriting the essay you hand them", "Tasks grounded in the prompt: summarise, extract, rewrite, classify"),
             ("Answering a date from memory", "Recall from frozen training data, which stops at the knowledge cutoff"),
             ("The same confident voice either way", "Fluent output whether right or wrong; no built-in 'unsure' signal"),
             ("You checking their answer", "Retrieval, tools, validation and evals built around the model")],
        fig=fan(("Your request", "what kind of job is it?", "c"),
                [("The answer is in the text you give it", "summarise, extract, rewrite: reliable", "g"),
                 ("It needs exact facts from memory", "dates, prices, citations: may be stale or invented; retrieve them instead", "w"),
                 ("It needs live data or exact maths", "today's price, a big sum: call a tool", "k"),
                 ("It needs a judgment you can't check", "medical, legal: add a human review step", "p")],
                "Routing a request by how much the model must recall on its own"),
        cap="A useful habit: before trusting an answer, ask where the facts came from. From the prompt is usually fine. From the model's memory needs checking.",
        line="Trust an LLM with the text you give it, and check anything it has to remember on its own."),
}
