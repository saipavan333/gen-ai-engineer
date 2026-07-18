window.CURRICULUM = {
  title: "Applied GenAI Engineer",
  sections: [
    {
      id: "start", num: "0", title: "Start Here", ready: true,
      blurb: "Get a free, zero-cost setup and the small slice of Python you actually need. Built for someone newer to coding.",
      lessons: [
        { n: "0.1", title: "How to use this course", file: "start-here/00-how-to-use.html", built: true },
        { n: "0.2", title: "Your free, no-cost toolkit", file: "start-here/01-setup.html", built: true },
        { n: "0.3", title: "The Python you'll actually use", file: "start-here/02-python-primer.html", built: true },
        { n: "0.4", title: "Python fluency: the next layer", file: "start-here/03-python-fluency.html", built: true },
        { n: "0.5", title: "Python drills", file: "start-here/04-python-drills.html", built: true }
      ]
    },
    {
      id: "t1", num: "1", title: "How LLMs Work", ready: true,
      blurb: "Open the box. Tokens, embeddings, context windows, attention, and sampling.",
      lessons: [
        { n: "1.1", title: "What is a language model?", file: "track1/01-what-is-an-llm.html", built: true },
        { n: "1.2", title: "Tokens & tokenization", file: "track1/02-tokens.html", built: true },
        { n: "1.3", title: "Embeddings: meaning as vectors", file: "track1/03-embeddings.html", built: true },
        { n: "1.4", title: "Context windows & attention", file: "track1/04-context-attention.html", built: true },
        { n: "1.5", title: "Sampling & decoding", file: "track1/05-sampling.html", built: true },
        { n: "1.6", title: "What LLMs can & can't do", file: "track1/06-capabilities-limits.html", built: true },
        { n: "1.7", title: "Interview check: How LLMs Work", file: "track1/07-interview.html", built: true },
        { n: "1.8", title: "Lab: Build a mini language model", file: "track1/lab.html", built: true },
        { n: "1.9", title: "Visual Lab: Watch a prediction happen", file: "track1/visual-lab.html", built: true }
      ]
    },
    {
      id: "t2", num: "2", title: "Prompt Engineering", ready: true,
      blurb: "Turn vague asks into reliable instructions. Few-shot, chain-of-thought, JSON output, and patterns.",
      lessons: [
        { n: "2.1", title: "Anatomy of a prompt", file: "track2/01-anatomy.html", built: true },
        { n: "2.2", title: "Few-shot prompting", file: "track2/02-few-shot.html", built: true },
        { n: "2.3", title: "Chain-of-thought & reasoning", file: "track2/03-chain-of-thought.html", built: true },
        { n: "2.4", title: "Structured output & JSON", file: "track2/04-structured-output.html", built: true },
        { n: "2.5", title: "Patterns & anti-patterns", file: "track2/05-patterns.html", built: true },
        { n: "2.6", title: "Interview check: Prompting", file: "track2/06-interview.html", built: true },
        { n: "2.7", title: "Lab: Build a prompt engine", file: "track2/lab.html", built: true }
      ]
    },
    {
      id: "t3", num: "3", title: "RAG & Vector Databases", ready: true,
      blurb: "Give a model your own documents as grounded, cited knowledge — and measure retrieval quality.",
      lessons: [
        { n: "3.1", title: "Why RAG exists", file: "track3/01-why-rag.html", built: true },
        { n: "3.2", title: "Chunking strategies", file: "track3/02-chunking.html", built: true },
        { n: "3.3", title: "Embeddings for retrieval", file: "track3/03-embeddings-retrieval.html", built: true },
        { n: "3.4", title: "Vector databases & indexes", file: "track3/04-vector-databases.html", built: true },
        { n: "3.5", title: "Retrieval & reranking", file: "track3/05-retrieval-reranking.html", built: true },
        { n: "3.6", title: "Hybrid search", file: "track3/06-hybrid-search.html", built: true },
        { n: "3.7", title: "Grounding & citations", file: "track3/07-grounding-citations.html", built: true },
        { n: "3.8", title: "Evaluating retrieval quality", file: "track3/08-evaluating-retrieval.html", built: true },
        { n: "3.9", title: "Interview check: RAG", file: "track3/09-interview.html", built: true },
        { n: "3.10", title: "Lab: Build a tiny RAG pipeline", file: "track3/lab.html", built: true }
      ]
    },
    {
      id: "t4", num: "4", title: "Agents & Tool Use", ready: true,
      blurb: "Let a model take actions: call tools, plan, remember, and use MCP — plus orchestration patterns.",
      lessons: [
        { n: "4.1", title: "From chatbot to agent", file: "track4/01-chatbot-to-agent.html", built: true },
        { n: "4.2", title: "Tool / function calling", file: "track4/02-tool-calling.html", built: true },
        { n: "4.3", title: "The agent loop (ReAct)", file: "track4/03-agent-loop.html", built: true },
        { n: "4.4", title: "Planning & decomposition", file: "track4/04-planning.html", built: true },
        { n: "4.5", title: "Memory", file: "track4/05-memory.html", built: true },
        { n: "4.6", title: "MCP (Model Context Protocol)", file: "track4/06-mcp.html", built: true },
        { n: "4.7", title: "Multi-agent & orchestration", file: "track4/07-multi-agent.html", built: true },
        { n: "4.8", title: "Failure modes & guards", file: "track4/08-failure-modes.html", built: true },
        { n: "4.9", title: "Interview check: Agents", file: "track4/09-interview.html", built: true },
        { n: "4.10", title: "Lab: Build an agent loop", file: "track4/lab.html", built: true }
      ]
    },
    {
      id: "t5", num: "5", title: "Fine-tuning & Adapters", ready: true,
      blurb: "When prompting and RAG aren't enough: LoRA/QLoRA, instruction tuning, prompt vs RAG vs fine-tune.",
      lessons: [
        { n: "5.1", title: "Prompt vs RAG vs fine-tune", file: "track5/01-prompt-rag-finetune.html", built: true },
        { n: "5.2", title: "How training actually works", file: "track5/02-how-training-works.html", built: true },
        { n: "5.3", title: "Data preparation", file: "track5/03-data-preparation.html", built: true },
        { n: "5.4", title: "LoRA & QLoRA", file: "track5/04-lora-qlora.html", built: true },
        { n: "5.5", title: "Instruction tuning", file: "track5/05-instruction-tuning.html", built: true },
        { n: "5.6", title: "Evaluating a fine-tune", file: "track5/06-evaluating-finetune.html", built: true },
        { n: "5.7", title: "Interview check: Fine-tuning", file: "track5/07-interview.html", built: true },
        { n: "5.8", title: "Lab: Prepare data & size a LoRA", file: "track5/lab.html", built: true }
      ]
    },
    {
      id: "t6", num: "6", title: "Evals & Observability", ready: true,
      blurb: "The skill that separates demos from products: measure quality, catch regressions, watch production.",
      lessons: [
        { n: "6.1", title: "Why evals decide everything", file: "track6/01-why-evals.html", built: true },
        { n: "6.2", title: "Golden sets", file: "track6/02-golden-sets.html", built: true },
        { n: "6.3", title: "LLM-as-judge", file: "track6/03-llm-as-judge.html", built: true },
        { n: "6.4", title: "Offline vs online evals", file: "track6/04-offline-online.html", built: true },
        { n: "6.5", title: "Tracing & observability", file: "track6/05-tracing-observability.html", built: true },
        { n: "6.6", title: "Regression-testing prompts", file: "track6/06-regression-testing.html", built: true },
        { n: "6.7", title: "Interview check: Evals", file: "track6/07-interview.html", built: true },
        { n: "6.8", title: "Lab: Build an eval harness", file: "track6/lab.html", built: true }
      ]
    },
    {
      id: "t7", num: "7", title: "Guardrails & Safety", ready: true,
      blurb: "Ship something you can trust: prompt injection, jailbreaks, PII, content safety, output validation.",
      lessons: [
        { n: "7.1", title: "The threat model", file: "track7/01-threat-model.html", built: true },
        { n: "7.2", title: "Prompt injection", file: "track7/02-prompt-injection.html", built: true },
        { n: "7.3", title: "Jailbreaks", file: "track7/03-jailbreaks.html", built: true },
        { n: "7.4", title: "PII & privacy", file: "track7/04-pii-privacy.html", built: true },
        { n: "7.5", title: "Content safety", file: "track7/05-content-safety.html", built: true },
        { n: "7.6", title: "Output validation", file: "track7/06-output-validation.html", built: true },
        { n: "7.7", title: "Defense in depth", file: "track7/07-defense-in-depth.html", built: true },
        { n: "7.8", title: "Interview check: Safety", file: "track7/08-interview.html", built: true },
        { n: "7.9", title: "Lab: Break a bot, then build the guard", file: "track7/lab.html", built: true }
      ]
    },
    {
      id: "t8", num: "8", title: "Serving, Latency & Cost", ready: true,
      blurb: "Make it fast and cheap: streaming, caching, model routing, quantization, batching, token budgets.",
      lessons: [
        { n: "8.1", title: "The cost & latency model", file: "track8/01-cost-latency-model.html", built: true },
        { n: "8.2", title: "Streaming", file: "track8/02-streaming.html", built: true },
        { n: "8.3", title: "Caching", file: "track8/03-caching.html", built: true },
        { n: "8.4", title: "Model routing", file: "track8/04-model-routing.html", built: true },
        { n: "8.5", title: "Quantization", file: "track8/05-quantization.html", built: true },
        { n: "8.6", title: "Batching & throughput", file: "track8/06-batching-throughput.html", built: true },
        { n: "8.7", title: "Budgeting tokens", file: "track8/07-budgeting-tokens.html", built: true },
        { n: "8.8", title: "Interview check: Serving", file: "track8/08-interview.html", built: true },
        { n: "8.9", title: "Lab: Build a cost & latency calculator", file: "track8/lab.html", built: true }
      ]
    },
    {
      id: "t13", num: "9", title: "Structured Data & Text-to-SQL", ready: true,
      blurb: "Turn plain-English questions into safe, correct database queries — the highest-leverage GenAI skill for a data engineer.",
      lessons: [
        { n: "9.1", title: "Why text-to-SQL (and where it breaks)", file: "track13/01-why-text-to-sql.html", built: true },
        { n: "9.2", title: "Schema-aware prompting", file: "track13/02-schema-aware-prompting.html", built: true },
        { n: "9.3", title: "Generating safe, correct SQL", file: "track13/03-safe-sql.html", built: true },
        { n: "9.4", title: "The self-correcting SQL agent", file: "track13/04-self-correcting-agent.html", built: true },
        { n: "9.5", title: "Interview check: Data & SQL agents", file: "track13/05-interview.html", built: true },
        { n: "9.6", title: "Lab: Build a safe text-to-SQL runner", file: "track13/lab.html", built: true }
      ]
    },
    {
      id: "t15", num: "10", title: "Multimodal AI", ready: true,
      blurb: "Give your systems eyes and ears: vision-language models, document AI, audio, and multimodal RAG.",
      lessons: [
        { n: "10.1", title: "Beyond text: vision-language models", file: "track15/01-vision-language-models.html", built: true },
        { n: "10.2", title: "Document AI & OCR", file: "track15/02-document-ai-ocr.html", built: true },
        { n: "10.3", title: "Audio: speech-to-text & TTS", file: "track15/03-audio.html", built: true },
        { n: "10.4", title: "Multimodal RAG", file: "track15/04-multimodal-rag.html", built: true },
        { n: "10.5", title: "Interview check: Multimodal", file: "track15/05-interview.html", built: true },
        { n: "10.6", title: "Lab: Document extraction you can trust", file: "track15/lab.html", built: true }
      ]
    },
    {
      id: "t12", num: "11", title: "Going Deeper", ready: true,
      blurb: "Senior-level depth in the topics that decide interviews: advanced RAG, reliable agents, and rigorous evaluation.",
      lessons: [
        { n: "11.1", title: "Advanced RAG", file: "track12/01-advanced-rag.html", built: true },
        { n: "11.2", title: "Advanced agents", file: "track12/02-advanced-agents.html", built: true },
        { n: "11.3", title: "Advanced evals", file: "track12/03-advanced-evals.html", built: true },
        { n: "11.4", title: "Lab: Advanced retrieval, measured", file: "track12/lab.html", built: true }
      ]
    },
    {
      id: "t14", num: "12", title: "Productionization & LLMOps", ready: true,
      blurb: "Ship it: wrap your app in a service, containerize it, gate changes with evals, and monitor it in production.",
      lessons: [
        { n: "12.1", title: "From notebook to a service", file: "track14/01-notebook-to-service.html", built: true },
        { n: "12.2", title: "Packaging & deploy", file: "track14/02-packaging-deploy.html", built: true },
        { n: "12.3", title: "CI for prompts & evals", file: "track14/03-ci-evals.html", built: true },
        { n: "12.4", title: "Monitoring in production", file: "track14/04-monitoring.html", built: true },
        { n: "12.5", title: "Interview check: LLMOps", file: "track14/05-interview.html", built: true },
        { n: "12.6", title: "Lab: Build a production monitor", file: "track14/lab.html", built: true }
      ]
    },
    {
      id: "t16", num: "13", title: "Frontier & Responsible AI", ready: true,
      blurb: "Where the field is heading and how to build responsibly: reasoning models, the frontier, bias, and regulation.",
      lessons: [
        { n: "13.1", title: "Reasoning models & test-time compute", file: "track16/01-reasoning-models.html", built: true },
        { n: "13.2", title: "The modern frontier", file: "track16/02-modern-frontier.html", built: true },
        { n: "13.3", title: "Responsible AI: bias & fairness", file: "track16/03-bias-fairness.html", built: true },
        { n: "13.4", title: "Governance & regulation", file: "track16/04-governance-regulation.html", built: true },
        { n: "13.5", title: "Interview check: Frontier & Responsible AI", file: "track16/05-interview.html", built: true },
        { n: "13.6", title: "Lab: Catch bias with disaggregated evaluation", file: "track16/lab.html", built: true }
      ]
    },
    {
      id: "t10", num: "14", title: "Capstones", ready: true,
      blurb: "End-to-end products that actually run — the portfolio that proves you can ship.",
      lessons: [
        { n: "14.1", title: "RAG assistant over your docs", file: "track10/01-rag-assistant.html", built: true },
        { n: "14.2", title: "A tool-using agent", file: "track10/02-tool-using-agent.html", built: true },
        { n: "14.3", title: "A prompt/RAG eval harness", file: "track10/03-eval-harness.html", built: true },
        { n: "14.4", title: "A fine-tuned domain model", file: "track10/04-finetuned-model.html", built: true },
        { n: "14.5", title: "A cost & latency-optimized chat service", file: "track10/05-optimized-chat-service.html", built: true }
      ]
    },
    {
      id: "t9", num: "15", title: "Interview Bank", ready: true,
      blurb: "What GenAI teams actually ask this year, with model answers and the reasoning behind each one.",
      lessons: [
        { n: "15.1", title: "Foundations Q&A", file: "track9/01-foundations-qa.html", built: true },
        { n: "15.2", title: "RAG Q&A", file: "track9/02-rag-qa.html", built: true },
        { n: "15.3", title: "Agents Q&A", file: "track9/03-agents-qa.html", built: true },
        { n: "15.4", title: "System design rounds", file: "track9/04-system-design.html", built: true },
        { n: "15.5", title: "Take-home patterns", file: "track9/05-take-home-patterns.html", built: true },
        { n: "15.6", title: "Behavioral & judgment", file: "track9/06-behavioral-judgment.html", built: true }
      ]
    },
    {
      id: "t11", num: "16", title: "Get Hired", ready: true,
      blurb: "Turn the course into a job: a study plan, a portfolio that proves you can ship, positioning for a data-engineer pivot, and a mock-interview drill.",
      lessons: [
        { n: "16.1", title: "Your study plan", file: "track11/01-study-plan.html", built: true },
        { n: "16.2", title: "Portfolio playbook", file: "track11/02-portfolio.html", built: true },
        { n: "16.3", title: "Positioning your experience", file: "track11/03-positioning.html", built: true },
        { n: "16.4", title: "Mock interview drill", file: "track11/04-mock-interview.html", built: true },
        { n: "16.5", title: "Lab: Generate your portfolio README", file: "track11/lab.html", built: true }
      ]
    }
  ]
};
