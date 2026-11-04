/* Pass 2 interactives: tiny core. Each play-tNN.js registers EZ.plays[name] = function (stage, root) {...}.
   A play builds its own controls and one <svg class="ez-svg ez-one"> inside .ez-stage, and redraws the svg
   when a control moves. Vanilla JS, no dependencies. Colours come from CSS classes (see styles.css). */
(function () {
  var EZ = window.EZ = window.EZ || { plays: {} };
  var NS = "http://www.w3.org/2000/svg";
  EZ.el = function (tag, attrs, parent, txt) {
    var e = document.createElement(tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (txt != null) e.textContent = txt;
    if (parent) parent.appendChild(e);
    return e;
  };
  EZ.s = function (tag, attrs, parent, txt) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (txt != null) e.textContent = txt;
    if (parent) parent.appendChild(e);
    return e;
  };
  EZ.svg = function (stage, w, h, label) {
    var s = EZ.s("svg", { "class": "ez-svg ez-one", viewBox: "0 0 " + w + " " + h, role: "img", "aria-label": label || "interactive diagram" }, stage);
    return s;
  };
  /* phones get their own layout (viewBox about 360 wide) so text stays readable at 390 px */
  EZ.narrow = function (stage) { return (stage.clientWidth || window.innerWidth) < 480; };
  /* redraw when the layout flips between narrow and wide */
  EZ.watch = function (stage, draw) {
    var was = EZ.narrow(stage), t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(function () { var n = EZ.narrow(stage); if (n !== was) { was = n; draw(); } }, 120); });
  };
  EZ.clear = function (node) { while (node.firstChild) node.removeChild(node.firstChild); };
  /* a labelled range slider; onInput(value) */
  EZ.slider = function (bar, label, min, max, step, val, fmt, onInput) {
    var lab = EZ.el("label", {}, bar);
    EZ.el("span", {}, lab, label);
    var r = EZ.el("input", { type: "range", min: min, max: max, step: step, value: val, "aria-label": label }, lab);
    var o = EZ.el("output", {}, lab, fmt ? fmt(+val) : val);
    r.addEventListener("input", function () { o.textContent = fmt ? fmt(+r.value) : r.value; onInput(+r.value); });
    return r;
  };
  EZ.buttons = function (bar, names, active, onPick) {
    var bs = names.map(function (n, i) {
      var b = EZ.el("button", { type: "button" }, bar, n);
      if (i === active) b.className = "on";
      b.addEventListener("click", function () { bs.forEach(function (x) { x.className = ""; }); b.className = "on"; onPick(i); });
      return b;
    });
    return bs;
  };
  /* arrow with polygon head, same as tools/ease/kit.py */
  EZ.arrow = function (g, x1, y1, x2, y2, cls) {
    var a = Math.atan2(y2 - y1, x2 - x1), h = 9, bx = x2 - h * Math.cos(a), by = y2 - h * Math.sin(a);
    var px = h * .55 * Math.sin(a), py = -h * .55 * Math.cos(a);
    EZ.s("line", { x1: x1, y1: y1, x2: bx, y2: by, "class": "ln " + (cls || "") }, g);
    EZ.s("polygon", { points: x2 + "," + y2 + " " + (bx + px) + "," + (by + py) + " " + (bx - px) + "," + (by - py), "class": "hd " + (cls || "") }, g);
  };
  EZ.text = function (g, x, y, s, cls, anchor, size) {
    var t = EZ.s("text", { x: x, y: y, "text-anchor": anchor || "middle" }, g, s);
    if (cls) t.setAttribute("class", cls);
    if (size) t.style.fontSize = size + "px";
    return t;
  };
  EZ.rect = function (g, x, y, w, h, cls, rx) {
    return EZ.s("rect", { x: x, y: y, width: Math.max(0, w), height: Math.max(0, h), rx: rx == null ? 8 : rx, "class": cls || "bx" }, g);
  };
  function boot() {
    var nodes = document.querySelectorAll("[data-ez-play]");
    for (var i = 0; i < nodes.length; i++) {
      var root = nodes[i], name = root.getAttribute("data-ez-play"), f = EZ.plays[name];
      if (!f) { console.error("ease: no play registered for '" + name + "'"); continue; }
      f(root.querySelector(".ez-stage"), root);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else setTimeout(boot, 0);
})();
