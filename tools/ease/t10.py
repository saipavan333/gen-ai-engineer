"""Pass 2, Section 10: Multimodal (folder track15/). Image-token counts use the rule the lesson
pages state (from Anthropic's vision docs): ceil(w/28) x ceil(h/28), long edge up to 2,576 px,
at most 4,784 visual tokens. Other numbers come from the pages' "At real scale" boxes."""
import math

from ease.kit import arrow, box, lines, path_arrow, raw, rect, svg, text, wrap
from ease.t08 import HAIKU, SONNET, bar, fold_where, label_lines, usd


def img_tokens(w, h):
    return math.ceil(w / 28) * math.ceil(h / 28)


def chip(x, y, w, t, tone, h=26):
    return rect(x, y, w, h, tone, rx=6) + text(x + w / 2, y + h - 8, t, "s b mono")


# ---------- 10.1 an image becomes patch tokens next to text tokens
def vlm_svg():
    W0, H0 = 1000, 1000
    gx, gy = math.ceil(W0 / 28), math.ceil(H0 / 28)
    n = gx * gy
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, f"A {W0:,} x {H0:,} px photo of a receipt" if not nw else f"A {W0:,} x {H0:,} px photo", "b", "start")
        # the photo cut into patches (drawn as 12 x 12 here; the real grid is 36 x 36)
        S = 150 if nw else 180
        px0, py0 = 14, 36
        body += rect(px0, py0, S, S, "k", rx=4)
        # a pretend receipt: lines of "text"
        for i in range(7):
            body += bar(px0 + 24, py0 + 22 + i * 18, S - 48 - (i % 3) * 18, 7, "fill-m", 2).replace('class="fill-m"', 'class="fill-m" opacity=".55"')
        k = 12
        for i in range(1, k):
            body += f'<line x1="{px0 + S * i / k:g}" y1="{py0}" x2="{px0 + S * i / k:g}" y2="{py0 + S}" class="ln thin" opacity=".5"/>'
            body += f'<line x1="{px0}" y1="{py0 + S * i / k:g}" x2="{px0 + S}" y2="{py0 + S * i / k:g}" class="ln thin" opacity=".5"/>'
        body += f'<rect x="{px0 + S * 3 / k:g}" y="{py0 + S * 2 / k:g}" width="{S / k:g}" height="{S / k:g}" class="ring"/>'
        body += text(px0, py0 + S + 18, "each square = 28 x 28 px", "s", "start")
        body += text(px0, py0 + S + 36, f"{gx} x {gy} = {n:,} patches (12 x 12 drawn)", "s ac-t", "start")
        if nw:
            # encoder to the right of the photo
            ex, ey, ew = px0 + S + 30, py0 + 20, W - (px0 + S + 30) - 12
            b, eh = box(ex, ey, ew, "Vision encoder", "one vector per patch", "c", size=14)
            body += b + arrow(px0 + S + 4, ey + eh / 2, ex - 3, ey + eh / 2)
            y = py0 + S + 62
            body += arrow(W / 2, y - 14, W / 2, y + 6)
            y += 14
        else:
            ex, ey, ew = px0 + S + 60, py0 + 40, 170
            b, eh = box(ex, ey, ew, "Vision encoder", "turns each patch into a vector", "c", size=14)
            body += b + arrow(px0 + S + 6, ey + eh / 2, ex - 4, ey + eh / 2)
            y = py0 + 40
        # context window row: image tokens then text tokens
        cx0 = 14 if nw else ex + ew + 50
        cw_ = W - cx0 - 14
        body += text(cx0, y + 4, "The context window the LLM reads", "s b", "start")
        if not nw:
            body += arrow(ex + ew + 4, ey + eh / 2, cx0 - 6, ey + eh / 2)
        y += 16
        x = cx0
        im_n = 5 if nw else 4
        for i in range(im_n):
            body += chip(x, y, 30, "img", "k")
            x += 34
        body += text(x + 8, y + 18, "…", "b", "start")
        x += 26
        row2 = nw
        body += text(cx0, y + 46, f"{n:,} image tokens", "s k-t", "start")
        yt = y + 58 if row2 or cw_ < 330 else y
        xt = cx0 if (row2 or cw_ < 330) else x + 6
        for t_ in ["What", "is", "the", "total?"]:
            ww = len(t_) * 8 + 16
            body += chip(xt, yt, ww, t_, "a")
            xt += ww + 4
        body += text(cx0, yt + 46, "+ your text tokens, read together", "s ac-t", "start")
        H = max(py0 + S + 50, yt + 60) if not nw else yt + 60
        out.append(svg(W, H, body, "An image cut into 28-pixel patches becomes tokens next to the text", cls))
    return raw(*out)


