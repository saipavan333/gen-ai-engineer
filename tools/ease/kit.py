"""Tiny inline-SVG kit for the pass-2 "simple first" diagrams.

Everything is themed through CSS classes defined in assets/styles.css (section "pass 2"),
which resolve to the course's CSS variables, so the pictures follow every theme preset.
No fixed pixel widths: every <svg> has a viewBox and width:100% (class ez-svg).

Layout helpers return HTML strings. Most return TWO svgs: a wide one (shown above 600 px)
and a tall one (shown on phones), so text stays readable at 390 px.

Tones: b neutral, a accent, c concept (blue), g good (green), k key (amber), w warn (red),
p practice (violet), d deep (teal).
"""
from __future__ import annotations

import html as _html

CH = {15: 8.0, 14: 7.5, 13: 7.0, 12: 6.5, 16: 8.6, 17: 9.1, 18: 9.6}  # rough avg glyph width (px) per font size
BOLD = 1.07


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


def wrap(text: str, width_px: float, size: int = 15, bold: bool = False) -> list[str]:
    """Greedy word wrap by estimated glyph width. '\n' forces a break."""
    cw = CH.get(size, size * 0.53) * (BOLD if bold else 1)
    maxc = max(4, int(width_px / cw))
    out = []
    for para in str(text).split("\n"):
        line = ""
        for w in para.split():
            if not line:
                line = w
            elif len(line) + 1 + len(w) <= maxc:
                line += " " + w
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def text(x, y, s, cls="", anchor="middle", size=None) -> str:
    st = f' style="font-size:{size}px"' if size else ""
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}"{c}{st}>{esc(s)}</text>'


def lines(x, y, rows, cls="", anchor="middle", size=15, lh=None) -> str:
    lh = lh or round(size * 1.3)
    return "".join(text(x, y + i * lh, r, cls, anchor, size if size != 15 else None) for i, r in enumerate(rows))


def arrow(x1, y1, x2, y2, cls="", head=9) -> str:
    """Straight arrow with an explicit polygon head (no marker ids, so no clashes)."""
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = head * 0.55 * math.sin(ang), -head * 0.55 * math.cos(ang)
    return (f'<line x1="{x1:g}" y1="{y1:g}" x2="{bx:g}" y2="{by:g}" class="ln {cls}"/>'
            f'<polygon points="{x2:g},{y2:g} {bx+px:g},{by+py:g} {bx-px:g},{by-py:g}" class="hd {cls}"/>')


