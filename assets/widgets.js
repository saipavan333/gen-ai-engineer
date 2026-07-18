/* ============================================================
   widgets.js — per-lesson interactive widgets.
   Drop <div class="lab" data-lab="NAME"></div> into a lesson.
   Registers into window.AGE_LABS (created by labs.js).
   ============================================================ */
(function () {
  "use strict";
  var W = (window.AGE_LABS = window.AGE_LABS || {});

  /* ---------------- primitives ---------------- */
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function h(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  /* standard shell: returns the body element to fill */
  function shell(el, kicker, sub) {
    var c = h("div", "lab-card");
    c.appendChild(h("div", "lab-head",
      '<span class="lab-kicker">&#9670; Interactive &middot; ' + esc(kicker) + '</span>' +
      '<span class="lab-sub">' + esc(sub || "") + '</span>'));
    var body = h("div", "wg-body");
    c.appendChild(body);
    el.appendChild(c);
    return body;
  }
  /* labelled range control; onInput(value) */
  function slider(parent, label, min, max, step, val, fmt, onInput) {
    var row = h("div", "wg-slider");
    row.innerHTML = '<label>' + esc(label) + ' <b class="wg-val"></b></label>' +
      '<input type="range" min="' + min + '" max="' + max + '" step="' + step + '" value="' + val + '">';
    parent.appendChild(row);
    var input = row.querySelector("input"), out = row.querySelector(".wg-val");
    function fire() { out.textContent = fmt ? fmt(+input.value) : input.value; onInput(+input.value); }
    input.addEventListener("input", fire);
    return { fire: fire, get: function () { return +input.value; } };
  }
  /* preset buttons; onPick(index) */
  function presets(parent, labels, onPick) {
    var bar = h("div", "lab-ex");
    bar.innerHTML = labels.map(function (l, i) {
      return '<button type="button" class="lab-ex-btn" data-i="' + i + '">' + esc(l) + "</button>";
    }).join("");
    parent.appendChild(bar);
    bar.addEventListener("click", function (e) {
      var b = e.target.closest(".lab-ex-btn");
      if (!b) return;
      Array.prototype.forEach.call(bar.children, function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      onPick(+b.getAttribute("data-i"));
    });
    if (bar.firstChild) bar.firstChild.classList.add("on");
    return bar;
  }
  /* horizontal comparison bars: rows = [[label, value0to1, note]] */
  function bars(rows, fmt) {
    return '<div class="wg-bars">' + rows.map(function (r) {
      var pct = Math.max(0, Math.min(1, r[1])) * 100;
      return '<div class="wg-bar"><span class="wb-l">' + esc(r[0]) + '</span>' +
        '<span class="wb-t"><i style="width:' + pct.toFixed(1) + '%"></i></span>' +
        '<span class="wb-v">' + (fmt ? fmt(r[1]) : pct.toFixed(0) + "%") + '</span>' +
        (r[2] ? '<span class="wb-n">' + esc(r[2]) + "</span>" : "") + "</div>";
    }).join("") + "</div>";
  }
  function verdict(kind, text) { return '<div class="wg-verdict ' + kind + '">' + text + "</div>"; }
  function pct(x) { return Math.round(x * 100) + "%"; }

  /* expose helpers so later batches can reuse them */
  window.AGE_WG = { esc: esc, h: h, shell: shell, slider: slider, presets: presets, bars: bars, verdict: verdict, pct: pct };

  /* ============ 1.4  attention weights ============ */
  W.attention = function (el) {
    var SENT = ["The", "trophy", "did", "not", "fit", "in", "the", "suitcase", "because", "it", "was", "too", "big"];
    /* illustrative weights for a few query positions */
    var ATT = {
      9:  { 1: 0.62, 7: 0.14, 4: 0.08, 12: 0.06 },     /* "it" -> trophy */
      12: { 1: 0.44, 9: 0.21, 7: 0.13, 4: 0.07 },      /* "big" -> trophy */
      4:  { 1: 0.38, 7: 0.27, 3: 0.11, 0: 0.05 }       /* "fit" -> trophy/suitcase */
    };
    var b = shell(el, "Attention", "how a model decides which earlier words matter");
    b.innerHTML = '<p class="wg-note">Click a highlighted word. The shading shows which earlier words it attends to when being understood.</p>' +
      '<div class="wg-sent" id="wgat"></div><div class="wg-out"></div>';
    var sent = b.querySelector("#wgat"), out = b.querySelector(".wg-out");
    function draw(qi) {
      var wmap = ATT[qi] || {};
      sent.innerHTML = SENT.map(function (w, i) {
        var a = wmap[i] || 0, q = (i === qi);
        var cls = "wg-w" + (ATT[i] ? " sel" : "") + (q ? " q" : "");
        return '<span class="' + cls + '" data-i="' + i + '" style="--a:' + a.toFixed(2) + '">' + esc(w) + "</span>";
      }).join(" ");
      var top = Object.keys(wmap).sort(function (a, c) { return wmap[c] - wmap[a]; })[0];
      out.innerHTML = '<div class="wg-lbl">&ldquo;' + esc(SENT[qi]) + '&rdquo; attends most to &ldquo;' + esc(SENT[top]) + '&rdquo;</div>' +
        bars(Object.keys(wmap).sort(function (a, c) { return wmap[c] - wmap[a]; })
          .map(function (i) { return [SENT[i], wmap[i]]; }), pct) +
        '<p class="wg-note">Resolving &ldquo;it&rdquo; to <b>trophy</b> rather than <b>suitcase</b> needs world knowledge, not grammar. Attention is the mechanism that lets the model reach back and use it.</p>';
    }
    sent.addEventListener("click", function (e) {
      var s = e.target.closest(".wg-w"); if (!s) return;
      var i = +s.getAttribute("data-i"); if (ATT[i]) draw(i);
    });
    draw(9);
  };

  /* ============ 4.5  memory & the context window ============ */
  W.memory = function (el) {
    var TURNS = [
      ["user", "Hi, I'm Pavan. I ordered a laptop stand last week.", 14],
      ["assistant", "Hello Pavan! I can help with that order.", 10],
      ["user", "It arrived damaged.", 6],
      ["assistant", "I'm sorry. I can arrange a replacement or a refund.", 13],
      ["user", "Let's do a refund.", 7],
      ["assistant", "Refund started. It reaches your card in 5 business days.", 14],
      ["user", "Actually, what was my name again?", 9]
    ];
    var b = shell(el, "Context window", "what the model forgets, and why it seems to lose the plot");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(budget) {
      var kept = [], used = 0;
      for (var i = TURNS.length - 1; i >= 0; i--) {
        if (used + TURNS[i][2] > budget) break;
        kept.unshift(i); used += TURNS[i][2];
      }
      var hasName = kept.indexOf(0) >= 0;
      out.innerHTML = '<div class="wg-lbl">conversation (oldest first) &mdash; ' + used + " of " + budget + " tokens kept</div>" +
        '<div class="wg-conv">' + TURNS.map(function (t, i) {
          return '<div class="wg-turn ' + t[0] + (kept.indexOf(i) >= 0 ? "" : " dropped") + '"><b>' + t[0] + "</b> " + esc(t[1]) + "</div>";
        }).join("") + "</div>" +
        verdict(hasName ? "ok" : "warn",
          hasName ? "The first turn still fits, so the model can answer &ldquo;what was my name?&rdquo; correctly."
                  : "The first turn has been dropped. Asked for the name, the model will either refuse or <b>invent one</b> &mdash; and users read that as the bot going senile.") +
        '<p class="wg-note">Nothing is remembered between calls. Every turn you resend the whole history, and when it no longer fits, something has to go. Real systems summarise old turns or store facts in a database instead of relying on the window.</p>';
    }
    slider(ctl, "context budget (tokens)", 10, 80, 5, 40, null, render).fire();
  };

  /* ============ 5.4  LoRA sizing ============ */
  W.lora = function (el) {
    var b = shell(el, "LoRA sizing", "why fine-tuning stopped needing a data centre");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    var base = 7, rank = 8;
    function render() {
      var full = base * 1e9;
      /* rough: 2 matrices per target module, d=4096, ~32 layers, 4 modules */
      var lp = rank * 4096 * 2 * 32 * 4;
      var frac = lp / full;
      var fullMem = full * 16 / 1e9;          /* fp16 weights + optimiser states, very rough */
      var loraMem = full * 2 / 1e9 + lp * 16 / 1e9;
      out.innerHTML = bars([
        ["full fine-tune (trainable)", 1, full.toLocaleString() + " params"],
        ["LoRA rank " + rank + " (trainable)", Math.max(frac, 0.004), lp.toLocaleString() + " params"]
      ], function (v) { return (v * 100).toFixed(2) + "%"; }) +
        '<div class="wg-kv"><div><span>trainable</span><b>' + (frac * 100).toFixed(2) + "%</b></div>" +
        "<div><span>full-tune memory</span><b>~" + fullMem.toFixed(0) + " GB</b></div>" +
        "<div><span>LoRA memory</span><b>~" + loraMem.toFixed(0) + " GB</b></div>" +
        "<div><span>adapter file</span><b>~" + (lp * 2 / 1e6).toFixed(0) + " MB</b></div></div>" +
        verdict(rank <= 32 ? "ok" : "neutral",
          rank <= 32 ? "Under 1% of the weights carry your adaptation. That is why this runs on a free Colab GPU instead of a cluster."
            : "High rank adds capacity you probably cannot fill with a small dataset &mdash; and you drift back toward full fine-tuning cost for little gain.") +
        '<p class="wg-note">You freeze the base model and train two small matrices beside it. Ship the adapter (megabytes, not gigabytes), swap adapters per customer, and roll back by deleting a file.</p>';
    }
    slider(ctl, "base model (billion params)", 1, 70, 1, 7, function (v) { return v + "B"; }, function (v) { base = v; render(); }).fire();
    slider(ctl, "LoRA rank", 4, 128, 4, 8, null, function (v) { rank = v; render(); }).fire();
    render();
  };

  /* ============ 8.4  model routing ============ */
  W.routing = function (el) {
    var TASKS = [
      ["classify a support ticket", "small", 0.97],
      ["extract fields from an invoice", "small", 0.96],
      ["summarise a 20-page contract", "mid", 0.93],
      ["debug a race condition in Go", "large", 0.88],
      ["multi-step migration plan", "large", 0.85]
    ];
    var PRICE = { small: 0.15, mid: 0.60, large: 3.00 };
    var b = shell(el, "Model routing", "most requests do not need your best model");
    var out = h("div", "wg-out");
    presets(b, ["Everything to large", "Routed by task"], function (i) { render(i); });
    b.appendChild(out);
    function render(mode) {
      var rows = TASKS.map(function (t) {
        var tier = mode === 0 ? "large" : t[1];
        return [t[0], tier, PRICE[tier], t[2]];
      });
      var cost = rows.reduce(function (a, r) { return a + r[2]; }, 0);
      var acc = rows.reduce(function (a, r) { return a + r[3]; }, 0) / rows.length;
      out.innerHTML = '<table class="wg-tbl"><tr><th>task</th><th>model</th><th>$/1M</th></tr>' +
        rows.map(function (r) { return "<tr><td>" + esc(r[0]) + '</td><td><code>' + r[1] + "</code></td><td>$" + r[2].toFixed(2) + "</td></tr>"; }).join("") + "</table>" +
        '<div class="wg-kv"><div><span>relative cost</span><b>$' + cost.toFixed(2) + "</b></div>" +
        "<div><span>average quality</span><b>" + pct(acc) + "</b></div></div>" +
        verdict(mode === 0 ? "warn" : "ok",
          mode === 0 ? "Paying large-model prices for classification and extraction &mdash; tasks a small model does at essentially the same accuracy."
            : "Roughly <b>" + Math.round((1 - cost / (PRICE.large * TASKS.length)) * 100) + "% cheaper</b> at nearly identical quality, because each task goes to the cheapest model that can still do it.") +
        '<p class="wg-note">Route on task type first, then add an escalation path: if the small model returns low confidence or fails validation, retry on the larger one. You pay the premium only when you need it.</p>';
    }
    render(0);
  };

  /* ============ 8.5  quantization ============ */
  W.quantization = function (el) {
    var LV = [
      ["fp16", 16, 14.0, 1.00, "reference quality"],
      ["int8", 8, 7.2, 0.995, "practically lossless for most tasks"],
      ["int4", 4, 3.9, 0.975, "small quality dip; usually acceptable"],
      ["int3", 3, 3.0, 0.91, "noticeable degradation on reasoning"]
    ];
    var b = shell(el, "Quantization", "how a 7B model fits on the laptop you already own");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(i) {
      var l = LV[i];
      out.innerHTML = '<div class="wg-kv"><div><span>precision</span><b>' + l[0] + "</b></div>" +
        "<div><span>bits / weight</span><b>" + l[1] + "</b></div>" +
        "<div><span>7B model size</span><b>~" + l[2].toFixed(1) + " GB</b></div>" +
        "<div><span>quality retained</span><b>" + pct(l[3]) + "</b></div></div>" +
        bars([["memory footprint", l[2] / 14], ["quality retained", l[3]]], pct) +
        verdict(l[3] >= 0.97 ? "ok" : "warn", esc(l[4]) +
          (l[3] >= 0.97 ? " &mdash; a good default for local and edge deployment." : " &mdash; measure on <em>your</em> eval set before shipping this.")) +
        '<p class="wg-note">Quantization stores weights at lower precision. You trade a little accuracy for a large drop in memory, which is what makes a 7B model runnable on consumer hardware for free.</p>';
    }
    slider(ctl, "precision", 0, 3, 1, 1, function (v) { return LV[v][0]; }, render).fire();
  };

  /* ============ 14.4  production monitor ============ */
  W.monitor = function (el) {
    var b = shell(el, "Production monitor", "the average is the number that lies to you");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(tail) {
      var lat = [], i;
      for (i = 0; i < 200; i++) {
        var base = 0.6 + (i % 17) * 0.03;
        lat.push(i % 100 < tail ? base * 4 : base);
      }
      lat.sort(function (a, c) { return a - c; });
      var mean = lat.reduce(function (a, c) { return a + c; }, 0) / lat.length;
      var p50 = lat[Math.round(0.50 * (lat.length - 1))];
      var p95 = lat[Math.round(0.95 * (lat.length - 1))];
      var p99 = lat[Math.round(0.99 * (lat.length - 1))];
      out.innerHTML = '<div class="wg-kv"><div><span>mean</span><b>' + mean.toFixed(2) + "s</b></div>" +
        "<div><span>p50</span><b>" + p50.toFixed(2) + "s</b></div>" +
        "<div><span>p95</span><b>" + p95.toFixed(2) + "s</b></div>" +
        "<div><span>p99</span><b>" + p99.toFixed(2) + "s</b></div></div>" +
        bars([["mean", mean / 4], ["p95", p95 / 4], ["p99", p99 / 4]], function (v) { return (v * 4).toFixed(2) + "s"; }) +
        verdict(p95 > 3 ? "warn" : "ok",
          p95 > 3 ? "p95 has breached the 3s alert threshold while the mean still looks acceptable. <b>" + tail + "% of users</b> are having a bad time and the average is hiding them."
            : "Healthy. Keep the alert on p95, not the mean.") +
        '<p class="wg-note">Drag the slider up slowly and watch the mean drift while p95 leaps. This is the shape of nearly every real incident &mdash; a slow tail, not a uniform slowdown.</p>';
    }
    slider(ctl, "share of requests hitting a slow path", 0, 30, 1, 0, function (v) { return v + "%"; }, render).fire();
  };

  /* ============ 16.3  disaggregated fairness ============ */
  W.fairness = function (el) {
    var b = shell(el, "Disaggregated evaluation", "the gap an overall score is built to hide");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(gap) {
      var a = 0.94, bb = Math.max(0.3, a - gap);
      var overall = (a + bb) / 2, d = a - bb;
      out.innerHTML = bars([["overall accuracy", overall], ["group A", a], ["group B", bb]], pct) +
        '<div class="wg-kv"><div><span>disparity</span><b>' + (d * 100).toFixed(0) + " pts</b></div>" +
        "<div><span>gate (max 5 pts)</span><b>" + (d <= 0.05 ? "PASS" : "BLOCKED") + "</b></div></div>" +
        verdict(d <= 0.05 ? "ok" : "warn",
          d <= 0.05 ? "Groups are within tolerance. Report both numbers anyway &mdash; the gap is a metric you track, not a box you tick once."
            : "Overall accuracy still reads <b>" + pct(overall) + "</b>, which passes most quality bars. Yet group B is <b>" + (d * 100).toFixed(0) + " points</b> worse on matched inputs. Ship on the aggregate and you ship discrimination you never measured.") +
        '<p class="wg-note">Matched pairs are what make this valid: identical qualifications, only the group differs. Any outcome difference can then only come from the attribute you varied.</p>';
    }
    slider(ctl, "hidden gap between groups", 0, 0.6, 0.02, 0, function (v) { return (v * 100).toFixed(0) + " pts"; }, render).fire();
  };

})();

/* ============ additions: gaps with no existing demo ============ */
(function () {
  "use strict";
  var W = (window.AGE_LABS = window.AGE_LABS || {});
  var G = window.AGE_WG, esc = G.esc, h = G.h, shell = G.shell, slider = G.slider,
      presets = G.presets, bars = G.bars, verdict = G.verdict, pct = G.pct;

  /* ============ 3.4  vector index trade-off ============ */
  W.vectorindex = function (el) {
    var b = shell(el, "Index trade-off", "exact search is perfect and does not scale");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(n) {
      var docs = Math.pow(10, n);
      var flatMs = docs * 0.00025, hnswMs = Math.log2(Math.max(docs, 2)) * 0.42;
      out.innerHTML = '<div class="wg-kv"><div><span>documents</span><b>' + docs.toLocaleString() + "</b></div>" +
        "<div><span>flat (exact)</span><b>" + (flatMs < 1 ? flatMs.toFixed(2) : Math.round(flatMs).toLocaleString()) + " ms</b></div>" +
        "<div><span>HNSW (approx)</span><b>" + hnswMs.toFixed(1) + " ms</b></div>" +
        "<div><span>HNSW recall</span><b>~97%</b></div></div>" +
        bars([["flat search time", Math.min(1, flatMs / 250)], ["HNSW search time", Math.min(1, hnswMs / 250)]],
          function (v) { return (v * 250).toFixed(1) + " ms"; }) +
        verdict(docs <= 10000 ? "ok" : "warn",
          docs <= 10000
            ? "At this size flat search is fine &mdash; exact results, no index to tune, no recall loss. Do not add an approximate index you do not need."
            : "Flat search is now the bottleneck. HNSW answers in near-constant time but returns <b>approximate</b> neighbours &mdash; you trade about 3% recall for a " + Math.round(flatMs / hnswMs) + "&times; speedup.") +
        '<p class="wg-note">Every vector database is this choice with a product wrapped around it. Ask what recall the index actually achieves on <em>your</em> data &mdash; the default settings are tuned for benchmarks, not your corpus.</p>';
    }
    slider(ctl, "corpus size", 2, 7, 1, 3, function (v) { return "10^" + v; }, render).fire();
  };

  /* ============ 8.3  caching ============ */
  W.caching = function (el) {
    var b = shell(el, "Caching", "the cheapest call is the one you never make");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    var hit = 0, calls = 100000;
    function render() {
      var base = calls * (2000 * 0.15 + 300 * 0.60) / 1e6;
      var cost = base * (1 - hit / 100);
      var lat = 1.9 * (1 - hit / 100) + 0.02 * (hit / 100);
      out.innerHTML = '<div class="wg-kv"><div><span>cost without cache</span><b>$' + base.toFixed(0) + "</b></div>" +
        "<div><span>cost with cache</span><b>$" + cost.toFixed(0) + "</b></div>" +
        "<div><span>saved</span><b>$" + (base - cost).toFixed(0) + "</b></div>" +
        "<div><span>average latency</span><b>" + lat.toFixed(2) + "s</b></div></div>" +
        bars([["spend", cost / base], ["latency", lat / 1.9]], pct) +
        verdict(hit >= 30 ? "ok" : "neutral",
          hit >= 30 ? "A cache hit is free and effectively instant. At this rate caching is doing more for your bill than any model swap would."
            : "Even a modest hit rate pays for itself. Support and documentation traffic is famously repetitive &mdash; measure before assuming your traffic is unique.") +
        '<p class="wg-note">Three levels, increasingly useful: <b>exact</b> (same string), <b>semantic</b> (similar meaning, via embeddings), and <b>prefix</b> (shared system prompt, billed at a discount by most providers). Always cache with a TTL &mdash; stale answers are their own kind of wrong.</p>';
    }
    slider(ctl, "cache hit rate", 0, 90, 5, 0, function (v) { return v + "%"; }, function (v) { hit = v; render(); }).fire();
    slider(ctl, "calls / month", 10000, 1000000, 10000, 100000, function (v) { return (v / 1000) + "k"; }, function (v) { calls = v; render(); }).fire();
    render();
  };

  /* ============ 8.6  batching & throughput ============ */
  W.batching = function (el) {
    var b = shell(el, "Batching", "throughput and latency pull in opposite directions");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(bs) {
      var perReq = 0.9 + bs * 0.055;            /* queueing + shared compute */
      var thru = bs / perReq;
      out.innerHTML = '<div class="wg-kv"><div><span>batch size</span><b>' + bs + "</b></div>" +
        "<div><span>latency / request</span><b>" + perReq.toFixed(2) + "s</b></div>" +
        "<div><span>throughput</span><b>" + thru.toFixed(1) + " req/s</b></div>" +
        "<div><span>GPU utilisation</span><b>" + Math.min(99, 18 + bs * 3.4).toFixed(0) + "%</b></div></div>" +
        bars([["throughput", Math.min(1, thru / 12)], ["latency (lower is better)", Math.min(1, perReq / 3)]],
          function (v) { return (v * 100).toFixed(0) + "%"; }) +
        verdict(bs <= 4 ? "neutral" : bs <= 16 ? "ok" : "warn",
          bs <= 4 ? "Low latency per user, but the GPU sits mostly idle &mdash; you are paying for hardware you are not using."
            : bs <= 16 ? "The useful middle. Throughput climbs steeply while per-request latency is still acceptable."
            : "Throughput gains have flattened but every user now waits noticeably longer. Past this point you are trading user experience for very little.") +
        '<p class="wg-note">Batching amortises the cost of loading weights across many requests. For interactive chat, favour small batches and continuous batching; for overnight bulk jobs, turn it all the way up &mdash; nobody is waiting.</p>';
    }
    slider(ctl, "batch size", 1, 32, 1, 1, null, render).fire();
  };

  /* ============ 16.1  test-time compute ============ */
  W.testtime = function (el) {
    var b = shell(el, "Test-time compute", "spending more thinking at inference, not more training");
    var ctl = h("div", "wg-ctl"), out = h("div", "wg-out");
    b.appendChild(ctl); b.appendChild(out);
    function render(n) {
      /* diminishing returns on a hard reasoning benchmark */
      var acc = 0.42 + 0.34 * (1 - Math.exp(-n / 5));
      var cost = n * 0.9, lat = 1.2 + n * 1.1;
      out.innerHTML = '<div class="wg-kv"><div><span>reasoning passes</span><b>' + n + "</b></div>" +
        "<div><span>accuracy</span><b>" + pct(acc) + "</b></div>" +
        "<div><span>relative cost</span><b>" + cost.toFixed(1) + "&times;</b></div>" +
        "<div><span>latency</span><b>" + lat.toFixed(1) + "s</b></div></div>" +
        bars([["accuracy", acc], ["cost", Math.min(1, cost / 20)], ["latency", Math.min(1, lat / 20)]], pct) +
        verdict(n <= 1 ? "neutral" : n <= 8 ? "ok" : "warn",
          n <= 1 ? "A single pass &mdash; fast and cheap, and correct for most everyday tasks."
            : n <= 8 ? "Accuracy is still climbing meaningfully for each extra pass. This is the range where reasoning models earn their price on genuinely hard problems."
            : "Accuracy has plateaued while cost and latency keep rising linearly. You are paying a great deal for a fraction of a point.") +
        '<p class="wg-note">This is the shift behind reasoning models: instead of a bigger model, let a good one think longer &mdash; sampling several attempts, checking its own work, and picking the best. The curve always flattens, so the engineering question is <b>where you stop</b>, per task.</p>';
    }
    slider(ctl, "reasoning passes", 1, 20, 1, 1, null, render).fire();
  };
})();

/* widgets registered after labs.js may already have mounted — mount again */
(function () {
  function go() { if (window.AGE_MOUNT) window.AGE_MOUNT(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
  setTimeout(go, 120);
})();
