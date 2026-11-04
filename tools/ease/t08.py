"""Pass 2, Section 8: Serving & cost (folder track8/).

Every number in these pictures is either computed here from the inputs the lesson page states
(its "At real scale" boxes) or labelled illustrative. Prices: the verified 2026-11-03 list prices.
"""
import math

from ease.kit import arrow, box, box_h, esc, lines, path_arrow, raw, rect, svg, text, wrap

SONNET = (2.0, 10.0)   # $ per million input / output tokens
HAIKU = (0.10, 0.50)   # up to 100K tokens
OPUS = (4.0, 20.0)


def usd(x, nd=None):
    if nd is None:
        nd = 0 if x >= 100 else (2 if x >= 1 else (4 if x >= 0.001 else 5))
    return f"${x:,.{nd}f}"


def bar(x, y, w, h, fill, rx=3):
    return f'<rect x="{x:g}" y="{y:g}" width="{max(0.0, w):g}" height="{h:g}" rx="{rx}" class="{fill}"/>'


def label_lines(x, y, s, width, size=13, cls="s", anchor="start", lh=None):
    """Wrapped text, returns (svg, height)."""
    ls = wrap(s, width, size)
    lh = lh or round(size * 1.32)
    return lines(x, y, ls, cls, anchor, size=size, lh=lh), len(ls) * lh


# ---------- 8.1 one request on a timeline and on a bill (inputs from the page's real-scale box)
def cost_latency_svg():
    tin, tout = 3000, 300
    pin, pout = SONNET
    cin, cout = tin * pin / 1e6, tout * pout / 1e6
    ttft, tps = 0.6, 60            # the page's illustrative speeds
    dec = tout / tps
    total = ttft + dec
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        L = 14 if nw else 20
        x0, x1 = (L, W - 16) if nw else (150, W - 24)
        sx = lambda t: x0 + (x1 - x0) * t / 6.0
        body = ""
        y = 22
        if nw:
            body += text(L, y, "One request: 3,000 tokens in,", "b", "start") + text(L, y + 19, "300 out, on Sonnet 5.5", "b", "start")
            y += 46
        else:
            body += text(L, y, "One request: 3,000 tokens in, 300 tokens out, on Sonnet 5.5 ($2 / $10 per million)", "b", "start")
            y += 30
        # --- time row
        body += text(L, y + 4, "TIME", "s b", "start")
        if not nw:
            body += text(L, y + 50, "what the", "s m", "start") + text(L, y + 66, "user waits for", "s m", "start")
        yb = y + 18 if nw else y + 28
        body += bar(sx(0), yb, sx(ttft) - sx(0), 34, "fill-c")
        n_ticks = 30
        for i in range(n_ticks):
            tx = sx(ttft + dec * (i + 0.5) / n_ticks)
            body += bar(tx - 3, yb + 4, 6, 26, "fill-a", 1)
        # axis
        ya = yb + 48
        body += f'<line x1="{sx(0):g}" y1="{ya:g}" x2="{sx(6):g}" y2="{ya:g}" class="ln thin"/>'
        for t in range(7):
            body += f'<line x1="{sx(t):g}" y1="{ya:g}" x2="{sx(t):g}" y2="{ya+5:g}" class="ln thin"/>' + text(sx(t), ya + 19, f"{t} s", "s m")
        # call-outs
        yc = ya + 44
        body += arrow(sx(ttft), yc - 12, sx(ttft), yb + 38, "ac")
        body += text(sx(ttft) - 4 if nw else sx(ttft) - 6, yc + 2, f"first token at {ttft} s (TTFT)", "s ac-t", "start")
        body += text(sx(total), yc + 22, f"last token at {total:.1f} s", "s", "end")
        body += arrow(sx(total), yc + 8, sx(total), yb + 38)
        if nw:
            ky = yc + 46
            body += bar(L, ky - 11, 14, 14, "fill-c") + text(L + 20, ky + 1, "prefill: reads all 3,000 input", "s", "start")
            body += text(L + 20, ky + 18, "tokens in one parallel pass", "s", "start")
            body += bar(L, ky + 31, 14, 14, "fill-a") + text(L + 20, ky + 43, f"decode: {tout} tokens, one at a time,", "s", "start")
            body += text(L + 20, ky + 60, f"at {tps} tokens/s = {dec:.0f} s", "s", "start")
            y = ky + 92
        else:
            body += text(sx(ttft / 2), yb - 8, "prefill", "s b")
            body += text(sx(ttft + dec / 2), yb - 8, f"decode: {tout} tokens, one at a time, at {tps} tokens/s = {dec:.0f} s", "s b")
            body += text(sx(0), yc + 46, "Prefill reads all 3,000 input tokens in one parallel pass, so a long prompt mostly delays the first token.", "s m", "start")
            y = yc + 84
        # --- money row
        body += text(L, y, "MONEY", "s b", "start")
        mx0, mx1 = (L, W - 16) if nw else (150, W - 24)
        scale = (mx1 - mx0) / (cin + cout)
        yb = y + 14 if nw else y - 14
        body += bar(mx0, yb, cin * scale, 34, "fill-c") + bar(mx0 + cin * scale + 2, yb, cout * scale - 2, 34, "fill-a")
        lab_y = yb + 54
        body += text(mx0, lab_y, f"input: {tin:,} x $2/M = {usd(cin)}", "s", "start")
        body += text(mx1, lab_y + (18 if nw else 0), f"output: {tout} x $10/M = {usd(cout)}", "s", "end")
        body += text(mx0, lab_y + (44 if nw else 26), f"Total {usd(cin + cout)} a request. Output costs 5x more per token,", "s b", "start")
        body += text(mx0, lab_y + (62 if nw else 44), f"yet input is {cin / (cin + cout):.0%} of this bill: there are 10x more input tokens.", "s", "start") if not nw else \
            text(mx0, lab_y + 62, f"yet input is {cin / (cin + cout):.0%} of this bill (10x more", "s", "start") + text(mx0, lab_y + 80, "input tokens).", "s", "start")
        H = lab_y + (96 if nw else 60)
        out.append(svg(W, H, body, "Timeline and bill of one request: prefill then decode; input and output cost", cls))
    return raw(*out)


