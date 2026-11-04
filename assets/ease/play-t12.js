/* Pass 2 interactives, Section 12 (track14 pages). Illustrative per-case results; the score and verdict are computed. */
(function () {
  var EZ = window.EZ;

  /* 12.3 an eval gate: 20 golden-set cases, baseline vs a candidate prompt, a pass mark from the slider */
  var INTENTS = ["refunds", "shipping", "account", "billing", "returns"]; /* 4 cases each */
  var BASE = [1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1]; /* v14 live: 17 of 20 pass */
  function cand(fix, brk) { var r = BASE.slice(); fix.forEach(function (i) { r[i] = 1; }); brk.forEach(function (i) { r[i] = 0; }); return r; }
  var CANDS = [
    ["v15a: warmer refund tone", cand([2], [5, 6, 13])],
    ["v15b: tighter format", cand([9, 17], [])],
    ["v15c: new examples", cand([2, 9], [0, 3])]
  ];
  function sum(a) { return a.reduce(function (s, v) { return s + v; }, 0); }

  EZ.plays.evalgate = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ci = 0, thr = 0.85;
    EZ.buttons(bar, CANDS.map(function (c) { return c[0]; }), 0, function (i) { ci = i; draw(); });
    EZ.slider(bar, "pass mark", 0.6, 1.0, 0.05, thr, function (v) { return v.toFixed(2); }, function (v) { thr = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);

    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 620, c = CANDS[ci][1];
      var cw = nw ? 13 : 20, gp = nw ? 2 : 3, grp = nw ? 5 : 10, x0 = nw ? 12 : 120;
      var iy = (nw ? 96 : 90) + 64, ly = iy + 30, ay = ly + 46, vy = ay + 56, H = vy + 40, svg = EZ.svg(host, W, H, "Golden-set results for the baseline and the candidate, and the gate verdict");
      function cx(i) { return x0 + i * (cw + gp) + Math.floor(i / 4) * grp; }
      var rows = [["v14 (live)", BASE], ["candidate", c]];
      if (!nw) EZ.text(svg, x0, 22, "20 golden-set cases, 4 per intent. Green = pass, red = fail.", "s m", "start", 12);
      var yr = nw ? [40, 96] : [40, 90];
      rows.forEach(function (r, k) {
        if (nw) EZ.text(svg, 12, yr[k] - 8, r[0] + ": " + sum(r[1]) + "/20", "s b", "start");
        else EZ.text(svg, x0 - 12, yr[k] + 19, r[0], "s b", "end");
        r[1].forEach(function (v, i) {
          var flip = k === 1 && v !== BASE[i];
          EZ.rect(svg, cx(i), yr[k], cw, 26, v ? "fill-g" : "fill-w", 3);
          if (flip) EZ.rect(svg, cx(i) - 2, yr[k] - 2, cw + 4, 30, "ring", 4);
        });
      });
      c.forEach(function (v, i) {
        if (v === BASE[i]) return;
        EZ.text(svg, cx(i) + cw / 2, yr[1] + 44, v ? "▲" : "▼", v ? "s ok-t" : "s wn-t");
      });
      for (var g = 0; g < 5; g++) EZ.text(svg, cx(g * 4) + (4 * cw + 3 * gp) / 2, iy, INTENTS[g], "s m", "middle", 12);
      /* score axis */
      var ax = nw ? 20 : 120, AL = nw ? 300 : 460, lo = 0.5;
      function sx(v) { return ax + AL * (v - lo) / (1 - lo); }
      var sb = sum(BASE) / 20, sc = sum(c) / 20, pass = !(sc < thr - 1e-9);
      EZ.s("line", { x1: ax, y1: ay, x2: ax + AL, y2: ay, "class": "grid" }, svg);
      [0.5, 0.75, 1.0].forEach(function (t) { EZ.s("line", { x1: sx(t), y1: ay - 4, x2: sx(t), y2: ay + 4, "class": "grid" }, svg); EZ.text(svg, sx(t), ay + 20, t.toFixed(2), "s m", "middle", 12); });
      EZ.rect(svg, ax, ly + 10, sx(sc) - ax, 14, pass ? "fill-g" : "fill-w", 3);
      EZ.text(svg, Math.min(sx(sc) + 6, ax + AL - 30), ly + 22, sc.toFixed(2), "s b", "start");
      EZ.rect(svg, ax, ly + 28, sx(sb) - ax, 8, "fill-m", 2);
      EZ.text(svg, ax, ly, "candidate score (thick) vs v14 " + sb.toFixed(2) + " (thin grey)", "s m", "start", 12);
      EZ.s("line", { x1: sx(thr), y1: ly + 4, x2: sx(thr), y2: ay + 6, "class": "ln wn dash" }, svg);
      /* verdict */
            EZ.rect(svg, 12, vy - 22, W - 24, 36, pass ? "bx tn-g" : "bx tn-w", 8);
      EZ.text(svg, W / 2, vy + 2, pass ? "Merge allowed: " + sc.toFixed(2) + " ≥ " + thr.toFixed(2) : "Merge blocked: " + sc.toFixed(2) + " < " + thr.toFixed(2) + ", exit 1", pass ? "b ok-t" : "b wn-t");
      if (nw) EZ.text(svg, 12, H - 8, "▼ pass→fail   ▲ fail→pass   red dash = pass mark", "s m", "start", 12);
      else EZ.text(svg, 12, H - 6, "Ringed squares changed. ▼ = passed before, fails now. ▲ = fixed. Red dashed line = the pass mark.", "s m", "start", 12);
      var down = [], up = 0;
      c.forEach(function (v, i) { if (BASE[i] && !v) down.push(INTENTS[Math.floor(i / 4)]); if (!BASE[i] && v) up++; });
      var msg = "<b>" + down.length + " pass→fail</b>, <b>" + up + " fail→pass</b>.";
      if (pass && down.length) msg += " The score passed, but " + down.length + " cases that worked before now fail (" + down.join(", ") + "). Comparing case by case, as the page's real-scale box suggests, catches what one number hides.";
      else if (!pass) msg += " The gate fails the build, so this prompt cannot ship until it is fixed.";
      else msg += " Nothing regressed and the score cleared the bar.";
      read.innerHTML = msg + " (Illustrative results on 20 cases; a real golden set has hundreds.)";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
