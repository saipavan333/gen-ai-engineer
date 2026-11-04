/* Pass 2 interactives, Track 6. Intervals are computed (Wilson score, z = 1.96); the judge is illustrative. */
(function () {
  var EZ = window.EZ;

  /* 6.2 how wide is the 95% Wilson interval for k passes out of n cases? */
  function wilson(k, n) {
    var z = 1.96, p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d;
    var h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d;
    return [Math.max(0, c - h), Math.min(1, c + h)];
  }
  var NS = [10, 20, 30, 50, 100, 200, 400, 1000];
  EZ.plays.goldensize = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ni = 1, rate = 85;
    EZ.slider(bar, "golden cases n", 0, NS.length - 1, 1, ni, function (v) { return String(NS[v]); }, function (v) { ni = v; draw(); });
    EZ.slider(bar, "observed pass rate", 50, 99, 1, rate, function (v) { return v + "%"; }, function (v) { rate = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, lab = nw ? 62 : 90, ax0 = 12 + lab, aw = W - ax0 - (nw ? 16 : 40);
      var rowH = 30, top = 58, H = top + NS.length * rowH + 40;
      var lo = 40, hi = 100;
      function X(p) { return ax0 + (p * 100 - lo) / (hi - lo) * aw; }
      var svg = EZ.svg(host, W, H, "95% Wilson intervals for different golden-set sizes");
      EZ.text(svg, 12, 20, "Same pass rate, different numbers of cases", "b", "start", nw ? 14 : 15);
      EZ.text(svg, 12, 40, "bar = 95% Wilson interval · dot = observed rate", "s m", "start", 12);
      [40, 50, 60, 70, 80, 90, 100].forEach(function (t) {
        var x = X(t / 100);
        EZ.s("line", { x1: x, y1: top - 4, x2: x, y2: top + NS.length * rowH, "class": "grid" }, svg);
        if (!nw || t % 20 === 0) EZ.text(svg, x, top + NS.length * rowH + 18, t + "%", "s m", "middle", 12);
      });
      NS.forEach(function (n, i) {
        var k = Math.round(rate / 100 * n), p = k / n, ci = wilson(k, n), y = top + i * rowH, me = i === ni;
        EZ.text(svg, ax0 - 10, y + 17, "n = " + n, me ? "s b" : "s m", "end", 12);
        if (me) EZ.rect(svg, 12, y, W - 24, rowH - 2, "bx tn-a", 6);
        var x1 = X(Math.max(ci[0], lo / 100)), x2 = X(ci[1]);
        EZ.rect(svg, x1, y + 9, Math.max(3, x2 - x1), 10, me ? "fill-a" : "fill-m", 4);
        if (ci[0] < lo / 100) EZ.text(svg, x1 + 2, y + 8, "◂ off scale", "s m", "start", 12);
        EZ.s("circle", { cx: X(p), cy: y + 14, r: me ? 6 : 4, "class": "fill-k" }, svg);
      });
      var n = NS[ni], k = Math.round(rate / 100 * n), ci = wilson(k, n);
      read.innerHTML = "<b>" + k + " of " + n + "</b> pass = " + (k / n * 100).toFixed(1) + "%. 95% Wilson interval: <b>" + (ci[0] * 100).toFixed(1) + "% to " + (ci[1] * 100).toFixed(1) + "%</b> (" +
        ((ci[1] - ci[0]) * 100).toFixed(1) + " points wide). " + (n <= 30 ? "With this few cases a 10-point change can be pure noise." : (n >= 400 ? "Now a few points of change start to mean something." : "Better, but small slices are still noisy."));
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 6.3 a made-up judge: score = true quality (0-10) + a bonus for whatever sits in slot 1 */
  var PAIRS = [["Pair 1: A clearly better", 8.0, 4.0], ["Pair 2: nearly equal", 6.5, 6.0], ["Pair 3: B a bit better", 5.0, 6.5]];
  EZ.plays.judgeswap = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), pi = 1, order = 0, bias = 1.0;
    EZ.buttons(bar, PAIRS.map(function (p) { return p[0]; }), pi, function (i) { pi = i; draw(); });
    var b2 = EZ.el("div", { "class": "ez-ctl" }, stage);
    EZ.buttons(b2, ["Order A, B", "Order B, A"], order, function (i) { order = i; draw(); });
    EZ.slider(b2, "slot-1 bonus", 0, 2, 0.1, bias, function (v) { return v.toFixed(1); }, function (v) { bias = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function verdict(o) {
      var p = PAIRS[pi], slots = o === 0 ? [["A", p[1]], ["B", p[2]]] : [["B", p[2]], ["A", p[1]]];
      var s1 = slots[0][1] + bias, s2 = slots[1][1];
      return { slots: slots, s: [s1, s2], win: s1 >= s2 ? slots[0][0] : slots[1][0] };
    }
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, v = verdict(order), v0 = verdict(0), v1 = verdict(1);
      var H = nw ? 300 : 270, svg = EZ.svg(host, W, H, "The same pair judged in both orders");
      EZ.text(svg, 12, 20, "Judge's scores out of 10 (illustrative biased judge)", "s m", "start", 12);
      var bx = nw ? 96 : 120, bw = W - bx - (nw ? 56 : 160), sc = bw / 12;
      v.slots.forEach(function (s, i) {
        var y = 40 + i * 58, q = s[1], bonus = i === 0 ? bias : 0, win = v.win === s[0];
        EZ.text(svg, 12, y + 18, "slot " + (i + 1) + ": " + s[0], win ? "b ac-t" : "b", "start", 14);
        EZ.text(svg, 12, y + 36, "quality " + q.toFixed(1), "s m", "start", 12);
        EZ.rect(svg, bx, y + 6, q * sc, 26, s[0] === "A" ? "fill-c" : "fill-k", 4);
        if (bonus > 0) EZ.rect(svg, bx + q * sc + 2, y + 6, bonus * sc, 26, "fill-w", 4);
        EZ.text(svg, bx + (q + bonus) * sc + 8, y + 24, (q + bonus).toFixed(1) + (win ? "  wins" : ""), win ? "b ac-t" : "s", "start", 13);
      });
      EZ.rect(svg, 12, 156, 14, 14, "fill-w", 3);
      EZ.text(svg, 32, 168, "red = bonus for sitting in slot 1 (the bias)", "s", "start", 12);
      var agree = v0.win === v1.win, y = 190;
      EZ.rect(svg, 12, y, W - 24, nw ? 96 : 66, agree ? "bx tn-g" : "bx tn-w", 10);
      if (nw) {
        EZ.text(svg, 24, y + 24, "A, B order → " + v0.win + " wins", order === 0 ? "b" : "s", "start", 13);
        EZ.text(svg, 24, y + 44, "B, A order → " + v1.win + " wins", order === 1 ? "b" : "s", "start", 13);
        EZ.text(svg, 24, y + 74, agree ? "Agree: count a win for " + v0.win : "Flip: position bias → tie", agree ? "b ok-t" : "b wn-t", "start", 14);
      } else {
        EZ.text(svg, 28, y + 26, "Order A, B → " + v0.win + " wins  ·  Order B, A → " + v1.win + " wins", "s", "start", 13);
        EZ.text(svg, 28, y + 50, agree ? "Both orders agree: count a win for " + v0.win : "The verdict flips with the order: position bias. Count it as a tie.", agree ? "b ok-t" : "b wn-t", "start", 14);
      }
      var gap = Math.abs(PAIRS[pi][1] - PAIRS[pi][2]);
      read.innerHTML = "Quality gap " + gap.toFixed(1) + " vs slot-1 bonus " + bias.toFixed(1) + ". " +
        (agree ? "The real gap is bigger than the bias, so swapping the order doesn't change the winner." : "The bias is bigger than the real gap, so whoever goes first wins. One run in one order would have reported a fake win.") +
        " These numbers are made up to show the mechanism; measure your own judge's flip rate.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
