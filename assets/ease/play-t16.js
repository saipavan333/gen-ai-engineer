/* Pass 2 interactives, Section 16 (Get hired). Numbers come from lesson 16.1: 6-8 hours a week for about
   ten weeks, five phases of two weeks each. So each phase is 12-16 hours and the plan is 60-80 hours in all. */
(function () {
  var EZ = window.EZ;

  var PHASES = [["Foundations", "k"], ["RAG", "c"], ["Agents + tuning", "p"], ["Eval, safety, serving", "g"], ["Interview + apply", "a"]];
  var LO = 6, HI = 8, WEEKS = 10, PER_LO = 2 * LO, PER_HI = 2 * HI, PER_MID = (PER_LO + PER_HI) / 2;

  function fmt(w) { return w < 10 ? w.toFixed(1).replace(/\.0$/, "") : String(Math.round(w)); }

  EZ.plays.studyplan = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), h = 7;
    EZ.slider(bar, "hours a week", 2, 20, 1, h, function (v) { return v + " h"; }, function (v) { h = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 620, lx = nw ? 12 : 150, gw = W - lx - 14;
      var perW = PER_MID / h, total = perW * PHASES.length, span = Math.max(WEEKS, Math.ceil(total / 5) * 5);
      var sx = gw / span, rowH = nw ? 44 : 34, top = 54;
      var H = top + PHASES.length * rowH + 58;
      var svg = EZ.svg(host, W, H, "Weeks to finish the plan at " + h + " hours a week");
      EZ.text(svg, 12, 18, nw ? "Each phase = " + PER_LO + "–" + PER_HI + " h of study" : "Each phase is " + PER_LO + "–" + PER_HI + " hours (2 weeks × " + LO + "–" + HI + " h). Bars use the middle, " + PER_MID + " h.", "s m", "start");
      /* week ticks */
      var step = span <= 10 ? 1 : 5;
      for (var k = 0; k <= span; k += step) {
        var x = lx + k * sx;
        EZ.s("line", { x1: x, y1: top - 8, x2: x, y2: top + PHASES.length * rowH, "class": "grid" }, svg);
        if (!nw || k % (span <= 10 ? 2 : 10) === 0 || k === span) EZ.text(svg, x, top + PHASES.length * rowH + 16, String(k), "s m", "middle", 12);
      }
      EZ.text(svg, lx + gw, top + PHASES.length * rowH + 32, "weeks", "s m", "end", 12);
      /* the page's 10-week reference */
      var rx = lx + WEEKS * sx;
      EZ.s("line", { x1: rx, y1: top - 14, x2: rx, y2: top + PHASES.length * rowH + 4, "class": "ln wn dash" }, svg);
      EZ.text(svg, rx + (rx > W - 120 ? -4 : 4), top - 20, "page's plan: 10 wk", "s wn-t", rx > W - 120 ? "end" : "start", 12);
      PHASES.forEach(function (p, i) {
        var y = top + i * rowH, x0 = lx + i * perW * sx;
        if (nw) EZ.text(svg, 12, y + 13, (i + 1) + ". " + p[0], "s b", "start", 12);
        else EZ.text(svg, lx - 8, y + 21, p[0], "s b", "end", 13);
        var by = nw ? y + 19 : y + 6;
        EZ.rect(svg, x0 + 1, by, Math.max(3, perW * sx - 2), 20, "fill-" + p[1], 4);
        var lab = fmt(perW) + " wk";
        var inside = perW * sx > 52;
        EZ.text(svg, inside ? x0 + perW * sx / 2 : x0 + perW * sx + 4, by + 15, lab, inside ? "badge-t" : "s", inside ? "middle" : "start", 12);
      });
      var y2 = top + PHASES.length * rowH + 48;
      var lo = LO * WEEKS / h, hi = HI * WEEKS / h;
      EZ.text(svg, 12, y2, "Finish in about " + fmt(total) + " weeks (range " + fmt(lo) + "–" + fmt(hi) + ")", "b ac-t", "start", 14);
      read.innerHTML = "At <b>" + h + " h a week</b>, each phase takes about <b>" + fmt(perW) + " weeks</b> and the whole plan about <b>" + fmt(total) + " weeks</b>. " +
        "That is the page's " + (LO * WEEKS) + "–" + (HI * WEEKS) + " hours divided by your weekly hours: " + fmt(lo) + " to " + fmt(hi) + " weeks. " +
        (h < LO ? "Slower than the page's pace: keep the order and the build-as-you-go rule, and expect a longer run." : h > HI ? "Faster than the page's pace: fine, as long as each phase still ends with something built." : "This is the page's own pace.");
    }
    draw(); EZ.watch(stage, draw);
  };
})();
