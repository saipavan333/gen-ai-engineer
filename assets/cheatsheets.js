/* cheatsheets.js — dense per-track reference cards. Keyed by track number.
   Rendered by cheatsheets.html, which also links each card to its lessons. */
window.AGE_CHEATSHEETS = {
"1": [
  { h: "The generation loop", items: [
    "tokenize → embed → attention → logits → softmax → sample → append, repeated (autoregression).",
    "A model predicts the next <b>token</b>, not truth — fluent and wrong is a valid high-probability output." ] },
  { h: "Tokens & embeddings", items: [
    "Tokens are sub-word pieces (BPE); ≈4 chars/token; you pay per token.",
    "An <b>embedding</b> is meaning as a vector; similarity = <b>cosine</b> (angle between vectors)." ] },
  { h: "Sampling dial", items: [
    "<b>temperature 0</b> = deterministic (use for extraction/SQL); higher = more creative.",
    "<b>top-p</b> (nucleus) samples from the smallest set of tokens summing to p." ] },
  { h: "Limits to remember", items: [
    "No facts past the knowledge cutoff → ground with RAG.",
    "Weak at multi-step math unless it reasons step by step; facts mid-long-context get missed (“lost in the middle”)." ] }
],
"2": [
  { h: "Prompt anatomy", items: [
    "<b>role · context · task · format · guardrail</b> — each removes one class of failure.",
    "The guardrail (refusal path) is what stops confident invention." ] },
  { h: "Techniques", items: [
    "<b>Few-shot</b>: one example usually fixes format; diminishing returns after a few.",
    "<b>Chain-of-thought</b>: “think step by step” for multi-step logic; skip it for extraction/classification." ] },
  { h: "Structured output", items: [
    "Ask for JSON, then in code <b>extract the JSON substring, parse, validate the schema, retry once</b>.",
    "“Almost JSON” (preamble, single quotes, extra key) breaks a strict parser." ] },
  { h: "Anti-patterns", items: [
    "Vague quality words (“good”), negative instructions (“don’t…”), fuzzy quantities (“a few”), unmeasurable length (“short”)." ] }
],
"3": [
  { h: "Pipeline", items: [
    "ingest → chunk → embed → index (offline) · then query → retrieve → rerank → ground → generate.",
    "Retrieval quality is measured <b>separately</b> from answer quality." ] },
  { h: "Chunking & search", items: [
    "Match chunk size to answer shape; <b>overlap</b> protects facts on boundaries; then measure recall.",
    "<b>Hybrid</b> = dense (meaning) + BM25 (exact tokens), fused with <b>RRF</b>; add a cross-encoder <b>reranker</b>." ] },
  { h: "Metrics", items: [
    "<b>recall@k</b> = did the right doc reach the model? <b>faithfulness</b> = is the answer supported by it?",
    "If the doc never enters context, the model can only invent." ] },
  { h: "Indexes", items: [
    "<b>Flat</b> = exact, fine to ~10k docs. <b>HNSW</b> = approximate, ~constant time, ~97% recall at scale." ] }
],
"4": [
  { h: "The loop", items: [
    "<b>thought → action → observation</b>, repeat until it can answer.",
    "Tool calling: the model <b>requests</b> a function; <b>your code executes</b> it and returns the result." ] },
  { h: "Guards (not optional)", items: [
    "<b>step budget</b> + <b>repeat detection</b> stop runaway loops.",
    "<b>Validate tool arguments</b>; give <b>least-privilege</b> tools; keep a human on irreversible actions." ] },
  { h: "Memory", items: [
    "Short-term = the conversation context; long-term = a store/database.",
    "Nothing persists between calls — you resend history each turn." ] },
  { h: "Interop", items: [ "<b>MCP</b> is an open protocol for exposing tools and data to models uniformly." ] }
],
"5": [
  { h: "Which knob?", items: [
    "Order by cost & reversibility: <b>prompt → RAG → fine-tune</b>. Move right only after the cheaper option measurably fails.",
    "Fine-tuning teaches <b>form</b> (tone, format), not <b>facts</b> (facts = RAG)." ] },
  { h: "LoRA / QLoRA", items: [
    "<b>LoRA</b>: freeze the base, train two small matrices; <1% of weights; ship a few-MB adapter, roll back by deleting it.",
    "<b>QLoRA</b>: LoRA on a 4-bit quantized base — fits a single small GPU." ] },
  { h: "Stages & pitfalls", items: [
    "<b>SFT</b> (instruction tuning) then <b>preference tuning</b> (RLHF / DPO).",
    "<b>Overfitting</b>: train loss ↓ but validation loss ↑ → early-stop, more/diverse data." ] }
],
"6": [
  { h: "Foundations", items: [
    "A <b>golden set</b> is fixed, human-labeled cases with known-good answers.",
    "<b>Gate per-case, not on the average</b> — an average hides the refusal that just broke." ] },
  { h: "Judges & types", items: [
    "<b>LLM-as-judge</b>: validate it against humans with <b>Cohen’s κ</b> (chance-corrected) before trusting scores.",
    "<b>Offline</b> evals (CI, regression shield) vs <b>online</b> evals (drift, reality check) — they feed each other." ] },
  { h: "Metrics", items: [ "faithfulness · answer relevance · context precision/recall; fix the seed and run the whole set before declaring a winner." ] }
],
"7": [
  { h: "Threat model", items: [
    "Both input and output are <b>untrusted</b>; the <b>trust boundary</b> is where untrusted data meets your code.",
    "<b>Injection</b>: direct (typed input) or <b>indirect</b> (hidden in retrieved content)." ] },
  { h: "Defense in depth", items: [
    "filter → instruction hierarchy → <b>least privilege</b> → output validation → human approval.",
    "Persuasion layers (filter, hierarchy) are bypassable; <b>structural</b> layers (least privilege, validation) hold even if the model is fooled." ] },
  { h: "Privacy & reference", items: [
    "<b>PII</b>: minimize what you send, <b>redact before the request</b> — don’t rely on the model.",
    "Map risks to the <b>OWASP Top 10 for LLM Applications</b>." ] }
],
"8": [
  { h: "Cost & latency", items: [
    "<b>Output dominates</b>: output tokens cost ~4× input and are generated serially — cap reply length first.",
    "<b>Prefill</b> (input, parallel, cheap) vs <b>decode</b> (output, serial, slow); latency is felt at <b>time-to-first-token</b> → stream." ] },
  { h: "Levers", items: [
    "<b>Caching</b>: exact / semantic / prefix. <b>Routing</b>: cheapest model that works, escalate on low confidence.",
    "<b>Quantization</b>: int8 ≈ lossless, int4 a small dip; measure on your eval set. <b>Batching</b> trades latency for throughput." ] }
],
"9": [
  { h: "Text-to-SQL safely", items: [
    "<b>Schema-ground</b> the prompt with the real tables/columns, or the model invents names.",
    "Safety lives in <b>code</b>: parse the SQL, <b>allowlist SELECT-only</b>, single statement, read-only, row limit." ] },
  { h: "Robustness", items: [
    "<b>Self-correct</b>: feed the database’s error back so the model fixes its query.",
    "<b>Safe ≠ correct</b> — the gate stops writes, but a wrong join/date needs evals and a human." ] }
],
"10": [
  { h: "Vision & audio", items: [
    "<b>VLM</b> reads image + text together; <b>CLIP</b> puts both in one shared embedding space (image search).",
    "<b>Whisper</b> = speech-to-text; multimodal RAG retrieves across modalities in a shared space." ] },
  { h: "Document AI", items: [
    "OCR → extract fields → <b>validate</b> (date trap, ranges) → <b>independent cross-check</b> → <b>route by risk</b>.",
    "A second, independent calculation beats a better reader; accuracy alone isn’t shippable." ] }
],
"11": [
  { h: "Advanced RAG", items: [
    "Query transform (rewrite/HyDE/split) · hybrid retrieve · rerank · compress context · <b>measure every stage</b>." ] },
  { h: "Advanced agents", items: [
    "Reflection/self-critique · plan-then-execute · <b>validate tool results</b> · bounded loops + budgets · an eval harness for task success." ] },
  { h: "Advanced evals", items: [
    "Validate the judge (κ) · fix the seed (temp 0) · run the whole golden set · prefer pairwise · confirm the gap beats run-to-run noise." ] }
],
"12": [
  { h: "Ship & operate", items: [
    "notebook → service → package/deploy → <b>CI for prompts & evals</b> → monitor.",
    "<b>Monitor</b>: p50/p95/p99 latency, error rate, cost/day, alert thresholds — alert on the tail, not the mean." ] },
  { h: "The flywheel", items: [
    "<b>Traces</b> record each request for debugging. monitor → find failure → fix + add to golden set → the gate blocks it forever.",
    "Ship changes behind a <b>canary</b> (guarded rollout) before going wide." ] }
],
"13": [
  { h: "Frontier", items: [
    "<b>Reasoning models</b> spend <b>test-time compute</b> (sample, self-check) — accuracy rises then plateaus while cost climbs.",
    "<b>Open-weight</b> (control, privacy, predictable cost) vs <b>closed</b> (peak capability, no infra) — use-case dependent." ] },
  { h: "Stay current", items: [
    "Two layers: <b>durable fundamentals</b> (invest deeply) vs <b>churning specifics</b> (look up when needed).",
    "New model? Ask: what capability, what cost/latency, how do I measure it on <b>my</b> data, does it change my architecture?" ] },
  { h: "Responsible AI", items: [
    "<b>Disaggregate</b> accuracy by group with matched pairs; <b>gate on the disparity</b>, not the average.",
    "Risk-based governance: human oversight for consequential decisions; document with a <b>model card</b>." ] }
]
};
