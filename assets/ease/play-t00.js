/* Pass 2 interactives, Section 0 (Start Here). */
(function () {
  var EZ = window.EZ;
  /* 0.3 an f-string: values flow into the {slots} of a fixed template */
  EZ.plays.fstring = function (stage) {
    var TOPICS = ["the water cycle", "black holes", "how tokens work"], topic = 0, grade = 5;
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage);
    EZ.buttons(bar, TOPICS, 0, function (i) { topic = i; draw(); });
    EZ.slider(bar, "grade", 1, 12, 1, grade, null, function (v) { grade = v; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function wrapText(s, max) {
      var out = [], line = "";
      s.split(" ").forEach(function (w) { if (!line) line = w; else if ((line + " " + w).length <= max) line += " " + w; else { out.push(line); line = w; } });
      out.push(line); return out;
    }
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, svg = EZ.svg(host, W, nw ? 300 : 250, "f-string filled with the chosen values");
      var t = TOPICS[topic];
      EZ.rect(svg, 10, 10, W - 20, 36, "bx tn-c");
      EZ.text(svg, 20, 34, 'topic = "' + t + '"   grade = ' + grade, "mono", "start", nw ? 13 : 15);
      EZ.text(svg, 10, 74, "template (never changes):", "s m", "start");
      var tl = wrapText('f"Explain {topic} to a grade-{grade} student in 3 sentences."', nw ? 36 : 64);
      tl.forEach(function (l, i) { EZ.text(svg, 10, 96 + i * 20, l, "mono k-t", "start", 14); });
      var y0 = 96 + tl.length * 20 + 6;
      EZ.arrow(svg, W / 2, y0, W / 2, y0 + 26, "ac");
      var res = "Explain " + t + " to a grade-" + grade + " student in 3 sentences.";
      var rl = wrapText(res, nw ? 34 : 60);
      EZ.rect(svg, 10, y0 + 32, W - 20, 18 + rl.length * 22, "bx tn-g");
      rl.forEach(function (l, i) { EZ.text(svg, 22, y0 + 56 + i * 22, l, "", "start"); });
      svg.setAttribute("viewBox", "0 0 " + W + " " + (y0 + 60 + rl.length * 22));
      read.innerHTML = "Finished prompt: <b>" + res.length + " characters</b>. Same template, new values: that is how one line of code can write thousands of prompts.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
