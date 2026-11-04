"""Lab 02 - Structured outputs: free-text prompting vs schema-constrained decoding.

Lessons: 2.1 anatomy, 2.2 few-shot, 2.4 structured output, 10.2 document AI (text half).
Run:   python labs/02_structured_output.py

The task: turn messy customer emails into a ticket the support system can store.
We compare two ways of asking for JSON over the same batch:
  A) "please reply in JSON" in the prompt, then json.loads + validate
  B) the JSON Schema passed as Ollama `format=` (constrained decoding), then validate
and finally a validate -> retry-with-the-error loop for the business rules a schema can't express.
"""
import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from common import chat, check_ollama, header, rate

check_ollama()


class Ticket(BaseModel):
    category: Literal["billing", "delivery", "refund", "technical", "other"]
    order_id: str | None = Field(description="Order id like ORD-12345 if present, else null")
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(max_length=120)


EMAILS = [
    "hiii my order ORD-55120 still not here after 9 days!!! need it for my sisters wedding on friday",
    "Charged twice for ORD-77301. Please fix asap, this is the second time.",
    "app crashes when i open the payments tab on android 15. no order involved",
    "I want my money back for ORD-10442, the mixer jar arrived cracked",
    "Just wanted to say the delivery guy was very polite. thanks!",
    "where is my refund?? ORD-90011 returned 3 weeks ago. also your chat bot is useless",
    "Can you change the address on ORD-31337 to Flat 4B, Kondapur, Hyderabad before it ships",
    "pls cancel subscription and refund last month, I didn't use it",
]

# What a human agent would file (the gold labels for a content check).
GOLD = ["delivery", "billing", "technical", "refund", "other", "refund", "delivery", "refund"]

VAGUE = "Extract a support ticket from this email as JSON."

SYSTEM = ("You convert customer emails into a support ticket. Reply with ONLY a JSON object with keys "
          "category (billing|delivery|refund|technical|other), order_id (string or null), "
          "urgency (low|medium|high), summary (under 120 characters).")


def try_parse(text: str):
    try:
        return Ticket.model_validate_json(text), None
    except ValidationError as e:
        return None, e.errors()[0]["msg"]
    except Exception as e:  # pragma: no cover
        return None, str(e)


header("A) Prompt-only JSON (no schema enforcement)")
ok_a = 0
for i, email in enumerate(EMAILS):
    raw = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": email}],
               num_predict=120).message.content
    t, err = try_parse(raw)
    ok_a += t is not None
    print(f"  #{i}: {'valid ' if t else 'INVALID'} {raw.strip()[:90]!r}" + (f"  <- {err}" if err else ""))

header("A2) Same, but with the vague prompt most first drafts use")
ok_a2 = 0
for i, email in enumerate(EMAILS[:4]):
    raw = chat([{"role": "system", "content": VAGUE}, {"role": "user", "content": email}],
               num_predict=160).message.content
    t, err = try_parse(raw)
    ok_a2 += t is not None
    print(f"  #{i}: {'valid ' if t else 'INVALID'} {raw.strip()[:90]!r}" + (f"  <- {err}" if err else ""))

header("B) Schema-constrained decoding (format = Ticket JSON Schema)")
ok_b, parsed = 0, []
for i, email in enumerate(EMAILS):
    raw = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": email}],
               fmt=Ticket.model_json_schema(), num_predict=120).message.content
    t, err = try_parse(raw)
    ok_b += t is not None
    parsed.append(t)
    print(f"  #{i}: {'valid ' if t else 'INVALID'} {t.model_dump() if t else raw[:80]}")

header("C) Schema-valid is not business-valid: validate rules, retry with the error")


def business_rules(t: Ticket, email: str):
    """Rules a JSON Schema cannot express. Returns an error string or None."""
    import re

    ids = re.findall(r"ORD-\d{5}", email)
    if ids and t.order_id != ids[0]:
        return f"order_id must be {ids[0]} (it appears in the email); you returned {t.order_id!r}"
    if not ids and t.order_id:
        return f"the email contains no order id, so order_id must be null; you returned {t.order_id!r}"
    if t.category == "refund" and "refund" not in email.lower() and "money back" not in email.lower():
        return "category refund is only allowed when the customer asks for money back"
    return None


fixed = 0
for i, (email, t) in enumerate(zip(EMAILS, parsed)):
    if t is None:
        continue
    err = business_rules(t, email)
    tries = 0
    while err and tries < 2:
        tries += 1
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": email},
                {"role": "assistant", "content": t.model_dump_json()},
                {"role": "user", "content": f"That ticket breaks a rule: {err}. Return the corrected JSON."}]
        t2, _ = try_parse(chat(msgs, fmt=Ticket.model_json_schema(), num_predict=120).message.content)
        if t2:
            t = t2
        err = business_rules(t, email)
    status = "ok" if not err else f"STILL BAD: {err}"
    if tries:
        fixed += err is None
        print(f"  #{i}: needed {tries} retry -> {status}")
    elif err:
        print(f"  #{i}: {status}")
print(f"  rule violations repaired by retry: {fixed}")

header("D) Content check against gold labels (shape-valid does not mean right)")
right = 0
for i, (t, g) in enumerate(zip(parsed, GOLD)):
    hit = t is not None and t.category == g
    right += hit
    if not hit:
        print(f"  #{i}: model said {t.category if t else None!r}, a human would file {g!r}: {EMAILS[i][:60]!r}")
print(f"  category accuracy: {right}/{len(GOLD)}")

header("Summary")
print(f"  vague-prompt valid:       {rate(ok_a2, 4)}")
print(f"  prompt-only valid:        {rate(ok_a, len(EMAILS))}")
print(f"  schema-constrained valid: {rate(ok_b, len(EMAILS))}")
print(f"  category accuracy (gold): {rate(right, len(GOLD))}")
if ok_a == ok_b:
    print("  On this model and these 8 emails a clear prompt already gives valid JSON every time, so the schema shows")
    print("  NO measurable advantage here. Its value is the guarantee on the inputs you have not tested yet.")
print("  Look: constrained decoding guarantees the SHAPE. It does not guarantee the CONTENT is right;")
print("  that is what the business-rule check + retry (and your eval set) are for.")
