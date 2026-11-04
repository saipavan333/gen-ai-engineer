/* Pass 2 interactives, Section 11 (Going deeper). Reciprocal Rank Fusion exactly as multi_query.py on
   lesson 11.1: for each query, for rank, chunk in enumerate(results): score[chunk] += 1 / (60 + rank).
   The ranked lists are illustrative. */
(function () {
  var EZ = window.EZ;
  var CHUNKS = { A: "2.0 upgrade guide", B: "general FAQ", C: "2.0 known bugs", D: "release notes 2.0", E: "login help", F: "pricing page", G: "old 1.x errors", H: "changelog" };
  var QUERIES = [
    ["original: “why's it broken since the update?”", ["E", "A", "F", "B", "G", "H"]],
    ["rewrite: “errors after version 2.0 upgrade”", ["C", "D", "A", "E", "B", "F"]],
    ["variant: “bug introduced in release 2.0”", ["C", "A", "D", "H", "E", "G"]],
    ["variant: “2.0 upgrade known issues”", ["D", "C", "A", "B", "F", "E"]]
  ];
  var TONE = { A: "fill-c", B: "fill-m", C: "fill-g", D: "fill-p", E: "fill-k", F: "fill-m", G: "fill-m", H: "fill-m" };
  EZ.plays.rrf = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), on = [true, false, false, false];
    var labels = ["original", "rewrite", "variant 2", "variant 3"];
    labels.forEach(function (l, i) {
      var b = EZ.el("button", { type: "button", "aria-pressed": on[i] ? "true" : "false" }, bar, l);
      if (on[i]) b.className = "on";
      b.addEventListener("click", function () {
        on[i] = !on[i];
        if (!on.some(Boolean)) on[i] = true;   // keep at least one list
        b.className = on[i] ? "on" : ""; b.setAttribute("aria-pressed", on[i] ? "true" : "false"); draw();
      });
    });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, score = {}, used = 0;
      QUERIES.forEach(function (q, i) {
        if (!on[i]) return; used++;
        q[1].forEach(function (c, rank) { score[c] = (score[c] || 0) + 1 / (60 + rank); });
      });
      var ranked = Object.keys(score).sort(function (a, b) { return score[b] - score[a] || (a < b ? -1 : 1); });
      var top = ranked.slice(0, 5);
      var cw = nw ? 44 : 50, rowH = nw ? 58 : 50, listH = QUERIES.length * rowH;
      var barTop = 30 + listH + 30, H = barTop + ranked.length * 26 + 14;
      var svg = EZ.svg(host, W, H, "Ranked lists for each query version and their fused scores");
      EZ.text(svg, 12, 18, "Each query's top 6 (rank 0 is best)", "s b", "start");
      QUERIES.forEach(function (q, i) {
        var y = 30 + i * rowH, act = on[i];
        var t = EZ.text(svg, 12, y + 12, q[0], act ? "s" : "s m", "start");
        if (!act) t.setAttribute("opacity", ".55");
        q[1].forEach(function (c, rank) {
          var x = 12 + rank * (cw + 6), yy = y + 18;
          var r = EZ.rect(svg, x, yy, cw, 24, act ? TONE[c] : "bx", 4);
          EZ.text(svg, x + cw / 2, yy + 17, c, "b", "middle", 13).setAttribute("style", act ? "fill:var(--bg);font-size:13px" : "font-size:13px;opacity:.5");
        });
      });
      EZ.text(svg, 12, barTop - 10, nw ? "Fused: add 1 / (60 + rank) per list" : "Fused score = sum of 1 / (60 + rank) over the lists that are on", "s b", "start");
      var mx = Math.max.apply(null, ranked.map(function (c) { return score[c]; }));
      var lx = nw ? 166 : 210, bw = W - lx - 64;
      ranked.forEach(function (c, i) {
        var y = barTop + i * 26, w = bw * score[c] / mx, isTop = top.indexOf(c) >= 0;
        EZ.text(svg, lx - 8, y + 15, c + " · " + CHUNKS[c], isTop ? "s b" : "s m", "end", nw ? 12 : null);
        EZ.rect(svg, lx, y + 3, w, 16, isTop ? "fill-a" : "fill-m", 3);
        EZ.text(svg, lx + w + 6, y + 16, score[c].toFixed(4), "s", "start");
      });
      read.innerHTML = "<b>" + used + " list" + (used > 1 ? "s" : "") + "</b> fused. Top 5 sent to the model: <b>" + top.join(", ") + "</b>. " +
        (used === 1 ? "With one list, fusion just keeps its order, so the vague original question puts “" + CHUNKS[ranked[0]] + "” first. Turn on the rewrites." :
          "A chunk that shows up high in many lists (" + ranked[0] + ", " + CHUNKS[ranked[0]] + ") beats one that is first in a single list.");
    }
    draw(); EZ.watch(stage, draw);
  };
})();
