"""Lab 12 - Test-time compute: buy accuracy with more samples (self-consistency), and see what it costs.

Lessons: 13.1 reasoning models, 2.3 chain-of-thought.
Run:   python labs/12_self_consistency.py    (about 40 local LLM calls)

Self-consistency (Wang et al., 2022, arXiv 2203.11171): sample several reasoning chains at temperature > 0,
then majority-vote the final answers. Reasoning models do a learned version of "think longer";
this lab makes the trade - accuracy vs tokens - visible on a model you can run yourself.
"""
import re
from collections import Counter

from common import chat, check_ollama, header

check_ollama()

PROBLEMS = [  # word problems with checked integer answers
    ("A shop sells pens at Rs 12 each or a box of 10 for Rs 100. Ravi needs 34 pens. What is the least he can pay in rupees?", 348),
    ("A train leaves at 9:40 and arrives at 13:15. How many minutes is the journey?", 215),
    ("Meera saves Rs 250 a week. After how many weeks will she first have more than Rs 4,000?", 17),
    ("A tank holds 1,200 litres. It is 35% full. How many litres must be added to make it 80% full?", 540),
    ("Three friends split a bill of Rs 1,845 with a 10% tip added on top, equally. How much does each pay in rupees?", 676.5),
]
SYSTEM = "Solve the problem. Think step by step briefly, then end with a final line exactly like: ANSWER: <number>"


def final_number(text):
    m = re.findall(r"ANSWER:\s*(?:Rs\.?\s*)?(-?[\d,]*\.?\d+)", text)
    return float(m[-1].replace(",", "")) if m else None


N_MAX = 7
samples = {}
tokens = {}
header(f"1) Sample {N_MAX} chains per problem at temperature 0.8 (different seeds)")
for i, (q, gold) in enumerate(PROBLEMS):
    outs, toks = [], 0
    for s in range(N_MAX):
        r = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}], temperature=0.8, seed=100 + s, num_predict=260)
        outs.append(final_number(r.message.content))
        toks += r.eval_count
    samples[i], tokens[i] = outs, toks
    print(f"  P{i + 1} gold={gold:<6} answers={outs}")

header("2) Accuracy vs number of samples (majority vote over the first N)")
for n in (1, 3, 5, 7):
    correct = 0
    for i, (_, gold) in enumerate(PROBLEMS):
        votes = Counter(a for a in samples[i][:n] if a is not None)
        top = votes.most_common(1)[0][0] if votes else None
        correct += top is not None and abs(top - gold) < 1e-6
    avg_tokens = sum(tokens.values()) / len(PROBLEMS) / N_MAX * n
    print(f"  N={n}: accuracy {correct}/{len(PROBLEMS)}   ~{avg_tokens:,.0f} output tokens per problem")
print("  Look: more samples cost tokens linearly; accuracy gains are bumpy and flatten out. A vote only helps")
print("  when the model is right more often than any single wrong answer. Measure the curve on YOUR task before")
print("  paying for N=7 (or for a reasoning model's long thinking) in production.")
