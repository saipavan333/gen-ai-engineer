"""Lab 06 - Evals you can trust: retrieval metrics, LLM-as-judge (and its bias), a regression gate.

Lessons: 6.1-6.6 (why evals, golden sets, LLM-as-judge, offline/online, tracing, regression), 3.8, 11.3.
Run:   python labs/06_evals.py    (about 40 local LLM calls; 5-10 minutes on a laptop GPU)

The golden set here has 12 questions, so every number has a wide error bar. That is deliberate:
section 5 shows you how wide, which is why real golden sets have hundreds of cases.
"""
import json
import math
import re

from pydantic import BaseModel

from common import ask, chat, check_ollama, header, rate
from raglib import GROUNDED_SYSTEM, Index, build_chunks, grounded_prompt, load_kb

check_ollama()

GOLD = [  # question, relevant doc ids, must-contain fact (None = unanswerable -> must refuse)
    ("How long do UPI refunds take?", ["ref-01"], "2 business days"),
    ("What does refund status RF-DONE mean?", ["ref-02"], "confirmed"),
    ("Is express delivery available for a sofa?", ["ship-02"], "not available"),
    ("How many days do I have to return a shirt?", ["ret-01"], "10 days"),
    ("My blender arrived broken. What should I do?", ["ret-02"], "48 hours"),
    ("I got charged two times for one order", ["pay-01"], "3 business days"),
    ("Can I get no-cost EMI on a Rs 4,000 phone?", ["pay-02"], "3,000"),
    ("How much is Plus membership?", ["sub-01"], "999"),
    ("Support called and asked for my OTP. Is that ok?", ["acc-01"], "scam"),
    ("How long do you keep my invoices after I delete my account?", ["acc-02"], "8 years"),
    ("Do you sell gift cards for Amazon?", [], None),
    ("What is the CEO's phone number?", [], None),
]
kb = load_kb()
chunks = build_chunks(kb)
idx = Index(chunks)


def docs_of(ranked):
    return [chunks[i]["doc"] for i, _ in ranked]


def metrics(ranked_docs, relevant, k):
    top = ranked_docs[:k]
    rel = set(relevant)
    recall = len(rel & set(top)) / len(rel)
    rr = next((1 / (i + 1) for i, d in enumerate(ranked_docs) if d in rel), 0.0)
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(top) if d in rel)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(len(rel), k)))
    return recall, rr, dcg / idcg


header("1) Retrieval metrics on the answerable questions (k=3)")
answerable = [g for g in GOLD if g[1]]
for name in ("dense_faiss", "lexical", "hybrid"):
    rs = [metrics(docs_of(getattr(idx, name)(q, 10)), rel, 3) for q, rel, _ in answerable]
    r, m, n = (sum(x[j] for x in rs) / len(rs) for j in range(3))
    print(f"  {name:12s} recall@3={r:.2f}  MRR={m:.2f}  nDCG@3={n:.2f}")
print("  Look: recall@k asks 'did we fetch it at all', MRR and nDCG reward putting it FIRST.")

header("2) Generate answers with two prompt versions (v1 = grounded, v2 = a 'friendlier' rewrite)")
V2_SYSTEM = "You are a warm, helpful assistant for our store. Use the context to help the customer as much as you can."
answers = {"v1": [], "v2": []}
for q, rel, fact in GOLD:
    passages = [chunks[i] for i, _ in idx.hybrid(q, 3)]
    for v, sysmsg in (("v1", GROUNDED_SYSTEM), ("v2", V2_SYSTEM)):
        answers[v].append(ask(grounded_prompt(q, passages), system=sysmsg, num_predict=110).strip())


def deterministic_checks(ans, fact):
    refused = "don't know" in ans.lower() or "do not know" in ans.lower()
    if fact is None:
        return {"correct": refused, "cited": True}
    return {"correct": fact.lower() in ans.lower(), "cited": bool(re.search(r"\[[a-z]+-\d+", ans))}


header("3) Regression gate: per-case checks, not just the average")
per = {v: [deterministic_checks(a, g[2]) for a, g in zip(answers[v], GOLD)] for v in answers}
for v in per:
    acc = sum(c["correct"] for c in per[v]) / len(GOLD)
    cit = sum(c["cited"] for c in per[v]) / len(GOLD)
    print(f"  {v}: correct={acc:.0%}  cited={cit:.0%}")
regressions = []
for i, g in enumerate(GOLD):
    lost = [k for k in ("correct", "cited") if per["v1"][i][k] and not per["v2"][i][k]]
    if lost:
        regressions.append((g[0], lost, answers["v2"][i]))
