"""Inject the STANDARD.md lesson-shape blocks into lesson pages as static HTML.

Source of truth: tools/shape-data/*.json (one entry per lesson number).
Each lesson gets marked regions that this script owns and rewrites on every run (idempotent):
  <!-- shape:analogy:start --> ... <!-- shape:analogy:end -->   after the first Concept box
  <!-- shape:scale:start -->   ... <!-- shape:scale:end -->     after the first Worked-example box
  <!-- shape:quiz:start -->    ... <!-- shape:quiz:end -->      after the last existing quiz
  <!-- shape:tail:start -->    ... <!-- shape:tail:end -->      before the closing "Next:" paragraph
Everything outside the markers is left byte-for-byte alone.

Usage:  python tools/lesson_shape.py            (writes pages)
        python tools/lesson_shape.py --check    (reports, writes nothing)
"""
from __future__ import annotations

import glob
import html
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB_FILES = {
    "01_generate_and_sample": "labs/01_generate_and_sample.py", "02_structured_output": "labs/02_structured_output.py",
    "03_rag_local": "labs/03_rag_local.py", "04_agent_tools": "labs/04_agent_tools.py",
    "05_mcp": "labs/05_mcp/client_agent.py", "06_evals": "labs/06_evals.py",
    "07_injection_exfiltration": "labs/07_injection_exfiltration.py", "08_llmops": "labs/08_llmops.py",
    "09_text_to_sql_duckdb": "labs/09_text_to_sql_duckdb.py", "10_ai_sql_udf": "labs/10_ai_sql_udf.py",
    "11_lora_tiny": "labs/11_lora_tiny.py", "12_self_consistency": "labs/12_self_consistency.py",
}
OUTPUT_NAME = {"05_mcp": "05_mcp"}


def load_data():
    data = {}
    for f in sorted(glob.glob(str(ROOT / "tools" / "shape-data" / "*.json"))):
        for e in json.loads(Path(f).read_text(encoding="utf-8")):
            if e["n"] in data:
                raise SystemExit(f"duplicate lesson {e['n']} in {f}")
            data[e["n"]] = e
    return data


def page_map():
    out = {}
    for p in glob.glob(str(ROOT / "*" / "*.html")):
        m = re.search(r'<body[^>]*data-lesson="([^"]+)"', Path(p).read_text(encoding="utf-8"))
        if m:
            out[m.group(1)] = Path(p)
    return out