# ---------- 10.2 two readers and a gate before money moves
def doc_svg():
    per_day = 1_200_000 / 250
    reviews = per_day * 0.06
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = ""
        y = 16
        if nw:
            b, h = box(14, y, W - 28, "Invoice image", "2 pages, 1000 x 1400 px", "k", size=14)
            body += b
            y += h + 34
            body += arrow(W / 2 - 60, y - 32, 96, y - 3) + arrow(W / 2 + 60, y - 32, W - 96, y - 3)
            o, oh = box(14, y, 158, "OCR", "exact characters, no idea which is the total", "c", size=14)
            v, vh = box(188, y, 158, "VLM", "reads the layout, returns JSON fields", "p", size=14)
            hh = max(oh, vh)
            o, _ = box(14, y, 158, "OCR", "exact characters, no idea which is the total", "c", h=hh, size=14)
            v, _ = box(188, y, 158, "VLM", "reads the layout, returns JSON fields", "p", h=hh, size=14)
            body += o + v
            y += hh + 34
            body += arrow(93, y - 32, W / 2 - 40, y - 3) + arrow(267, y - 32, W / 2 + 40, y - 3)
            ck, ch = box(14, y, W - 28, "Checks before payment", "schema valid · line items + tax = total · OCR digits = VLM digits · vendor exists", "w", size=14)
            body += ck
            y += ch + 34
            body += arrow(93, y - 32, 93, y - 3, "ok") + arrow(267, y - 32, 267, y - 3, "wn")
            p_, ph = box(14, y, 158, "Pay", "all checks pass", "g", size=14)
            r_, rh = box(188, y, 158, "Person reviews", f"if any check fails: {reviews:.0f} a day at 6%", "w", size=14)
            body += p_ + r_
            y += max(ph, rh) + 10
        else:
            b, h = box(14, 70, 150, "Invoice image", "2 pages, 1000 x 1400 px", "k", size=14)
            body += b
            o, oh = box(214, 16, 190, "OCR (e.g. Tesseract)", "exact characters, no idea which number is the total", "c", size=14)
            v, vh = box(214, 16 + oh + 18, 190, "VLM", "reads the layout, returns JSON: vendor, total, due date", "p", size=14)
            body += o + v
            mid = 70 + h / 2
            body += path_arrow([(166, mid), (188, mid), (188, 16 + oh / 2), (211, 16 + oh / 2)])
            body += path_arrow([(166, mid), (188, mid), (188, 16 + oh + 18 + vh / 2), (211, 16 + oh + 18 + vh / 2)])
            ck, ch = box(454, 30, 140, "Checks", "schema valid; items + tax = total; OCR digits = VLM digits; vendor exists", "w", size=14)
            body += ck
            body += path_arrow([(406, 16 + oh / 2), (430, 16 + oh / 2), (430, 30 + ch / 2), (451, 30 + ch / 2)])
            body += path_arrow([(406, 16 + oh + 18 + vh / 2), (430, 16 + oh + 18 + vh / 2), (430, 30 + ch / 2), (451, 30 + ch / 2)])
            p_, ph = box(630, 16, 116, "Pay", "all pass", "g", size=14)
            r_, rh = box(630, 16 + ph + 18, 116, "Person", f"any fails: {reviews:.0f} a day", "w", size=14)
            body += p_ + r_
            cy = 30 + ch / 2
            body += path_arrow([(596, cy), (612, cy), (612, 16 + ph / 2), (627, 16 + ph / 2)], "ok")
            body += path_arrow([(596, cy), (612, cy), (612, 16 + ph + 18 + rh / 2), (627, 16 + ph + 18 + rh / 2)], "wn")
            y = max(16 + oh + 18 + vh, 30 + ch, 16 + ph + 18 + rh) + 12
        tail = f"{per_day:,.0f} invoices a day (the page's example). If 6% fail a check, a person reviews {reviews:.0f} a day: about one full-time job."
        tl, th = label_lines(14, y + 8, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 12, body, "OCR and a VLM read the same invoice; checks decide pay or human review", cls))
    return raw(*out)


