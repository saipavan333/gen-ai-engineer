/* Pass 2 interactives, Section 10 (Multimodal). Image tokens follow the rule stated on lesson 10.1
   (from Anthropic's vision docs): ceil(w / 28) x ceil(h / 28); long edge up to 2,576 px; at most 4,784 tokens;
   bigger images are downscaled. The docs do not give the exact resize rounding, so a downscaled size is an estimate. */
(function () {
  var EZ = window.EZ, P = 28, EDGE = 2576, CAP = 4784;
  function tok(w, h) { return Math.ceil(w / P) * Math.ceil(h / P); }
  function fit(w, h) {
    var long = Math.max(w, h), s = long > EDGE ? EDGE / long : 1, w2 = Math.round(w * s), h2 = Math.round(h * s);
    var edge = s < 1;
    while (tok(w2, h2) > CAP) { var f = Math.sqrt(CAP / tok(w2, h2)) * 0.999; w2 = Math.floor(w2 * f); h2 = Math.floor(h2 * f); }
    return { w: w2, h: h2, t: tok(w2, h2), down: edge || w2 !== w || h2 !== h };
  }
  var PRESETS = [["1000 x 1000", 1000, 1000], ["phone photo 4032 x 3024", 4032, 3024], ["resized 1092 x 819", 1092, 819], ["invoice page 1000 x 1400", 1000, 1400]];
  EZ.plays.imagetokens = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), W0 = 1000, H0 = 1000, rw, rh;
    EZ.buttons(bar, PRESETS.map(function (p) { return p[0]; }), 0, function (i) { set(rw, PRESETS[i][1]); set(rh, PRESETS[i][2]); });
    var bar2 = EZ.el("div", { "class": "ez-ctl" }, stage);
    rw = EZ.slider(bar2, "width", 28, 4200, 1, W0, function (v) { return v + " px"; }, function (v) { W0 = v; draw(); });
    rh = EZ.slider(bar2, "height", 28, 4200, 1, H0, function (v) { return v + " px"; }, function (v) { H0 = v; draw(); });
    function set(r, v) { r.value = v; r.dispatchEvent(new Event("input")); }
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, r = fit(W0, H0), gx = Math.ceil(r.w / P), gy = Math.ceil(r.h / P);
      var box = nw ? 200 : 230, sc = box / Math.max(W0, H0), bw = W0 * sc, bh = H0 * sc;
      var rows = [];
      if (r.down) rows.push(["Over the limits, so it is downscaled", "s wn-t"], ["to about " + r.w + " x " + r.h + " px (estimate)", "s wn-t"]);
      rows.push([gx + " x " + gy + " patches of 28 x 28 px", "s"]);
      rows.push([r.t.toLocaleString("en-US") + (r.down ? " tokens (the cap is 4,784)" : " image tokens"), "b ac-t"]);
      rows.push(["Input cost per 1 million images:", "s m"]);
      [["Haiku 5.5", 0.10], ["Sonnet 5.5", 2], ["Opus 5.5", 4]].forEach(function (m) {
        rows.push([m[0] + " ($" + (m[1] < 1 ? m[1].toFixed(2) : m[1]) + "/M): $" + Math.round(r.t * m[1]).toLocaleString("en-US"), "s"]);
      });
      var H = nw ? 28 + bh + 26 + rows.length * 22 : Math.max(box + 44, 38 + rows.length * 22), svg = EZ.svg(host, W, H, "Image cut into 28-pixel patches");
      var x0 = 12, y0 = 28;
      EZ.text(svg, x0, 18, "Your image: " + W0 + " x " + H0 + " px", "s b", "start");
      EZ.rect(svg, x0, y0, bw, bh, "bx tn-k", 3);
      /* the patch grid on the (possibly downscaled) image, drawn inside the original outline */
      var dw = r.w * sc * (W0 / r.w), dh = r.h * sc * (H0 / r.h), cw = dw / (r.w / P), ch = dh / (r.h / P);
      if (cw >= 3.2) {
        for (var i = 1; i < gx; i++) EZ.s("line", { x1: x0 + i * cw, y1: y0, x2: x0 + i * cw, y2: y0 + bh, "class": "ln thin", opacity: .45 }, svg);
        for (var j = 1; j < gy; j++) EZ.s("line", { x1: x0, y1: y0 + j * ch, x2: x0 + bw, y2: y0 + j * ch, "class": "ln thin", opacity: .45 }, svg);
      } else {
        EZ.text(svg, x0 + bw / 2, y0 + bh / 2 + 5, "patches too small to draw", "s m");
      }
      EZ.s("rect", { x: x0, y: y0, width: Math.min(cw, bw), height: Math.min(ch, bh), "class": "ring" }, svg);
      var tx = nw ? 12 : x0 + box + 30, ty = nw ? y0 + bh + 26 : y0 + 10, lh = 22;
      rows.forEach(function (rw_, k) { EZ.text(svg, tx, ty + k * lh, rw_[0], rw_[1], "start"); });
      read.innerHTML = "ceil(" + r.w + " / 28) x ceil(" + r.h + " / 28) = " + gx + " x " + gy + " = <b>" + r.t.toLocaleString("en-US") + " tokens</b>." +
        (r.down ? " Long edge is capped at 2,576 px and the count at 4,784 tokens; the docs don't state the exact resize rounding, so the downscaled size is our estimate." : " Halve both sides and the tokens drop to about a quarter.") +
        " The ring marks one patch.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