# ---------- 8.2 streaming as a sequence diagram (browser, your server, model)
def stream_seq_svg():
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        lanes = [("Browser", 60 if nw else 120), ("Your server", 180 if nw else 380), ("Model", 300 if nw else 640)]
        fs = 12 if nw else 13
        body = ""
        top = 20
        for name, x in lanes:
            body += rect(x - (48 if nw else 70), top, 96 if nw else 140, 34, "c", rx=8) + text(x, top + 22, name, "b")
        steps = [  # (from, to, label, cls, gap after)
            (0, 1, "question (HTTP POST)", "", 38),
            (1, 2, "prompt, stream=True", "", 0),
        ]
        y = top + 64
        H_est = 470 if nw else 430
        for x in [l[1] for l in lanes]:
            body += f'<line x1="{x}" y1="{top+34}" x2="{x}" y2="{H_est-60}" class="grid dash"/>'
        def msg(a, b, y, lab, c=""):
            xa, xb = lanes[a][1], lanes[b][1]
            s = arrow(xa + (6 if xb > xa else -6), y, xb + (-6 if xb > xa else 6), y, c)
            s += text((xa + xb) / 2, y - 7, lab, "s" + (" ac-t" if c == "ac" else ""), size=fs)
            return s
        body += msg(0, 1, y, "question (POST)")
        yq = y
        y += 38
        body += msg(1, 2, y, "prompt, stream=True")
        y0 = y
        y += 16
        # prefill gap on the model lane
        body += rect(lanes[2][1] - 9, y, 18, 46, "k", rx=4)
        body += text(lanes[2][1] + (-16 if nw else 18), y + 28, "prefill", "s k-t", "end" if nw else "start", fs)
        y += 64
        body += msg(2, 1, y, "token 1", "ac")
        body += msg(1, 0, y + 22, "SSE event: token 1", "ac")
        body += text(lanes[0][1] - (46 if nw else 66), y + 50, "first words on screen", "s ac-t", "start", fs)
        # brace for TTFT on the left
        bx = 10 if nw else 26
        body += f'<polyline points="{bx+8},{yq:g} {bx},{yq:g} {bx},{y+22:g} {bx+8},{y+22:g}" class="ln thin"/>'
        cy = (yq + y + 22) / 2
        body += f'<text x="{bx+16:g}" y="{cy:g}" class="s b" text-anchor="middle" transform="rotate(-90 {bx+16:g} {cy:g})">TTFT</text>'
        y += 74
        for k in range(3):
            body += msg(2, 1, y + k * 18, "", "thin")
            body += msg(1, 0, y + k * 18 + 9, "", "thin")
        body += text(lanes[2][1] + (-14 if nw else 18), y + 26, "decode: one", "s", "end" if nw else "start", fs)
        body += text(lanes[2][1] + (-14 if nw else 18), y + 42, "token at a time", "s", "end" if nw else "start", fs)
        y += 76
        body += msg(2, 1, y, "last token + stop")
        body += msg(1, 0, y + 24, "done event")
        y += 52
        out.append(svg(W, y - 10, body, "Sequence: browser, server and model exchange a streamed answer chunk by chunk", cls))
    return raw(*out)


# ---------- 8.3 the cache stack, with the page's HR-assistant numbers computed
def cache_numbers():
    n = 200_000
    pre, var, outt = 6000, 1500, 250
    pin, pout = SONNET
    read = 0.10
    none = (pre + var) * pin / 1e6 + outt * pout / 1e6
    writes = 288 * pre * 2.50 / 1e6
    pc = pre * read / 1e6 + var * pin / 1e6 + outt * pout / 1e6
    d_none = n * none
    d_pc = n * pc + writes
    d_exact = n * 0.85 * pc
    d_sem = n * 0.75 * pc
    return dict(none=none, pc=pc, d_none=d_none, d_pc=d_pc, d_exact=d_exact, d_sem=d_sem)


