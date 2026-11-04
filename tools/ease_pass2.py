"""Pass 2 ("simple first, then deep"): inject a plain-English opening, an everyday picture with a
part-by-part map, a themed inline-SVG mechanism diagram, an optional interactive, a "Going deeper"
divider and an "In one line" recap into lesson pages.

Source of truth: tools/ease/tNN.py (one module per curriculum section; LESSONS = {"1.2": {...}}).
Owned regions (rewritten on every run, idempotent; everything else is left alone):
  <!-- ease:top:start --> ... <!-- ease:top:end -->     right after the page's <h1>
  <!-- ease:line:start --> ... <!-- ease:line:end -->   just before </main>
  <!-- ease:js:start --> ... <!-- ease:js:end -->       just before </body> (legible.js always, plus the play scripts)
The pass-1 "School-kid picture" box (shape:analogy region) is folded into the Everyday picture,
so the analogy is not shown twice. tools/lesson_shape.py keeps it folded on reruns.

Usage:  python tools/ease_pass2.py --tracks 1,2      (writes those sections' pages)
        python tools/ease_pass2.py                   (all modules present)
        python tools/ease_pass2.py --check           (reports, writes nothing)
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lesson_shape  # noqa: E402  (page_map, load_data)

FOLD = "  <!-- analogy folded into the Everyday picture at the top of this page (pass 2, tools/ease_pass2.py) -->\n"
JS_VER = "1"


def region(name, body):
    return f"\n<!-- ease:{name}:start -->\n{body}<!-- ease:{name}:end -->\n"


def strip(s: str) -> str:
    return re.sub(r"\n<!-- ease:(\w+):start -->\n.*?<!-- ease:\1:end -->\n", "", s, flags=re.S)


def split_breaks(pic: str):
    m = re.search(r"\s*(?:The (?:analogy|picture) breaks (?:because|when|where|down)?|Where it breaks:)\s*", pic)
    if not m:
        return pic, None
    tail = pic[m.end():].strip()
    return pic[:m.start()].strip(), tail[0].upper() + tail[1:] if tail else None


def render_top(n, e, shape):
    pic, breaks = e.get("pic"), e.get("breaks")
    if not pic:
        if n not in shape:
            raise SystemExit(f"{n}: no 'pic' and no pass-1 analogy to fold in")
        pic, b0 = split_breaks(shape[n]["analogy"])
        breaks = breaks or b0
    if not breaks:
        raise SystemExit(f"{n}: the analogy must say where it breaks")
    for k in ("plain", "map", "fig", "cap", "line"):
        if not e.get(k):
            raise SystemExit(f"{n}: missing '{k}'")
    plain = "".join(f"    <p>{p}</p>\n" for p in e["plain"])
    rows = "".join(f"      <tr><td>{a}</td><td>{b}</td></tr>\n" for a, b in e["map"])
    out = ['<section class="ease" aria-label="Simple first">\n',
           '  <div class="ease-start">\n    <div class="ease-label">Start here</div>\n', plain, '  </div>\n',
           '  <div class="ease-pic">\n    <div class="ease-label">Everyday picture</div>\n',
           f'    <p>{pic}</p>\n',
           '    <div class="tbl-wrap"><table class="t amap">\n      <tr><th>In the picture</th><th>In the real system</th></tr>\n',
           rows, '    </table></div>\n',
           f'    <p class="ease-breaks"><b>Where the picture breaks.</b> {breaks}</p>\n  </div>\n',
           '  <figure class="ease-fig">\n    <div class="ease-label">How it works</div>\n',
           f'    {e["fig"]}\n    <figcaption>{e["cap"]}</figcaption>\n  </figure>\n']
    if e.get("play"):
        name, hint = e["play"]
        out.append(f'  <div class="ez-play" data-ez-play="{name}">\n    <div class="ease-label">Try it</div>\n'
                   f'    <p class="ez-hint">{hint}</p>\n    <div class="ez-stage"></div>\n  </div>\n')
    out.append('</section>\n<h2 class="deeper-h" id="going-deeper">Going deeper</h2>\n')
    return "".join(out)


def inject(s, n, e, shape, track):
    s = strip(s)
    h1 = s.index("</h1>") + len("</h1>")
    s = s[:h1] + region("top", render_top(n, e, shape)) + s[h1:]
    me = s.rindex("</main>")
    s = s[:me] + region("line", f'  <p class="ease-line"><b>In one line:</b> {e["line"]}</p>\n') + s[me:]
    # every lesson loads the phone-legibility pass (review, 4 Nov 2026); plays add their core + module
    js = (f'<script src="../assets/ease/diagram-fonts.js?v={JS_VER}"></script>\n'
          f'<script src="../assets/ease/legible.js?v={JS_VER}"></script>\n')
    if e.get("play"):
        js += (f'<script src="../assets/ease/ease.js?v={JS_VER}"></script>\n'
               f'<script src="../assets/ease/play-t{track:02d}.js?v={JS_VER}"></script>\n')
    be = s.rindex("</body>")
    s = s[:be] + region("js", js) + s[be:]
    # fold the pass-1 analogy box
    s = re.sub(r"(<!-- shape:analogy:start -->\n).*?(<!-- shape:analogy:end -->)", lambda m: m.group(1) + FOLD + m.group(2), s, flags=re.S)
    return s


def main():
    check = "--check" in sys.argv
    tracks = None
    if "--tracks" in sys.argv:
        tracks = [int(x) for x in sys.argv[sys.argv.index("--tracks") + 1].split(",")]
    mods = sorted(p.stem for p in (ROOT / "tools" / "ease").glob("t[0-9][0-9].py"))
    if tracks is not None:
        mods = [m for m in mods if int(m[1:]) in tracks]
    pages, shape = lesson_shape.page_map(), lesson_shape.load_data()
    count = 0
    for m in mods:
        mod = importlib.import_module(f"ease.{m}")
        track = int(m[1:])
        for n, e in mod.LESSONS.items():
            if n.split(".")[0] != str(track):
                raise SystemExit(f"{n} is in module {m}")
            p = pages[n]
            old = p.read_text(encoding="utf-8")
            new = inject(old, n, e, shape, track)
            count += 1
            if check:
                print(f"{n:6s} {p.relative_to(ROOT)}  {'would change' if new != old else 'unchanged'}")
            elif new != old:
                p.write_text(new, encoding="utf-8", newline="\n")
                print(f"{n:6s} {p.relative_to(ROOT)} updated")
    print(f"{count} lessons processed")


if __name__ == "__main__":
    main()
