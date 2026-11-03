"""Generate the Track 17 flow diagrams in the course's diagram style (white card, soft gradients)."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "diagrams"
FONT = "Inter, ui-sans-serif, Segoe UI, Roboto, DejaVu Sans, Helvetica, Arial, sans-serif"
FILL = {"plain": ("#ffffff", "#f3f7fc", "#94a3b8"), "concept": ("#eff5ff", "#dde9ff", "#4f46e5"),
        "example": ("#eefaf0", "#d7f1de", "#15803d"), "key": ("#fff6ea", "#ffecca", "#c2410c"),
        "warn": ("#fef1ef", "#fde2dd", "#b91c1c"), "deep": ("#eafaf6", "#d3f1ea", "#0f766e")}


def flow(name, title, steps, note, w=880, h=300):
    n = len(steps)
    gap, top, bh = 26, 70, 132
    bw = (w - 40 - gap * (n - 1)) / n
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="{FONT}">', "<defs>"]
    for k, (a, b, _) in FILL.items():
        p.append(f'<linearGradient id="g_{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
    p.append('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#64748b"/></marker></defs>')
    p.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>')
    p.append(f'<text x="{w/2}" y="34" font-size="17" font-weight="bold" fill="#0f172a" text-anchor="middle">{escape(title)}</text>')
    for i, (head, lines, style) in enumerate(steps):
        x = 20 + i * (bw + gap)
        stroke = FILL[style][2]
        p.append(f'<rect x="{x:.1f}" y="{top}" width="{bw:.1f}" height="{bh}" rx="12" fill="url(#g_{style})" stroke="{stroke}" stroke-width="1.6"/>')
        fs = min(13.5, (bw - 14) / (len(head) * 0.64))  # shrink long headings so they never overflow the box
        p.append(f'<text x="{x + bw/2:.1f}" y="{top + 26}" font-size="{fs:.1f}" font-weight="bold" fill="{stroke}" text-anchor="middle">{escape(head)}</text>')
        for j, line in enumerate(lines):
            mono = line.startswith("`") and line.endswith("`")
            t = line.strip("`") if mono else line
            fs_line = min(11.5 if mono else 12, (bw - 12) / (len(t) * (0.62 if mono else 0.55)))
            fam = ' font-family="ui-monospace, Consolas, monospace"' if mono else ""
            p.append(f'<text x="{x + bw/2:.1f}" y="{top + 50 + j * 18}" font-size="{fs_line:.1f}"{fam} fill="#334155" text-anchor="middle">{escape(t)}</text>')
        if i < n - 1:
            ax = x + bw + 3
            p.append(f'<line x1="{ax:.1f}" y1="{top + bh/2}" x2="{ax + gap - 6:.1f}" y2="{top + bh/2}" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>')
    p.append(f'<rect x="20" y="{top + bh + 22}" width="{w - 40}" height="44" rx="10" fill="url(#g_note)" stroke="#cbd5e1"/>' if False else
             f'<rect x="20" y="{top + bh + 22}" width="{w - 40}" height="44" rx="10" fill="#f1f5f9" stroke="#cbd5e1"/>')
    p.append(f'<text x="{w/2}" y="{top + bh + 49}" font-size="12.5" fill="#334155" text-anchor="middle">{escape(note)}</text>')
    p.append("</svg>")
    (OUT / name).write_text("\n".join(p), encoding="utf-8")
    print("wrote", name)


flow("t17-ai-sql.svg", "LLM functions inside SQL: one model call per row that reaches them",
     [("1. Source table", ["10 M review rows", "in the warehouse"], "plain"),
      ("2. Filter + dedupe", ["WHERE date = today", "SELECT DISTINCT text", "10 M -> 40 K rows"], "key"),
      ("3. AI function", ["`AI.GENERATE / AI_COMPLETE`", "`/ ai_query`", "1 call per row"], "concept"),
      ("4. Model endpoint", ["managed LLM", "quota, cost, latency", "per call"], "deep"),
      ("5. New column", ["label / JSON / text", "validate + eval it", "then GROUP BY"], "example")],
     "Cost scales with rows that reach step 3. Cut rows before the AI function, constrain the output, and eval it like any model.")

flow("t17-bigquery.svg", "BigQuery: RAG without leaving SQL",
     [("Docs table", ["content column", "(text to embed)"], "plain"),
      ("AI.GENERATE_EMBEDDING", ["remote embedding", "model in Vertex AI", "-> embedding column"], "concept"),
      ("Vector index", ["CREATE VECTOR INDEX", "(optional, for", "large tables)"], "key"),
      ("VECTOR_SEARCH", ["query embedding", "top_k nearest rows", "distance_type"], "deep"),
      ("AI.GENERATE", ["prompt = question", "+ retrieved rows", "-> grounded answer"], "example")],
     "Needs your account: a Google Cloud project with billing and a connection to the model platform. Check current model names in the docs.")

flow("t17-databricks.svg", "Databricks: Mosaic AI Vector Search + ai_query",
     [("Delta table", ["governed by", "Unity Catalog"], "plain"),
      ("Vector Search index", ["built from the table", "embeddings kept", "in sync"], "concept"),
      ("vector_search()", ["`query_text => ...`", "`query_type => 'HYBRID'`", "`num_results => 3`"], "deep"),
      ("ai_query()", ["endpoint, request", "`responseFormat`", "`failOnError => false`"], "key"),
      ("Result", ["answer + sources", "trace + evaluate", "with MLflow"], "example")],
     "Needs your account: a workspace with Foundation Model APIs and a serverless or pro SQL warehouse (vector_search is not on classic warehouses).")

flow("t17-snowflake.svg", "Snowflake Cortex: Cortex Search + AI_COMPLETE",
     [("Table", ["support_transcripts", "text + attributes"], "plain"),
      ("Cortex Search service", ["CREATE ... ON text_col", "TARGET_LAG = '1 day'", "EMBEDDING_MODEL"], "concept"),
      ("Hybrid retrieval", ["vector + keyword", "+ semantic rerank", "filters on attributes"], "deep"),
      ("AI_COMPLETE", ["model, prompt", "response_format", "for structured output"], "key"),
      ("Result", ["grounded answer", "role CORTEX_USER", "governs access"], "example")],
     "Needs your account: a Snowflake trial or paid account with Cortex available in your region. Model list changes; check the docs.")
