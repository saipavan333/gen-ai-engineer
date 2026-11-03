"""Open pages in headless Chrome and check: console errors, that app.js ran, quiz count, and local links.

    python tools/check_pages.py                     # pages changed vs main (git diff) + new pages
    python tools/check_pages.py track17/*.html      # specific pages
Writes tools/check-report.json. Needs Chrome or Edge installed (no downloads).
"""
import glob
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
BROWSER = next((b for b in BROWSERS if os.path.exists(b)), None)
PROFILE = tempfile.mkdtemp(prefix="pagecheck-")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.links.append(v)


def changed_pages():
    out = subprocess.run(["git", "diff", "--name-only", "main"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    new = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    return sorted({p for p in out + new if p.endswith(".html")})


def check(rel):
    path = ROOT / rel
    r = subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={PROFILE}/w{threading.get_ident()}",
                        "--enable-logging=stderr", "--v=0", "--virtual-time-budget=6000", "--dump-dom", path.as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    dom = r.stdout
    console = [m.group(1) for m in re.finditer(r"INFO:CONSOLE[^\]]*\] \"(.*?)\", source", r.stderr)]
    errors = [c for c in console if re.search(r"Uncaught|Error|Failed|404|undefined is not", c)]
    p = Links(); p.feed(path.read_text(encoding="utf-8"))
    broken = []
    for href in p.links:
        u = urlparse(href)
        if u.scheme in ("http", "https", "mailto", "data", "javascript") or href.startswith("#"):
            continue
        target = (path.parent / unquote(u.path)).resolve()
        if u.path and not target.exists():
            broken.append(href)
    return {"page": rel, "console_errors": errors, "console_all": len(console),
            "app_ran": ("quiz-result" in dom) or ("site-header" in dom), "quizzes": len(re.findall(r'class="quiz(?: [^"]*)?"', dom)),
            "broken_local_links": broken, "dom_bytes": len(dom)}


def main():
    pages = [str(Path(a).as_posix()) for g in sys.argv[1:] for a in glob.glob(g, root_dir=ROOT)] if sys.argv[1:] else changed_pages()
    if not BROWSER:
        sys.exit("no Chrome/Edge found")
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(check, pages))
    bad = [r for r in res if r["console_errors"] or r["broken_local_links"] or not r["app_ran"]]
    for r in res:
        flag = "OK  " if r not in bad else "FAIL"
        print(f"{flag} {r['page']:45s} quizzes~{r['quizzes']:2d} console={r['console_all']} errors={len(r['console_errors'])} broken={r['broken_local_links']}")
        for e in r["console_errors"]:
            print("       ", e[:200])
    shutil.rmtree(PROFILE, ignore_errors=True)  # one small profile per worker, removed when done
    (ROOT / "tools" / "check-report.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n{len(res) - len(bad)}/{len(res)} pages clean")


if __name__ == "__main__":
    main()