def cache_svg():
    c = cache_numbers()
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        fw = W - 28 if nw else 420
        body = text(14, 20, "Each request falls through the layers until one can answer it", "s m", "start") if not nw else \
            text(14, 20, "A request falls through the layers", "s m", "start")
        y = 34
        stages = [("1. Exact-match cache", "same text seen before?", "hit: 15% of requests", "a"),
                  ("2. Semantic cache", "a similar question, similarity ≥ 0.92?", "hit: 10% more", "p"),
                  ("3. Model call + prompt cache", "6,000-token fixed prefix read from cache at $0.10/M, the rest at $2/M", "fresh answer, then stored in caches 1 and 2", "c")]
        exit_w = 0 if nw else 0
        bw = fw - (0 if nw else 150)
        for i, (t, s, hit, tone) in enumerate(stages):
            b, hh = box(14, y, bw, t, s, tone)
            body += b
            if nw:
                body += text(14 + bw, y + hh + 18, ("→ " if i < 2 else "") + hit, "s ok-t", "end")
                if i < 2:
                    body += arrow(40, y + hh + 2, 40, y + hh + 34)
                    body += text(48, y + hh + 22, "miss", "s m", "start")
                y += hh + 40
            else:
                body += arrow(14 + bw + 4, y + hh / 2, 14 + bw + 30, y + hh / 2, "ok")
                hl, _ = label_lines(14 + bw + 36, y + hh / 2 - 6, hit + (" in milliseconds, $0" if i < 2 else ""), 118, 13, "s ok-t")
                body += hl
                if i < 2:
                    body += arrow(14 + bw / 2, y + hh + 2, 14 + bw / 2, y + hh + 28)
                    body += text(14 + bw / 2 + 8, y + hh + 19, "miss", "s m", "start")
                y += hh + 30
        flow_end = y
        # bars: cost per day
        rows = [("no caching", c["d_none"], "fill-w"), ("+ prompt cache", c["d_pc"], "fill-c"),
                ("+ exact cache", c["d_exact"], "fill-a"), ("+ semantic cache", c["d_sem"], "fill-p")]
        if nw:
            y = flow_end + 6
            bx0, bmax = 14, W - 90
        else:
            y = 60
            bx0, bmax = 14 + fw + 34, W - 20 - (14 + fw + 34) - 56
        head_x = 14 if nw else 14 + fw + 34
        body += text(head_x, y, "Cost per day, 200,000 requests (computed)", "s b", "start") if nw else \
            text(head_x, y - 8, "Cost per day (computed)", "s b", "start")
        y += 14 if nw else 4
        for name, v, f in rows:
            w = bmax * v / c["d_none"]
            if nw:
                body += text(14, y + 14, name, "s", "start")
                body += bar(14, y + 20, w, 16, f) + text(14 + w + 6, y + 33, usd(v), "s b", "start")
                y += 44
            else:
                body += text(bx0, y + 12, name, "s", "start")
                body += bar(bx0, y + 20, w, 24, f) + text(bx0 + w + 6, y + 37, usd(v), "s b", "start")
                y += 66
        H = (max(y, flow_end) + 4) if not nw else y + 4
        out.append(svg(W, H, body, "Exact, semantic and prompt caching stacked, with cost per day", cls))
    return raw(*out)


# ---------- 8.4 router vs cascade, two mini flows with the page's e-commerce numbers
def route_numbers():
    n = 1_000_000
    tin, tout = 1500, 200
    s = tin * SONNET[0] / 1e6 + tout * SONNET[1] / 1e6
    h = tin * HAIKU[0] / 1e6 + tout * HAIKU[1] / 1e6
    return dict(s=s, h=h, all_s=n * s, router=0.75 * n * h + 0.25 * n * s, cascade=n * h + 0.30 * n * s,
                r_h=0.75 * n * h, r_s=0.25 * n * s, c_h=n * h, c_s=0.30 * n * s)


def node(x, y, w, t, s, tone, h=None):
    return box(x, y, w, t, s, tone, h=h, size=14)


