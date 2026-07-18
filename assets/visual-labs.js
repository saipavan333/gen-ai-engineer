/* ============================================================
   visual-labs.js — full-page animated mechanism explorers.
   Stage 0 tokenize · 1 embed · 2 attend · 3 score · 4 sample · 5 append
   Pure SVG + vanilla JS. No dependencies, works offline.
   ============================================================ */
(function () {
  "use strict";
  var root = document.getElementById("vlab");
  if (!root) return;

  var SVG = document.getElementById("vl-svg"),
      NS  = "http://www.w3.org/2000/svg",
      capEl   = document.getElementById("vl-caption"),
      textEl  = document.getElementById("vl-text"),
      tempEl  = document.getElementById("vl-temp"),
      tvalEl  = document.getElementById("vl-tval"),
      speedEl = document.getElementById("vl-speed"),
      stagesEl= document.getElementById("vl-stages");

  var COLORS = ["#818cf8","#22d3ee","#c084fc","#f59e0b","#f472b6","#34d399","#60a5fa","#fb7185"];

  /* a small real bigram model, so every number on screen is earned */
  var CORPUS = ("the model reads the prompt and predicts the next token . " +
    "the model reads the context before it answers . the next token depends on the prompt . " +
    "a model can predict the next word from the prompt . the prompt guides the model output . " +
    "the model predicts one token at a time . the next word follows the context .").split(/\s+/);
  var BIGRAM = {};
  for (var i = 0; i < CORPUS.length - 1; i++) {
    var a = CORPUS[i], b = CORPUS[i + 1];
    (BIGRAM[a] = BIGRAM[a] || {})[b] = (BIGRAM[a][b] || 0) + 1;
  }

  function el(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function clear() { while (SVG.firstChild) SVG.removeChild(SVG.firstChild); }
  function tokenize(t) { return t.trim().toLowerCase().split(/\s+/).filter(Boolean); }

  /* deterministic pseudo-embedding so the picture is stable per word */
  function vec(word, n) {
    var h = 0, out = [];
    for (var i = 0; i < word.length; i++) h = (h * 31 + word.charCodeAt(i)) >>> 0;
    for (var j = 0; j < n; j++) { h = (h * 1103515245 + 12345) >>> 0; out.push(((h >>> 16) % 1000) / 1000); }
    return out;
  }
  function attention(toks) {
    /* last token attends to earlier ones; content words win over function words */
    var STOP = {the:1, a:1, an:1, of:1, and:1, to:1, ".":1};
    var last = toks.length - 1, w = [], tot = 0;
    for (var i = 0; i < last; i++) {
      var s = STOP[toks[i]] ? 0.12 : 1.0;
      s *= 1 / (1 + (last - i) * 0.35);              // recency
      s *= 0.6 + vec(toks[i], 1)[0] * 0.8;            // stable per-word jitter
      w.push(s); tot += s;
    }
    return w.map(function (x) { return tot ? x / tot : 0; });
  }
  function distribution(lastTok, temperature) {
    var counts = BIGRAM[lastTok];
    if (!counts) {                                   // unseen word -> near-flat
      counts = {}; ["the","model","token","prompt","."].forEach(function (k) { counts[k] = 1; });
    }
    var keys = Object.keys(counts);
    var logits = keys.map(function (k) { return Math.log(counts[k] + 0.15); });
    var scaled = logits.map(function (l) { return l / Math.max(temperature, 0.05); });
    var top = Math.max.apply(null, scaled);
    var ex = scaled.map(function (s) { return Math.exp(s - top); });
    var sum = ex.reduce(function (p, c) { return p + c; }, 0);
    return keys.map(function (k, i) { return { tok: k, p: ex[i] / sum }; })
               .sort(function (x, y) { return y.p - x.p; }).slice(0, 6);
  }

  var CAPTIONS = [
    "<b>Tokenize.</b> The model never sees letters or words — it sees tokens. Your sentence is cut into the units it was trained on.",
    "<b>Embed.</b> Each token becomes a list of numbers. Similar meanings land near each other, which is what makes the arithmetic work at all.",
    "<b>Attend.</b> To predict what comes next, the model weighs every earlier token. Thicker beams carry more influence — notice how little it spends on words like “the”.",
    "<b>Score.</b> Out comes a probability for <em>every</em> token it knows. This is the model's actual belief, and temperature has not touched it yet.",
    "<b>Sample.</b> Now temperature reshapes the distribution, and one token is drawn. Low temperature keeps picking the favourite; high temperature spreads the chance around.",
    "<b>Append.</b> The chosen token joins the sentence — and the whole loop starts again from step 1. That repetition is all “generation” is."
  ];

  var stage = -1, playing = false, timer = null, chosen = null, toks = [], dist = [], att = [];

  function speedMs() { return [0, 2100, 1500, 1050, 700, 420][+speedEl.value] || 1050; }
  function temp() { return +tempEl.value / 10; }

  function markStages() {
    Array.prototype.forEach.call(stagesEl.children, function (li, i) {
      li.classList.toggle("on", i === stage);
      li.classList.toggle("done", i < stage);
    });
  }

  function draw() {
    clear();
    var W = 900, cx = W / 2;
    if (stage < 0) {
      SVG.appendChild(el("text", { x: cx, y: 190, "text-anchor": "middle", class: "vl-hint" },
        "press play"));
      return;
    }
    /* ---------- row of tokens (always visible from stage 0) ---------- */
    var boxW = Math.min(120, Math.floor(760 / Math.max(toks.length, 1))), gap = 10;
    var totalW = toks.length * boxW + (toks.length - 1) * gap;
    var x0 = cx - totalW / 2;
    toks.forEach(function (t, i) {
      var x = x0 + i * (boxW + gap);
      var g = el("g", { class: "vl-tok", style: "animation-delay:" + (i * 70) + "ms" });
      g.appendChild(el("rect", { x: x, y: 26, width: boxW, height: 40, rx: 9,
        fill: COLORS[i % COLORS.length] + "26", stroke: COLORS[i % COLORS.length], "stroke-width": 1.6 }));
      g.appendChild(el("text", { x: x + boxW / 2, y: 51, "text-anchor": "middle", class: "vl-tok-t" }, t));
      SVG.appendChild(g);
    });

    /* ---------- stage 1: embeddings ---------- */
    if (stage >= 1) {
      toks.forEach(function (t, i) {
        var x = x0 + i * (boxW + gap), v = vec(t, 8);
        v.forEach(function (val, j) {
          var cell = el("rect", { x: x + 6 + (j % 4) * ((boxW - 12) / 4), y: 78 + Math.floor(j / 4) * 13,
            width: (boxW - 12) / 4 - 2, height: 11, rx: 2,
            fill: COLORS[i % COLORS.length], "fill-opacity": (0.18 + val * 0.72).toFixed(2),
            class: "vl-cell", style: "animation-delay:" + (i * 60 + j * 22) + "ms" });
          SVG.appendChild(cell);
        });
      });
    }

    /* ---------- stage 2: attention beams ---------- */
    if (stage >= 2 && toks.length > 1) {
      var last = toks.length - 1, lx = x0 + last * (boxW + gap) + boxW / 2;
      att.forEach(function (wgt, i) {
        var sx = x0 + i * (boxW + gap) + boxW / 2;
        var d = "M " + sx + " 120 C " + sx + " 165, " + lx + " 165, " + lx + " 120";
        SVG.appendChild(el("path", { d: d, fill: "none", stroke: "#818cf8",
          "stroke-opacity": (0.16 + wgt * 0.8).toFixed(2),
          "stroke-width": (1 + wgt * 11).toFixed(1), class: "vl-beam",
          style: "animation-delay:" + (i * 90) + "ms" }));
        if (wgt > 0.16) {
          SVG.appendChild(el("text", { x: (sx + lx) / 2, y: 158, "text-anchor": "middle",
            class: "vl-wgt" }, Math.round(wgt * 100) + "%"));
        }
      });
    }

    /* ---------- stages 3-4: probability bars ---------- */
    if (stage >= 3) {
      var bx = 250, by = 196, bw = 400, rowH = 26;
      SVG.appendChild(el("text", { x: bx, y: by - 8, class: "vl-lbl" },
        stage >= 4 ? "after temperature " + temp().toFixed(1) : "the model's belief"));
      dist.forEach(function (d, i) {
        var y = by + i * rowH;
        SVG.appendChild(el("text", { x: bx - 12, y: y + 13, "text-anchor": "end", class: "vl-btok" }, d.tok));
        SVG.appendChild(el("rect", { x: bx, y: y, width: bw, height: 16, rx: 8, fill: "#ffffff14" }));
        var isPick = chosen && d.tok === chosen && stage >= 4;
        SVG.appendChild(el("rect", { x: bx, y: y, width: Math.max(2, d.p * bw), height: 16, rx: 8,
          fill: isPick ? "#34d399" : "#818cf8", class: "vl-bar",
          style: "animation-delay:" + (i * 70) + "ms" }));
        SVG.appendChild(el("text", { x: bx + bw + 12, y: y + 13, class: "vl-bpct" },
          Math.round(d.p * 100) + "%"));
        if (isPick) SVG.appendChild(el("text", { x: bx + bw + 58, y: y + 13, class: "vl-pick" }, "◄ drawn"));
      });
    }

    /* ---------- stage 5: appended ---------- */
    if (stage >= 5 && chosen) {
      SVG.appendChild(el("text", { x: cx, y: 366, "text-anchor": "middle", class: "vl-final" },
        toks.join(" ") + " " + chosen));
    }
  }

  function recompute() {
    toks = tokenize(textEl.value);
    if (!toks.length) toks = ["the"];
    att = attention(toks);
    dist = distribution(toks[toks.length - 1], stage >= 4 ? temp() : 1.0);
  }

  function setStage(s) {
    stage = s;
    if (stage === 0) { chosen = null; recompute(); }
    if (stage === 3) { dist = distribution(toks[toks.length - 1], 1.0); }
    if (stage === 4) {
      dist = distribution(toks[toks.length - 1], temp());
      var r = Math.random(), acc = 0;
      chosen = dist[dist.length - 1].tok;
      for (var i = 0; i < dist.length; i++) { acc += dist[i].p; if (r <= acc) { chosen = dist[i].tok; break; } }
    }
    if (stage === 5 && chosen) { textEl.value = (toks.join(" ") + " " + chosen).trim(); }
    capEl.innerHTML = CAPTIONS[stage] || "";
    markStages();
    draw();
  }

  function stop() { playing = false; clearTimeout(timer); document.getElementById("vl-play").textContent = "▶ Play"; }
  function tick() {
    if (!playing) return;
    if (stage >= 5) { stop(); return; }
    setStage(stage + 1);
    timer = setTimeout(tick, speedMs());
  }

  document.getElementById("vl-play").addEventListener("click", function () {
    if (playing) { stop(); return; }
    playing = true; this.textContent = "❚❚ Pause";
    if (stage >= 5 || stage < 0) setStage(0); else setStage(stage + 1);
    timer = setTimeout(tick, speedMs());
  });
  document.getElementById("vl-step").addEventListener("click", function () {
    stop(); setStage(stage >= 5 || stage < 0 ? 0 : stage + 1);
  });
  document.getElementById("vl-reset").addEventListener("click", function () {
    stop(); stage = -1; chosen = null; capEl.innerHTML = "Press play. The model is about to choose the next word — you'll see exactly how."; markStages(); draw();
  });
  tempEl.addEventListener("input", function () {
    tvalEl.textContent = temp().toFixed(1);
    if (stage >= 4) { setStage(4); }
  });
  textEl.addEventListener("input", function () { stop(); stage = -1; markStages(); draw(); });
  stagesEl.addEventListener("click", function (e) {
    var li = e.target.closest("li"); if (!li) return;
    stop(); var s = +li.getAttribute("data-s");
    if (s === 0 || stage >= 0) { if (s === 0) setStage(0); else { for (var k = Math.max(stage,0); k < s; k++) setStage(k + 1); } }
    else setStage(0);
  });

  tvalEl.textContent = temp().toFixed(1);
  draw();
})();
