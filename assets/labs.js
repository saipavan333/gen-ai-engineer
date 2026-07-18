/* ============================================================
   labs.js — interactive per-lesson "labs". Drop
   <div class="lab" data-lab="NAME"></div> into a lesson.
   ============================================================ */
(function () {
  "use strict";
  var LABS = (window.AGE_LABS = window.AGE_LABS || {});
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  /* ---------- Tokenizer Forge (Track 1) ---------- */
  LABS.tokenizer = function (el) {
    var examples = [
      ["Retrieval-augmented generation grounds the model in your documents.", "Sentence"],
      ["How many R's are in strawberry?", "Letters"],
      ["antidisestablishmentarianism", "Long word"],
      ["def add(a, b): return a + b  # 1234567", "Code + numbers"]
    ];
    var w = document.createElement("div"); w.className = "lab-card lab-tok";
    w.innerHTML =
      '<div class="lab-head"><span class="lab-kicker">◆ Interactive · Tokenizer Forge</span>' +
      '<span class="lab-sub">type anything — watch it shatter into tokens</span></div>' +
      '<div class="lab-ex">' + examples.map(function (e, i) { return '<button type="button" class="lab-ex-btn" data-i="' + i + '">' + esc(e[1]) + "</button>"; }).join("") + "</div>" +
      '<textarea class="lab-ta" rows="2" spellcheck="false"></textarea>' +
      '<div class="lab-stats"></div><div class="lab-tiles"></div>';
    el.appendChild(w);
    var ta = w.querySelector(".lab-ta"), tiles = w.querySelector(".lab-tiles"), stats = w.querySelector(".lab-stats");
    ta.value = examples[0][0];
    var COLORS = ["#818cf8", "#22d3ee", "#c084fc", "#f59e0b", "#f472b6", "#34d399", "#60a5fa", "#fb7185"];
    function tokenize(text) {
      var re = /\s?[A-Za-z]+|\s?[0-9]+|\s?[^\sA-Za-z0-9]+|\s+/g, m, out = [];
      while ((m = re.exec(text)) !== null) {
        var t = m[0], lead = /^\s/.test(t) ? " " : "", core = t.replace(/^\s/, "");
        if (/^[A-Za-z]+$/.test(core) && core.length > 6) { var i = 0, f = true; while (i < core.length) { var sz = (i === 0 ? 5 : 4); out.push((f ? lead : "") + core.slice(i, i + sz)); f = false; i += sz; } }
        else if (/^[0-9]+$/.test(core) && core.length > 3) { (core.match(/[0-9]{1,3}/g) || [core]).forEach(function (p, k) { out.push((k === 0 ? lead : "") + p); }); }
        else { out.push(t); }
      }
      return out;
    }
    function render() {
      var text = ta.value, toks = tokenize(text);
      tiles.innerHTML = toks.map(function (t, i) { var lead = /^\s/.test(t), core = t.replace(/^\s/, ""); return '<span class="lab-tile" style="--tc:' + COLORS[i % COLORS.length] + '">' + (lead ? '<i class="sp">·</i>' : "") + esc(core || "␣") + "</span>"; }).join("");
      var chars = text.length, n = toks.length, ratio = n ? (chars / n).toFixed(1) : "0", words = text.trim() ? text.trim().split(/\s+/).length : 0, per = n / 1e6 * 0.15;
      stats.innerHTML = "<b>" + n + "</b> tokens · " + words + " words · " + chars + " chars · ~<b>" + ratio + "</b> chars/token" +
        '<span class="lab-cost">· marks a leading space owned by the token. Illustrative cost at $0.15 / 1M tokens: <b>$' + per.toFixed(6) + "</b> per call · <b>$" + (per * 1e6).toFixed(2) + "</b> per million calls</span>";
    }
    ta.addEventListener("input", render);
    Array.prototype.forEach.call(w.querySelectorAll(".lab-ex-btn"), function (b) { b.addEventListener("click", function () { ta.value = examples[+b.getAttribute("data-i")][0]; render(); }); });
    render();
  };

  /* ---------- Retrieval toy (Track 3) ---------- */
  LABS.retrieval = function (el) {
    var CORPUS = [
      "Refunds are issued within 5 business days to your original payment method.",
      "You can return any item within 30 days of delivery for a full refund.",
      "Standard shipping is free on orders over $50; express shipping costs $9.99.",
      "Our support team is available Monday to Friday, 9am to 6pm EST.",
      "To reset your password, click Forgot Password on the login page.",
      "Gift cards are non-refundable and never expire."
    ];
    var EX = ["How long do refunds take?", "Is shipping free?", "How do I reset my password?", "Can I get money back for a gift card?"];
    var STOP = { the:1,a:1,an:1,is:1,are:1,to:1,of:1,for:1,on:1,in:1,do:1,my:1,you:1,your:1,can:1,how:1,get:1,it:1,and:1,within:1,any:1,i:1 };
    var w = document.createElement("div"); w.className = "lab-card lab-rag";
    w.innerHTML =
      '<div class="lab-head"><span class="lab-kicker">◆ Interactive · Retrieval</span>' +
      '<span class="lab-sub">ask a question — watch which chunks get retrieved</span></div>' +
      '<div class="lab-ex" id="rex"></div>' +
      '<input class="lab-q" id="rq" placeholder="Ask about refunds, shipping, passwords…">' +
      '<div class="lab-topk" id="rtopk"></div><div class="lab-docs" id="rdocs"></div><div class="lab-answer" id="rans"></div>';
    el.appendChild(w);
    var q = w.querySelector("#rq"), docs = w.querySelector("#rdocs"), ans = w.querySelector("#rans"), topk = w.querySelector("#rtopk"), exEl = w.querySelector("#rex");
    exEl.innerHTML = EX.map(function (e) { return '<button type="button" class="lab-ex-btn" data-q="' + esc(e) + '">' + esc(e) + "</button>"; }).join("");
    function words(s) { return s.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(function (x) { return x.length > 2 && !STOP[x]; }); }
    function score(qw, dw) { if (!qw.length || !dw.length) return 0; var set = {}; dw.forEach(function (x) { set[x] = 1; }); var inter = 0; qw.forEach(function (x) { if (set[x]) inter++; }); return inter / Math.sqrt(qw.length * dw.length); }
    function hl(text, qw) { return esc(text).replace(/[A-Za-z0-9]+/g, function (word) { return qw.indexOf(word.toLowerCase()) > -1 ? "<mark>" + word + "</mark>" : word; }); }
    function shorten(s) { return s.length > 56 ? s.slice(0, 54) + "…" : s; }
    function render() {
      var qw = words(q.value);
      var scored = CORPUS.map(function (d, i) { return { i: i, d: d, s: score(qw, words(d)) }; });
      var max = Math.max.apply(null, scored.map(function (x) { return x.s; }).concat([0.0001]));
      var ranked = scored.slice().sort(function (a, b) { return b.s - a.s; });
      var k = 2, got = ranked.filter(function (x) { return x.s > 0; }).slice(0, k), onSet = {};
      got.forEach(function (x) { onSet[x.i] = 1; });
      docs.innerHTML = scored.map(function (x) {
        var pct = x.s > 0 ? Math.round(x.s / max * 100) : 0, on = onSet[x.i];
        return '<div class="lab-doc' + (on ? " on" : "") + '"><span class="lab-doc-t">' + hl(x.d, qw) + "</span>" +
          '<span class="lab-doc-bar"><i style="width:' + pct + '%"></i></span>' +
          '<span class="lab-doc-s">' + (x.s > 0 ? x.s.toFixed(2) : "—") + "</span>" + (on ? '<span class="lab-doc-tag">retrieved</span>' : '<span class="lab-doc-pad"></span>') + "</div>";
      }).join("");
      topk.textContent = "top-" + k + " chunks by similarity → sent to the model as grounded context";
      ans.innerHTML = got.length ? "<b>Grounded answer</b> is written using only: " + got.map(function (x) { return "“" + esc(shorten(x.d)) + "”"; }).join("  +  ")
        : "<b>No relevant chunk found</b> — a good RAG system should say “I don’t know” rather than guess.";
    }
    q.addEventListener("input", render);
    Array.prototype.forEach.call(exEl.querySelectorAll(".lab-ex-btn"), function (b) { b.addEventListener("click", function () { q.value = b.getAttribute("data-q"); render(); }); });
    q.value = EX[0]; render();
  };


  /* ---------- Text-to-SQL playground (Track 13) ---------- */
  LABS.sql = function (el) {
    var customers=[{id:1,name:"Ada Lovelace",country:"Canada"},{id:2,name:"Bo Zhang",country:"USA"},{id:3,name:"Cyrus Vane",country:"Canada"}];
    var orders=[{id:1,cid:1,amount:120,status:"paid"},{id:2,cid:2,amount:80,status:"paid"},{id:3,cid:1,amount:50,status:"refunded"},{id:4,cid:3,amount:200,status:"paid"}];
    function cust(id){for(var i=0;i<customers.length;i++)if(customers[i].id===id)return customers[i];return null;}
    var Q=[
      {q:"How many orders are there?", sql:"SELECT COUNT(*) AS orders FROM orders;", run:function(){return {cols:["orders"],rows:[[orders.length]]};}},
      {q:"Total revenue from paid orders", sql:"SELECT SUM(amount) AS revenue\nFROM orders\nWHERE status = 'paid';", run:function(){var s=0;orders.forEach(function(o){if(o.status==="paid")s+=o.amount;});return {cols:["revenue"],rows:[["$"+s.toFixed(2)]]};}},
      {q:"Total spend by customers in Canada", sql:"SELECT SUM(o.amount) AS spent\nFROM orders o\nJOIN customers c ON c.id = o.customer_id\nWHERE c.country = 'Canada';", run:function(){var s=0;orders.forEach(function(o){var c=cust(o.cid);if(c&&c.country==="Canada")s+=o.amount;});return {cols:["spent"],rows:[["$"+s.toFixed(2)]]};}},
      {q:"Top customer by total spend", sql:"SELECT c.name, SUM(o.amount) AS spend\nFROM orders o\nJOIN customers c ON c.id = o.customer_id\nGROUP BY c.id\nORDER BY spend DESC\nLIMIT 1;", run:function(){var m={};orders.forEach(function(o){m[o.cid]=(m[o.cid]||0)+o.amount;});var best=null,k;for(k in m){if(!best||m[k]>best.v)best={id:+k,v:m[k]};}var c=cust(best.id);return {cols:["name","spend"],rows:[[c.name,"$"+best.v.toFixed(2)]]};}}
    ];
    var w=document.createElement("div"); w.className="lab-card lab-sql";
    w.innerHTML='<div class="lab-head"><span class="lab-kicker">◆ Interactive · Text-to-SQL</span><span class="lab-sub">ask in English → see the SQL → run it (read-only)</span></div>'
      +'<div class="lab-schema">customers(<b>id</b>, name, country) · orders(<b>id</b>, customer_id, amount, status)</div>'
      +'<div class="lab-ex" id="sqex"></div>'
      +'<div class="lab-sql-label">generated SQL</div><pre class="lab-sql-code" id="sqlcode"></pre>'
      +'<div class="lab-sql-label">result</div><div class="lab-table" id="sqlres"></div>';
    el.appendChild(w);
    var exEl=w.querySelector("#sqex"), code=w.querySelector("#sqlcode"), res=w.querySelector("#sqlres");
    exEl.innerHTML=Q.map(function(e,i){return '<button type="button" class="lab-ex-btn" data-i="'+i+'">'+esc(e.q)+'</button>';}).join("");
    function kw(sql){return esc(sql).replace(/\b(SELECT|FROM|WHERE|JOIN|ON|GROUP BY|ORDER BY|LIMIT|SUM|COUNT|AS|DESC)\b/g,'<span class="k">$1</span>');}
    function show(i){var e=Q[i]; code.innerHTML=kw(e.sql); var r=e.run();
      res.innerHTML='<table><thead><tr>'+r.cols.map(function(c){return '<th>'+esc(c)+'</th>';}).join("")+'</tr></thead><tbody>'+r.rows.map(function(row){return '<tr>'+row.map(function(v){return '<td>'+esc(v)+'</td>';}).join("")+'</tr>';}).join("")+'</tbody></table>';}
    Array.prototype.forEach.call(exEl.querySelectorAll(".lab-ex-btn"),function(b){b.addEventListener("click",function(){show(+b.getAttribute("data-i"));});});
    show(0);
  };


  /* ---------- Runnable code cells (Pyodide, lazy-loaded) ---------- */
  var HEAVY = /\b(ollama|transformers|torch|chromadb|sentence_transformers|whisper|fastapi|uvicorn|peft|trl|bitsandbytes|datasets|langchain|openai|anthropic|requests|micropip|tiktoken|sklearn|cv2|PIL)\b/;
  var pyPromise = null;
  function getPy() {
    if (!pyPromise) {
      pyPromise = import("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.mjs").then(function (m) { return m.loadPyodide(); });
    }
    return pyPromise;
  }
  function fallbackCopy(t) {
    try { var ta = document.createElement("textarea"); ta.value = t; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select(); var ok = document.execCommand("copy"); document.body.removeChild(ta); return ok; }
    catch (e) { return false; }
  }
  function copyText(t) {
    if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
      return navigator.clipboard.writeText(t).then(function () { return true; }).catch(function () { return fallbackCopy(t); });
    }
    return Promise.resolve(fallbackCopy(t));
  }
  function isPythonBlock(fname, code) {
    if (/\.py$/i.test(fname)) return true;
    if (fname && /\.(sql|sh|yml|yaml|json|jsonl|md|txt|toml|ini|js|html|css)$/i.test(fname)) return false;
    if (/^\s*(FROM|RUN|CMD|COPY|WORKDIR|ENTRYPOINT)\s/m.test(code)) return false;
    if (/^\s*(SELECT|CREATE\s+TABLE|INSERT\s+INTO|UPDATE\s|DELETE\s+FROM|WITH\s)/im.test(code)) return false;
    if (/^\s*(pip install|curl |docker |git |ollama |uvicorn |npm |python |export )/m.test(code)) return false;
    if (/^\s*(name:|on:|jobs:|steps:|runs-on:)/m.test(code)) return false;
    return /^\s*(import\s+\w|from\s+\w+\s+import|def\s+\w+\s*\(|class\s+\w+)/m.test(code) || /\bprint\s*\(/.test(code);
  }
  function attachRunner(pre) {
    if (pre.getAttribute("data-run")) return;
    var codeEl = pre.querySelector("code"); if (!codeEl) return;
    var lab = pre.previousElementSibling;
    var fname = (lab && lab.classList && lab.classList.contains("code-label") && lab.querySelector(".fname")) ? lab.querySelector(".fname").textContent.trim() : "";
    var code = codeEl.textContent;
    if (!isPythonBlock(fname, code)) return;
    pre.setAttribute("data-run", "1");
    var bar = document.createElement("div"); bar.className = "run-bar";
    if (HEAVY.test(code)) {
      var cbtn = document.createElement("button"); cbtn.className = "run-btn colab"; cbtn.type = "button";
      cbtn.textContent = "Copy code & open Colab ↗";
      var note = document.createElement("span"); note.className = "run-status";
      note.textContent = "needs a real model — paste into the new notebook (Ctrl+V) and run";
      cbtn.addEventListener("click", function () {
        copyText(code).then(function (ok) {
          cbtn.textContent = ok ? "✓ Copied — opening Colab…" : "Opening Colab… (copy the code manually)";
          window.open("https://colab.research.google.com/#create=true", "_blank", "noopener");
          setTimeout(function () { cbtn.textContent = "Copy code & open Colab ↗"; }, 2800);
        });
      });
      bar.appendChild(cbtn); bar.appendChild(note);
      pre.parentNode.insertBefore(bar, pre.nextSibling);
      return;
    }
    var btn = document.createElement("button"); btn.className = "run-btn"; btn.type = "button"; btn.textContent = "▶ Run";
    var status = document.createElement("span"); status.className = "run-status";
    var copyBtn = document.createElement("button"); copyBtn.className = "copy-btn"; copyBtn.type = "button"; copyBtn.textContent = "Copy";
    copyBtn.addEventListener("click", function () { copyText(code).then(function (ok) { copyBtn.textContent = ok ? "Copied ✓" : "Ctrl+C"; setTimeout(function () { copyBtn.textContent = "Copy"; }, 1600); }); });
    bar.appendChild(btn); bar.appendChild(copyBtn); bar.appendChild(status);
    var out = document.createElement("pre"); out.className = "run-out"; out.style.display = "none";
    pre.parentNode.insertBefore(bar, pre.nextSibling);
    pre.parentNode.insertBefore(out, bar.nextSibling);
    btn.addEventListener("click", function () {
      out.style.display = "block"; out.textContent = ""; btn.disabled = true;
      status.textContent = pyPromise ? "running…" : "loading Python (first run only)…";
      getPy().then(function (py) {
        status.textContent = "running…";
        py.setStdout({ batched: function (t) { out.textContent += t + "\n"; } });
        py.setStderr({ batched: function (t) { out.textContent += t + "\n"; } });
        return py.runPythonAsync(code);
      }).then(function (r) {
        if (r !== undefined && r !== null) out.textContent += "=> " + r + "\n";
        if (!out.textContent) out.textContent = "(ran with no output)";
        status.textContent = "done"; btn.disabled = false;
      }).catch(function (e) { out.textContent += String(e); status.textContent = "error"; btn.disabled = false; });
    });
  }
  function initRunners() {
    Array.prototype.forEach.call(document.querySelectorAll("main.lesson pre"), attachRunner);
  }

  function mountAll() {
    Array.prototype.forEach.call(document.querySelectorAll(".lab[data-lab]"), function (el) {
      if (el.getAttribute("data-mounted")) return;
      var fn = LABS[el.getAttribute("data-lab")];
      if (fn) { try { fn(el); el.setAttribute("data-mounted", "1"); } catch (e) {} }
    });
    initRunners();
  }
  window.AGE_MOUNT = mountAll;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mountAll); else mountAll();
  setTimeout(mountAll, 250);
})();
