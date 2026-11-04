/* Pass 2 interactives, Track 5. Every number is computed in the browser from the stated inputs. */
(function () {
  var EZ = window.EZ;
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }

  /* 5.2 gradient descent on a 2-D bowl: loss = (x - 3)^2 + 4 (y - 1)^2, start (-1, 3).
     Gradient = (2(x - 3), 8(y - 1)). Each step: (x, y) -= lr * gradient. */
  EZ.plays.descent = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), lr = 0.1, n = 15;
    EZ.slider(bar, "learning rate", 0.02, 0.3, 0.01, lr, function (v) { return v.toFixed(2); }, function (v) { lr = v; draw(); });
    EZ.slider(bar, "steps", 1, 40, 1, n, null, function (v) { n = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function loss(x, y) { return (x - 3) * (x - 3) + 4 * (y - 1) * (y - 1); }
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 560, H = nw ? 300 : 330;
      var px0 = 12, py0 = 34, pw = W - 24, ph = H - 34 - 40;
      var xmin = -2, xmax = 6, ymin = -1.5, ymax = 3.5;
      function X(x) { return px0 + (x - xmin) / (xmax - xmin) * pw; }
      function Y(y) { return py0 + (ymax - y) / (ymax - ymin) * ph; }
      var svg = EZ.svg(host, W, H, "Gradient descent path on a 2-D loss bowl");
      EZ.text(svg, 12, 20, nw ? "Contours of equal loss (toy bowl)" : "Contours of equal loss on a toy bowl: steep up and down, gentle left and right", "s m", "start");
      EZ.rect(svg, px0, py0, pw, ph, "bx", 8);
      var cid = "ezclip-descent-" + (nw ? "n" : "w"), cp = EZ.s("clipPath", { id: cid }, svg);
      EZ.s("rect", { x: px0, y: py0, width: pw, height: ph, rx: 8 }, cp);
      var cg = EZ.s("g", { "clip-path": "url(#" + cid + ")" }, svg);
      [1, 4, 9, 16, 25, 36].forEach(function (L) {
        var rx = Math.sqrt(L), ry = Math.sqrt(L) / 2;
        EZ.s("ellipse", { cx: X(3), cy: Y(1), rx: rx / (xmax - xmin) * pw, ry: ry / (ymax - ymin) * ph, "class": "grid" }, cg);
      });
      EZ.s("circle", { cx: X(3), cy: Y(1), r: 6, "class": "fill-g" }, svg);
      EZ.text(svg, X(3) + 10, Y(1) + 18, "lowest loss", "s ok-t", "start", 12);
      var x = -1, y = 3, pts = [[x, y]], off = false;
      for (var i = 0; i < n; i++) {
        x = x - lr * 2 * (x - 3); y = y - lr * 8 * (y - 1);
        if (x < xmin || x > xmax || y < ymin || y > ymax) { off = true; break; }
        pts.push([x, y]);
      }
      for (var k = 0; k < pts.length - 1; k++) {
        EZ.s("line", { x1: X(pts[k][0]), y1: Y(pts[k][1]), x2: X(pts[k + 1][0]), y2: Y(pts[k + 1][1]), "class": "ln ac" }, svg);
      }
      pts.forEach(function (p, k) { EZ.s("circle", { cx: X(p[0]), cy: Y(p[1]), r: k ? 4 : 7, "class": k ? "fill-a" : "fill-k" }, svg); });
      EZ.text(svg, X(-1) + 10, Y(3) - 8, "start", "s k-t", "start", 12);
      var last = pts[pts.length - 1], L0 = loss(-1, 3), L = loss(last[0], last[1]);
      var yf = 1 - 8 * lr, xf = 1 - 2 * lr;
      var verdict = off ? "flew off the chart" : (Math.abs(yf) > 1 ? "blowing up" : (yf < 0 ? "zig-zagging but settling" : "smooth"));
      EZ.text(svg, 12, H - 14, (off ? "Left the chart at step " + pts.length + " of " + n : "After " + (pts.length - 1) + " steps: loss " + L0.toFixed(1) + " → " + L.toFixed(2)), off ? "b wn-t" : "b", "start", 14);
      read.innerHTML = "Path: <b>" + verdict + "</b>. Each step multiplies the up-down error by " + yf.toFixed(2) +
        " (1 − 8 × learning rate) and the left-right error by " + xf.toFixed(2) + " (1 − 2 × learning rate). " +
        "The steep direction sets the limit: past 0.125 it zig-zags, past 0.25 it blows up, while the gentle direction is still crawling.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 5.4 LoRA trainable parameters vs rank and target modules, Qwen2.5-7B config (as on the page):
     hidden 3,584, MLP 18,944, 28 layers, k/v project to 512, 7.61B parameters in total.
     Per adapted matrix: r * (d_in + d_out). r = 16, all linear = 40,370,176. */
  var MATS = [["q", 3584, 3584], ["k", 3584, 512], ["v", 3584, 512], ["o", 3584, 3584], ["gate", 3584, 18944], ["up", 3584, 18944], ["down", 18944, 3584]];
  var SETS = [["q + v (LoRA paper)", ["q", "v"]], ["attention q k v o", ["q", "k", "v", "o"]], ["all linear (7)", ["q", "k", "v", "o", "gate", "up", "down"]]];
  var RANKS = [1, 2, 4, 8, 16, 32, 64, 128], LAYERS = 28, TOTAL = 7.61e9;
  EZ.plays.lorarank = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ri = 4, si = 2;
    EZ.slider(bar, "rank r", 0, RANKS.length - 1, 1, ri, function (v) { return String(RANKS[v]); }, function (v) { ri = v; draw(); });
    var bb = EZ.el("div", { "class": "ez-ctl" }, stage);
    EZ.buttons(bb, SETS.map(function (s) { return s[0]; }), si, function (i) { si = i; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var r = RANKS[ri], on = SETS[si][1], nw = EZ.narrow(stage), W = nw ? 340 : 600;
      var rowH = nw ? 44 : 30, top = 44, lab = nw ? 0 : 150, bx = 12 + lab, bw = W - bx - (nw ? 12 : 110);
      var max = 128 * (3584 + 18944);
      var H = top + MATS.length * rowH + 64;
      var svg = EZ.svg(host, W, H, "Trainable LoRA parameters per matrix in one layer");
      EZ.text(svg, 12, 20, "One transformer layer of Qwen2.5-7B, r = " + r, "b", "start");
      EZ.text(svg, 12, 38, "bar = r × (inputs + outputs); grey = no adapter", "s m", "start", 12);
      var layer = 0;
      MATS.forEach(function (m, i) {
        var y = top + i * rowH, has = on.indexOf(m[0]) >= 0, p = r * (m[1] + m[2]);
        if (has) layer += p;
        var label = m[0] + "  " + fmt(m[1]) + " → " + fmt(m[2]);
        if (nw) {
          EZ.text(svg, 12, y + 14, label, has ? "s b" : "s m", "start", 12);
          EZ.rect(svg, 12, y + 20, bw, 14, "bx", 3);
          if (has) EZ.rect(svg, 12, y + 20, Math.max(2, bw * p / max), 14, "fill-a", 3);
          EZ.text(svg, W - 12, y + 14, has ? fmt(p) : "frozen", has ? "s" : "s m", "end", 12);
        } else {
          EZ.text(svg, bx - 8, y + 17, label, has ? "s b" : "s m", "end", 12);
          EZ.rect(svg, bx, y + 4, bw, 18, "bx", 3);
          if (has) EZ.rect(svg, bx, y + 4, Math.max(2, bw * p / max), 18, "fill-a", 3);
          EZ.text(svg, bx + bw + 8, y + 18, has ? fmt(p) : "frozen", has ? "s" : "s m", "start", 12);
        }
      });
      var all = layer * LAYERS, y2 = top + MATS.length * rowH + 20;
      EZ.text(svg, 12, y2, "Per layer " + fmt(layer) + " × 28 layers = " + fmt(all), "b", "start", nw ? 13 : 15);
      EZ.text(svg, 12, y2 + 22, (all / TOTAL * 100).toFixed(2) + "% of 7.61B · adapter about " + (all * 2 / 1e6).toFixed(0) + " MB in bf16", "s ac-t", "start", 13);
      read.innerHTML = "Doubling r doubles every bar. Choosing which matrices to adapt matters as much: the three MLP matrices (gate, up, down) are wide, so 'all linear' costs about " +
        (90112 / 11264).toFixed(0) + "× as much as q + v at the same rank. The bar scale is fixed at r = 128, so you can compare settings.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
