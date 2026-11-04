/* Pass 2 interactives, Track 2. The prompt parts are the lesson's own example; the reply preview and the
   "pinned down" count are illustrative (a count of open questions, not a measured score). */
(function () {
  var EZ = window.EZ;

  function wrapText(s, maxc) {
    var out = [], line = "";
    s.split(" ").forEach(function (w) {
      if (!line) line = w; else if ((line + " " + w).length <= maxc) line += " " + w; else { out.push(line); line = w; }
    });
    if (line) out.push(line);
    return out;
  }

  /* 2.1 prompt builder: toggle the five parts */
  var PARTS = [
    ["Role", "You are a meticulous customer-support assistant.", "c"],
    ["Task", "Classify the support ticket's urgency.", "a"],
    ["Context", "Ticket: “My card was charged twice and no one has replied in 3 days.”", "k"],
    ["Examples", "“Password reset link expired” → low. “Site is down for every customer” → high.", "p"],
    ["Format", "Answer with exactly one word: high, medium, or low.", "g"]
  ];
  /* each open question is answered when any of the listed parts is on */
  var QS = [
    ["Who is answering, and how carefully?", [0]],
    ["What is the job?", [1]],
    ["Which ticket?", [2]],
    ["What counts as high vs low?", [3]],
    ["Which labels are allowed?", [3, 4]],
    ["How long should the reply be?", [4]],
    ["What does a good reply look like?", [3]]
  ];
  function reply(on) {
    if (!on[1] && !on[2]) return "“Hi! How can I help you today?”";
    if (!on[1]) return "“Sorry to hear about the double charge! Have you tried contacting your bank?”";
    if (!on[2]) return "“Sure, please paste the ticket you'd like me to classify.”";
    if (on[4]) return "“high”";
    if (on[3]) return "“Urgency: high, because the customer was charged twice.”";
    return "“This ticket seems quite urgent. The customer was charged twice and has waited 3 days, so I'd suggest…”";
  }
  EZ.plays.promptbuilder = function (stage) {
    var on = [true, true, true, false, true];
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), btns = [];
    PARTS.forEach(function (p, i) {
      var b = EZ.el("button", { type: "button", "aria-pressed": on[i] ? "true" : "false" }, bar, p[0]);
      if (on[i]) b.className = "on";
      b.addEventListener("click", function () { on[i] = !on[i]; b.className = on[i] ? "on" : ""; b.setAttribute("aria-pressed", on[i] ? "true" : "false"); draw(); });
      btns.push(b);
    });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 640, SW = nw ? 316 : 330, x0 = 12, maxc = Math.floor((SW - 24) / 7.1);
      /* measure the stack */
      var blocks = PARTS.map(function (p, i) { var ls = on[i] ? wrapText(p[1], maxc) : []; return { p: p, i: i, ls: ls, h: on[i] ? 30 + ls.length * 17 : 28 }; });
      var stackH = 0; blocks.forEach(function (b) { stackH += b.h + 6; });
      var answered = QS.map(function (q) { return q[1].some(function (k) { return on[k]; }); });
      var n = answered.filter(Boolean).length;
      var rx = nw ? 12 : SW + 40, ry = nw ? 60 + stackH + 30 : 40;
      var rl = wrapText(reply(on), nw ? 44 : 34);
      var H = nw ? ry + 40 + QS.length * 21 + 34 + rl.length * 17 + 16 : Math.max(60 + stackH + 10, 40 + 40 + QS.length * 21 + 40 + rl.length * 17 + 16);
      var svg = EZ.svg(host, W, H, "The assembled prompt and which questions it leaves open");
      EZ.text(svg, x0, 20, "What is sent (one request)", "b", "start");
      EZ.text(svg, x0, 40, "system message", "s m", "start");
      var y = 48;
      blocks.forEach(function (b) {
        if (b.i === 1) { EZ.text(svg, x0, y + 14, "user message", "s m", "start"); y += 22; }
        if (on[b.i]) {
          EZ.rect(svg, x0, y, SW, b.h, "bx tn-" + b.p[2], 8);
          EZ.text(svg, x0 + 10, y + 19, b.p[0], "s b", "start");
          b.ls.forEach(function (l, k) { EZ.text(svg, x0 + 10, y + 37 + k * 17, l, "s", "start"); });
        } else {
          var r = EZ.rect(svg, x0, y, SW, b.h, "bx fade", 8); r.setAttribute("stroke-dasharray", "5 4");
          EZ.text(svg, x0 + 10, y + 19, b.p[0] + ": left out", "s m", "start");
        }
        y += b.h + 6;
      });
      /* checklist + meter */
      EZ.text(svg, rx, ry, "Questions the model must guess", "b", "start");
      var mw = nw ? 316 : W - rx - 12;
      EZ.rect(svg, rx, ry + 10, mw, 14, "bx", 7);
      EZ.rect(svg, rx, ry + 10, mw * n / QS.length, 14, n === QS.length ? "fill-g" : "fill-a", 7);
      EZ.text(svg, rx, ry + 42, n + " of " + QS.length + " pinned down (illustrative count)", "s m", "start");
      QS.forEach(function (q, k) {
        var yy = ry + 66 + k * 21, ok = answered[k];
        EZ.text(svg, rx, yy, ok ? "✓" : "?", ok ? "b ok-t" : "b wn-t", "start");
        EZ.text(svg, rx + 18, yy, q[0], ok ? "s m" : "s", "start");
      });
      var yr = ry + 66 + QS.length * 21 + 12;
      EZ.text(svg, rx, yr, "Likely reply (illustrative):", "s b", "start");
      rl.forEach(function (l, k) { EZ.text(svg, rx, yr + 20 + k * 17, l, on[4] && on[1] && on[2] ? "s ok-t" : "s", "start"); });
      var miss = PARTS.filter(function (p, i) { return !on[i]; }).map(function (p) { return p[0]; });
      read.innerHTML = miss.length ? "Left out: <b>" + miss.join(", ") + "</b>. Every part you drop is a question the model answers by guessing." :
        "All five parts are on. The model has nothing left to guess about the shape of the answer, so it can be parsed by code.";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
