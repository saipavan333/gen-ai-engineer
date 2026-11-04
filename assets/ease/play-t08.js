/* Pass 2 interactives, Section 8 (Serving & cost). All numbers are computed from the slider values;
   the speeds are illustrative, the prices are the verified list prices used on the lesson pages. */
(function () {
  var EZ = window.EZ;
  function niceMax(v) {
    var steps = [1, 2, 5, 10, 15, 20, 30, 40, 60, 80, 100];
    for (var i = 0; i < steps.length; i++) if (v <= steps[i]) return steps[i];
    return Math.ceil(v / 20) * 20;
  }
  function tickStep(m) { return m <= 2 ? 0.5 : m <= 5 ? 1 : m <= 10 ? 2 : m <= 20 ? 5 : m <= 40 ? 10 : 20; }

  /* 8.2 streamed vs not streamed on one timeline */
  EZ.plays.streaming = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ttft = 0.8, tps = 50, n = 600;
    EZ.slider(bar, "prefill (TTFT)", 0.1, 3, 0.1, ttft, function (v) { return v.toFixed(1) + " s"; }, function (v) { ttft = v; draw(); });
    EZ.slider(bar, "speed", 10, 150, 5, tps, function (v) { return v + " tok/s"; }, function (v) { tps = v; draw(); });
    EZ.slider(bar, "answer length", 50, 1500, 50, n, function (v) { return v + " tokens"; }, function (v) { n = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 560, H = nw ? 250 : 220;
      var dec = n / tps, total = ttft + dec, mx = niceMax(total);
      var x0 = nw ? 12 : 120, x1 = W - 16, sx = function (t) { return x0 + (x1 - x0) * t / mx; };
      var svg = EZ.svg(host, W, H, "Timeline of a streamed and a non-streamed answer");
      var lanes = [["Not streamed", false], ["Streamed", true]];
      lanes.forEach(function (ln, k) {
        var y = nw ? 22 + k * 86 : 34 + k * 74;
        if (nw) EZ.text(svg, 12, y, ln[0], "b", "start"); else EZ.text(svg, x0 - 12, y + 30, ln[0], "b", "end");
        var yb = nw ? y + 10 : y + 8;
        if (!ln[1]) {
          EZ.rect(svg, sx(0), yb, sx(total) - sx(0), 34, "bx tn-w", 4);
          EZ.text(svg, (sx(0) + sx(total)) / 2, yb + 22, "blank screen", "s wn-t");
          EZ.rect(svg, sx(total) - 4, yb - 4, 8, 42, "fill-a", 2);
          EZ.text(svg, sx(total), yb + 56, "all text at " + total.toFixed(1) + " s", "s b", sx(total) > x1 - 60 ? "end" : "middle");
        } else {
          EZ.rect(svg, sx(0), yb, Math.max(1, sx(ttft) - sx(0)), 34, "bx tn-w", 4);
          var chunks = Math.max(4, Math.min(60, Math.round(n / 25)));
          for (var i = 0; i < chunks; i++) {
            var a = sx(ttft + dec * i / chunks), b = sx(ttft + dec * (i + 1) / chunks);
            EZ.rect(svg, a + 0.5, yb + 4, Math.max(1, b - a - 1.5), 26, "fill-a", 1);
          }
          EZ.text(svg, sx(ttft), yb + 56, "first words at " + ttft.toFixed(1) + " s", "s ac-t", sx(ttft) < x0 + 70 ? "start" : "middle");
        }
      });
      var ya = nw ? 214 : 186;
      EZ.s("line", { x1: sx(0), y1: ya, x2: sx(mx), y2: ya, "class": "ln thin" }, svg);
      var st = tickStep(mx);
      for (var t = 0; t <= mx + 1e-9; t += st) {
        EZ.s("line", { x1: sx(t), y1: ya, x2: sx(t), y2: ya + 5, "class": "ln thin" }, svg);
        EZ.text(svg, sx(t), ya + 19, (st < 1 ? t.toFixed(1) : t) + " s", "s m");
      }
      var hidden = total - ttft;
      read.innerHTML = "Decode: " + n + " tokens / " + tps + " per s = <b>" + dec.toFixed(1) + " s</b>. Both finish at <b>" + total.toFixed(1) + " s</b>. " +
        "Streaming puts words on screen at <b>" + ttft.toFixed(1) + " s</b>, hiding " + hidden.toFixed(1) + " s (" + Math.round(100 * hidden / total) + "%) of the wait. Speeds are illustrative; measure your own.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 8.7 where the tokens and the dollars of one request go */
  var MODELS = [["Haiku 5.5", 0.10, 0.50], ["Sonnet 5.5", 2, 10], ["Opus 5.5", 4, 20]];
  EZ.plays.tokenbudget = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), mi = 1;
    var parts = [["system prompt", 1200, 10000, 100, "fill-c"], ["retrieved context", 4000, 20000, 250, "fill-k"], ["chat history", 2000, 30000, 250, "fill-p"], ["output", 300, 2000, 25, "fill-a"]];
    var val = parts.map(function (p) { return p[1]; });
    EZ.buttons(bar, MODELS.map(function (m) { var f = function (x) { return x < 1 ? x.toFixed(2) : String(x); }; return m[0] + " $" + f(m[1]) + " / $" + f(m[2]); }), mi, function (i) { mi = i; draw(); });
    var bar2 = EZ.el("div", { "class": "ez-ctl" }, stage);
    parts.forEach(function (p, k) {
      EZ.slider(bar2, p[0], 0, p[2], p[3], p[1], function (v) { return v.toLocaleString("en-US"); }, function (v) { val[k] = v; draw(); });
    });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function money(x) { return x >= 100 ? "$" + Math.round(x).toLocaleString("en-US") : x >= 1 ? "$" + x.toFixed(2) : "$" + x.toFixed(x >= 0.01 ? 4 : 5); }
    function draw() {
      EZ.clear(host);
      var m = MODELS[mi], nw = EZ.narrow(stage), W = nw ? 340 : 560;
      var cost = val.map(function (v, k) { return v * (k === 3 ? m[2] : m[1]) / 1e6; });
      var tTot = val.reduce(function (a, b) { return a + b; }, 0), cTot = cost.reduce(function (a, b) { return a + b; }, 0);
      var H = nw ? 300 : 236, svg = EZ.svg(host, W, H, "Tokens and cost of one request, split by part");
      var lx = nw ? 12 : 80, bw = W - lx - 14;
      [["tokens", val, tTot], ["cost", cost, cTot]].forEach(function (row, r) {
        var y = nw ? 12 + r * 62 : 16 + r * 56;
        if (nw) EZ.text(svg, 12, y + 12, r ? "share of the cost" : "share of the tokens", "s b", "start");
        else EZ.text(svg, lx - 10, y + 26, r ? "cost" : "tokens", "s b", "end");
        var yb = nw ? y + 20 : y + 6, x = lx;
        if (row[2] <= 0) { EZ.rect(svg, lx, yb, bw, 30, "bx", 4); return; }
        row[1].forEach(function (v, k) {
          var w = bw * v / row[2];
          if (w > 0) EZ.rect(svg, x, yb, Math.max(0, w - 1.5), 30, parts[k][4], 3);
          x += w;
        });
      });
      var y = nw ? 150 : 134;
      parts.forEach(function (p, k) {
        var yy = y + k * (nw ? 36 : 24);
        EZ.rect(svg, 12, yy - 11, 14, 14, p[4], 3);
        if (nw) {
          EZ.text(svg, 32, yy + 1, p[0], "s b", "start");
          EZ.text(svg, 32, yy + 18, val[k].toLocaleString("en-US") + " tok · " + money(cost[k]) + " · " + (cTot ? Math.round(100 * cost[k] / cTot) : 0) + "% of cost", "s", "start");
        } else {
          EZ.text(svg, 32, yy + 1, p[0], "s b", "start");
          EZ.text(svg, 190, yy + 1, val[k].toLocaleString("en-US") + " tokens", "s", "start");
          EZ.text(svg, 330, yy + 1, money(cost[k]), "s", "start");
          EZ.text(svg, 430, yy + 1, (tTot ? Math.round(100 * val[k] / tTot) : 0) + "% tok, " + (cTot ? Math.round(100 * cost[k] / cTot) : 0) + "% cost", "s m", "start");
        }
      });
      var big = 0; cost.forEach(function (c, k) { if (c > cost[big]) big = k; });
      read.innerHTML = "On " + m[0] + ": <b>" + money(cTot) + "</b> a request, <b>" + money(cTot * 1e6) + "</b> per 1 million requests. " +
        "Biggest cost: <b>" + parts[big][0] + "</b>, so trim that first." + (mi === 0 ? " (Haiku 5.5 price applies to prompts up to 100K tokens.)" : "") +
        " Output is priced " + (m[2] / m[1]) + "x input, which is why its share of the cost is bigger than its share of the tokens.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