def block_end(s: str, start: int) -> int:
    """Index just after the </div> that closes the <div ...> starting at `start`."""
    depth, i = 0, start
    tag = re.compile(r"<(/?)div\b[^>]*>", re.I)
    for m in tag.finditer(s, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    raise ValueError("unbalanced div")


def strip_regions(s: str) -> str:
    # exact inverse of wrap(): wrap adds "\n<start>\n ... <end>\n", so remove exactly that
    return re.sub(r"\n<!-- shape:(\w+):start -->\n.*?<!-- shape:\1:end -->\n", "", s, flags=re.S)


def lab_excerpt(lab_id: str, max_lines: int = 14) -> str:
    out = ROOT / "labs" / "outputs" / f"{OUTPUT_NAME.get(lab_id, lab_id)}.txt"
    if not out.exists():
        return ""
    lines = [l for l in out.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("=====")]
    tail = lines[-max_lines:]
    return html.escape("\n".join(tail))


def render_quiz(q, rng):
    opts = list(q["options"])
    rng.shuffle(opts)
    lis = "".join(
        f'\n      <li data-correct="{"true" if o["correct"] else "false"}"><span class="opt">{chr(65 + i)}) {o["t"]}</span>'
        f'\n        <div class="why">{o["why"]}</div></li>' for i, o in enumerate(opts))
    return f'  <div class="quiz">\n    <p class="quiz-q">{q["q"]}</p>\n    <ul class="quiz-options">{lis}\n    </ul>\n  </div>\n'


def render(e, n):
    rng = random.Random(f"shape-{n}")
    parts = {}
    parts["analogy"] = (f'  <div class="box note shape-analogy">\n    <div class="box-label">School-kid picture</div>\n'
                        f'    <p>{e["analogy"]}</p>\n  </div>\n')
    sc = e["scale"]
    parts["scale"] = (f'  <div class="box example shape-scale">\n    <div class="box-label">At real scale: {sc["title"]}</div>\n'
                      f'    {sc["html"]}\n  </div>\n')
    parts["quiz"] = "".join(render_quiz(q, rng) for q in e.get("quiz", []))
    lab = e["lab"]
    path = LAB_FILES[lab["id"]]
    exc = lab_excerpt(lab["id"])
    rel = "../" + path
    lab_html = (f'  <div class="box practice shape-lab">\n    <div class="box-label">Run it locally: <code>{path}</code></div>\n'
                f'    <p>Free and offline once set up: Ollama with <code>qwen2.5:7b</code>, plus the packages in '
                f'<a href="../labs/README.md">labs/README.md</a>. From the course folder:</p>\n'
                f'<pre><code>python {path}</code></pre>\n'
                f'    <p><strong>What to look for:</strong> {lab["look_for"]}</p>\n'
                f'    <p class="shape-smalln"><strong>Small samples:</strong> these labs use 5 to 20 cases so they run in minutes '
                f'on a laptop. Where they report a rate, they print n and a 95% Wilson interval. Read them as a demonstration '
                f'of the mechanism, not as a measured rate for your system; for that you need hundreds of cases and several seeds.</p>\n')
    if exc:
        lab_html += (f'    <details class="sol">\n      <summary><span class="chev">▸</span> Recorded output (our run, 2026-11-03, qwen2.5:7b on a laptop GPU)</summary>\n'
                     f'      <div class="sol-body"><pre><code>{exc}</code></pre>\n'
                     f'      <p>Your numbers will differ a little run to run. Full log: <a href="../labs/outputs/{OUTPUT_NAME.get(lab["id"], lab["id"])}.txt">labs/outputs</a>. Source: <a href="{rel}">{path}</a>.</p></div>\n    </details>\n')
    lab_html += "  </div>\n"
    ex = "".join(
        f'    <p><strong>{x["level"]}.</strong> {x["q"]}</p>\n'
        f'    <details class="sol">\n      <summary><span class="chev">▸</span> Solution</summary>\n'
        f'      <div class="sol-body"><p>{x["a"]}</p></div>\n    </details>\n' for x in e["exercises"])
    ex_html = f'  <div class="box practice shape-exercises">\n    <div class="box-label">Exercises: warm-up, transfer, stretch</div>\n{ex}  </div>\n'
    iv = "".join(
        f'    <p><span class="shape-lvl">{x["level"]}</span> {x["q"]}</p>\n'
        f'    <details class="sol">\n      <summary><span class="chev">▸</span> Model answer</summary>\n'
        f'      <div class="sol-body"><p>{x["a"]}</p></div>\n    </details>\n' for x in e["interview"])
    iv_html = f'  <div class="box deep shape-interview">\n    <div class="box-label">Interview questions</div>\n{iv}  </div>\n'
    src = "".join(f'      <li><a href="{html.escape(s["u"], quote=True)}" target="_blank" rel="noopener">{s["t"]}</a></li>\n' for s in e["sources"])
    src_html = (f'  <div class="box key shape-sources">\n    <div class="box-label">Sources (checked 2026-11-03)</div>\n'
                f'    <ul>\n{src}    </ul>\n  </div>\n')
    parts["tail"] = lab_html + ex_html + iv_html + src_html
    return parts


def wrap(name, body):
    return f"\n<!-- shape:{name}:start -->\n{body}<!-- shape:{name}:end -->\n"


def inject(s: str, parts: dict) -> str:
    s = strip_regions(s)
    main_end = s.index("</main>")
    # tail: before the last <p> in <main> that bridges to the next lesson, else before </main>
    last_p = s.rfind("\n  <p>", 0, main_end)
    tail_at = last_p if last_p != -1 and "Next" in s[last_p:main_end] and "</div>" not in s[last_p:main_end] else main_end
    s = s[:tail_at] + wrap("tail", parts["tail"]) + s[tail_at:]
    # quiz: after the last existing quiz block
    qs = [m.start() for m in re.finditer(r'<div class="quiz"', s)]
    if parts["quiz"]:
        if qs:
            q_end = block_end(s, qs[-1])
            s = s[:q_end] + wrap("quiz", parts["quiz"]) + s[q_end:]
        else:
            t = s.index("<!-- shape:tail:start -->")
            s = s[:t] + wrap("quiz", parts["quiz"]) + s[t:]
    # scale: after the first worked example, else before the key points / first practice box
    m = re.search(r'<div class="box example"', s)
    anchor = block_end(s, m.start()) if m else None
    if anchor is None:
        m2 = re.search(r'<div class="box (key|practice)"', s)
        anchor = m2.start() if m2 else s.index("<!-- shape:tail:start -->")
    s = s[:anchor] + wrap("scale", parts["scale"]) + s[anchor:]
    # analogy: after the first concept box, else after the lead paragraph
    m = re.search(r'<div class="box concept"', s)
    if m:
        a = block_end(s, m.start())
    else:
        lead = re.search(r'<p class="lead">.*?</p>', s, re.S)
        a = lead.end() if lead else s.index("<main")
    s = s[:a] + wrap("analogy", parts["analogy"]) + s[a:]
    return s


def main():
    check = "--check" in sys.argv
    data, pages = load_data(), page_map()
    missing = [n for n in data if n not in pages]
    if missing:
        raise SystemExit(f"no page for lessons {missing}")
    for n, e in sorted(data.items(), key=lambda kv: [int(x) for x in kv[0].split(".")]):
        if e["lab"]["id"] not in LAB_FILES:
            raise SystemExit(f"{n}: unknown lab id {e['lab']['id']}")
        p = pages[n]
        old = p.read_text(encoding="utf-8")
        new = inject(old, render(e, n))
        if check:
            print(f"{n:6s} {p.relative_to(ROOT)}  {'would change' if new != old else 'unchanged'}")
        elif new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            print(f"{n:6s} {p.relative_to(ROOT)} updated")
    print(f"{len(data)} lessons processed")


if __name__ == "__main__":
    main()
