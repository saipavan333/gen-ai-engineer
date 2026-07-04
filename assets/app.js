/* ============================================================
   app.js — builds the course chrome from CURRICULUM and wires
   up interactivity. Pure vanilla JS, no network, no storage:
   it runs by just opening the HTML file.
   ============================================================ */
(function () {
  "use strict";
  var C = window.CURRICULUM;
  var body = document.body;
  var base = body.getAttribute("data-base") || "";
  var isHome = body.getAttribute("data-page") === "home";
  var curN = body.getAttribute("data-lesson") || "";

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function link(href) { return base + href; }

  /* ---- favicon (injected so every page gets it, no per-file edits) ---- */
  if (!document.querySelector('link[rel="icon"]')) {
    var fav = document.createElement("link");
    fav.rel = "icon"; fav.type = "image/svg+xml"; fav.href = link("assets/favicon.svg");
    document.head.appendChild(fav);
  }

  /* ---- flat ordered list of built lessons (for prev/next) ---- */
  var flat = [];
  C.sections.forEach(function (s) {
    s.lessons.forEach(function (l) {
      if (l.built) flat.push({ n: l.n, title: l.title, file: l.file, section: s });
    });
  });
  var curIdx = -1;
  for (var i = 0; i < flat.length; i++) { if (flat[i].n === curN) { curIdx = i; break; } }
  var cur = curIdx >= 0 ? flat[curIdx] : null;

  /* ===========================================================
     HEADER
     =========================================================== */
  var header = el("header", "site-header");
  var brand = el("a", "brand");
  brand.href = link("index.html");
  brand.innerHTML = '<img class="logo" src="' + link("assets/favicon.svg") + '" alt="" width="26" height="26"><span class="brand-name">Applied GenAI Engineer</span>';
  header.appendChild(brand);

  if (!isHome && cur) {
    var crumb = el("span", "crumb", "Track " + cur.section.num + " · " + cur.section.title);
    header.appendChild(crumb);
  }
  header.appendChild(el("span", "spacer"));

  if (!isHome && cur) {
    // position within this section's built lessons
    var sLessons = cur.section.lessons.filter(function (l) { return l.built; });
    var posIdx = 0;
    for (var j = 0; j < sLessons.length; j++) { if (sLessons[j].n === cur.n) { posIdx = j + 1; break; } }
    header.appendChild(el("span", "pos", "Lesson " + posIdx + " of " + sLessons.length));
    var menu = el("button", "menu-btn", "&#8801; Menu");
    menu.setAttribute("aria-label", "Toggle lesson menu");
    menu.addEventListener("click", function () { body.classList.toggle("nav-open"); });
    // place menu button at the far left, before brand, on mobile
    header.insertBefore(menu, header.firstChild);
  }

  /* ===========================================================
     HOME
     =========================================================== */
  if (isHome) {
    document.body.insertBefore(header, document.body.firstChild);
    var roadmap = document.getElementById("roadmap");
    if (roadmap) renderRoadmap(roadmap);
    wireQuizzes();
    scrollTopOnLoad();
    return;
  }

  /* ===========================================================
     SIDEBAR (collapsible accordion — current track auto-opens)
     =========================================================== */
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
        a.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + "</span>";
        if (l.n === curN) a.className = "active";
        li.appendChild(a);
      } else {
        var sp = el("span", "locked");
        sp.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title +
          '</span><span class="lock-ico">soon</span>';
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

  /* ===========================================================
     PREV / NEXT
     =========================================================== */
  var nav = el("nav", "lesson-nav");
  var prev = curIdx > 0 ? flat[curIdx - 1] : null;
  var next = curIdx >= 0 && curIdx < flat.length - 1 ? flat[curIdx + 1] : null;

  var prevEl;
  if (prev) {
    prevEl = el("a");
    prevEl.href = link(prev.file);
    prevEl.innerHTML = '<div class="dir">&larr; Previous</div><div class="ttl">' + prev.title + "</div>";
  } else {
    prevEl = el("a", "empty"); prevEl.href = "#";
  }
  var nextEl;
  if (next) {
    nextEl = el("a", "next");
    nextEl.href = link(next.file);
    nextEl.innerHTML = '<div class="dir">Next &rarr;</div><div class="ttl">' + next.title + "</div>";
  } else {
    nextEl = el("a", "next empty"); nextEl.href = "#";
  }
  nav.appendChild(prevEl);
  nav.appendChild(nextEl);

  /* ===========================================================
     PAGE FOOTER
     =========================================================== */
  var foot = el("div", "page-foot");
  foot.innerHTML =
    '<span>Applied GenAI Engineer &middot; a self-paced path</span>' +
    '<a href="' + link("index.html") + '">&uarr; Course home</a>';

  /* ===========================================================
     ASSEMBLE
     =========================================================== */
  var main = document.querySelector("main.lesson");
  var layout = el("div", "layout");
  var content = el("div", "content");
  if (main) content.appendChild(main);
  content.appendChild(nav);
  content.appendChild(foot);
  layout.appendChild(sidebar);
  layout.appendChild(content);

  var scrim = el("div", "scrim");
  scrim.addEventListener("click", function () { body.classList.remove("nav-open"); });

  // rebuild body
  while (body.firstChild) body.removeChild(body.firstChild);
  body.appendChild(header);
  body.appendChild(scrim);
  body.appendChild(layout);

  // close mobile nav after following a lesson link
  sidebar.addEventListener("click", function (e) {
    if (e.target.closest("a")) body.classList.remove("nav-open");
  });

  wireQuizzes();
  scrollTopOnLoad();

  /* ===========================================================
     HELPERS
     =========================================================== */
  function renderRoadmap(target) {
    C.sections.forEach(function (s) {
      var built = s.lessons.filter(function (l) { return l.built; }).length;
      var card = el("div", "track-card" + (s.ready ? "" : " locked"));
      var statusCls = s.ready ? "ready" : "soon";
      var statusTxt = s.ready ? "Ready" : "Coming next";
      var meta = s.ready
        ? built + " lessons &middot; concept, demo, quiz, practice"
        : s.lessons.length + " lessons planned";

      var head = el("button", "tk-head");
      head.type = "button";
      head.setAttribute("aria-expanded", "false");
      head.innerHTML =
        '<div class="tk-num">' + s.num + "</div>" +
        '<div class="tk-body"><h3>' + s.title + "</h3><p>" + s.blurb + "</p>" +
        '<div class="tk-meta"><span>' + meta + "</span></div></div>" +
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
            var a = el("a");
            a.href = link(l.file);
            a.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title + "</span>";
            li.appendChild(a);
          } else {
            li.className = "soon";
            li.innerHTML = '<span class="ln">' + l.n + '</span><span>' + l.title +
              '</span><span class="soon-tag">soon</span>';
          }
          ul.appendChild(li);
        });
        inner.appendChild(ul);
        var start = el("a", "tk-start");
        start.href = link(s.lessons[0].file);
        start.innerHTML = "Start this track &rarr;";
        inner.appendChild(start);
        drawer.appendChild(inner);
        card.appendChild(drawer);
        head.addEventListener("click", function () {
          var open = card.classList.toggle("open");
          head.setAttribute("aria-expanded", open ? "true" : "false");
        });
      } else {
        head.disabled = true;
      }
      target.appendChild(card);
    });
  }

  function wireQuizzes() {
    var quizzes = document.querySelectorAll(".quiz");
    quizzes.forEach(function (q) {
      // inject tag
      if (!q.querySelector(".quiz-tag")) {
        var tag = el("div", "quiz-tag", "Check yourself");
        q.insertBefore(tag, q.firstChild);
      }
      var opts = Array.prototype.slice.call(q.querySelectorAll(".quiz-options > li"));
      opts.forEach(function (li) {
        if (!li.querySelector(".badge")) {
          li.insertAdjacentHTML("beforeend",
            '<span class="badge ok">&#10003;</span><span class="badge no">&#10007;</span>');
        }
        li.addEventListener("click", function () {
          if (q.classList.contains("answered")) return;
          q.classList.add("answered");
          var ok = li.getAttribute("data-correct") === "true";
          li.classList.add("chosen");
          opts.forEach(function (o) {
            if (o.getAttribute("data-correct") === "true") o.classList.add("correct");
          });
          if (ok) { q.classList.add("right"); }
          else { q.classList.add("wrong-final"); li.classList.add("wrong"); }
          var res = q.querySelector(".quiz-result");
          if (res) res.textContent = ok
            ? "Correct — nicely done."
            : "Not quite. Read why each option is right or wrong above.";
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

  function scrollTopOnLoad() {
    if (!window.location.hash) window.scrollTo(0, 0);
  }
})();
