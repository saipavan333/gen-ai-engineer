/* Pass 2 interactives, Track 1. Same algorithms as tools/ease/t01.py (numbers are computed, inputs are toy data). */
(function () {
  var EZ = window.EZ;

  /* 1.2 byte-pair encoding on a toy corpus */
  var CORPUS = [["low", 5], ["lower", 2], ["newest", 6], ["widest", 3]];
  function applyOne(sy, a, b) {
    var out = [], i = 0;
    while (i < sy.length) { if (i < sy.length - 1 && sy[i] === a && sy[i + 1] === b) { out.push(a + b); i += 2; } else { out.push(sy[i]); i++; } }
    return out;
  }
  function learn(n) {
    var words = CORPUS.map(function (c) { return c[0].split(""); }), merges = [];
    for (var k = 0; k < n; k++) {
      var counts = {}, order = [];
      CORPUS.forEach(function (c, wi) {
        var sy = words[wi];
        for (var i = 0; i < sy.length - 1; i++) { var key = sy[i] + "\u0000" + sy[i + 1]; if (!(key in counts)) { counts[key] = 0; order.push(key); } counts[key] += c[1]; }
      });
      if (!order.length) break;
      var best = order[0];
      order.forEach(function (key) { if (counts[key] > counts[best]) best = key; });
      var p = best.split("\u0000");
      merges.push([p[0], p[1], counts[best]]);
      words = words.map(function (sy) { return applyOne(sy, p[0], p[1]); });
    }
    return merges;
  }
  EZ.plays.bpe = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), word = "lowest", n = 4;
    var WORDS = ["lowest", "newer", "widest", "slowest"];
    EZ.buttons(bar, WORDS, 0, function (i) { word = WORDS[i]; draw(); });
    EZ.slider(bar, "merges learned", 0, 10, 1, n, null, function (v) { n = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var merges = learn(n), sy = word.split("");
      merges.forEach(function (m) { sy = applyOne(sy, m[0], m[1]); });
      var nw = EZ.narrow(stage), W = nw ? 340 : 520;
      var svg = EZ.svg(host, W, 132 + (nw ? Math.max(1, merges.length) : Math.ceil(Math.max(1, merges.length) / 2)) * 22, "BPE tokens for " + word);
      EZ.text(svg, 12, 24, '"' + word + '" after ' + merges.length + " merges", "b", "start");
      var x = 12;
      sy.forEach(function (t) { var w = Math.max(30, t.length * 17 + 14); EZ.rect(svg, x, 40, w, 38, "bx tn-a", 7); EZ.text(svg, x + w / 2, 65, t, "b mono"); x += w + 8; });
      EZ.text(svg, 12, 110, nw ? "Merges so far (times seen):" : "Merges learned so far (pair → new token, times seen):", "s m", "start");
      merges.forEach(function (m, i) {
        var col = nw ? 0 : i % 2, row = nw ? i : Math.floor(i / 2);
        EZ.text(svg, 12 + col * 250, 136 + row * 22, (i + 1) + ". " + m[0] + " + " + m[1] + " → " + m[0] + m[1] + "  (" + m[2] + "x)", "s", "start");
      });
      if (!merges.length) EZ.text(svg, 12, 136, "none yet: every letter is its own token", "s", "start");
      read.innerHTML = "<b>" + sy.length + " tokens</b> instead of " + word.length + " letters. Fewer tokens means a cheaper, shorter input for the model.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 1.3 nearest neighbours by cosine similarity on toy 2-D vectors */
  var EMB = [["My flight was cancelled", .95, .30, "c"], ["The airline scrapped my trip", .80, .60, "c"], ["Train delayed two hours", .92, -.02, "c"],
    ["I like pizza", -.62, .70, "k"], ["Pasta for dinner tonight", -.75, .55, "k"], ["Refund to my card", -.12, -.95, "g"], ["Where is my money back?", .40, -.85, "g"]];
  var QS = [["Flight got cancelled, now what?", .92, .22], ["What should I cook?", -.70, .62], ["Has my refund arrived?", .28, -.92]];
  function cos(a, b) { return (a[0] * b[0] + a[1] * b[1]) / (Math.hypot(a[0], a[1]) * Math.hypot(b[0], b[1])); }
  EZ.plays.embed = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), qi = 0;
    EZ.buttons(bar, QS.map(function (q) { return q[0]; }), 0, function (i) { qi = i; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), q = QS[qi], W = nw ? 340 : 640, H = nw ? 290 : 340, cx = nw ? 170 : 305, cy = nw ? 150 : 170, R = nw ? 115 : 140;
      var svg = EZ.svg(host, W, H, "Nearest texts to the question");
      EZ.s("line", { x1: cx - R - 20, y1: cy, x2: cx + R + 20, y2: cy, "class": "grid" }, svg);
      EZ.s("line", { x1: cx, y1: cy - R - 10, x2: cx, y2: cy + R + 10, "class": "grid" }, svg);
      var ranked = EMB.map(function (e) { return [cos([q[1], q[2]], [e[1], e[2]]), e]; }).sort(function (a, b) { return b[0] - a[0]; });
      var top = ranked.slice(0, 3).map(function (r) { return r[1][0]; });
      EMB.forEach(function (e, k) {
        var px = cx + e[1] * R, py = cy - e[2] * R, on = top.indexOf(e[0]) >= 0;
        EZ.s("line", { x1: cx, y1: cy, x2: px, y2: py, "class": "ln thin" + (on ? " ac" : ""), opacity: on ? 1 : .3 }, svg);
        EZ.s("circle", { cx: px, cy: py, r: on ? 8 : 6, "class": "dot tn-" + e[3] }, svg);
        EZ.text(svg, px + (e[1] < 0 ? -11 : 11), py + 5, nw ? String(k + 1) : e[0], on ? "s b" : "s m", e[1] < 0 ? "end" : "start");
      });
      var qx = cx + q[1] * R * .62, qy = cy - q[2] * R * .62;
      EZ.s("circle", { cx: qx, cy: qy, r: 9, "class": "fill-a" }, svg);
      EZ.s("circle", { cx: qx, cy: qy, r: 15, "class": "ring" }, svg);
      EZ.text(svg, 14, 22, nw ? "ring = the question" : "Question: " + q[0], "s ac-t", "start");
      read.innerHTML = (nw ? EMB.map(function (e, k) { return (k + 1) + " " + e[0]; }).join(" · ") + "<br>" : "") + "Top 3: " + ranked.slice(0, 3).map(function (r) { return "<b>" + r[1][0] + "</b> " + r[0].toFixed(2); }).join(" · ") +
        ". Furthest: " + ranked[ranked.length - 1][1][0] + " " + ranked[ranked.length - 1][0].toFixed(2) + ". (Toy 2-D vectors; real ones have hundreds of numbers.)";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 1.5 temperature + top-p on illustrative scores */
  var CANDS = [["sunny", 3.0], ["cloudy", 2.2], ["rainy", 1.8], ["nice", 1.5], ["humid", 0.9], ["purple", -1.0]];
  EZ.plays.sampling = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), T = 1.0, P = 1.0, drawn = null, seed = 7;
    EZ.slider(bar, "temperature", 0.1, 2.0, 0.1, T, function (v) { return v.toFixed(1); }, function (v) { T = v; drawn = null; draw(); });
    EZ.slider(bar, "top-p", 0.1, 1.0, 0.05, P, function (v) { return v.toFixed(2); }, function (v) { P = v; drawn = null; draw(); });
    var btn = EZ.el("button", { type: "button" }, bar, "Draw a token");
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    function probs() {
      var m = Math.max.apply(null, CANDS.map(function (c) { return c[1]; }));
      var e = CANDS.map(function (c) { return Math.exp((c[1] - m) / T); }), z = e.reduce(function (a, b) { return a + b; }, 0);
      var p = e.map(function (v) { return v / z; });
      var order = p.map(function (v, i) { return i; }).sort(function (a, b) { return p[b] - p[a]; }), keep = {}, cum = 0;
      for (var k = 0; k < order.length; k++) { keep[order[k]] = 1; cum += p[order[k]]; if (cum >= P) break; }
      var kz = 0; p.forEach(function (v, i) { if (keep[i]) kz += v; });
      return { p: p, keep: keep, q: p.map(function (v, i) { return keep[i] ? v / kz : 0; }) };
    }
    btn.addEventListener("click", function () {
      var r = probs(), u = rnd(), acc = 0;
      for (var i = 0; i < CANDS.length; i++) { acc += r.q[i]; if (u <= acc) { drawn = i; break; } }
      if (drawn == null) drawn = 0;
      draw();
    });
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), BW = nw ? 190 : 330, r = probs(), svg = EZ.svg(host, nw ? 340 : 520, 236, "Next-token probabilities");
      EZ.text(svg, 10, 20, nw ? "(illustrative scores)" : 'After "The weather today is"  (illustrative scores)', "s m", "start");
      CANDS.forEach(function (c, i) {
        var y = 34 + i * 32, w = BW * r.q[i], w0 = BW * r.p[i];
        EZ.text(svg, 76, y + 19, c[0], i === drawn ? "b ac-t" : "", "end");
        EZ.rect(svg, 86, y + 4, Math.max(1.5, w0), 22, "bx" + (r.keep[i] ? "" : " tn-w"), 4);
        if (r.keep[i]) EZ.rect(svg, 86, y + 7, Math.max(2, w), 16, "fill-a", 3);
        EZ.text(svg, 92 + Math.max(w, w0), y + 20, r.keep[i] ? (r.q[i] * 100).toFixed(1) + "%" : "cut", r.keep[i] ? "s" : "s wn-t", "start");
      });
      var kept = Object.keys(r.keep).length;
      read.innerHTML = "<b>" + kept + " of " + CANDS.length + "</b> tokens survive top-p " + P.toFixed(2) + ". Favourite: <b>" + (r.q[0] * 100).toFixed(1) + "%</b>." +
        (drawn != null ? " Drew: <b>" + CANDS[drawn][0] + "</b>." : "") + " Grey bar = probability before top-p, blue = after rescaling.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