def routing_svg():
    r = route_numbers()
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = ""
        y = 22
        # --- A: router
        body += text(14, y, f"A. Classifier router: {usd(r['router'], 2)} a day ({1 - r['router'] / r['all_s']:.0%} less than all-Sonnet {usd(r['all_s'])})" if not nw else
                     "A. Classifier router", "b", "start")
        if nw:
            body += text(14, y + 18, f"{usd(r['router'], 2)} a day ({1 - r['router'] / r['all_s']:.0%} less)", "s ac-t", "start")
            y += 10
        y += 16
        if nw:
            q, qh = node(14, y, 120, "Query", "1M a day", "b")
            rt, rh = node(14, y + qh + 30, 120, "Router", "easy or hard?", "k")
            body += q + rt + arrow(74, y + qh + 2, 74, y + qh + 28)
            ry = y + qh + 30 + rh / 2
            hk, hh = node(180, y, 166, "Haiku 5.5", f"75%: {usd(r['r_h'], 2)}", "g")
            sn, sh = node(180, y + qh + 30 + rh - 46, 166, "Sonnet 5.5", f"25%: {usd(r['r_s'])}", "c")
            body += hk + sn
            body += path_arrow([(136, ry), (156, ry), (156, y + hh / 2), (177, y + hh / 2)], "ok")
            body += path_arrow([(136, ry), (156, ry), (156, y + qh + 30 + rh - 46 + sh / 2), (177, y + qh + 30 + rh - 46 + sh / 2)])
            y = max(y + qh + 30 + rh, y + qh + 30 + rh - 46 + sh) + 26
        else:
            q, qh = node(14, y + 20, 140, "Query", "1M a day", "b")
            rt, rh = node(200, y + 20, 150, "Router", "small classifier: easy or hard?", "k")
            hk, hh = node(430, y, 316, "Haiku 5.5 ($0.10 / $0.50)", f"75% of traffic: 750,000 x {usd(r['h'], 5)} = {usd(r['r_h'], 2)}", "g")
            sn, sh = node(430, y + hh + 14, 316, "Sonnet 5.5 ($2 / $10)", f"25%: 250,000 x {usd(r['s'], 3)} = {usd(r['r_s'])}", "c")
            body += q + rt + hk + sn + arrow(156, y + 20 + qh / 2, 197, y + 20 + qh / 2)
            my = y + 20 + rh / 2
            body += path_arrow([(352, my), (390, my), (390, y + hh / 2), (427, y + hh / 2)], "ok")
            body += path_arrow([(352, my), (390, my), (390, y + hh + 14 + sh / 2), (427, y + hh + 14 + sh / 2)])
            body += text(412, y + hh / 2 - 7, "easy", "s ok-t", "middle", 12) + text(412, y + hh + 14 + sh / 2 - 7, "hard", "s", "middle", 12)
            y = y + hh + 14 + sh + 34
        # --- B: cascade
        body += f'<line x1="14" y1="{y-14:g}" x2="{W-14}" y2="{y-14:g}" class="grid"/>'
        body += text(14, y + 8, f"B. Cascade: {usd(r['cascade'])} a day ({1 - r['cascade'] / r['all_s']:.0%} less)" if not nw else "B. Cascade", "b", "start")
        if nw:
            body += text(14, y + 26, f"{usd(r['cascade'])} a day ({1 - r['cascade'] / r['all_s']:.0%} less)", "s ac-t", "start")
            y += 40
            hk, hh = node(14, y, 150, "Haiku 5.5 first", f"every query: {usd(r['c_h'])}", "g")
            ck, chh = node(196, y, 150, "Check", "schema ok? retrieval score ok? no refusal?", "k")
            body += hk + ck + arrow(166, y + hh / 2, 193, y + hh / 2)
            yy = y + max(hh, chh) + 34
            ok, oh = node(14, yy, 150, "Answer", "70% pass", "g")
            sn, sh = node(196, yy, 150, "Sonnet 5.5", f"30% escalate: {usd(r['c_s'])}", "c")
            body += ok + sn
            body += path_arrow([(240, y + chh + 2), (240, yy - 10), (90, yy - 10), (90, yy - 3)], "ok")
            body += arrow(300, y + chh + 2, 300, yy - 3, "wn")
            body += text(165, yy - 16, "pass", "s ok-t") + text(308, (y + chh + yy) / 2 + 4, "fail", "s wn-t", "start")
            y = yy + max(oh, sh) + 20
        else:
            y += 22
            q, qh = node(14, y + 10, 140, "Query", "1M a day", "b")
            hk, hh = node(200, y + 10, 160, "Haiku 5.5 first", f"every query: {usd(r['c_h'])}", "g")
            ck, chh = node(400, y, 150, "Check", "schema valid? retrieval score ok? no refusal?", "k")
            ok, oh = node(596, y - 4, 150, "Answer", "70% pass", "g")
            sn, sh = node(596, y + oh + 14, 150, "Sonnet 5.5", f"30% escalate: {usd(r['c_s'])}", "c")
            body += q + hk + ck + ok + sn
            body += arrow(156, y + 10 + qh / 2, 197, y + 10 + qh / 2) + arrow(362, y + 10 + hh / 2, 397, y + 10 + hh / 2)
            cy = y + chh / 2
            body += path_arrow([(552, cy), (572, cy), (572, y - 4 + oh / 2), (593, y - 4 + oh / 2)], "ok")
            body += path_arrow([(552, cy), (572, cy), (572, y + oh + 14 + sh / 2), (593, y + oh + 14 + sh / 2)], "wn")
            body += text(582, y - 4 + oh / 2 - 7, "pass", "s ok-t", "middle", 12) + text(582, y + oh + 14 + sh / 2 - 7, "fail", "s wn-t", "middle", 12)
            y = y + oh + 14 + sh + 22
        tail = ("Escalated users wait for two calls. And a misroute is not free: 2% of traffic sent to the wrong tier, at $3 per support contact, costs $60,000 a day."
                if not nw else "Escalated users wait for two calls. A 2% misroute at $3 per support contact costs $60,000 a day.")
        tl, th = label_lines(14, y + 4, tail, W - 28, 13, "s wn-t")
        body += tl
        out.append(svg(W, y + th + 8, body, "Two ways to route: a classifier router and a cascade, with cost per day", cls))
    return raw(*out)


