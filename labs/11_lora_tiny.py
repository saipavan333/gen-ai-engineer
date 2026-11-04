"""Lab 11 - LoRA, for real: the parameter math for Qwen2.5-7B, then an actual LoRA fine-tune on a laptop CPU.

Lessons: 5.1-5.6 (prompt vs RAG vs fine-tune, training, data, LoRA/QLoRA, instruction tuning, evaluating a fine-tune).
Run:   python labs/11_lora_tiny.py     (about 1-2 minutes on CPU, no downloads)

Part 2 uses a TINY randomly initialised GPT-2-shaped model (toy on purpose): it lets you watch every
mechanism of LoRA - frozen base, small trainable adapter, loss falling, adapter file size, merge - in
a minute on any laptop. The same PEFT calls work unchanged on a real 7B model with a GPU.
LoRA paper: https://arxiv.org/abs/2106.09685   PEFT docs: https://huggingface.co/docs/peft
"""
import os
import tempfile

import torch
from peft import LoraConfig, get_peft_model
from transformers import GPT2Config, GPT2LMHeadModel

from common import header

torch.manual_seed(0)
torch.set_num_threads(min(4, os.cpu_count() or 1))  # small model: more threads only add contention

header("1) LoRA parameter math on the real Qwen2.5-7B config (from its config.json on Hugging Face)")
cfg = dict(hidden=3584, inter=18944, layers=28, heads=28, kv_heads=4)  # huggingface.co/Qwen/Qwen2.5-7B/raw/main/config.json
hd = cfg["hidden"] // cfg["heads"]
kv = cfg["kv_heads"] * hd
shapes = {"q_proj": (cfg["hidden"], cfg["hidden"]), "k_proj": (cfg["hidden"], kv), "v_proj": (cfg["hidden"], kv),
          "o_proj": (cfg["hidden"], cfg["hidden"]), "gate_proj": (cfg["hidden"], cfg["inter"]),
          "up_proj": (cfg["hidden"], cfg["inter"]), "down_proj": (cfg["inter"], cfg["hidden"])}
TOTAL_7B = 7.61e9  # parameter count stated on the Qwen2.5-7B model card
for r in (8, 16, 64):
    per_layer = sum(r * (a + b) for a, b in shapes.values())
    n = per_layer * cfg["layers"]
    print(f"  r={r:3d}: {n:>12,} trainable params = {100 * n / TOTAL_7B:.2f}% of 7.61B; adapter ~{n * 2 / 1e6:,.0f} MB in bf16")
print("  Each adapted matrix W (d_in x d_out) gets A (d_in x r) and B (r x d_out): r*(d_in+d_out) new params.")
print("  Memory rule of thumb: full fine-tune in mixed precision with Adam needs weights+grads+optimizer state")
print("  (many bytes per parameter); LoRA needs those only for the adapter. QLoRA also stores the frozen base in 4-bit.")

header("2) A real LoRA fine-tune on a tiny model (toy on purpose)")
VOCAB = "0123456789|"
stoi = {c: i for i, c in enumerate(VOCAB)}


def batch(direction, n=64, length=24):
    xs = []
    for _ in range(n):
        s = torch.randint(0, 10, (1,)).item()
        seq = [(s + (i if direction == "up" else -i)) % 10 for i in range(length)]
        xs.append([stoi["|"]] + seq)
    return torch.tensor(xs)


def loss_on(model, direction):
    model.eval()
    with torch.no_grad():
        x = batch(direction, 256)
        return model(input_ids=x, labels=x).loss.item()


def train(model, direction, steps, lr):
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    model.train()
    for _ in range(steps):
        x = batch(direction)
        loss = model(input_ids=x, labels=x).loss
        loss.backward(); opt.step(); opt.zero_grad()


base = GPT2LMHeadModel(GPT2Config(vocab_size=len(VOCAB), n_positions=32, n_embd=128, n_layer=4, n_head=4))
total = sum(p.numel() for p in base.parameters())
print(f"  base model: {total:,} params. Pre-training it on 'count UP' sequences (0123456789012...)")
train(base, "up", steps=300, lr=3e-3)
print(f"  base loss  count-up={loss_on(base, 'up'):.3f}   count-down={loss_on(base, 'down'):.3f}  <- it never saw 'down'")

snapshot = {k: v.clone() for k, v in base.state_dict().items()}
lcfg = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, target_modules=["c_attn", "c_proj", "c_fc"], fan_in_fan_out=True)
model = get_peft_model(base, lcfg)
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  LoRA r=8 on attention + MLP: trainable={trainable:,} of {total + trainable:,} ({100 * trainable / (total + trainable):.1f}%)")
for step in (0, 100, 200, 300):
    if step:
        train(model, "down", steps=100, lr=3e-3)
    print(f"    after {step:3d} LoRA steps: count-down loss={loss_on(model, 'down'):.3f}  count-up loss={loss_on(model, 'up'):.3f}")

changed = sum(not torch.equal(snapshot[k], v) for k, v in model.get_base_model().state_dict().items()
              if "lora" not in k and k in snapshot)
print(f"  frozen base tensors changed during LoRA training: {changed}  (expect 0)")
with model.disable_adapter():
    print(f"  adapter switched OFF: count-up loss={loss_on(model, 'up'):.3f}  count-down loss={loss_on(model, 'down'):.3f}"
          "  <- the old skill is back: forgetting lived in the adapter, not the base")
with tempfile.TemporaryDirectory() as d:
    model.save_pretrained(d)
    size = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d))
    print(f"  saved adapter: {size / 1024:.0f} KB  vs base model ~{total * 4 / 1024:.0f} KB in fp32")

with torch.no_grad():
    x = batch("down", 128)
    before = model(input_ids=x).logits
    merged = model.merge_and_unload()
    after = merged(input_ids=x).logits
print(f"  merge_and_unload: max logit difference after merging = {(before - after).abs().max().item():.2e}  (merged = same model, no adapter overhead)")
print("  Look: count-down loss falls while the base stays byte-identical. But count-up loss rose: with the adapter")
print("  on, the model forgot the old skill. That is why you eval BOTH the new task and the old ones (Lesson 5.6),")
print("  and why keeping adapters separate (swap or disable per task) is a real advantage of LoRA.")