# ---------- 10.3 the 1-second voice-agent budget (the page's illustrative latencies)
def voice_svg():
    first_clause = round(8 / 50 * 1000)
    segs = [("end of speech", "detect the user stopped", 300, "fill-m"), ("STT", "final transcript", 150, "fill-c"),
            ("LLM", "time to first token", 350, "fill-p"), ("LLM", f"first 8 tokens at 50/s", first_clause, "fill-a"),
            ("TTS", "first audio out", 150, "fill-g")]
    total = sum(s[2] for s in segs)
    target = 1000
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "Voice agent: from the user going quiet to the first sound of the reply" if not nw else "From user quiet to first reply sound", "b", "start")
        # pipeline
        y = 36
        stages = [("Mic", "k"), ("STT", "c"), ("LLM", "p"), ("TTS", "g"), ("Speaker", "k")]
        n = len(stages)
        g = 12 if nw else 40
        bw = (W - 28 - (n - 1) * g) / n
        for i, (t, tone) in enumerate(stages):
            x = 14 + i * (bw + g)
            body += rect(x, y, bw, 34, tone, rx=8) + text(x + bw / 2, y + 22, t, "b", size=12 if nw else 15)
            if i < n - 1:
                body += arrow(x + bw + 2, y + 17, x + bw + g - 2, y + 17)
        y += 62
        x0, x1 = 14, W - 14
        sc = (x1 - x0) / 1200
        x = x0
        tx = x0 + target * sc
        body += f'<line x1="{tx:g}" y1="{y-14:g}" x2="{tx:g}" y2="{y+44:g}" class="ln wn"/>' + text(tx - 4, y - 4, "1,000 ms target", "s wn-t", "end")
        for name, sub, ms, f in segs:
            w = ms * sc
            body += bar(x, y, w - 2, 34, f, 3)
            body += text(x + w / 2, y + 22, f"{ms}", "s b").replace('class="s b"', 'class="s b" style="fill:var(--bg)"', 1)
            x += w
        body += text(x - 2, y + 58, f"total {total:,} ms", "s b wn-t", "end")
        y += 80
        for i, (name, sub, ms, f) in enumerate(segs):
            if nw:
                yy = y + i * 20
                body += bar(14, yy - 11, 14, 14, f) + text(34, yy + 1, f"{name}: {sub}, {ms} ms", "s", "start")
            else:
                col, row = i % 2, i // 2
                xx, yy = 14 + col * 370, y + row * 22
                body += bar(xx, yy - 11, 14, 14, f) + text(xx + 20, yy + 1, f"{name}: {sub}, {ms} ms", "s", "start")
        y += (5 * 20 if nw else 66) + 6
        tail = f"Three models in a row add up: {total:,} ms is {total - target} ms over. Streaming each stage and starting speech on the first clause is how real systems win the time back."
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Latency budget of a voice agent: each stage adds delay", cls))
    return raw(*out)