def path_arrow(points, cls="", head=9) -> str:
    """Polyline through points, arrow head on the last segment."""
    import math
    (x1, y1), (x2, y2) = points[-2], points[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    px, py = head * 0.55 * math.sin(ang), -head * 0.55 * math.cos(ang)
    pts = " ".join(f"{x:g},{y:g}" for x, y in points[:-1]) + f" {bx:g},{by:g}"
    return (f'<polyline points="{pts}" class="ln {cls}"/>'
            f'<polygon points="{x2:g},{y2:g} {bx+px:g},{by+py:g} {bx-px:g},{by-py:g}" class="hd {cls}"/>')


def rect(x, y, w, h, tone="b", rx=10, extra="") -> str:
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" class="bx tn-{tone}" {extra}/>'


def box(x, y, w, title, sub="", tone="b", h=None, size=15, num=None) -> tuple[str, float]:
    """A labelled box. Returns (svg, height). Title bold, sub smaller; both wrapped to the width."""
    tl = wrap(title, w - 18, size, bold=True)
    sl = wrap(sub, w - 18, size - 2) if sub else []
    lh, slh = round(size * 1.3), round((size - 2) * 1.32)
    need = 16 + len(tl) * lh + (6 + len(sl) * slh if sl else 0) + 6
    h = max(h or 0, need)
    body_h = len(tl) * lh + (6 + len(sl) * slh if sl else 0)
    y0 = y + (h - body_h) / 2 + size * 0.95
    out = rect(x, y, w, h, tone)
    out += f'<g class="vzb">' + lines(x + w / 2, y0, tl, "b", size=size, lh=lh)
    if sl:
        out += lines(x + w / 2, y0 + len(tl) * lh + 6, sl, "s", size=size - 2, lh=slh)
    out += "</g>"
    if num is not None:
        out += f'<circle cx="{x+2:g}" cy="{y+2:g}" r="11" class="badge"/>' + text(x + 2, y + 6.5, num, "badge-t")
    return out, h


def box_h(w, title, sub="", size=15) -> float:
    tl = wrap(title, w - 18, size, bold=True)
    sl = wrap(sub, w - 18, size - 2) if sub else []
    lh, slh = round(size * 1.3), round((size - 2) * 1.32)
    return 16 + len(tl) * lh + (6 + len(sl) * slh if sl else 0) + 6


def svg(w, h, body, label, cls="") -> str:
    return (f'<svg class="ez-svg {cls}" viewBox="0 0 {w:g} {h:g}" role="img" aria-label="{esc(label)}" '
            f'preserveAspectRatio="xMidYMid meet">{body}</svg>')


def _norm(steps):
    out = []
    for s in steps:
        if isinstance(s, dict):
            out.append((s.get("t", ""), s.get("s", ""), s.get("tone", "b")))
        else:
            t, sub, *rest = list(s) + [""]
            out.append((t, sub, rest[0] if rest and rest[0] else "b"))
    return out


def flow(steps, label, loop=None, numbered=True, tones=None) -> str:
    """Steps in order, left to right (wide) or top to bottom (tall).
    steps: [(title, sub, tone?)]; loop: (from_idx, to_idx, text) draws a back arrow."""
    st = _norm(steps)
    n = len(st)
    # ---- wide
    W, pad = 760, 14
    G = 46 if n <= 4 else 34
    bw = (W - 2 * pad - (n - 1) * G) / n
    top = 22
    h = max(box_h(bw, t, s) for t, s, _ in st)
    body = ""
    for i, (t, s, tone) in enumerate(st):
        x = pad + i * (bw + G)
        b, _ = box(x, top, bw, t, s, tone, h=h, num=(i + 1) if numbered else None)
        body += b
        if i < n - 1:
            body += arrow(x + bw + 4, top + h / 2, x + bw + G - 4, top + h / 2)
    H = top + h + 16
    if loop:
        a, b2, lt = loop
        xa = pad + a * (bw + G) + bw / 2
        xb = pad + b2 * (bw + G) + bw / 2
        yl = top + h + 30
        body += path_arrow([(xa, top + h + 2), (xa, yl), (xb, yl), (xb, top + h + 4)], "ac")
        tl = wrap(lt, abs(xa - xb) - 20 if abs(xa - xb) > 120 else 300, 14)
        body += lines((xa + xb) / 2, yl + 20, tl, "s ac-t", size=14)
        H = yl + 20 + len(tl) * 18 + 4
    wide = svg(W, H, body, label, "ez-wide")
    # ---- tall
    W2 = 360
    lane = 56 if loop else 0
    bx, bw2, G2 = 12, W2 - 24 - lane, 34
    y = 16
    body = ""
    ys = []
    for i, (t, s, tone) in enumerate(st):
        hh = box_h(bw2, t, s)
        b, hh = box(bx, y, bw2, t, s, tone, num=(i + 1) if numbered else None)
        body += b
        ys.append((y, hh))
        if i < n - 1:
            body += arrow(bx + bw2 / 2, y + hh + 3, bx + bw2 / 2, y + hh + G2 - 3)
        y += hh + G2
    H2 = y - G2 + 14
    if loop:
        a, b2, lt = loop
        ya = ys[a][0] + ys[a][1] / 2
        yb = ys[b2][0] + ys[b2][1] / 2
        xr = bx + bw2 + lane - 22
        body += path_arrow([(bx + bw2 + 2, ya), (xr, ya), (xr, yb), (bx + bw2 + 4, yb)], "ac")
        cy = (ya + yb) / 2
        body += (f'<text x="{xr+14:g}" y="{cy:g}" text-anchor="middle" class="s ac-t" '
                 f'transform="rotate(-90 {xr+14:g} {cy:g})">{esc(lt)}</text>')
    tall = svg(W2, H2, body, label, "ez-tall")
    return wide + tall


def fan(src, outs, label, out_label="") -> str:
    """One source box feeding several outputs (a router, a fan-out, a split)."""
    s = _norm([src])[0]
    o = _norm(outs)
    # wide: source left, outputs stacked right
    W = 760
    sw, ow = 230, 300
    ohs = [box_h(ow, t, d) for t, d, _ in o]
    gap = 12
    tot = sum(ohs) + gap * (len(o) - 1)
    sh = box_h(sw, s[0], s[1])
    top = 18
    H = top + max(tot, sh) + 18
    sy = top + (max(tot, sh) - sh) / 2
    body, _ = box(20, sy, sw, s[0], s[1], s[2], h=sh)
    y = top + (max(tot, sh) - tot) / 2
    for (t, d, tone), hh in zip(o, ohs):
        b, _ = box(W - 20 - ow, y, ow, t, d, tone, h=hh)
        body += b + path_arrow([(20 + sw + 2, sy + sh / 2), (20 + sw + 60, sy + sh / 2), (W - 20 - ow - 60, y + hh / 2), (W - 20 - ow - 3, y + hh / 2)])
        y += hh + gap
    if out_label:
        body += text(W / 2 + 10, 14, out_label, "s m")
    wide = svg(W, H, body, label, "ez-wide")
    # tall: source top, outputs below off a spine
    W2 = 360
    sh2 = box_h(W2 - 24, s[0], s[1])
    body, _ = box(12, 14, W2 - 24, s[0], s[1], s[2], h=sh2)
    y = 14 + sh2 + 34
    spine_x = 26
    body += f'<line x1="{spine_x}" y1="{14+sh2:g}" x2="{spine_x}" y2="{y-34+14:g}" class="ln"/>'
    last_mid = 0
    for t, d, tone in o:
        hh = box_h(W2 - 70, t, d)
        b, _ = box(56, y, W2 - 68, t, d, tone, h=hh)
        body += b + arrow(spine_x, y + hh / 2, 53, y + hh / 2)
        last_mid = y + hh / 2
        y += hh + 14
    body += f'<line x1="{spine_x}" y1="{14+sh2:g}" x2="{spine_x}" y2="{last_mid:g}" class="ln"/>'
    tall = svg(W2, y + 4, body, label, "ez-tall")
    return wide + tall


def stack(layers, label, enter="request", leave="safe answer", blocked=None) -> str:
    """Layers a request passes through, top to bottom (defence in depth, a network stack).
    blocked: optional {layer_index: 'what this layer stops'} shown at the side."""
    blocked = blocked or {}
    out = []
    for W, cls, side in ((760, "ez-wide", 250), (360, "ez-tall", 0)):
        L = _norm(layers)
        bw = W - 40 - side
        y = 40
        body = text(20 + bw / 2, 22, "↓ " + enter, "s m")
        for i, (t, d, tone) in enumerate(L):
            hh = box_h(bw, t, d)
            b, hh = box(20, y, bw, t, d, tone, h=hh, num=i + 1)
            body += b
            if side and i in blocked:
                body += arrow(20 + bw + 4, y + hh / 2, 20 + bw + 40, y + hh / 2, "wn")
                bl = wrap(blocked[i], side - 50, 13)
                body += lines(20 + bw + 48, y + hh / 2 - (len(bl) - 1) * 8 + 4, bl, "s", anchor="start", size=13, lh=16)
            if i < len(L) - 1:
                body += arrow(20 + bw / 2, y + hh + 2, 20 + bw / 2, y + hh + 24)
            y += hh + 26
        body += text(20 + bw / 2, y + 6, "↓ " + leave, "s m")
        out.append(svg(W, y + 18, body, label, cls))
    return "".join(out)


def compare(left, right, label, verdict="") -> str:
    """Before/after or option A vs option B. left/right = (title, [bullets], tone)."""
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        cols = 2 if W > 400 else 1
        cw = (W - 40 - (cols - 1) * 24) / cols
        blocks = []
        for title, items, tone in (left, right):
            rows = []
            for it in items:
                ws = wrap(it, cw - 40, 14)
                rows.append(ws)
            h = 46 + sum(len(r) * 18 + 8 for r in rows) + 8
            blocks.append((title, rows, tone, h))
        body = ""
        if cols == 2:
            h = max(b[3] for b in blocks)
            for i, (title, rows, tone, _) in enumerate(blocks):
                x = 20 + i * (cw + 24)
                body += _col(x, 14, cw, h, title, rows, tone)
            y = 14 + h
        else:
            y = 14
            for i, (title, rows, tone, h) in enumerate(blocks):
                body += _col(20, y, cw, h, title, rows, tone)
                y += h + (34 if i == 0 else 0)
                if i == 0:
                    body += text(W / 2, y - 12, "vs", "b m")
        if verdict:
            vl = wrap(verdict, W - 60, 14)
            body += lines(W / 2, y + 26, vl, "s", size=14, lh=18)
            y += 26 + len(vl) * 18
        out.append(svg(W, y + 10, body, label, cls))
    return "".join(out)


def _col(x, y, w, h, title, rows, tone):
    body = rect(x, y, w, h, tone)
    body += text(x + w / 2, y + 28, title, "b")
    yy = y + 54
    for r in rows:
        body += f'<circle cx="{x+20:g}" cy="{yy-5:g}" r="3" class="dot tn-{tone}"/>'
        body += lines(x + 32, yy, r, "", anchor="start", size=14, lh=18)
        yy += len(r) * 18 + 8
    return body


def raw(wide: str, tall: str | None = None) -> str:
    """Hand-drawn diagram(s). Pass full <svg> strings built with svg(); if only one, it serves both widths."""
    if tall is None:
        return wide.replace('class="ez-svg', 'class="ez-svg ez-one', 1)
    return wide + tall
