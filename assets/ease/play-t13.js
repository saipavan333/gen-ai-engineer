/* Pass 2 interactives, Section 13 (track16 pages). Tiers, examples, obligations and dates are the ones lesson 13.4 lists. */
(function () {
  var EZ = window.EZ;

  /* 13.4 pick a use case, see its EU AI Act risk tier and what that tier asks of you */
  var TIERS = [
    ["Unacceptable risk", "banned", "w"],
    ["High risk", "strict obligations", "k"],
    ["Limited risk", "transparency", "c"],
    ["Minimal risk", "no special rules", "g"]
  ];
  var DUTIES = [
    ["Prohibited outright.", "Not a compliance task:", "it is off the table."],
    ["Risk management", "Data governance", "Documentation", "Human oversight", "Transparency", "Accuracy and robustness testing", "Record-keeping"],
    ["Light obligations,", "mostly about honesty."],
    ["Essentially no special", "obligations."]
  ];
  var USES = [
    ["Song recommender", 3, "Recommendations sit in the minimal tier."],
    ["Spam filter", 3, "A low-stakes classifier: minimal risk."],
    ["Retail FAQ chatbot", 2, "Tell users they are talking to an AI, not a human."],
    ["AI-generated content", 2, "AI-generated content may need a label."],
    ["Resume screener", 1, "Hiring is high-risk. Build bias tests per group (13.3), human oversight and audit trails in from day one. Annex III rules apply from 2 December 2027."],
    ["Loan scoring", 1, "Credit scoring is high-risk. Log every decision and let an officer override rejects. Annex III rules apply from 2 December 2027."],
    ["Government social scoring", 0, "Banned. Prohibited practices applied from 2 February 2025."]
  ];

  EZ.plays.riskclass = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ui = 5;
    EZ.buttons(bar, USES.map(function (u) { return u[0]; }), ui, function (i) { ui = i; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);

    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), u = USES[ui], t = u[1];
      var PW = nw ? 316 : 300, px = 12, py = 30, th = 54;
      var W = nw ? 340 : 620, H = nw ? py + 4 * th + 46 + DUTIES[t].length * 22 + 6 : 262;
      var svg = EZ.svg(host, W, H, "EU AI Act risk tier for " + u[0]);
      EZ.text(svg, px, 18, "Risk tiers: more possible harm, more rules (top = most)", "s m", "start", 12);
      for (var i = 0; i < 4; i++) {
        var y1 = py + i * th, y2 = y1 + th - 4, w1 = PW * (0.28 + 0.72 * i / 4), w2 = PW * (0.28 + 0.72 * (i + 1) / 4), c = px + PW / 2;
        var pts = (c - w1 / 2) + "," + y1 + " " + (c + w1 / 2) + "," + y1 + " " + (c + w2 / 2) + "," + y2 + " " + (c - w2 / 2) + "," + y2;
        var on = i === t;
        var poly = EZ.s("polygon", { points: pts, "class": "bx tn-" + TIERS[i][2] }, svg);
        if (!on) poly.setAttribute("opacity", ".4");
        else EZ.s("polygon", { points: pts, "class": "ring" }, svg);
        EZ.text(svg, c, y1 + 22, TIERS[i][0], on ? "b" : "s b", "middle", on ? 14 : 13);
        EZ.text(svg, c, y1 + 40, TIERS[i][1], on ? "s" : "s m", "middle", 12);
      }
      var dx = nw ? 12 : 340, dy = nw ? py + 4 * th + 46 : 52;
      if (!nw) EZ.arrow(svg, px + PW / 2 + PW * (0.28 + 0.72 * (t + 0.5) / 4) / 2 + 6, py + t * th + th / 2, dx - 10, py + t * th + th / 2, "ac");
      EZ.text(svg, dx, dy - 22 + (nw ? 4 : 0), u[0] + " → " + TIERS[t][0].toLowerCase(), "b ac-t", "start", nw ? 14 : 15);
      DUTIES[t].forEach(function (d, k) {
        var bullet = t === 1;
        if (bullet) EZ.s("circle", { cx: dx + 5, cy: dy + k * 22 - 5, r: 3, "class": "dot tn-k" }, svg);
        EZ.text(svg, dx + (bullet ? 16 : 0), dy + k * 22, d, "s", "start", 13);
      });
      read.innerHTML = "<b>" + u[0] + ":</b> " + u[2] + " The same kind of model can sit in any tier; the use decides. (Engineering literacy, not legal advice.)";
    }
    draw(); EZ.watch(stage, draw);
  };
})();