# ---------- 8.5 what fits on a 24 GB GPU (Qwen2.5-7B facts from the page)
def quant_svg():
    params = 7.61e9
    kv_tok = 2 * 28 * 4 * 128 * 2          # bytes per token
    kv = 16 * 8000 * kv_tok / 1e9          # GB
    rows = [("bf16 (16 bits)", params * 2 / 1e9, 16), ("int8 (8 bits)", params / 1e9, 8), ("Q4_K_M (~4.9 bits)", 4.7, 4)]
    gpu = 24.0
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = ""
        y = 22
        body += text(14, y, "One weight, stored with fewer bits" if not nw else "One weight, fewer bits", "b", "start")
        y += 14
        for name, _, bits in rows:
            sq = 9 if nw else 14
            gx = 14 if nw else 180
            if not nw:
                body += text(170, y + 12, name, "s", "end")
            else:
                body += text(14, y + 12, name, "s", "start")
                y += 18
            for b in range(bits):
                body += bar(gx + b * (sq + 3), y, sq, sq, "fill-a" if bits == 16 else ("fill-c" if bits == 8 else "fill-g"), 2)
            body += text(gx + bits * (sq + 3) + 6, y + sq - 1, f"{bits} bits" if bits != 4 else "4 bits + scales", "s m", "start")
            y += sq + 12
        y += 18
        body += text(14, y, "Qwen2.5-7B on a 24 GB GPU" if nw else "Qwen2.5-7B plus the KV cache for 16 chats x 8,000 tokens, on a 24 GB GPU", "b", "start")
        if nw:
            body += text(14, y + 18, "+ KV cache, 16 chats x 8,000 tokens", "s m", "start")
            y += 18
        y += 16
        lx = 14 if nw else 160
        bw = (W - lx - 20) if nw else (W - lx - 60)
        sc = bw / gpu
        for name, wgb, _ in rows:
            if nw:
                body += text(14, y + 12, name, "s", "start")
                y += 18
            else:
                body += text(lx - 8, y + 20, name, "s", "end")
            body += f'<rect x="{lx}" y="{y}" width="{bw:g}" height="28" rx="4" class="bx"/>'
            body += bar(lx, y, wgb * sc, 28, "fill-a", 4) + bar(lx + wgb * sc, y, kv * sc, 28, "fill-k", 0)
            free = gpu - round(wgb, 1) - round(kv, 1)   # from the rounded figures the page prints
            body += text(lx + wgb * sc / 2, y + 19, f"{wgb:.1f}", "s b", size=12).replace('class="s b"', 'class="s b" style="fill:var(--bg);font-size:12px"', 1)
            body += text(lx + wgb * sc + kv * sc / 2, y + 19, f"{kv:.1f}", "s b").replace('class="s b"', 'class="s b" style="fill:var(--bg);font-size:12px"', 1)
            if free * sc > 110:
                body += text(lx + bw - 6, y + 19, f"{free:.1f} GB free", "s ok-t", "end")
                y += 40
            else:
                body += text(lx + bw, y + 44, f"only {free:.1f} GB left for everything else: too tight", "s wn-t", "end")
                y += 58
        body += (f'<line x1="{lx+bw:g}" y1="{y-148:g}" x2="{lx+bw:g}" y2="{y-6:g}" class="ln wn"/>' + text(lx + bw + 6, y - 128, "24 GB", "s wn-t", "start")) if not nw else ""
        y += 6
        body += bar(14, y - 11, 14, 14, "fill-a") + text(34, y + 1, "weights (GB)", "s", "start")
        body += bar(130, y - 11, 14, 14, "fill-k") + text(150, y + 1, f"KV cache {kv:.1f} GB", "s", "start")
        if not nw:
            body += text(300, y + 1, f"KV per token = 2 x 28 layers x 4 heads x 128 dims x 2 bytes = {kv_tok:,} bytes", "s m", "start")
        y += 26
        tail = "Fewer bits per weight leaves room for more conversations on the same card."
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Bits per weight and GPU memory at three precisions", cls))
    return raw(*out)


# ---------- 8.6 static vs continuous batching on 4 slots (illustrative request lengths)
LENS = [8, 2, 3, 2, 7, 2, 2, 3]   # decode steps per request (illustrative)
SLOTS = 4


def static_sched(lens, k):
    out, t = [], 0
    for i in range(0, len(lens), k):
        grp = lens[i:i + k]
        for j, L in enumerate(grp):
            out.append((j, t, t + L, i + j))
        t += max(grp)
    return out, t


