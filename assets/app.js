/* ============================================================
   app.js — builds the course chrome from CURRICULUM, tracks
   progress (localStorage), and wires interactivity. Vanilla JS.
   ============================================================ */
(function () {
  "use strict";
  var C = window.CURRICULUM;
  var body = document.body;
  var base = body.getAttribute("data-base") || "";
  var isHome = body.getAttribute("data-page") === "home";
  var curN = body.getAttribute("data-lesson") || "";
  var THEMES = ["graphite", "midnight", "sunset", "forest", "vivid"];
  try { var _t = localStorage.getItem("age_theme"); if (_t) document.documentElement.setAttribute("data-theme", _t); } catch (e) {}

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function link(href) { return base + href; }

  /* ---- favicon ---- */
  if (!document.querySelector('link[rel="icon"]')) {
    var fav = document.createElement("link");
    fav.rel = "icon"; fav.type = "image/svg+xml"; fav.href = link("assets/favicon.svg");
    document.head.appendChild(fav);
  }
  /* ---- premium fonts (Space Grotesk display + Inter body) ---- */
  if (!document.getElementById("age-fonts")) {
    var pc = document.createElement("link"); pc.rel = "preconnect"; pc.href = "https://fonts.gstatic.com"; pc.crossOrigin = "";
    document.head.appendChild(pc);
    var gf = document.createElement("link"); gf.id = "age-fonts"; gf.rel = "stylesheet";
    gf.href = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;450;500;600;700&display=swap";
    document.head.appendChild(gf);
  }
  /* ---- interactive labs (mounted per data-lab attribute) ---- */
  if (!document.getElementById("age-labs")) {
    var ls = document.createElement("script"); ls.id = "age-labs"; ls.src = link("assets/labs.js?v=20");
    document.head.appendChild(ls);
    var ws = document.createElement("script"); ws.id = "age-widgets"; ws.src = link("assets/widgets.js?v=20");
    document.head.appendChild(ws);
    var gs = document.createElement("script"); gs.id = "age-glossary"; gs.src = link("assets/glossary.js?v=20");
    document.head.appendChild(gs);
    var rs = document.createElement("script"); rs.id = "age-refs-js"; rs.src = link("assets/references.js?v=20");
    document.head.appendChild(rs);
    var acss = document.createElement("link"); acss.rel = "stylesheet"; acss.href = link("assets/gd-assistant.css?v=20"); document.head.appendChild(acss);
    var ajs = document.createElement("script"); ajs.id = "age-assistant"; ajs.defer = true; ajs.src = link("assets/gd-assistant.js?v=20"); document.head.appendChild(ajs);
  }

  /* ---- progress (saved on this device) ---- */
  var PKEY = "age_progress_v1";
  function loadDone() { try { return JSON.parse(localStorage.getItem(PKEY)) || {}; } catch (e) { return {}; } }
  function saveDone() { try { localStorage.setItem(PKEY, JSON.stringify(DONE)); } catch (e) {} }
  var DONE = loadDone();
  var RKEY = "age_review_v1", DAY = 86400000, SR = [1, 3, 7, 21, 60];
  function loadRev() { try { return JSON.parse(localStorage.getItem(RKEY)) || {}; } catch (e) { return {}; } }
  function saveRev() { try { localStorage.setItem(RKEY, JSON.stringify(REV)); } catch (e) {} }
  var REV = loadRev();
  Object.keys(DONE).forEach(function (n) { if (!REV[n]) REV[n] = { reviews: 0, due: Date.now() + DAY, done: Date.now() }; });
  saveRev();
  function dueCount() { var now = Date.now(), c = 0, k; for (k in REV) { if (REV[k] && REV[k].due <= now) c++; } return c; }

  /* ---- flat ordered list of built lessons ---- */
  var flat = [];
  C.sections.forEach(function (s) {
    s.lessons.forEach(function (l) { if (l.built) flat.push({ n: l.n, title: l.title, file: l.file, section: s }); });
  });
  var curIdx = -1;
  for (var i = 0; i < flat.length; i++) { if (flat[i].n === curN) { curIdx = i; break; } }
  var cur = curIdx >= 0 ? flat[curIdx] : null;

  function isLab(l) { return /(^|\/)lab\.html$/.test(l.file || ""); }
  function isVisual(l) { return /visual-lab\.html$/.test(l.file || ""); }

  /* =============== HEADER =============== */
  var header = el("header", "site-header");
  var brand = el("a", "brand");
  brand.href = link("index.html");
  brand.innerHTML = '<img class="logo" src="' + link("assets/favicon.svg") + '" alt="" width="26" height="26"><span class="brand-name">Applied GenAI Engineer</span>';
  header.appendChild(brand);
  var lbl = el("a", "hdr-link hdr-labs", "⚙ Labs");
  lbl.href = link("labs.html");
  header.appendChild(lbl);
  var msl = el("a", "hdr-link hdr-mastery", "★ Mastery");
  msl.href = link("mastery.html");
  header.appendChild(msl);
  var csl = el("a", "hdr-link hdr-cheats", "⚡ Cheat sheets");
  csl.href = link("cheatsheets.html");
  header.appendChild(csl);
  var rvl = el("a", "hdr-link hdr-review");
  rvl.href = link("review.html");
  var _dc = dueCount();
  rvl.innerHTML = "\u21bb Review" + (_dc > 0 ? ' <span class="hdr-badge">' + _dc + "</span>" : "");
  header.appendChild(rvl);
  var tdots = el("span", "theme-dots");
  THEMES.forEach(function (name) { var d = el("button", "tdot tdot-" + name); d.type = "button"; d.setAttribute("data-theme", name); d.setAttribute("aria-label", "Theme: " + name); tdots.appendChild(d); });
  tdots.addEventListener("click", function (e) { var b = e.target.closest(".tdot"); if (!b) return; var t = b.getAttribute("data-theme"); if (t === "graphite") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", t); try { localStorage.setItem("age_theme", t); } catch (_e) {} });
  header.appendChild(tdots);
  if (!isHome && cur) {
    var hasCheat = /^(1|2|3|4|5|6|7|8|9|10|11|12|13)$/.test(cur.section.num);
    if (hasCheat) {
      var crumb = el("a", "crumb crumb-link", "Track " + cur.section.num + " · " + cur.section.title + " · cheat sheet");
      crumb.href = link("cheatsheets.html#t" + cur.section.num);
      header.appendChild(crumb);
    } else {
      header.appendChild(el("span", "crumb", "Track " + cur.section.num + " · " + cur.section.title));
    }
  }
  header.appendChild(el("span", "spacer"));
  if (!isHome && cur) {
    var sLessons = cur.section.lessons.filter(function (l) { return l.built; });
    var posIdx = 0;
    for (var j = 0; j < sLessons.length; j++) { if (sLessons[j].n === cur.n) { posIdx = j + 1; break; } }
    header.appendChild(el("span", "pos", "Lesson " + posIdx + " of " + sLessons.length));
    var menu = el("button", "menu-btn", "&#8801; Menu");
    menu.setAttribute("aria-label", "Toggle lesson menu");
    menu.addEventListener("click", function () { body.classList.toggle("nav-open"); });
    header.insertBefore(menu, header.firstChild);
  }

  /* =============== HOME =============== */
  if (isHome) {
    document.body.insertBefore(header, document.body.firstChild);
    var roadmap = document.getElementById("roadmap");
    if (roadmap) renderRoadmap(roadmap);
    setupResume();
    wireQuizzes();
    scrollTopOnLoad();
    return;
  }

  /* =============== SIDEBAR (accordion) =============== */
  var sidebar = el("aside", "sidebar");
  C.sections.forEach(function (s) {
    var hasCurrent = s.lessons.some(function (l) { return l.built && l.n === curN; });
    var grp = el("div", "nav-group" + (s.ready ? "" : " locked") + (hasCurrent ? " open" : ""));
    var t = el("button", "nav-title");
    t.type = "button";
    t.setAttribute("aria-expanded", hasCurrent ? "true" : "false");
    t.innerHTML = '<span class="tnum">' + s.num + '</span><span class="tname">' + s.title +
      '</span><span class="nav-chev" aria-hidden="true">&#9656;</span>';
    grp.appendChild(t);
    var ul = el("ul", "nav-list");
    s.lessons.forEach(function (l) {
      var li = el("li");
      if (l.built) {
        var a = el("a");
        a.href = link(l.file);
        var cls = []; if (l.n === curN) cls.push("active"); if (DONE[l.n]) cls.push("done"); if (isLab(l) || isVisual(l)) cls.push("is-lab");
        if (cls.length) a.className = cls.join(" ");
        a.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + "</span>" +
          (isVisual(l) ? '<span class="ln-lab vis">VISUAL</span>' : isLab(l) ? '<span class="ln-lab">LAB</span>' : "") +
          (DONE[l.n] ? '<span class="ln-check" aria-hidden="true">&#10003;</span>' : "");
        li.appendChild(a);
      } else {
        var sp = el("span", "locked");
        sp.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + '</span><span class="lock-ico">soon</span>';
        li.appendChild(sp);
      }
      ul.appendChild(li);
    });
    grp.appendChild(ul);
    t.addEventListener("click", function () {
      var open = grp.classList.toggle("open");
      t.setAttribute("aria-expanded", open ? "true" : "false");
    });
    sidebar.appendChild(grp);
  });

  /* =============== PREV / NEXT =============== */
  var nav = el("nav", "lesson-nav");
  var prev = curIdx > 0 ? flat[curIdx - 1] : null;
  var next = curIdx >= 0 && curIdx < flat.length - 1 ? flat[curIdx + 1] : null;
  var prevEl;
  if (prev) { prevEl = el("a"); prevEl.href = link(prev.file); prevEl.innerHTML = '<div class="dir">&larr; Previous</div><div class="ttl">' + prev.title + "</div>"; }
  else { prevEl = el("a", "empty"); prevEl.href = "#"; }
  var nextEl;
  if (next) { nextEl = el("a", "next"); nextEl.href = link(next.file); nextEl.innerHTML = '<div class="dir">Next &rarr;</div><div class="ttl">' + next.title + "</div>"; }
  else { nextEl = el("a", "next empty"); nextEl.href = "#"; }
  nav.appendChild(prevEl); nav.appendChild(nextEl);

  /* =============== COMPLETION CONTROL =============== */
  var doneRow = el("div", "lesson-done" + (DONE[curN] ? " is-done" : ""));
  var db = el("button", "done-btn"); db.type = "button";
  db.innerHTML = DONE[curN] ? '&#10003; Completed &mdash; tap to undo' : 'Mark this lesson complete';
  db.addEventListener("click", function () {
    if (DONE[curN]) { delete DONE[curN]; } else { DONE[curN] = 1; }
    saveDone();
    if (DONE[curN]) { REV[curN] = { reviews: 0, due: Date.now() + DAY, done: Date.now() }; } else { delete REV[curN]; }
    saveRev();
    var d = !!DONE[curN];
    doneRow.classList.toggle("is-done", d);
    db.innerHTML = d ? '&#10003; Completed &mdash; tap to undo' : 'Mark this lesson complete';
  });
  doneRow.appendChild(db);

  /* =============== PAGE FOOTER =============== */
  var foot = el("div", "page-foot");
  foot.innerHTML = '<span>Applied GenAI Engineer &middot; a self-paced path</span>' +
    '<a href="' + link("index.html") + '">&uarr; Course home</a>';

  /* =============== ASSEMBLE =============== */
  var main = document.querySelector("main.lesson");
  var layout = el("div", "layout");
  var content = el("div", "content");
  if (main) content.appendChild(main);
  content.appendChild(doneRow);
  content.appendChild(nav);
  content.appendChild(foot);
  layout.appendChild(sidebar);
  layout.appendChild(content);
  var scrim = el("div", "scrim");
  scrim.addEventListener("click", function () { body.classList.remove("nav-open"); });

  while (body.firstChild) body.removeChild(body.firstChild);
  var readbar = el("div", "read-bar"); var readi = el("i"); readbar.appendChild(readi);
  body.appendChild(readbar);
  body.appendChild(header);
  body.appendChild(scrim);
  body.appendChild(layout);

  sidebar.addEventListener("click", function (e) { if (e.target.closest("a")) body.classList.remove("nav-open"); });

  function onScroll() {
    var de = document.documentElement;
    var max = de.scrollHeight - de.clientHeight;
    var y = window.scrollY || de.scrollTop || 0;
    readi.style.width = (max > 0 ? Math.min(100, y / max * 100) : 0) + "%";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  wireQuizzes();
  scrollTopOnLoad();

  /* =============== HELPERS =============== */
  function setupResume() {
    var nextL = null;
    for (var i = 0; i < flat.length; i++) { if (!DONE[flat[i].n]) { nextL = flat[i]; break; } }
    var d = 0; flat.forEach(function (f) { if (DONE[f.n]) d++; });
    var r = document.getElementById("home-resume");
    if (!r) return;
    if (d === 0) { r.textContent = "Start where you left off"; r.setAttribute("href", link(flat[0].file)); }
    else if (nextL) { r.textContent = "Resume → " + nextL.title; r.setAttribute("href", link(nextL.file)); }
    else { r.textContent = "You finished it — review ↺"; r.setAttribute("href", link(flat[0].file)); }
  }

  function renderRoadmap(target) {
    var total = 0, gdone = 0;
    C.sections.forEach(function (s) { s.lessons.forEach(function (l) { if (l.built) { total++; if (DONE[l.n]) gdone++; } }); });
    var gp = total ? Math.round(gdone / total * 100) : 0;
    var banner = el("div", "progress-banner");
    banner.innerHTML = '<div class="pb-top"><span><b>' + gdone + '</b> of <b>' + total + '</b> lessons complete</span><span class="pb-pct">' + gp + '%</span></div><div class="pb-bar"><i style="width:' + gp + '%"></i></div>';
    target.appendChild(banner);
    C.sections.forEach(function (s) {
      var built = s.lessons.filter(function (l) { return l.built; }).length;
      var d = s.lessons.filter(function (l) { return l.built && DONE[l.n]; }).length;
      var allDone = built > 0 && d === built;
      var card = el("div", "track-card" + (s.ready ? "" : " locked") + (allDone ? " complete" : ""));
      var statusCls = s.ready ? "ready" : "soon";
      var statusTxt = s.ready ? (allDone ? "✓ Done" : "Ready") : "Coming next";
      var nLabs = s.lessons.filter(function (l) { return l.built && isLab(l); }).length;
      var meta = s.ready ? built + " lessons" + (nLabs ? " &middot; <b>" + nLabs + " hands-on lab</b>" : "") + " &middot; concept, demo, quiz, practice" : s.lessons.length + " lessons planned";
      var prog = s.ready ? '<span class="tk-prog"><span class="tk-prog-t">' + d + '/' + built + '</span><span class="tk-prog-bar"><i style="width:' + (built ? Math.round(d / built * 100) : 0) + '%"></i></span></span>' : "";
      var head = el("button", "tk-head"); head.type = "button"; head.setAttribute("aria-expanded", "false");
      head.innerHTML =
        '<div class="tk-num">' + s.num + "</div>" +
        '<div class="tk-body"><h3>' + s.title + "</h3><p>" + s.blurb + "</p>" +
        '<div class="tk-meta"><span>' + meta + "</span></div></div>" +
        prog +
        '<span class="tk-status ' + statusCls + '">' + statusTxt + "</span>" +
        '<span class="tk-chev" aria-hidden="true">&#9656;</span>';
      card.appendChild(head);
      if (s.ready) {
        var drawer = el("div", "tk-drawer");
        var inner = el("div", "tk-drawer-inner");
        var ul = el("ul", "tk-lessons");
        s.lessons.forEach(function (l) {
          var li = el("li");
          if (l.built) {
            var a = el("a"); a.href = link(l.file);
            var rc = []; if (DONE[l.n]) rc.push("done"); if (isLab(l) || isVisual(l)) rc.push("is-lab"); if (rc.length) a.className = rc.join(" ");
            a.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + "</span>" +
          (isVisual(l) ? '<span class="ln-lab vis">VISUAL</span>' : isLab(l) ? '<span class="ln-lab">LAB</span>' : "") +
              (DONE[l.n] ? '<span class="ln-check" aria-hidden="true">&#10003;</span>' : "");
            li.appendChild(a);
          } else {
            li.className = "soon";
            li.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + '</span><span class="soon-tag">soon</span>';
          }
          ul.appendChild(li);
        });
        inner.appendChild(ul);
        var start = el("a", "tk-start"); start.href = link(s.lessons[0].file); start.innerHTML = "Start this track &rarr;";
        inner.appendChild(start);
        drawer.appendChild(inner); card.appendChild(drawer);
        head.addEventListener("click", function () { var open = card.classList.toggle("open"); head.setAttribute("aria-expanded", open ? "true" : "false"); });
      } else { head.disabled = true; }
      target.appendChild(card);
    });
  }

  function wireQuizzes() {
    var quizzes = document.querySelectorAll(".quiz");
    quizzes.forEach(function (q) {
      if (!q.querySelector(".quiz-tag")) { q.insertBefore(el("div", "quiz-tag", "Check yourself"), q.firstChild); }
      var opts = Array.prototype.slice.call(q.querySelectorAll(".quiz-options > li"));
      opts.forEach(function (li) {
        if (!li.querySelector(".badge")) {
          li.insertAdjacentHTML("beforeend", '<span class="badge ok">&#10003;</span><span class="badge no">&#10007;</span>');
        }
        li.addEventListener("click", function () {
          if (q.classList.contains("answered")) return;
          q.classList.add("answered");
          var ok = li.getAttribute("data-correct") === "true";
          li.classList.add("chosen");
          opts.forEach(function (o) { if (o.getAttribute("data-correct") === "true") o.classList.add("correct"); });
          if (ok) { q.classList.add("right"); } else { q.classList.add("wrong-final"); li.classList.add("wrong"); }
          var res = q.querySelector(".quiz-result");
          if (res) res.textContent = ok ? "Correct — nicely done." : "Not quite. Read why each option is right or wrong above.";
        });
      });
      if (!q.querySelector(".quiz-result")) q.appendChild(el("div", "quiz-result"));
      if (!q.querySelector(".quiz-reset")) {
        var rb = el("button", "quiz-reset", "Try again");
        rb.addEventListener("click", function () {
          q.classList.remove("answered", "right", "wrong-final");
          opts.forEach(function (o) { o.classList.remove("chosen", "correct", "wrong"); });
          var res = q.querySelector(".quiz-result"); if (res) res.textContent = "";
        });
        q.appendChild(rb);
      }
    });
  }

  function scrollTopOnLoad() { if (!window.location.hash) window.scrollTo(0, 0); }

  /* ---- glossary: click any .term to see its definition ---- */
  function normTerm(s) {
    return s.toLowerCase()
      .replace(/&amp;/g, "&").replace(/&#39;|&rsquo;|&lsquo;/g, "'").replace(/&quot;|&ldquo;|&rdquo;/g, '"')
      .replace(/[‘’]/g, "'").replace(/[“”]/g, '"')
      .replace(/^["']+|["']+$/g, "").replace(/\s+/g, " ").trim();
  }
  function defFor(text) {
    var G = window.AGE_GLOSSARY; if (!G) return null;
    var k = normTerm(text);
    if (G[k]) return G[k];
    if (k.charAt(k.length - 1) === "s" && G[k.slice(0, -1)]) return G[k.slice(0, -1)];
    if (G[k + "s"]) return G[k + "s"];
    return null;
  }
  function setupGlossary() {
    if (document.getElementById("age-termpop")) return;
    var pop = el("div", "term-pop"); pop.id = "age-termpop"; pop.style.display = "none";
    pop.innerHTML = '<span class="tp-term"></span><span class="tp-def"></span><button class="tp-x" aria-label="close">&times;</button>';
    document.body.appendChild(pop);
    var open = false;
    function hide() { pop.style.display = "none"; open = false; }
    function show(term) {
      var def = defFor(term.textContent);
      if (!def) return;
      pop.querySelector(".tp-term").textContent = term.textContent;
      pop.querySelector(".tp-def").textContent = def;
      pop.style.display = "block"; pop.style.visibility = "hidden";
      var r = term.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight;
      var left = Math.min(Math.max(8, r.left + r.width / 2 - pw / 2), window.innerWidth - pw - 8);
      var top = r.bottom + 8; if (top + ph > window.innerHeight - 8 && r.top - ph - 8 > 0) top = r.top - ph - 8;
      pop.style.left = (left + window.scrollX) + "px"; pop.style.top = (top + window.scrollY) + "px";
      pop.style.visibility = "visible"; open = true;
    }
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest(".term");
      if (t) { e.preventDefault(); if (open && pop._for === t) { hide(); } else { show(t); pop._for = t; } return; }
      if (open && !e.target.closest("#age-termpop")) hide();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && open) hide(); });
    pop.querySelector(".tp-x").addEventListener("click", hide);
    window.addEventListener("scroll", function () { if (open) hide(); }, { passive: true });
  }
  setupGlossary();

  /* ---- "Go deeper" references, appended to a lesson that has them ---- */
  function renderRefs() {
    if (isHome) return;
    var mainEl = document.querySelector("main.lesson"); if (!mainEl) return;
    if (mainEl.querySelector(".lesson-refs")) return;
    var R = window.AGE_REFERENCES;
    if (!R) { setTimeout(renderRefs, 150); return; }
    var refs = R[curN]; if (!refs || !refs.length) return;
    var KIND = { paper: "Paper", guide: "Guide", docs: "Docs", tool: "Tool", video: "Video" };
    var sec = el("section", "lesson-refs");
    var items = refs.map(function (r) {
      return '<li><a href="' + r.u + '" target="_blank" rel="noopener">' +
        '<span class="ref-kind ref-' + (r.k || "guide") + '">' + (KIND[r.k] || "Link") + "</span>" +
        '<span class="ref-title">' + r.t + '</span>' +
        '<span class="ref-ext" aria-hidden="true">&#8599;</span></a></li>';
    }).join("");
    sec.innerHTML = '<div class="refs-head"><span class="refs-eyebrow">Go deeper</span>' +
      '<p>Primary sources and canonical guides for this topic — open in a new tab.</p></div>' +
      '<ul class="refs-list">' + items + "</ul>";
    mainEl.appendChild(sec);
  }
  renderRefs();
})();
