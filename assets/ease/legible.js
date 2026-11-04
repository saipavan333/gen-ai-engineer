/* Phone legibility for lesson diagrams (pass-2 review, Nov 2026).
 * The older diagrams under "Going deeper" are 700-1000-unit SVG files shown as <img>, so on a
 * 390 px phone their labels render at 4-8 px. For each diagram in the lesson:
 *   - <img src="*.svg">: read the file once, find its smallest label in drawing units, and if that
 *     label would render under FLOOR px, let the picture scroll sideways at the width where the
 *     smallest label is FLOOR px (with a "swipe" cue). An image's text can't be resized in place.
 *   - inline <svg>: raise the small labels to FLOOR in place when that moves no label out of its
 *     box, onto another label or out of the picture; otherwise scroll sideways the same way.
 * Re-runs on resize. Wide screens are untouched when nothing there falls under the floor.
 * Same method as Gradient Descent's gd-legible.js and Claude Mastery's legible.js.
 */
(function () {
  "use strict";
  var FLOOR = 9.1; // a hair over 9 px so rounding never lands under it
  var css = document.createElement("style");
  css.textContent = ".ez-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}" +
    ".ez-scrolling>img,.ez-scrolling>svg{max-width:none!important}" +
    ".ez-scrolling::after{content:'swipe sideways to see the whole diagram \\2192';display:block;position:sticky;left:0;font-size:13px;color:var(--muted,#888);padding:2px 0 6px}";
  document.head.appendChild(css);

  function wrapOf(el) {
    var p = el.parentNode;
    return p && p.classList && p.classList.contains("ez-scroll") ? p : null;
  }
  function scrollAt(el, minWidth) {
    var box = wrapOf(el);
    if (!box) {
      box = document.createElement("div");
      box.className = "ez-scroll";
      el.parentNode.insertBefore(box, el);
      box.appendChild(el);
    }
    box.classList.add("ez-scrolling");
    el.style.minWidth = Math.ceil(minWidth) + "px";
  }
  function unscroll(el) {
    var box = wrapOf(el);
    el.style.minWidth = "";
    if (box) box.classList.remove("ez-scrolling");
  }

  /* ---- images: smallest label of the SVG file, in drawing units (cached per file) ---- */
  var info = {};
  function measureFile(src) {
    if (info[src]) return info[src];
    // precomputed table (assets/ease/diagram-fonts.js) so this also works when the course is opened from disk
    var key = decodeURIComponent(src.split(/[?#]/)[0].split("/").pop()), T = window.EZ_DIAGRAM_FONTS;
    if (T && T[key]) return (info[src] = Promise.resolve({ vbw: T[key][0], min: T[key][1] }));
    info[src] = fetch(src).then(function (r) { return r.ok ? r.text() : null; }).then(function (txt) {
      if (!txt) return null;
      var doc = new DOMParser().parseFromString(txt, "image/svg+xml");
      var svg = doc.documentElement;
      if (!svg || svg.nodeName.toLowerCase() !== "svg") return null;
      var vb = (svg.getAttribute("viewBox") || "").trim().split(/[\s,]+/).map(Number);
      var vbw = vb.length === 4 ? vb[2] : parseFloat(svg.getAttribute("width"));
      if (!vbw) return null;
      // lay the drawing out at 1 unit = 1 px inside a shadow root, so its own <style> can't leak
      var host = document.createElement("div");
      host.style.cssText = "position:absolute;left:-99999px;top:0;visibility:hidden;pointer-events:none";
      document.body.appendChild(host);
      var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
      var live = document.importNode(svg, true);
      live.setAttribute("width", vbw);
      live.removeAttribute("height");
      root.appendChild(live);
      var min = Infinity;
      Array.prototype.forEach.call(live.querySelectorAll("text"), function (t) {
        if (!t.textContent.trim()) return;
        var m = t.getCTM && t.getCTM(), k = m ? Math.hypot(m.a, m.b) : 1;
        var fs = parseFloat(getComputedStyle(t).fontSize) * k;
        if (fs && fs < min) min = fs;
      });
      host.remove();
      return isFinite(min) ? { vbw: vbw, min: min } : null;
    }).catch(function () { return null; });
    return info[src];
  }
  function legibleImg(img) {
    measureFile(img.src).then(function (d) {
      if (!d) return;
      unscroll(img);
      var w = img.getBoundingClientRect().width;
      if (!w) return;
      if (d.min * w / d.vbw >= FLOOR) return;
      scrollAt(img, d.vbw * FLOOR / d.min);
    });
  }

  /* ---- inline SVG ---- */
  function restore(t) {
    if (t.dataset.fs0 == null) return;
    t.style.fontSize = t.dataset.fs0;
    delete t.dataset.fs0;
  }
  function legibleSvg(svg) {
    var vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width) return;
    var texts = Array.prototype.filter.call(svg.querySelectorAll("text"), function (t) { return t.textContent.trim(); });
    texts.forEach(restore);
    unscroll(svg);
    var w = svg.getBoundingClientRect().width;
    if (!w || !texts.length) return;
    var need = FLOOR / (w / vb.width);
    var fs = function (t) { return parseFloat(getComputedStyle(t).fontSize); };
    var small = texts.filter(function (t) { return fs(t) < need - 0.01; });
    if (!small.length) return;
    var rects = Array.prototype.map.call(svg.querySelectorAll("rect"), function (r) { try { return r.getBBox(); } catch (e) { return null; } })
      .filter(function (b) { return b && b.width > 4 && b.height > 4 && b.width < vb.width * 0.98; });
    var inside = function (a, r) { return a.x >= r.x + 1.5 && a.y >= r.y - 0.5 && a.x + a.width <= r.x + r.width - 1.5 && a.y + a.height <= r.y + r.height + 0.5; };
    var hit = function (a, b) { return Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x) > 1 && Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y) > 1; };
    var outOf = function (b) { return b.x < vb.x - 0.5 || b.x + b.width > vb.x + vb.width + 0.5 || b.y < vb.y - 0.5 || b.y + b.height > vb.y + vb.height + 0.5; };
    var bb = function (t) { try { return t.getBBox(); } catch (e) { return { x: 0, y: 0, width: 0, height: 0 }; } };
    var b0 = texts.map(bb);
    small.forEach(function (t) { t.dataset.fs0 = t.style.fontSize || ""; t.style.fontSize = need.toFixed(2) + "px"; });
    var b1 = texts.map(bb), bad = false;
    for (var i = 0; i < texts.length && !bad; i++) {
      if (outOf(b1[i]) && !outOf(b0[i])) bad = true;
      for (var k = 0; k < rects.length && !bad; k++) if (inside(b0[i], rects[k]) && !inside(b1[i], rects[k])) bad = true;
      for (var j = i + 1; j < texts.length && !bad; j++) if (hit(b1[i], b1[j]) && !hit(b0[i], b0[j])) bad = true;
    }
    if (!bad) return;
    small.forEach(restore);
    scrollAt(svg, (vb.width * FLOOR) / Math.min.apply(null, texts.map(fs)));
  }

  function all() {
    var main = document.querySelector("main") || document.body;
    Array.prototype.forEach.call(main.querySelectorAll("img"), function (img) {
      if (/\.svg(\?|#|$)/i.test(img.getAttribute("src") || "")) {
        if (img.complete) legibleImg(img); else img.addEventListener("load", function () { legibleImg(img); }, { once: true });
      }
    });
    // inline figures, but not the pass-2 plays (they redraw a phone layout of their own) or icons
    Array.prototype.forEach.call(main.querySelectorAll("svg[viewBox]"), function (svg) {
      if (svg.closest(".ez-play,header,nav,button,.logo")) return;
      legibleSvg(svg);
    });
  }
  var timer = 0;
  if (document.readyState === "complete") all(); else window.addEventListener("load", all);
  window.addEventListener("resize", function () { clearTimeout(timer); timer = setTimeout(all, 150); });
  window.EZLegible = all;
  window.EZLegible.measureFile = measureFile;
})();
