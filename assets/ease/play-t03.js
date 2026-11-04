/* Pass 2 interactives, Track 3 (RAG). Chunking is computed exactly like the lesson's chunk_text();
   retrieval and hybrid scores are illustrative inputs, and everything derived from them is computed live. */
(function () {
  var EZ = window.EZ;
  function wrapText(s, maxc) {
    var out = [], line = "";
    s.split(" ").forEach(function (w) { if (!line) line = w; else if ((line + " " + w).length <= maxc) line += " " + w; else { out.push(line); line = w; } });
    if (line) out.push(line);
    return out;
  }

  /* 3.2 chunker: same algorithm as chunk_text(text, size, overlap) on the lesson page (word-based) */
  var DOC = "The X200 blender ships with a 3-year limited warranty. Returns are free within 30 days of delivery. " +
    "To start a return, open the app and tap Orders, then Return. Refunds appear in 5 to 7 business days. " +
    "The motor is rated at 1200 watts and includes overheat protection.";
  var WORDS = DOC.split(" ");
  var SENTS = (function () { var out = [], st = 0; WORDS.forEach(function (w, i) { if (/[.!?]$/.test(w)) { out.push([st, i + 1]); st = i + 1; } }); return out; })();
  function spans(n, size, ov) {
    var step = size - ov, out = [];
    for (var i = 0; i < n; i += step) { out.push([i, Math.min(i + size, n)]); if (i + size >= n) break; }
    return out;
  }
  EZ.plays.chunker = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), size = 14, ov = 3;
    EZ.slider(bar, "chunk size (words)", 4, 30, 1, size, null, function (v) { size = v; draw(); });
    EZ.slider(bar, "overlap (words)", 0, 10, 1, ov, null, function (v) { ov = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var o = Math.min(ov, Math.floor(size / 2)), sp = spans(WORDS.length, size, o), n = WORDS.length;
      var nw = EZ.narrow(stage), W = nw ? 340 : 620, x0 = 10, sw = W - 20, cw = sw / n;
      var maxc = Math.floor((sw - 44) / 6.4);
      var rows = sp.map(function (s) { return wrapText(WORDS.slice(s[0], s[1]).join(" "), maxc); });
      var H = 128; rows.forEach(function (r) { H += r.length * 17 + 14; });
      var svg = EZ.svg(host, W, H, "Chunks of the paragraph");
      EZ.text(svg, x0, 18, "The paragraph as " + n + " words (one cell each)", "s b", "start");
      for (var i = 0; i < n; i++) EZ.rect(svg, x0 + i * cw, 28, Math.max(1, cw - 1), 14, "bx", 1);
      sp.forEach(function (s, k) {
        var y = 50 + (k % 2) * 22;
        EZ.rect(svg, x0 + s[0] * cw, y, (s[1] - s[0]) * cw - 1, 16, "bx " + (k % 2 ? "tn-a" : "tn-c"), 3);
        if ((s[1] - s[0]) * cw > 16) EZ.text(svg, x0 + (s[0] + s[1]) / 2 * cw, y + 13, String(k + 1), "s b", "middle", 11);
        if (k > 0 && sp[k - 1][1] > s[0]) EZ.rect(svg, x0 + s[0] * cw, 26, (sp[k - 1][1] - s[0]) * cw, 72, "fill-k", 0).setAttribute("opacity", ".4");
      });
      var y = 118;
      sp.forEach(function (s, k) {
        EZ.text(svg, x0, y + 13, "#" + (k + 1), "s b ac-t", "start");
        var shared = k > 0 ? Math.max(0, sp[k - 1][1] - s[0]) : 0, wi = 0;
        rows[k].forEach(function (ln, li) {
          var t = EZ.text(svg, x0 + 36, y + 13 + li * 17, "", "s", "start");
          ln.split(" ").forEach(function (w, j) {
            var ts = EZ.s("tspan", {}, t, (j ? " " : "") + w);
            if (wi < shared) ts.setAttribute("style", "fill:var(--c-key);font-weight:700");
            wi++;
          });
        });
        y += rows[k].length * 17 + 14;
      });
      var whole = SENTS.filter(function (st) { return sp.some(function (s) { return s[0] <= st[0] && s[1] >= st[1]; }); }).length;
      var emb = sp.reduce(function (a, s) { return a + s[1] - s[0]; }, 0);
      read.innerHTML = "<b>" + sp.length + " chunks</b>, step = " + size + " − " + o + " = " + (size - o) + " words. " + emb + " words embedded for " + n + " in the text (" +
        Math.round((emb / n - 1) * 100) + "% repeated). Sentences that sit whole in at least one chunk: <b>" + whole + " of " + SENTS.length + "</b>." +
        (o < ov ? " (Overlap capped at half the chunk size.)" : "") + " Amber words are repeated from the chunk before.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 3.5 top-k + similarity threshold over illustrative scored chunks */
  var CH = ["The X200 has a 3-year limited warranty.", "Warranty claims need the order number.", "Returns are free within 30 days.",
    "Open the app and tap Orders, then Return.", "The X200 motor is rated at 1200 watts.", "Cancel under Settings > Billing."];
  var QS = [["How long is the X200 warranty?", [.82, .71, .46, .30, .39, .12]],
    ["How do I send my blender back?", [.31, .28, .66, .74, .22, .35]],
    ["Who won the 2022 World Cup?", [.21, .18, .15, .10, .11, .09]]];
  EZ.plays.topk = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), qi = 0, k = 3, th = 0.5;
    EZ.buttons(bar, QS.map(function (q) { return q[0]; }), 0, function (i) { qi = i; draw(); });
    var b2 = EZ.el("div", { "class": "ez-ctl" }, stage);
    EZ.slider(b2, "k", 1, 6, 1, k, null, function (v) { k = v; draw(); });
    EZ.slider(b2, "threshold", 0, 0.95, 0.05, th, function (v) { return v.toFixed(2); }, function (v) { th = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 620, x0 = 10, bw = nw ? 250 : 420, sc = QS[qi][1];
      var order = sc.map(function (v, i) { return i; }).sort(function (a, b) { return sc[b] - sc[a]; });
      var RH = 42, H = 40 + order.length * RH + 30;
      var svg = EZ.svg(host, W, H, "Which chunks reach the prompt");
      EZ.text(svg, x0, 18, "Chunks ranked by similarity (illustrative scores)", "s m", "start");
      var used = [];
      order.forEach(function (i, r) {
        var y = 30 + r * RH, intop = r < k, ok = intop && sc[i] >= th;
        if (ok) used.push(i);
        EZ.text(svg, x0, y + 13, (r + 1) + ". " + CH[i], intop ? "s" : "s m", "start");
        EZ.rect(svg, x0, y + 18, Math.max(2, bw * sc[i]), 13, ok ? "fill-g" : (intop ? "fill-w" : "fill-m"), 3);
        var lx = x0 + bw * sc[i] + 6, tx0 = x0 + bw * th; if (lx - 8 < tx0 && tx0 < lx + 36) lx = tx0 + 6;
        EZ.text(svg, lx, y + 30, sc[i].toFixed(2) + (ok ? "  → prompt" : (intop ? "  below threshold" : "")), ok ? "s ok-t" : (intop ? "s wn-t" : "s m"), "start");
        if (r === k - 1 && k < order.length) { EZ.s("line", { x1: x0, y1: y + RH - 4, x2: W - 10, y2: y + RH - 4, "class": "ln thin dash" }, svg); EZ.text(svg, W - 10, y + RH - 8, "top-" + k + " cut", "s m", "end"); }
      });
      var tx = x0 + bw * th;
      order.forEach(function (i, r) { EZ.s("line", { x1: tx, y1: 30 + r * RH + 16, x2: tx, y2: 30 + r * RH + 33, "class": "ln wn" }, svg); });
      EZ.s("line", { x1: tx, y1: 30 + (order.length - 1) * RH + 33, x2: tx, y2: 30 + order.length * RH, "class": "ln wn dash" }, svg);
      EZ.text(svg, Math.min(tx + 4, W - 110), 30 + order.length * RH + 18, "threshold " + th.toFixed(2), "s wn-t", "start");
      read.innerHTML = used.length ? "<b>" + used.length + " chunk" + (used.length > 1 ? "s" : "") + " reach the prompt.</b> The model answers from them and cites them." :
        "<b>Refuse.</b> No chunk in the top " + k + " clears " + th.toFixed(2) + " (best is " + sc[order[0]].toFixed(2) + "), so the system says it doesn't know and never calls the model.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 3.6 hybrid: weighted mix of dense and min-max-normalised BM25 vs RRF (k = 60, ranks from 1) */
  var HC = ["To stop your subscription, open Settings > Billing.", "Error E-417: motor overheated. Unplug it and let it cool.", "Billing runs on the 1st of every month.",
    "Error E-412: the lid is not locked.", "Payments can be paused from the Billing page.", "The X200 motor has overheat protection.", "Error codes are listed in the manual."];
  var HQ = [["stop paying every month", 0, [.78, .10, .52, .08, .70, .20, .14], [1.4, 0, 2.6, 0, 0, 0, 0]],
    ["error E-417", 1, [.12, .55, .10, .57, .11, .50, .40], [0, 6.8, 0, 2.3, 0, 0, 2.9]]];
  function ranks(v) { var o = v.map(function (x, i) { return i; }).filter(function (i) { return v[i] > 0; }).sort(function (a, b) { return v[b] - v[a]; }), r = {}; o.forEach(function (i, k) { r[i] = k + 1; }); return r; }
  EZ.plays.hybrid = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), qi = 0, al = 0.5;
    EZ.buttons(bar, HQ.map(function (q) { return "“" + q[0] + "”"; }), 0, function (i) { qi = i; draw(); });
    EZ.slider(bar, "alpha (1 = all dense)", 0, 1, 0.05, al, function (v) { return v.toFixed(2); }, function (v) { al = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var q = HQ[qi], d = q[2], b = q[3], bmax = Math.max.apply(null, b), bmin = Math.min.apply(null, b);
      var bn = b.map(function (x) { return bmax > bmin ? (x - bmin) / (bmax - bmin) : 0; });
      var mix = d.map(function (x, i) { return al * x + (1 - al) * bn[i]; });
      var dr = ranks(d), br = ranks(b), rrf = d.map(function (x, i) { return (dr[i] ? 1 / (60 + dr[i]) : 0) + (br[i] ? 1 / (60 + br[i]) : 0); });
      var mo = mix.map(function (x, i) { return i; }).sort(function (a, c) { return mix[c] - mix[a]; });
      var ro = rrf.map(function (x, i) { return i; }).sort(function (a, c) { return rrf[c] - rrf[a]; });
      var nw = EZ.narrow(stage), W = nw ? 340 : 640, x0 = 10, bw = nw ? 210 : 260, RH = 38;
      var H = nw ? 44 + mo.length * RH + 24 + 40 + ro.length * 22 + 10 : Math.max(44 + mo.length * RH + 14, 18 + 40 + ro.length * 22 + 14);
      var svg = EZ.svg(host, W, H, "Hybrid ranking");
      EZ.text(svg, x0, 18, "Weighted mix (illustrative scores)", "s b", "start");
      EZ.rect(svg, x0, 26, 12, 10, "fill-c", 2); EZ.text(svg, x0 + 16, 35, "dense part", "s", "start", 12);
      EZ.rect(svg, x0 + 96, 26, 12, 10, "fill-k", 2); EZ.text(svg, x0 + 112, 35, "BM25 part", "s", "start", 12);
      mo.forEach(function (i, r) {
        var y = 44 + r * RH, w1 = bw * al * d[i], w2 = bw * (1 - al) * bn[i], right = i === q[1];
        var lab = "[" + (i + 1) + "] " + (nw ? HC[i].slice(0, 40) + (HC[i].length > 40 ? "…" : "") : HC[i]);
        EZ.text(svg, x0, y + 12, lab, right ? "s b ok-t" : "s", "start");
        EZ.rect(svg, x0, y + 17, Math.max(1, w1), 12, "fill-c", 2);
        EZ.rect(svg, x0 + w1, y + 17, Math.max(0, w2), 12, "fill-k", 2);
        EZ.text(svg, x0 + w1 + w2 + 6, y + 28, mix[i].toFixed(2), "s", "start", 12);
      });
      var rx = nw ? x0 : 450, ry = nw ? 44 + mo.length * RH + 24 : 18;
      EZ.text(svg, rx, ry, "RRF, k = 60", "s b", "start");
      EZ.text(svg, rx + (nw ? 90 : 0), ry + (nw ? 0 : 17), "(no weight to tune)", "s m", "start", 12);
      ro.forEach(function (i, r) {
        var right = i === q[1];
        EZ.text(svg, rx, ry + (nw ? 26 : 40) + r * 22, (r + 1) + ".  [" + (i + 1) + "]  " + rrf[i].toFixed(4), right ? "s b ok-t" : (rrf[i] ? "s" : "s m"), "start");
      });
      EZ.text(svg, rx, ry + (nw ? 26 : 40) + ro.length * 22, "[n] = chunk number", "s m", "start", 12);
      var mixOk = mo[0] === q[1], rrfOk = ro[0] === q[1];
      read.innerHTML = "Right chunk (green): <b>" + HC[q[1]] + "</b><br>Weighted mix at alpha " + al.toFixed(2) + ": " + (mixOk ? "<b>top 1 is right</b>" : "<b>top 1 is wrong</b>") +
        ". RRF: " + (rrfOk ? "<b>top 1 is right</b>" : "<b>top 1 is wrong</b>") + ". BM25 scores are rescaled to 0–1 before mixing; RRF uses only the ranks.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
