/* Pass 2 interactives, Section 14 (track10 pages). Prices are Anthropic list prices per million tokens
   (Sonnet 5.5 $2 in / $10 out, cache read $0.10, 5-minute cache write $2.50; Haiku 5.5 $0.10 in / $0.50 out).
   Token counts per chat are illustrative and stated on the picture. Everything else is computed. */
(function () {
  var EZ = window.EZ;

  var P = 3000, U = 500, O = 300;                       /* cached prefix, new input, output (illustrative) */
  var S = { inp: 2.0, out: 10.0, read: 0.10, write: 2.50 }, HK = { inp: 0.10, out: 0.50 };
  function sonnetParts(h) { return [P * (h * S.read + (1 - h) * S.write) / 1e3, U * S.inp / 1e3, O * S.out / 1e3]; } /* $ per 1,000 chats */
  function haiku() { return (P + U) * HK.inp / 1e3 + O * HK.out / 1e3; }
  var BASE = [P * S.inp / 1e3, U * S.inp / 1e3, O * S.out / 1e3];  /* all Sonnet, no prompt caching */
  function tot(a) { return a.reduce(function (s, v) { return s + v; }, 0); }
  var BREAK = (S.write - S.inp) / (S.write - S.read);  /* hit rate where caching starts to pay */

  EZ.plays.chatcost = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), h = 0.6, r = 0.5;
    EZ.slider(bar, "prompt-cache hit rate", 0, 0.95, 0.05, h, function (v) { return Math.round(v * 100) + "%"; }, function (v) { h = v; draw(); });
    EZ.slider(bar, "routed to Haiku", 0, 1, 0.05, r, function (v) { return Math.round(v * 100) + "%"; }, function (v) { r = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);

    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 620;
      var lx = nw ? 12 : 168, BW = nw ? 290 : 380, k = BW / 10;  /* $10 per 1,000 fills the bar */
      var sp = sonnetParts(h), hk = haiku();
      var mix = [(1 - r) * sp[0], (1 - r) * sp[1], (1 - r) * sp[2], r * hk];
      var y0 = nw ? 50 : 40, H = nw ? 430 : 360;
      var svg = EZ.svg(host, W, H, "Cost per 1,000 chats for the chosen cache hit rate and routing share");
      EZ.text(svg, 12, 18, nw ? "Cost per 1,000 chats" : "Cost per 1,000 chats. Illustrative tokens per chat: 3,000 cached prefix + 500 new input + 300 output.", "s m", "start", 12);
      if (nw) EZ.text(svg, 12, 34, "tokens/chat: 3,000 prefix + 500 new + 300 out", "s m", "start", 12);
      var CLS = ["fill-c", "fill-p", "fill-k", "fill-g"];
      [["All Sonnet, no cache", BASE], ["Your mix", mix]].forEach(function (row, i) {
        var y = y0 + i * (nw ? 58 : 46), x = lx, by = nw ? y + 8 : y;
        if (nw) EZ.text(svg, 12, y, row[0], "s b", "start");
        else EZ.text(svg, lx - 10, y + 17, row[0], "s b", "end");
        row[1].forEach(function (v, j) { var w = v * k; if (w > 0.3) EZ.rect(svg, x, by, w, 24, CLS[j], 3); x += w; });
        if (nw) EZ.text(svg, W - 12, y, "$" + tot(row[1]).toFixed(2), "s b", "end");
        else EZ.text(svg, x + 6, by + 17, "$" + tot(row[1]).toFixed(2), "s b", "start");
      });
      var ly = y0 + (nw ? 128 : 100), names = ["prefix (Sonnet)", "new input (Sonnet)", "output (Sonnet)", "Haiku, all tokens"];
      names.forEach(function (n, j) {
        var cx = nw ? 12 + (j % 2) * 165 : 12 + j * 150, cy = nw ? ly + Math.floor(j / 2) * 20 : ly;
        EZ.rect(svg, cx, cy - 10, 12, 12, CLS[j], 2); EZ.text(svg, cx + 18, cy, n, "s", "start", 12);
      });
      /* panel 2: prefix cost on the Sonnet path vs hit rate, with the break-even point */
      var py = ly + (nw ? 64 : 44), ph = nw ? 120 : 110, ax = nw ? 44 : 168, AL = nw ? 280 : 400, ymax = 8;
      EZ.text(svg, 12, py, nw ? "Prefix cost per 1,000 Sonnet chats" : "Prefix cost per 1,000 Sonnet chats as the hit rate grows", "s b", "start", 13);
      var top = py + 16, bot = top + ph;
      function X(v) { return ax + AL * v; } function Y(v) { return bot - ph * v / ymax; }
      EZ.s("line", { x1: ax, y1: bot, x2: ax + AL, y2: bot, "class": "grid" }, svg);
      EZ.s("line", { x1: ax, y1: top, x2: ax, y2: bot, "class": "grid" }, svg);
      [0, 4, 8].forEach(function (v) { EZ.text(svg, ax - 6, Y(v) + 4, "$" + v, "s m", "end", 12); });
      [0, 0.5, 1].forEach(function (v) { EZ.text(svg, X(v), bot + 16, Math.round(v * 100) + "%", "s m", "middle", 12); });
      var noCache = P * S.inp / 1e3;
      EZ.s("line", { x1: ax, y1: Y(noCache), x2: ax + AL, y2: Y(noCache), "class": "ln thin dash" }, svg);
      EZ.text(svg, ax + AL, Y(noCache) - 6, "no caching $" + noCache.toFixed(2), "s m", "end", 12);
      EZ.s("line", { x1: X(0), y1: Y(sonnetParts(0)[0]), x2: X(1), y2: Y(sonnetParts(1)[0]), "class": "ln ac" }, svg);
      EZ.s("line", { x1: X(BREAK), y1: top, x2: X(BREAK), y2: bot, "class": "ln wn dash" }, svg);
      EZ.text(svg, X(BREAK) + 6, top + 10, "break-even " + (BREAK * 100).toFixed(0) + "%", "s wn-t", "start", 12);
      EZ.s("circle", { cx: X(h), cy: Y(sp[0]), r: 7, "class": "fill-a" }, svg);
      EZ.s("circle", { cx: X(h), cy: Y(sp[0]), r: 12, "class": "ring" }, svg);
      EZ.text(svg, 12, bot + 40, nw ? "Misses pay the cache write price ($2.50)." : "Below break-even, caching costs more: every miss pays the $2.50 cache write instead of $2 input.", "s", "start", 12);
      var t = tot(mix), b = tot(BASE);
      read.innerHTML = "<b>$" + t.toFixed(2) + "</b> per 1,000 chats, <b>" + Math.round((1 - t / b) * 100) + "% less</b> than all-Sonnet without caching ($" + b.toFixed(2) + "). At a million chats a day that is $" + Math.round(t * 1000).toLocaleString("en-US") +
        " a day. Haiku's own cache price isn't used here, so its path is priced without caching. Routing only saves money if the small model answers those messages well enough: check it with your eval.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