# ---------- 10.4 two indexes, one fused list, a VLM that looks at the images
def mmrag_svg():
    clip_gb = 2_000_000 * 512 * 4 / 1e9
    cap_gb = 2_000_000 * 384 * 4 / 1e9
    cap_cost = (img_tokens(800, 800) + 100) * HAIKU[0] / 1e6 + 80 * HAIKU[1] / 1e6
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = ""
        if nw:
            y = 14
            q, qh = box(14, y, W - 28, "Query", "“curved velvet sofa”", "a", size=14)
            body += q
            y += qh + 32
            body += arrow(100, y - 30, 93, y - 3) + arrow(260, y - 30, 267, y - 3)
            a1, h1 = box(14, y, 158, "CLIP index", f"image vectors, 2M x 512 = {clip_gb:.1f} GB", "k", size=14)
            a2, h2 = box(188, y, 158, "Caption index", f"VLM captions, MiniLM 384-dim = {cap_gb:.1f} GB", "c", size=14)
            hh = max(h1, h2)
            a1, _ = box(14, y, 158, "CLIP index", f"image vectors, 2M x 512 = {clip_gb:.1f} GB", "k", h=hh, size=14)
            a2, _ = box(188, y, 158, "Caption index", f"VLM captions, MiniLM 384-dim = {cap_gb:.1f} GB", "c", h=hh, size=14)
            body += a1 + a2
            body += text(93, y + hh + 16, "top 50", "s m") + text(267, y + hh + 16, "top 50", "s m")
            y += hh + 40
            body += arrow(93, y - 18, W / 2 - 30, y - 2) + arrow(267, y - 18, W / 2 + 30, y - 2)
            f, fh = box(14, y, W - 28, "Fuse with RRF", "reciprocal rank fusion, as in Track 3", "p", size=14)
            body += f
            y += fh + 30
            body += arrow(W / 2, y - 28, W / 2, y - 3)
            v, vh = box(14, y, W - 28, "VLM answers", "looks at the top 5 images + captions, shows them as citations", "g", size=14)
            body += v
            y += vh + 10
        else:
            q, qh = box(14, 70, 130, "Query", "“curved velvet sofa”", "a", size=14)
            a1, h1 = box(196, 14, 210, "CLIP index", f"image vectors: 2M x 512 dims = {clip_gb:.1f} GB", "k", size=14)
            a2, h2 = box(196, 14 + h1 + 30, 210, "Caption index", f"VLM captions, MiniLM 384 dims = {cap_gb:.1f} GB", "c", size=14)
            f, fh = box(456, 58, 120, "Fuse (RRF)", "top 50 + top 50", "p", size=14)
            v, vh = box(616, 40, 130, "VLM answers", "sees the top 5 images, cites them", "g", size=14)
            body += q + a1 + a2 + f + v
            mid = 70 + qh / 2
            body += path_arrow([(146, mid), (170, mid), (170, 14 + h1 / 2), (193, 14 + h1 / 2)])
            body += path_arrow([(146, mid), (170, mid), (170, 14 + h1 + 30 + h2 / 2), (193, 14 + h1 + 30 + h2 / 2)])
            fm = 58 + fh / 2
            body += path_arrow([(408, 14 + h1 / 2), (432, 14 + h1 / 2), (432, fm), (453, fm)])
            body += path_arrow([(408, 14 + h1 + 30 + h2 / 2), (432, 14 + h1 + 30 + h2 / 2), (432, fm), (453, fm)])
            body += arrow(578, fm, 613, 40 + vh / 2)
            y = max(14 + h1 + 30 + h2, 40 + vh) + 14
        tail = (f"Captions are written once, ahead of time: an 800 x 800 photo is {img_tokens(800, 800)} image tokens, about {usd(cap_cost, 6)} on Haiku 5.5, "
                f"so {usd(cap_cost * 2e6)} for the whole 2-million-image catalogue (half that through the Batch API).")
        tl, th = label_lines(14, y + 6, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 10, body, "Multimodal RAG: two indexes, fused, then a VLM grounds the answer", cls))
    return raw(*out)


