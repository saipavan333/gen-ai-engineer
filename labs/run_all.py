"""Run the labs and record their output in labs/outputs/<lab>.txt.

    python labs/run_all.py                 # every lab, in order (about 40-60 minutes on a laptop GPU)
    python labs/run_all.py 03 06           # only labs whose name starts with 03 or 06
"""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABS = sorted(p for p in HERE.glob("[0-9][0-9]_*.py")) + [HERE / "05_mcp" / "client_agent.py"]
LABS = sorted(LABS, key=lambda p: p.parent.name if p.parent != HERE else p.name)


def name_of(p: Path) -> str:
    return "05_mcp" if p.parent.name == "05_mcp" else p.stem


def main():
    wanted = sys.argv[1:]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", TRANSFORMERS_VERBOSITY="error")
    (HERE / "outputs").mkdir(exist_ok=True)
    results = []
    for p in LABS:
        n = name_of(p)
        if wanted and not any(n.startswith(w) for w in wanted):
            continue
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, str(p)], cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8")
        out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "Loading weights" not in l and "Warning" not in l)
        (HERE / "outputs" / f"{n}.txt").write_text(out + "\n", encoding="utf-8")
        results.append((n, r.returncode, time.perf_counter() - t0))
        print(f"{'PASS' if r.returncode == 0 else 'FAIL'}  {n:28s} exit={r.returncode}  {time.perf_counter() - t0:6.0f}s", flush=True)
    bad = [n for n, rc, _ in results if rc]
    print(f"\n{len(results) - len(bad)}/{len(results)} labs exited 0" + (f"; failed: {bad}" if bad else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