print(f"  cases where v2 lost something v1 had: {len(regressions)}")
for q, lost, a in regressions[:6]:
    print(f"    - {q!r} lost {lost}")
    print(f"      v2 said: {a[:120]!r}")
print("  Look: v2 averages look 'fine' on correctness but it dropped citations almost everywhere, and on the")
print("  unanswerable questions it refused politely but not in the contract phrase the UI detects. Read the")
print("  failing cases: some are real regressions, some show your check is too brittle. Both need a decision.")
gate = "BLOCK" if regressions else "PASS"
print(f"  gate decision for shipping v2: {gate}  (any per-case regression on a must-pass case blocks)")


class Verdict(BaseModel):
    faithful: bool
    reason: str


header("4) LLM-as-judge: faithfulness of v1 answers to their retrieved context")
JUDGE = ("You are a strict grader. Given CONTEXT and ANSWER, decide if every factual claim in the ANSWER is "
         "supported by the CONTEXT. A refusal is faithful. Reply as JSON.")
agree = 0
for (q, rel, fact), ans, chk in zip(GOLD, answers["v1"], per["v1"]):
    passages = [chunks[i] for i, _ in idx.hybrid(q, 3)]
    ctx = "\n".join(p["text"] for p in passages)
    v = Verdict.model_validate_json(chat([{"role": "system", "content": JUDGE},
                                          {"role": "user", "content": f"CONTEXT:\n{ctx}\n\nANSWER:\n{ans}"}],
                                         fmt=Verdict.model_json_schema(), num_predict=120).message.content)
    agree += v.faithful == chk["correct"]
print(f"  judge 'faithful' agrees with the deterministic fact check on {agree}/{len(GOLD)} cases")
print("  Look: faithful != correct. An answer can be faithful to the WRONG passage. Calibrate any judge")
print("  against human labels before you trust it (report agreement and Cohen's kappa, not vibes).")

header("5) Judge position bias: same pair, swapped order")


class Pick(BaseModel):
    better: str  # "A" or "B"


PAIRS = [  # (question, good answer, subtly wrong answer)
    ("How long do card refunds take?", "Card refunds take 5 to 7 business days [ref-01].", "Card refunds take 2 business days [ref-01]."),
    ("Return window for electronics?", "Electronics have a 7 day replacement-only window [ret-01].", "Electronics can be returned within 10 days [ret-01]."),
    ("Express shipping price?", "Express shipping costs Rs 99 [ship-02].", "Express shipping costs Rs 49 [ship-02]."),
    ("When is standard shipping free?", "On orders over Rs 499 [ship-01].", "On orders over Rs 999 [ship-01]."),
    ("Duplicate charge reversal time?", "Within 3 business days [pay-01].", "Within 7 business days [pay-01]."),
]
PJ = "Pick the better, more accurate answer to the question. Reply JSON {\"better\": \"A\" or \"B\"}."
consistent = correct_both = 0
for q, good, bad in PAIRS:
    picks = []
    for a, b in ((good, bad), (bad, good)):
        p = Pick.model_validate_json(chat([{"role": "system", "content": PJ},
                                           {"role": "user", "content": f"Question: {q}\nA: {a}\nB: {b}"}],
                                          fmt=Pick.model_json_schema(), num_predict=20).message.content).better
        picks.append(p)
    good_first, good_second = picks[0] == "A", picks[1] == "B"
    consistent += good_first == good_second
    correct_both += good_first and good_second
    print(f"  {q:35s} order1 picked {picks[0]}, order2 picked {picks[1]}  -> {'consistent' if good_first == good_second else 'FLIPPED'}")
print(f"  consistent verdicts: {rate(consistent, len(PAIRS))}   correct in both orders: {rate(correct_both, len(PAIRS))}")
print("  n=5 pairs is a demo, not a measurement of this judge's bias: the intervals span most of 0-100%.")
print("  Look: with no reference passage in the judge prompt, the judge has to guess which number is right.")
print("  Always judge both orders and count a win only when both agree; give the judge the reference.")

header("6) How wide is the error bar on 12 cases?")
p = sum(c["correct"] for c in per["v1"]) / len(GOLD)
k1 = sum(c["correct"] for c in per["v1"])
print(f"  v1 accuracy {rate(k1, len(GOLD))}  (Wilson interval)")
print("  At n=400 the same accuracy would be roughly +/- " + (f"{1.96 * math.sqrt(p * (1 - p) / 400):.1%}" if 0 < p < 1 else "n/a"))
print(json.dumps({"v1_correct": round(p, 3), "regressions": len(regressions), "judge_consistent": consistent}))
