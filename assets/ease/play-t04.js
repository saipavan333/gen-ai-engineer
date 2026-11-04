/* Pass 2 interactives, Track 4 (Agents). Both plays walk a scripted, illustrative run (no model is called);
   the step budget logic is the same as run_agent(max_steps) in lesson 4.3. */
(function () {
  var EZ = window.EZ;
  function wrapText(s, maxc) {
    var out = [], line = "";
    s.split(" ").forEach(function (w) { if (!line) line = w; else if ((line + " " + w).length <= maxc) line += " " + w; else { out.push(line); line = w; } });
    if (line) out.push(line);
    return out;
  }
  function node(g, x, y, w, h, title, sub, on, tone) {
    var r = EZ.rect(g, x, y, w, h, on ? "bx tn-" + tone : "bx", 9);
    if (on) r.setAttribute("stroke-width", "3");
    EZ.text(g, x + w / 2, y + 19, title, on ? "b" : "b m", "middle", 14);
    if (sub) EZ.text(g, x + w / 2, y + 36, sub, "s", "middle", 12);
  }

  /* 4.3 agent loop: a scripted 4-step run */
  var RUN = [
    { think: "I need the order's status first.", act: "get_order(order_id=\"4417\")", obs: "{status: shipped, carrier: DHL, tracking: JD0142}" },
    { think: "It shipped. Now find when it arrives.", act: "track_parcel(\"JD0142\")", obs: "error: carrier API timed out" },
    { think: "The call timed out. Try once more.", act: "track_parcel(\"JD0142\")", obs: "{eta: Thursday}" },
    { think: "I have both facts, so I can answer.", fin: "Order 4417 shipped with DHL and should arrive on Thursday." }
  ];
  function events(budget) {
    var ev = [];
    for (var s = 1; s <= RUN.length; s++) {
      if (s > budget) { ev.push({ n: "stop", s: s }); return ev; }
      ev.push({ n: "guard", s: s }, { n: "think", s: s });
      if (RUN[s - 1].fin) { ev.push({ n: "final", s: s }); return ev; }
      ev.push({ n: "act", s: s }, { n: "obs", s: s });
    }
    return ev;
  }
  function line(e, budget) {
    var r = RUN[e.s - 1];
    if (e.n === "guard") return ["Budget check: step " + e.s + " of max " + budget + ", go on", "m"];
    if (e.n === "think") return ["Think: " + r.think, ""];
    if (e.n === "act") return ["Act: " + r.act, "k"];
    if (e.n === "obs") return ["Observe: " + r.obs, e.s === 2 ? "w" : "c"];
    if (e.n === "final") return ["Answer: " + r.fin, "g"];
    return ["Stopped: hit max steps (" + budget + ") before an answer", "w"];
  }
  EZ.plays.agentloop = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), budget = 6, p = -1;
    var bStep = EZ.el("button", { type: "button" }, bar, "Step ▸");
    var bReset = EZ.el("button", { type: "button" }, bar, "Reset");
    EZ.slider(bar, "max_steps", 1, 6, 1, budget, null, function (v) { budget = v; p = -1; draw(); });
    bStep.addEventListener("click", function () { var ev = events(budget); if (p < ev.length - 1) p++; draw(); });
    bReset.addEventListener("click", function () { p = -1; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var ev = events(budget), cur = p >= 0 ? ev[p] : null, at = cur ? cur.n : "";
      var nw = EZ.narrow(stage), W = nw ? 340 : 660, tx = nw ? 12 : 340, tw = nw ? 316 : 308, maxc = Math.floor(tw / 6.6);
      var tl = [];
      for (var i = 0; i <= p; i++) { var L = line(ev[i], budget); wrapText(L[0], maxc).forEach(function (s, k) { tl.push([s, L[1], i === p, k === 0]); }); }
      var keep = 14; if (tl.length > keep) tl = tl.slice(tl.length - keep);
      var ty0 = nw ? 292 : 30, H = nw ? ty0 + 26 + Math.max(1, tl.length) * 17 + 10 : Math.max(284, ty0 + 20 + keep * 17 + 10);
      var svg = EZ.svg(host, W, H, "Agent loop, step by step");
      /* diagram */
      var g = svg;
      node(g, 20, 20, 130, 46, "Budget check", "step ≤ " + budget + "?", at === "guard", "p");
      node(g, 180, 20, 130, 46, "Stopped", "hit max steps", at === "stop", "w");
      node(g, 20, 110, 130, 46, "Think", "pick the next move", at === "think", "a");
      node(g, 180, 110, 130, 46, "Act", "call a tool", at === "act", "k");
      node(g, 20, 200, 130, 46, "Final answer", "no tool call", at === "final", "g");
      node(g, 180, 200, 130, 46, "Observe", "result appended", at === "obs", "c");
      EZ.arrow(g, 85, 69, 85, 107, at === "think" ? "ac" : "");
      EZ.arrow(g, 153, 43, 177, 43, at === "stop" ? "wn" : "");
      EZ.arrow(g, 153, 133, 177, 133, at === "act" ? "ac" : "");
      EZ.arrow(g, 245, 159, 245, 197, at === "obs" ? "ac" : "");
      EZ.arrow(g, 85, 159, 85, 197, at === "final" ? "ok" : "");
      var back = EZ.s("polyline", { points: "313,223 326,223 326,8 85,8 85,12", "class": "ln" + (at === "guard" && cur.s > 1 ? " ac" : "") }, g);
      EZ.s("polygon", { points: "85,19 80,10 90,10", "class": "hd" + (at === "guard" && cur.s > 1 ? " ac" : "") }, g);
      EZ.text(g, 160, 270, cur ? "Step " + cur.s + (cur.n === "stop" ? " (blocked)" : "") : "Press Step to start", "s b ac-t", "middle");
      /* transcript */
      EZ.text(g, tx, nw ? ty0 + 6 : 20, "Messages so far (the model reads all of them)", "s b", "start");
      if (!tl.length) EZ.text(g, tx, (nw ? ty0 + 6 : 20) + 22, "Goal: “Has order 4417 shipped, and when will it arrive?”", "s m", "start", 12);
      tl.forEach(function (t, k) {
        var cls = "s" + (t[2] ? " b" : "") + (t[1] === "w" ? " wn-t" : t[1] === "g" ? " ok-t" : t[1] === "k" ? " k-t" : t[1] === "m" ? " m" : "");
        EZ.text(g, tx + (t[3] ? 0 : 12), (nw ? ty0 + 6 : 20) + 22 + k * 17, t[0], cls, "start", 12.5);
      });
      var steps = cur ? cur.s : 0;
      read.innerHTML = !cur ? "Budget: <b>" + budget + "</b> steps. This run needs 4 steps, because one tool call fails and is retried." :
        cur.n === "stop" ? "<b>The guard fired.</b> The loop was stopped before step " + cur.s + ", so the user gets no answer, but you also don't pay for a runaway loop." :
        cur.n === "final" ? "<b>Done in " + steps + " steps.</b> The answer is built from the two tool results, not from memory." :
        "Step <b>" + steps + "</b> of at most " + budget + ": <b>" + cur.n + "</b>.";
    }
    draw(); EZ.watch(stage, draw);
  };

  /* 4.6 one MCP tool call, step by step (illustrative order data) */
  var ACT = ["Host app + model", "MCP client", "MCP server", "Order system"];
  var MS = [
    [0, 1, "tool call get_order(“4417”)", "The model, inside the host app, decides it needs a tool and emits a tool call. The tool and its schema were found earlier with <code>tools/list</code>."],
    [1, 2, "tools/call get_order", "The client sends one JSON-RPC request: <code>{\"jsonrpc\": \"2.0\", \"id\": 7, \"method\": \"tools/call\", \"params\": {\"name\": \"get_order\", \"arguments\": {\"order_id\": \"4417\"}}}</code>. Under the 2026-07-28 spec the request carries its own protocol version, so no handshake came first."],
    [2, 3, "server's code runs the query", "The server checks the arguments, then its own code talks to the real system. The model never touches the order database."],
    [3, 2, "row: shipped, DHL", "The order system returns the row to the server."],
    [2, 1, "result: “shipped, DHL”", "The server sends the JSON-RPC result back to the client, with the same id (7)."],
    [1, 0, "tool result message", "The client hands the result to the host, which appends it to the conversation as a tool result."],
    [0, 0, "model answers", "The model reads the tool result and writes: “Yes, order 4417 shipped with DHL.” One tool call, there and back."]
  ];
  EZ.plays.mcpflow = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), p = -1;
    var bStep = EZ.el("button", { type: "button" }, bar, "Step ▸");
    var bReset = EZ.el("button", { type: "button" }, bar, "Reset");
    bStep.addEventListener("click", function () { if (p < MS.length - 1) p++; draw(); });
    bReset.addEventListener("click", function () { p = -1; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 640, m = 10, cw = (W - 2 * m) / 4, step = nw ? 40 : 36;
      var xs = ACT.map(function (a, i) { return m + cw * i + cw / 2; });
      var top = 10, hh = nw ? 44 : 36, y0 = top + hh + 26, H = y0 + MS.length * step + 10;
      var svg = EZ.svg(host, W, H, "One MCP tool call");
      ACT.forEach(function (a, i) {
        var on = p >= 0 && (MS[p][0] === i || MS[p][1] === i), bw = cw - 8;
        EZ.rect(svg, xs[i] - bw / 2, top, bw, hh, on ? "bx tn-a" : "bx", 8);
        if (nw) { var ws = wrapText(a, 11); ws.forEach(function (s, k) { EZ.text(svg, xs[i], top + 18 + k * 15 - (ws.length - 1) * 4, s, "b", "middle", 12); }); }
        else EZ.text(svg, xs[i], top + 23, a, "b", "middle", 13);
        EZ.s("line", { x1: xs[i], y1: top + hh, x2: xs[i], y2: H - 6, "class": "grid dash" }, svg);
      });
      if (p < 0) EZ.text(svg, W / 2, y0 - 6, "User asks the host: “Has order 4417 shipped?” Press Step.", "s ac-t", "middle", 12.5);
      for (var k = 0; k < MS.length; k++) {
        var e = MS[k], y = y0 + k * step, cur = k === p, cls = cur ? "ac" : "thin", future = k > p;
        if (future) { var gx1 = xs[e[0]], gx2 = xs[e[1]]; if (gx1 !== gx2) { var gl = EZ.s("line", { x1: gx1, y1: y + 20, x2: gx2, y2: y + 20, "class": "ln thin dash" }, svg); gl.setAttribute("opacity", ".35"); } continue; }
        var lab = (k + 1) + ". " + e[2];
        if (e[0] === e[1]) {
          var x = xs[e[0]];
          EZ.s("polyline", { points: x + "," + (y + 10) + " " + (x + 26) + "," + (y + 10) + " " + (x + 26) + "," + (y + 22) + " " + (x + 8) + "," + (y + 22), "class": "ln " + cls }, svg);
          EZ.s("polygon", { points: (x + 2) + "," + (y + 22) + " " + (x + 10) + "," + (y + 18) + " " + (x + 10) + "," + (y + 26), "class": "hd " + cls }, svg);
          EZ.text(svg, x + 32, y + 20, lab, cur ? "s b ac-t" : "s m", "start", 12);
        } else {
          var xa = xs[e[0]], xb = xs[e[1]], d = xb > xa ? 1 : -1;
          EZ.arrow(svg, xa + d * 4, y + 20, xb - d * 4, y + 20, cls);
          var hw = lab.length * 3.4, cx = Math.min(Math.max((xa + xb) / 2, hw + 4), W - hw - 4);
          EZ.text(svg, cx, y + 12, lab, cur ? "s b ac-t" : "s m", "middle", 12);
        }
      }
      read.innerHTML = p < 0 ? "Seven messages make one tool call. The host app holds the model; the server is a separate program that could be on another machine." :
        "<b>Step " + (p + 1) + " of " + MS.length + ".</b> " + MS[p][3];
    }
    draw(); EZ.watch(stage, draw);
  };
})();
