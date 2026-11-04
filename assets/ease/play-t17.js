/* Pass 2 interactives, Section 17 (GenAI on your data platform). Inputs are lesson 17.1's own:
   120 input + 5 output tokens per call, Claude Haiku 5.5 list price $0.10 / $0.50 per million tokens (checked 2026-11-03).
   The Lab 10 preset is labs/10_ai_sql_udf.py: 6 rows, 2 AI columns, review 6 duplicates review 1 -> 12 AI cells, 10 calls. */
(function () {
  var EZ = window.EZ;
  var TIN = 120, TOUT = 5, PIN = 0.10, POUT = 0.50;
  var PER_CALL = TIN * PIN / 1e6 + TOUT * POUT / 1e6;
  var ROWS = [6, 100, 1000, 10000, 60000, 100000, 1000000, 2000000, 12000000, 50000000, 100000000];

  function n(v) { return Math.round(v).toLocaleString("en-US"); }
  function usd(v) {
    if (v >= 1) return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (v >= 0.01) return "$" + v.toFixed(2);
    return "$" + v.toPrecision(2);
  }
  function short(v) { return v >= 1e6 ? (v / 1e6).toLocaleString("en-US", { maximumFractionDigits: 1 }) + " M" : v >= 1e4 ? (v / 1e3).toLocaleString("en-US") + " K" : String(v); }

  EZ.plays.dedupe = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ri = 8, share = 75, cols = 1;
    var PRESETS = [["Marketplace back-fill (12 M)", 8, 75, 1], ["Lab 10 (6 rows)", 0, 83, 2]];
    var rS, sS, cS;
    EZ.buttons(bar, PRESETS.map(function (p) { return p[0]; }), 0, function (i) {
      var p = PRESETS[i];
      rS.value = p[1]; sS.value = p[2]; cS.value = p[3];
      [rS, sS, cS].forEach(function (r) { r.dispatchEvent(new Event("input")); });
    });
    rS = EZ.slider(bar, "rows", 0, ROWS.length - 1, 1, ri, function (v) { return short(ROWS[v]); }, function (v) { ri = v; draw(); });
    sS = EZ.slider(bar, "distinct texts", 5, 100, 1, share, function (v) { return v + "%"; }, function (v) { share = v; draw(); });
    cS = EZ.slider(bar, "AI columns", 1, 3, 1, cols, null, function (v) { cols = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);

    function draw() {
      EZ.clear(host);
      var rows = ROWS[ri], distinct = Math.max(1, Math.round(rows * share / 100));
      var without = rows * cols, withd = distinct * cols, saved = without - withd;
      var nw = EZ.narrow(stage), W = nw ? 340 : 620, x0 = 12, lab = nw ? 0 : 190, bw = W - x0 - lab - 16;
      var small = rows <= 24, cellH = 0;
      if (small) cellH = 34 + rows * 22;
      var H = (nw ? 156 : 126) + cellH + 4;
      var svg = EZ.svg(host, W, H, "Model calls with and without SELECT DISTINCT");
      EZ.text(svg, x0, 18, short(rows) + " rows × " + cols + " AI column" + (cols > 1 ? "s" : "") + ", " + share + "% distinct", "b", "start", 14);
      var bars = [["without dedupe", without, "fill-w"], ["SELECT DISTINCT first", withd, "fill-g"]];
      var y = 32;
      bars.forEach(function (b) {
        if (nw) { EZ.text(svg, x0, y + 12, b[0], "s", "start", 12); y += 16; }
        else EZ.text(svg, x0 + lab - 10, y + 17, b[0], "s b", "end", 13);
        var w = Math.max(3, bw * b[1] / without), bx = x0 + lab;
        EZ.rect(svg, bx, y + 2, w, 22, b[2], 4);
        var t = n(b[1]) + " calls · " + usd(b[1] * PER_CALL);
        var inside = w > t.length * 7.4 + 14;
        EZ.text(svg, inside ? bx + w - 8 : bx + w + 6, y + 18, t, inside ? "badge-t" : "s b", inside ? "end" : "start", 13);
        y += 32;
      });
      EZ.text(svg, x0, y + 10, "Saved: " + n(saved) + " calls (" + Math.round(100 * saved / without) + "% of the calls)", "s ac-t", "start", 13);
      y += 26;
      if (small) {
        /* the real cells: duplicates are the last rows, each a copy of an earlier one (as in Lab 10, row 6 = row 1) */
        EZ.text(svg, x0, y + 12, "Every AI cell: blue = a model call, grey = duplicate text, no call", "s m", "start", 12);
        y += 22;
        var cw = nw ? 58 : 80;
        for (var r = 0; r < rows; r++) {
          var dup = r >= distinct;
          EZ.text(svg, x0, y + 15, "row " + (r + 1) + (dup ? " = row " + ((r - distinct) % distinct + 1) : ""), dup ? "s m" : "s", "start", 12);
          for (var c = 0; c < cols; c++) {
            var cx = x0 + (nw ? 112 : 130) + c * (cw + 6);
            EZ.rect(svg, cx, y + 2, cw, 18, dup ? "bx" : "fill-a", 3);
            EZ.text(svg, cx + cw / 2, y + 15, dup ? "cache" : "call", dup ? "s m" : "badge-t", "middle", 12);
          }
          y += 22;
        }
      }
      read.innerHTML = "Without dedupe: <b>" + n(without) + " calls</b> (" + usd(without * PER_CALL) + "). With SELECT DISTINCT before the AI function: <b>" + n(withd) +
        " calls</b> (" + usd(withd * PER_CALL) + "). Priced at " + TIN + " input + " + TOUT + " output tokens a call, Claude Haiku 5.5 list price ($0.10 / $0.50 per million, checked 2026-11-03)." +
        (rows === 6 && cols === 2 && withd === 10 ? " This is Lab 10: 12 AI cells, 10 model calls." : "");
    }
    draw(); EZ.watch(stage, draw);
  };
})();