def cont_sched(lens, k):
    free, out = [0] * k, []
    for i, L in enumerate(lens):
        s = min(range(k), key=lambda j: (free[j], j))
        out.append((s, free[s], free[s] + L, i))
        free[s] += L
    return out, max(free)


def batching_svg():
    st, t_st = static_sched(LENS, SLOTS)
    ct, t_ct = cont_sched(LENS, SLOTS)
    busy = sum(LENS)
    tmax = max(t_st, t_ct)
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        lx = 58 if nw else 96
        cw = (W - lx - 16) / tmax
        rh = 24 if nw else 26
        body = text(14, 20, f"8 waiting requests, a GPU with {SLOTS} batch slots (lengths illustrative)" if not nw else f"8 requests, {SLOTS} batch slots (illustrative)", "s m", "start")
        y = 48
        for title, sched, tend in ((f"Static batching: done at step {t_st}", st, t_st), (f"Continuous batching: done at step {t_ct}", ct, t_ct)):
            body += text(14, y, title, "b", "start")
            y += 12
            for s in range(SLOTS):
                yy = y + s * (rh + 6)
                body += text(lx - 8, yy + rh - 7, f"slot {s+1}", "s m", "end")
                body += f'<rect x="{lx}" y="{yy}" width="{cw*tend:g}" height="{rh}" rx="3" class="bx tn-w"/>'
            for (s, a, b, i) in sched:
                yy = y + s * (rh + 6)
                body += bar(lx + a * cw + 1, yy + 1, (b - a) * cw - 2, rh - 2, "fill-c" if i < 4 else "fill-a", 3)
                body += text(lx + (a + b) / 2 * cw, yy + rh - 7, f"R{i+1}", "s b").replace('class="s b"', 'class="s b" style="fill:var(--bg)"', 1)
            idle = SLOTS * tend - busy
            y += SLOTS * (rh + 6) + 4
            body += text(lx, y + 12, f"{idle} of {SLOTS * tend} slot-steps idle (shaded)" + ("" if nw else (": every slot waits for the longest request in its batch" if sched is st else ": a freed slot takes the next request at once")), "s wn-t" if sched is st else "s ok-t", "start")
            y += 36
        # axis
        y -= 8
        body += f'<line x1="{lx}" y1="{y}" x2="{lx+cw*tmax:g}" y2="{y}" class="ln thin"/>'
        for t in range(0, tmax + 1, 3 if nw else 1):
            body += f'<line x1="{lx+t*cw:g}" y1="{y}" x2="{lx+t*cw:g}" y2="{y+4}" class="ln thin"/>' + text(lx + t * cw, y + 17, str(t), "s m")
        body += text(lx + cw * tmax, y + 34, "decode steps →", "s m", "end")
        y += 60
        tail = f"Same 8 requests, same GPU: continuous batching finishes in {t_ct} steps instead of {t_st}, so the same GPU gets through {t_st / t_ct:.1f}x as many requests in the same time."
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Gantt chart: static batching leaves slots idle, continuous batching refills them", cls))
    return raw(*out)


# ---------- 8.7 an 8-step agent: every call re-sends a growing prompt (page's numbers)
def budget_svg():
    pre, step, outt, n = 3700, 950, 150, 8
    calls = [(pre, step * k, outt) for k in range(n)]
    tin = sum(a + b for a, b, _ in calls)
    tout = n * outt
    cost = tin * SONNET[0] / 1e6 + tout * SONNET[1] / 1e6
    mx = max(a + b + c for a, b, c in calls)
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 20, "Tokens sent on each call of one 8-step support-agent task" if not nw else "Tokens per call, one 8-step task", "b", "start")
        lx = 60 if nw else 70
        bw = W - lx - (50 if nw else 90)
        y = 40
        rh = 20 if nw else 22
        for k, (a, b, c) in enumerate(calls):
            sc = bw / mx
            body += text(lx - 8, y + rh - 6, f"call {k+1}", "s", "end")
            body += bar(lx, y, a * sc, rh, "fill-c", 2) + bar(lx + a * sc, y, b * sc, rh, "fill-k", 0) + bar(lx + (a + b) * sc + 2, y, c * sc + 2, rh, "fill-a", 2)
            body += text(lx + (a + b + c) * sc + 10, y + rh - 6, f"{a + b:,}", "s m", "start")
            y += rh + 7
        y += 10
        items = [("fill-c", "fixed prefix 3,700 (system + tools)"), ("fill-k", "history: +950 per step"), ("fill-a", "output 150")]
        if nw:
            for f, t in items:
                body += bar(14, y - 11, 14, 14, f) + text(34, y + 1, t, "s", "start")
                y += 20
        else:
            x = 14
            for f, t in items:
                body += bar(x, y - 11, 14, 14, f) + text(x + 20, y + 1, t, "s", "start")
                x += 20 + len(t) * 7 + 26
            y += 20
        y += 8
        tail = (f"Whole task: {tin:,} input + {tout:,} output tokens = {usd(cost)} on Sonnet 5.5. "
                f"The growing history is {sum(b for _, b, _ in calls) / tin:.0%} of the input, and the prefix repeats 8 times: those are the two things to trim or cache.")
        tl, th = label_lines(14, y, tail, W - 28, 13, "s")
        body += tl
        out.append(svg(W, y + th + 4, body, "Stacked bars: each agent call re-sends the fixed prefix plus a growing history", cls))
    return raw(*out)