LESSONS = {
    "10.1": dict(
        plain=["A vision-language model (VLM) is a language model that can also look at pictures.",
               "You can hand it a photo, a screenshot or a chart and ask questions about it.",
               "It cuts the image into small squares called patches and turns each one into a token.",
               "Those image tokens sit in the context window next to your words, and the model reads them together.",
               "It is great at describing, but weak at counting, exact positions and tiny text."],
        map=[("Cutting the photo into stickers", "Splitting the image into patches; on Claude each patch is 28 x 28 pixels"),
             ("A short code for each sticker", "A vision encoder turns each patch into a vector, an image token"),
             ("Reading the sticker list with the sentence", "Image tokens and text tokens share one context window"),
             ("Small print cut across two stickers", "Fine detail is easily lost: VLMs misread small text and miscount")],
        fig=vlm_svg(),
        cap="Bigger images mean more patches, so more tokens, a higher bill and a slower reply. The 1,000 x 1,000 = 1,296 tokens example is the one this page quotes from Anthropic's vision docs.",
        play=("imagetokens", "Pick a preset or drag the width and height. The token count uses the page's rule, ceil(width / 28) x ceil(height / 28), including the size caps."),
        line="A VLM cuts a picture into small squares and reads them as tokens, right next to your words."),
    "10.2": dict(
        plain=["A scanned invoice is a picture, not data your systems can use.",
               "Document AI turns that picture into clean fields, such as vendor, total and due date.",
               "OCR (optical character recognition) copies every character exactly but doesn't know what any of it means.",
               "A VLM understands the layout and can return the fields as JSON, but it can misread a digit.",
               "For money, use both, check the sums, and send anything that disagrees to a person."],
        map=[("The friend who reads every word in order", "OCR, e.g. Tesseract: exact text, no structure"),
             ("The friend who just says “the total is $42”", "A VLM asked for JSON fields from the image"),
             ("Comparing what the two friends said", "Cross-check OCR digits against the VLM's total and account number"),
             ("Asking a grown-up when they disagree", "Schema validation, sum checks, then human review for failures")],
        fig=doc_svg(),
        cap="Two imperfect readers check each other, then plain code checks the arithmetic. Only invoices that pass everything get paid automatically. Volumes are the page's accounts-payable example.",
        line="Let one reader understand the document and another check the exact digits, then verify before you pay."),
    "10.3": dict(
        plain=["Voice apps need two extra pieces around a language model.",
               "Speech-to-text (STT) turns what someone says into text; Whisper is a free, open model for this.",
               "Text-to-speech (TTS) turns the model's written reply back into a voice.",
               "So a voice assistant is a chain: listen, think, speak.",
               "The hard part is speed, because every link in the chain adds delay."],
        map=[("The first runner writing down what you said", "Speech-to-text, e.g. Whisper"),
             ("The second runner thinking of an answer", "The LLM, with prompting, RAG or tools as usual"),
             ("The third runner reading it out loud", "Text-to-speech"),
             ("A wrong word carried to the finish line", "Transcription errors flow into the answer"),
             ("Runners overlapping instead of waiting", "Streaming each stage; starting speech on the first clause")],
        fig=voice_svg(),
        cap="Top: the chain. Bottom: the page's illustrative budget for a real-time agent, in milliseconds. The total is computed from the five stages and lands just over the 1-second target.",
        line="A voice app is listen, think, speak, and every step must be quick."),
    "10.4": dict(
        plain=["Normal RAG (retrieval-augmented generation) searches text to ground the answer.",
               "Lots of knowledge lives in pictures: product photos, charts, diagrams and scanned pages.",
               "Multimodal RAG makes images searchable too.",
               "One way puts pictures and words on the same map (CLIP); another writes a caption for each picture and searches the captions.",
               "Then a VLM looks at the images it found and answers, showing them as its sources."],
        map=[("Pins for pictures and sentences on one map", "CLIP: images and text embedded into the same vector space"),
             ("Pinning your question and looking nearby", "Embed the query and take the nearest image vectors"),
             ("A note written next to each picture's pin", "Caption-then-embed: a VLM describes each image as text"),
             ("Fine print the map can't hold", "Prices or model numbers must also exist as text or metadata")],
        fig=mmrag_svg(),
        cap="The query searches both indexes, the two ranked lists are fused, and the VLM sees the actual images it cites. Index sizes and caption cost are computed from the page's 2-million-image catalogue example.",
        line="Multimodal RAG finds the right pictures as well as the right text, then lets a VLM look at them before it answers."),
}
fold_where(LESSONS)
