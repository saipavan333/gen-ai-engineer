/* Pass 2 interactives, Section 15 (Interview bank). Wording comes from lesson 15.4's worked example and practice solutions. */
(function () {
  var EZ = window.EZ;

  /* rough word wrap by average glyph width (13 px text is about 7 px per character) */
  function wrap(s, px, cw) {
    var max = Math.max(8, Math.floor(px / (cw || 7))), out = [], line = "";
    s.split(" ").forEach(function (w) {
      if (!line) line = w; else if ((line + " " + w).length <= max) line += " " + w; else { out.push(line); line = w; }
    });
    if (line) out.push(line);
    return out;
  }

  /* 15.4 one framework, three design prompts from the page */
  var STEPS = ["Clarify", "Data & knowledge", "Core design", "Evaluation", "Safety", "Cost & latency", "Iterate"];
  var TONES = ["k", "c", "a", "g", "w", "p", "d"];
  var DESIGNS = [
    { name: "Support assistant", full: "Design a customer-support assistant", changed: [],
      note: "Answers from help docs and takes no actions.",
      rows: ["Help docs only, about 50k questions a day, under 2 s perceived, no money-moving actions in v1.",
        "Private, changing policy docs, so RAG: chunk with overlap + metadata, embed, vector DB, re-index on change.",
        "Moderate input → hybrid retrieve + rerank → grounded prompt with citations → LLM; small model for easy queries.",
        "Golden set of real questions: recall@k, MRR, faithfulness via LLM judge; gate in CI; A/B online.",
        "Fence user input as data, moderate in and out, validate output, redact PII in logs. No actions: small blast radius.",
        "Cache repeats, stream the answer, cap output, trim retrieved context.",
        "Trace every request, mine failures into the golden set, send low-confidence answers to a human."] },
    { name: "Codebase Q&A", full: "Design a tool that answers questions about a company's codebase", changed: [1, 2, 3, 4],
      note: "Same skeleton (RAG + grounding + eval + serving). The data step changes most.",
      rows: ["Same first question: what does good look like, at what scale, latency and cost?",
        "Code needs structure-aware chunking: split on function and class boundaries, keep the imports.",
        "Same RAG skeleton, with hybrid search: exact symbol names matter and dense search alone blurs identifiers.",
        "Code-specific golden questions.",
        "Still no actions, so mainly input and output handling, and not leaking private code in logs.",
        "Same serving levers as the support assistant.",
        "Same flywheel: trace, monitor, fold failures back into the golden set."] },
    { name: "…that opens PRs", full: "Now it should also be able to open pull requests", changed: [0, 2, 3, 4, 5, 6],
      note: "An action-taking agent: safety jumps to the front.",
      rows: ["Scope changed: it now takes an irreversible-ish action. Call that out before redrawing.",
        "Treat repo content as untrusted input: it can carry injected instructions.",
        "It becomes an agent: a loop with least-privilege tools.",
        "Evaluate the agent on representative tasks on every change.",
        "Validate the generated diff. Never auto-merge: open a PR for human review. Sandbox any code execution.",
        "Bound the loop with a step cap, so cost and runaway runs stay limited.",
        "Log every action, and fold failures back into the task suite."] }
  ];

  EZ.plays.designround = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), di = 1;
    EZ.buttons(bar, DESIGNS.map(function (d) { return d.name; }), 1, function (i) { di = i; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var d = DESIGNS[di], nw = EZ.narrow(stage), W = nw ? 340 : 620;
      var tw = 156, cx = nw ? 12 : 190, cw = nw ? W - 24 : W - cx - 40, lh = 17;
      /* measure */
      var blocks = d.rows.map(function (r) { var L = wrap(r, cw - 24, 6.7); return { L: L, h: Math.max(nw ? 0 : 40, 14 + L.length * lh) }; });
      var H = 44;
      blocks.forEach(function (b) { H += (nw ? 32 : 0) + b.h + 14; });
      var svg = EZ.svg(host, W, H + 8, "System-design layers for: " + d.full);
      var tl = wrap("“" + d.full + "”", W - 24, 7.6);
      EZ.text(svg, 12, 20, tl[0], "b", "start");
      if (tl[1]) EZ.text(svg, 12, 38, tl[1], "b", "start");
      var y = tl[1] ? 52 : 36, ys = [];
      blocks.forEach(function (b, i) {
        var on = di === 0 || d.changed.indexOf(i) >= 0, tone = on ? TONES[i] : "b";
        if (nw) {
          EZ.rect(svg, 12, y, 170, 26, "bx tn-" + tone, 13);
          EZ.text(svg, 97, y + 18, (i + 1) + ". " + STEPS[i], "b", "middle", 13);
          if (on && di > 0) EZ.text(svg, 190, y + 18, di === 2 && i === 4 ? "jumps to the front" : "changes", "s ac-t", "start");
          y += 32;
        } else {
          EZ.rect(svg, 12, y, tw, b.h, "bx tn-" + tone, 10);
          var front = di === 2 && i === 4;
          EZ.text(svg, 12 + tw / 2, y + b.h / 2 + (front ? -3 : 5), (i + 1) + ". " + STEPS[i], "b", "middle", 13);
          if (front) EZ.text(svg, 12 + tw / 2, y + b.h / 2 + 15, "now goes first", "s wn-t", "middle", 12);
          EZ.arrow(svg, 12 + tw + 3, y + b.h / 2, cx - 3, y + b.h / 2, "thin");
        }
        EZ.rect(svg, cx, y, cw, b.h, "bx" + (on ? " tn-" + tone : ""), 8);
        var ty = y + (b.h - b.L.length * lh) / 2 + 12.5;
        b.L.forEach(function (ln, k) { EZ.text(svg, cx + 12, ty + k * lh, ln, on ? "" : "m", "start", 13); });
        ys.push([y, b.h]);
        y += b.h + 14;
      });
      if (!nw) {
        var xr = cx + cw + 18, ye = ys[3][0] + ys[3][1] / 2, yi = ys[6][0] + ys[6][1] / 2;
        EZ.s("polyline", { points: (cx + cw + 3) + "," + yi + " " + xr + "," + yi + " " + xr + "," + ye, "class": "ln ac" }, svg);
        EZ.arrow(svg, xr, ye, cx + cw + 4, ye, "ac");
      }
      read.innerHTML = (di === 0 ? "<b>Baseline.</b> " : "<b>" + d.changed.length + " of 7</b> layers change. ") + d.note +
        (di === 0 ? " It is the worked example above; pick another prompt to see which layers move." : " Coloured = changed from the support assistant; grey = same as before.") +
        (nw ? "" : " The blue loop: failures go back into evaluation.");
    }
    draw(); EZ.watch(stage, draw);
  };
})();