C = cache_numbers()
R = route_numbers()

LESSONS = {
    "8.1": dict(
        plain=["Every call to a language model costs two things: money and time.",
               "Both are counted in tokens, the small chunks of text the model reads and writes.",
               "You pay for the tokens you send in and the tokens that come back, and output tokens cost more each.",
               "Time has two parts: reading your whole prompt (prefill), then writing the answer one token at a time (decode).",
               "If you can count the tokens, you can predict the bill and the wait before you launch."],
        map=[("Kilometres on the way there", "Input tokens: your prompt, priced per million"),
             ("The pricier kilometres on the way back", "Output tokens: often several times the input price (Sonnet 5.5: $2 in, $10 out)"),
             ("Reading out a long address before the driver sets off", "Prefill: the model reads the whole prompt; this sets the time to first token (TTFT)"),
             ("Driving home one street at a time", "Decode: one token per step, so a long answer means a long wait")],
        fig=cost_latency_svg(),
        cap="Top: time. The wide block is prefill; each thin bar after it is a slice of the answer being written. Bottom: money for the same request. The token counts, prices and speeds are the page's own example; the dollar split is computed from them.",
        line="Count the tokens in and out, and you know both the bill and the wait."),
    "8.2": dict(
        plain=["A model writes its answer one token at a time.",
               "Without streaming, your app waits for the very last token, then shows everything at once.",
               "With streaming, each token is sent to the screen the moment it is written.",
               "The answer takes just as long to finish, but the user starts reading almost at once.",
               "The number users feel is TTFT (time to first token): how long until the first word appears."],
        map=[("The cook finishing a slice", "The model producing the next token (decode)"),
             ("Handing each slice over as soon as it is ready", "Forwarding each chunk to the browser as a server-sent event (SSE)"),
             ("Getting the first slice after one minute", "Time to first token, mostly the prefill time"),
             ("The whole pizza arriving at the same time either way", "Total generation time is unchanged; only when you see it changes"),
             ("A half-cut box nobody can use", "JSON or a tool call: code needs the whole thing, so don't stream to a parser")],
        fig=stream_seq_svg(),
        cap="Time runs downward. Your server opens one long connection to the browser and relays each token as an event, so the first words appear one TTFT after the question, not after the whole answer.",
        play=("streaming", "Move the sliders for prefill time, generation speed and answer length. The top lane waits for the end; the bottom lane streams. The times are computed from your settings, which are illustrative."),
        line="Streaming doesn't make the model faster; it lets people start reading sooner."),
    "8.3": dict(
        plain=["Many apps get asked the same things again and again.",
               "A cache is a store of answers you already paid for, kept so a repeat costs almost nothing.",
               "An exact cache matches identical questions; a semantic cache matches questions with the same meaning.",
               "Prompt caching is different: the provider reuses its work on a long, fixed start of your prompt, so each call is cheaper.",
               "The risk is serving a stored answer to someone it doesn't fit."],
        map=[("The same book already on the desk", "Exact-match cache: identical text, stored answer, no model call"),
             ("Guessing 'the boy wizard book' means yesterday's book", "Semantic cache: embedding similarity above a threshold, such as 0.92"),
             ("The reading pack photocopied once for every student", "Prompt caching: a byte-identical prefix read from cache at $0.10 per million on Sonnet 5.5, instead of $2"),
             ("Each student still writing their own homework", "With prompt caching the model still writes a fresh answer every time")],
        fig=cache_svg(),
        cap=f"A request only reaches the model if both response caches miss, and even then the long fixed prefix is cheap. The costs use the page's HR-assistant assumptions: {usd(C['d_none'])} a day falls to about {usd(C['d_sem'])}. The semantic layer saves the least and carries the most risk.",
        breaks='The librarian can see the books, while a semantic cache only sees how similar two questions look, not whether the answer really fits. The photocopy is not kept forever either: a prompt cache only matches the exact start of the prompt, costs 1.25 times the normal price to write, and is thrown away after 5 minutes without a read (or 1 hour if you pay for that).',
        line="Don't pay twice for the same work: store answers, and let the provider reuse the shared start of your prompt."),
    "8.4": dict(
        plain=["Big models are smart but cost a lot; small models are cheap and fast.",
               "Most real questions are easy, like order status or opening hours.",
               "Model routing sends each question to the cheapest model that can handle it.",
               "A cascade tries the small model first and passes the question up only if a check fails.",
               "It only saves money if you measure how often the router gets it wrong."],
        map=[("The nurse at the front desk", "The router: rules, a small classifier, or an LLM call"),
             ("Nurse practitioner, doctor, head surgeon", "Model tiers, for example Haiku 5.5, Sonnet 5.5 and Opus 5.5"),
             ("Passing a patient up when it looks worse", "A cascade escalating when the cheap answer fails a check"),
             ("Sending a hard case to the wrong room", "A misroute: a hard query answered badly by the small model")],
        fig=routing_svg(),
        cap=f"Both designs use the page's e-commerce example: 1 million requests a day, 1,500 tokens in and 200 out. All-Sonnet costs {usd(R['all_s'])} a day; the costs shown are computed from the verified prices.",
        line="Send easy questions to a cheap model and save the big one for the hard ones, then check the router's mistakes."),
    "8.5": dict(
        plain=["A model is billions of numbers called weights.",
               "Normally each weight takes 16 bits of memory.",
               "Quantization stores each weight with fewer bits, such as 8 or 4, by rounding it.",
               "The model gets much smaller and faster, and usually loses only a little quality.",
               "That is how a 7-billion-weight model runs on a laptop in this course."],
        map=[("Writing 152.3847 cm", "A 16-bit weight (bf16 or fp16)"),
             ("Writing just 152 cm", "An 8-bit or 4-bit weight: rounded to fewer levels"),
             ("Less paper for the whole class list", "Less memory: 15.2 GB at bf16 down to 4.7 GB for the Q4 file of Qwen2.5-7B"),
             ("Measuring the important heights more carefully", "Smarter methods keep scales and sensitive weights at higher precision")],
        fig=quant_svg(),
        cap="Top: the same weight in fewer bits. Bottom: memory on a 24 GB card, using the page's Qwen2.5-7B facts. Weights shrink with the bits; the KV cache for 16 chats stays the same, so the space you save becomes room for more users.",
        line="Quantization rounds a model's numbers so it fits in less memory, at a small cost in quality."),
    "8.6": dict(
        plain=["A GPU can do a huge amount of work at once.",
               "Serving one request at a time leaves most of it sitting idle.",
               "Batching runs many requests together, so one GPU serves many users.",
               "Continuous batching goes further: when one request finishes, a waiting one takes its place straight away.",
               "The trade-off: each user's answer comes out a bit slower, but far more users get served."],
        map=[("The bus seats", "Batch slots: requests decoded together in one GPU pass"),
             ("Waiting until all 40 seats are full", "Static batching: a batch runs until its longest request ends"),
             ("Kids hopping on and off at every stop", "Continuous batching: a freed slot takes the next request (vLLM does this)"),
             ("Each passenger's growing bag of notes", "The KV cache: memory per request that grows with its length")],
        fig=batching_svg(),
        cap="Each bar is one request being decoded. With static batching, short requests finish and their slots sit idle (shaded) until the longest one ends. Continuous batching fills those gaps. The schedules are computed from the illustrative lengths.",
        line="Batching keeps the GPU's seats full, and continuous batching refills a seat the moment it is free."),
    "8.7": dict(
        plain=["Every request pays for every token in it, every single time.",
               "A request is made of parts: instructions, examples, chat history, retrieved documents and the answer.",
               "A token budget means counting each part, finding the biggest one and trimming that first.",
               "Small cuts add up fast, because they repeat on millions of calls.",
               "Agents need extra care, because their history grows on every step."],
        map=[("The phone's data-usage screen", "Measuring tokens per part of the prompt"),
             ("The one app using 80% of the data", "The biggest part, often retrieved context or history"),
             ("Turning off autoplay in that app", "Summarise history, retrieve less, cap the output, cache the fixed prefix"),
             ("The monthly limit resetting", "Only per request: an agent's history keeps growing within one task")],
        fig=budget_svg(),
        cap="This is the page's 8-step agent. Each call re-sends the fixed prefix plus everything said and done in earlier steps, so input grows on every step. The totals are computed; trimming tool output and caching the prefix are the page's two fixes.",
        play=("tokenbudget", "Drag each part of the request and pick a model. The bars and the cost per request and per 1 million requests are recomputed from the list prices."),
        line="Measure where your tokens go, then cut the biggest part first."),
}


def fold_where(lessons):
    """The injector only splits 'The analogy breaks ...'. Pass-1 analogies that say 'Where it breaks: ...'
    are split here, so the break sentence is shown once, in the 'Where the picture breaks' line."""
    import re
    import lesson_shape
    shape = lesson_shape.load_data()
    for n, e in lessons.items():
        if e.get("pic") or n not in shape:
            continue
        a = shape[n]["analogy"]
        m = re.search(r"\s*Where it breaks:\s*", a)
        if m:
            tail = a[m.end():].strip()
            # an explicit breaks= in the lesson wins (review, 4 Nov 2026: 8.3 adds the prompt-cache limits)
            e["pic"], e["breaks"] = a[:m.start()].strip(), e.get("breaks") or (tail[0].upper() + tail[1:])
    return lessons


fold_where(LESSONS)
