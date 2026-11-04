/* Pass 2 interactives, Section 9 (Text-to-SQL). The gate mirrors safe_run.py on lesson 9.3:
   validate() (one statement, SELECT/WITH only), a read-only connection (mode=ro), and the row-cap wrapper. */
(function () {
  var EZ = window.EZ;
  var CANDS = [
    ["Canada total", ["SELECT SUM(o.amount) AS total_spent", "FROM orders o", "JOIN customers c ON c.id = o.customer_id", "WHERE c.country = 'Canada';"]],
    ["Stacked DROP", ["SELECT * FROM customers; DROP TABLE customers;"]],
    ["DELETE", ["DELETE FROM orders"]],
    ["WITH ... DELETE", ["WITH x AS (SELECT 1) DELETE FROM orders"]],
    ["Whole table", ["SELECT * FROM orders"]],
    ["Trailing comment", ["SELECT name FROM customers -- newest first"]]
  ];
  /* validate(): same steps as the Python on the page */
  function normalise(sql) { return sql.trim().replace(/;+$/, "").trim(); }   // sql.strip().rstrip(";").strip()
  function writes(q) { return /\b(insert|update|delete|drop|alter|create|replace)\b/i.test(q); }
  function gate(sql) {
    var q = normalise(sql), res = [];
    var one = q.indexOf(";") < 0;
    res.push(["1. One statement only", one, one ? "no “;” left after stripping the trailing one" : "a “;” inside: stacked statements blocked"]);
    if (!one) return { q: q, res: res };
    var rd = /^(select|with)/.test(q.toLowerCase());
    res.push(["2. Reads only", rd, rd ? "starts with " + q.split(/\s+/)[0].toUpperCase() + (q.toLowerCase().indexOf("with") === 0 ? ": the prefix check lets it in" : "") : "starts with " + q.split(/\s+/)[0].toUpperCase() + ": only SELECT allowed"]);
    if (!rd) return { q: q, res: res };
    var w = writes(q);
    res.push(["3. Read-only connection", !w, w ? "mode=ro: the database refuses the write" : "a read: the connection allows it"]);
    if (w) return { q: q, res: res };
    res.push(["4. Row-cap wrapper", true, "result bounded to 1,000 rows"]);
    return { q: q, res: res, wrapped: true };
  }
  EZ.plays.sqlgate = function (stage) {
    var bar = EZ.el("div", { "class": "ez-ctl" }, stage), ci = 0;
    EZ.buttons(bar, CANDS.map(function (c) { return c[0]; }), 0, function (i) { ci = i; draw(); });
    var host = EZ.el("div", {}, stage), read = EZ.el("p", { "class": "ez-read" }, stage);
    function draw() {
      EZ.clear(host);
      var nw = EZ.narrow(stage), W = nw ? 340 : 600, c = CANDS[ci], sql = c[1].join("\n"), g = gate(sql);
      var mono = nw ? 11 : 12.5, cw = mono * 0.6, maxc = Math.floor((W - 40) / cw);
      function wrapLine(s) { var out = []; while (s.length > maxc) { var k = s.lastIndexOf(" ", maxc); if (k < 10) k = maxc; out.push(s.slice(0, k)); s = "  " + s.slice(k).trim(); } out.push(s); return out; }
      var src = []; c[1].forEach(function (l) { src = src.concat(wrapLine(l)); });
      var outl = [];
      if (g.wrapped) { outl.push("SELECT * FROM ("); g.q.split("\n").forEach(function (l) { outl = outl.concat(wrapLine(l)); }); outl.push(") LIMIT 1000"); }
      var rowH = 54, H = 40 + src.length * 17 + 24 + 4 * rowH + (g.wrapped ? 40 + outl.length * 17 : 10) + 10;
      var svg = EZ.svg(host, W, H, "Safety gate checks for one candidate query");
      EZ.text(svg, 12, 18, "Model wrote:", "s b", "start");
      EZ.rect(svg, 12, 26, W - 24, src.length * 17 + 12, "bx", 6);
      src.forEach(function (l, i) { var t = EZ.text(svg, 20, 43 + i * 17, l, "mono", "start"); t.style.fontSize = mono + "px"; });
      var y = 26 + src.length * 17 + 12 + 22, x0 = 12, bw = W - 24;
      var names = ["1. One statement only", "2. Reads only", "3. Read-only connection", "4. Row-cap wrapper"];
      names.forEach(function (nm, k) {
        var r = g.res[k], yy = y + k * rowH, h = rowH - 12;
        var cls = !r ? "bx" : r[1] ? "bx tn-g" : "bx tn-w";
        EZ.rect(svg, x0, yy, bw, h, cls, 8);
        EZ.text(svg, x0 + 12, yy + 18, nm, "b" + (r ? "" : " m"), "start", nw ? 13 : 14);
        var badge = !r ? "not reached" : r[1] ? "PASS" : "BLOCKED";
        EZ.text(svg, x0 + bw - 12, yy + 18, badge, "b " + (!r ? "m" : r[1] ? "ok-t" : "wn-t"), "end", 13);
        if (r) EZ.text(svg, x0 + 12, yy + 35, r[2], "s", "start");
        if (k < 3) EZ.arrow(svg, x0 + 30, yy + h + 1, x0 + 30, yy + rowH - 1, r && r[1] ? "ok" : "");
      });
      y += 4 * rowH + 10;
      if (g.wrapped) {
        EZ.text(svg, 12, y + 4, "What actually runs:", "s b ok-t", "start");
        outl.forEach(function (l, i) { var t = EZ.text(svg, 20, y + 24 + i * 17, l, "mono", "start"); t.style.fontSize = mono + "px"; });
      }
      var stop = g.res.filter(function (r) { return !r[1]; })[0];
      var why = {
        0: "Fine: a normal read. The trailing “;” is stripped, and the wrapper caps the result.",
        1: "The semicolon check stops it before anything runs.",
        2: "It is one statement, but it does not start with SELECT or WITH.",
        3: "It slips past validate(): one statement, starts with WITH. SQLite allows WITH before DELETE. The read-only connection is what stops it, which is why the page has more than one layer.",
        4: "A read of the whole table is allowed, but the wrapper means at most 1,000 rows come back.",
        5: "The newlines around the query matter: without them the “-- comment” would swallow “) LIMIT 1000”."
      };
      read.innerHTML = (stop ? "<b>Blocked at " + stop[0].replace(/^\d\. /, "") + ".</b> " : "<b>Runs.</b> ") + why[ci];
    }
    draw(); EZ.watch(stage, draw);
  };
})();
