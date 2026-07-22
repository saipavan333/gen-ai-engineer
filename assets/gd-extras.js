/* Gradient Descent — site extras: creator byline, tasteful page effects, and nav memory
   (resume-where-you-left-off + a reliable Back). Namespaced .gdx. Self-contained, offline. */
(function(){
"use strict";
if(window.__gdxLoaded)return; window.__gdxLoaded=true;

var LAST="gdx_last_v1", TRAIL="gdx_trail_v1";
function jget(store,k,d){try{return JSON.parse(store.getItem(k))||d}catch(e){return d}}
function jset(store,k,v){try{store.setItem(k,JSON.stringify(v))}catch(e){}}
function reduce(){return !!(window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches);}
function esc(s){var d=document.createElement("div");d.textContent=(s==null?"":String(s));return d.innerHTML;}
function sameOrigin(u){try{return new URL(u,location.href).origin===location.origin}catch(e){return false}}
var inLessons=/\/lessons\//.test(location.pathname);
var isHome=/(^|\/)(index\.html)?$/.test(location.pathname) || document.body.getAttribute("data-page")==="home" || /(^|\s)home(\s|$)/.test(document.body.className||"");

function pageTitle(){
  var h=document.querySelector("main.content h1, main.lesson h1, article.content h1, .lesson-title, .lesson-head h1, main h1, h1");
  return ((h&&h.textContent)||document.title||"").replace(/\s*·.*$/,"").replace(/\s+/g," ").trim();
}
function isLesson(){return !isHome && !!document.querySelector("article.content, main.lesson, main.content");}   /* real lesson on any course */

function boot(){
  injectA11y();
  recordNav();
  mountTopCredit();
  injectByline();
  runEffects();
  injectBack();
  if(isHome) injectResume();
}

/* ---------- creator byline at the top ----------
   Blend the credit INTO the course's own header/top bar (so it reads as part of
   the banner, adapting to each course's UI) rather than a separate strip above it.
   Headers are often built by the course's own JS, so we wait for one to appear;
   only if a page truly has no top bar do we fall back to the slim ribbon. */
var HEADER_SEL="header.site-header, .site-header, .topbar, header.masthead, .masthead, header.site-head, header.app-header";
function headerEl(){
  var list=document.querySelectorAll(HEADER_SEL);
  for(var i=0;i<list.length;i++){ var h=list[i]; if(h.offsetParent!==null || h.getClientRects().length) return h; }
  return list[0]||null;
}
function mountTopCredit(){
  var h=headerEl(); if(h){ injectHeaderCredit(h); return; }
  var done=false;
  function finish(hdr){ if(done)return; done=true; try{mo.disconnect()}catch(e){} if(hdr)injectHeaderCredit(hdr); else injectTopByline(); }
  var mo=new MutationObserver(function(){ var hh=headerEl(); if(hh)finish(hh); });
  try{ mo.observe(document.documentElement,{childList:true,subtree:true}); }catch(e){ injectTopByline(); return; }
  setTimeout(function(){ finish(headerEl()); }, 4000);   /* no header ever appeared → ribbon fallback */
}
/* credit that lives inside the existing header bar (right-aligned via CSS margin) */
function injectHeaderCredit(h){
  if(!h || document.querySelector(".gdx-headcredit, .gdx-topcredit"))return;
  var s=document.createElement("span"); s.className="gdx-headcredit";
  s.innerHTML='<span class="gdx-sig">Built by <b>U E Sai Pavan Vamshi Krishna</b></span>';
  h.appendChild(s);
}
/* fallback only: a slim ribbon for pages with no top bar at all */
function injectTopByline(){
  if(document.querySelector(".gdx-topcredit, .gdx-headcredit"))return;
  var b=document.createElement("div"); b.className="gdx-topcredit";
  b.innerHTML='<span class="gdx-sig">Built by <b>U E Sai Pavan Vamshi Krishna</b></span>';
  document.body.insertBefore(b, document.body.firstChild);
}

/* ---------- accessibility: skip link, main landmark, labelled diagrams ---------- */
function injectA11y(){
  var main=document.querySelector("article.content")||document.querySelector("main.lesson")||document.querySelector("main.content")||document.querySelector(".main")||document.querySelector(".home-wrap")||document.querySelector("main")||document.querySelector(".wrap");
  if(main){
    if(!main.id) main.id="gdx-main";
    if(!document.querySelector("main, [role=main]")) main.setAttribute("role","main");
    if(!main.hasAttribute("tabindex")) main.setAttribute("tabindex","-1");
    if(!document.querySelector(".gdx-skip")){
      var s=document.createElement("a"); s.className="gdx-skip"; s.href="#"+main.id; s.textContent="Skip to content";
      document.body.insertBefore(s, document.body.firstChild);
    }
  }
  [].forEach.call(document.querySelectorAll("figure.diagram"),function(fig){   /* give each diagram an accessible name from its caption */
    var svg=fig.querySelector("svg"), cap=fig.querySelector("figcaption");
    if(svg && !svg.getAttribute("role") && svg.getAttribute("aria-hidden")==null){
      svg.setAttribute("role","img");
      if(cap && cap.textContent.trim()) svg.setAttribute("aria-label", cap.textContent.replace(/\s+/g," ").trim());
    }
  });
}

/* ---------- nav memory ---------- */
function recordNav(){
  var u=location.pathname, t=pageTitle();
  var tr=jget(sessionStorage,TRAIL,[]);
  if(!tr.length || tr[tr.length-1].u!==u){ tr.push({u:u,t:t}); if(tr.length>30)tr=tr.slice(-30); jset(sessionStorage,TRAIL,tr); }
  if(isLesson()) jset(localStorage,LAST,{u:u,t:t,ts:Date.now()});   /* remember the last real lesson read */
}
function trailPrev(){var tr=jget(sessionStorage,TRAIL,[]);return tr.length>=2?tr[tr.length-2]:null;}

/* ---------- creator byline (every page, single source) ---------- */
function injectByline(){
  if(document.querySelector(".gdx-credit"))return;
  var f=document.createElement("footer"); f.className="gdx-credit";
  f.innerHTML='<span class="gdx-sig">Built by <b>U E Sai Pavan Vamshi Krishna</b></span>';
  document.body.appendChild(f);
}

/* ---------- tasteful page effects (only when motion is allowed; content stays visible otherwise) ---------- */
function runEffects(){
  if(reduce())return;
  document.documentElement.classList.add("gdx-anim");   /* entrance = CSS opacity keyframe (always ends visible) */
  if(!("IntersectionObserver" in window))return;
  var sel="article.content > h2, article.content > figure, article.content > .keypoints, article.content > .quiz, article.content > details, main.lesson > h2, main.lesson > figure, main.lesson > .box, main.content > h2, main.content > figure, main.content > p.lesson-lede, .track-card, .lab-card, .p-item, .home-wrap section";
  var els=[].slice.call(document.querySelectorAll(sel));
  if(!els.length)return;
  els.forEach(function(el){el.classList.add("gdx-reveal");});
  var io=new IntersectionObserver(function(ents){ents.forEach(function(en){if(en.isIntersecting){en.target.classList.add("gdx-seen");io.unobserve(en.target);}});},{rootMargin:"0px 0px -6% 0px"});
  els.forEach(function(el){io.observe(el);});
}

/* ---------- reliable Back, in the breadcrumb (returns to the previous page you were on) ---------- */
function injectBack(){
  var crumb=document.querySelector(".topbar .crumb"); if(!crumb||crumb.querySelector(".gdx-back"))return;
  var a=document.createElement("a"); a.className="gdx-back"; a.href="#"; a.textContent="← Back";
  a.title="Back to the previous page you were on";
  a.onclick=function(e){
    e.preventDefault();
    if(document.referrer && sameOrigin(document.referrer)){ history.back(); return; }   /* the true previous page */
    var p=trailPrev(); if(p){ location.href=p.u; return; }                               /* fallback: session trail */
    location.href=(inLessons?"../index.html":"index.html");                              /* last resort: home */
  };
  crumb.insertBefore(a, crumb.firstChild);
}

/* ---------- resume where you left off (home page) ---------- */
function injectResume(){
  var d=jget(localStorage,LAST,null); if(!d||!d.u||document.querySelector(".gdx-resume"))return;
  var main=document.querySelector(".main")||document.querySelector(".home-wrap")||document.querySelector("main")||document.querySelector(".app"); if(!main)return;
  var a=document.createElement("a"); a.className="gdx-resume"; a.href=d.u;
  a.innerHTML='<span class="gdx-resume-ic">▸</span><span class="gdx-resume-tx"><b>Resume where you left off</b><span>'+esc(d.t||"Continue the course")+'</span></span><span class="gdx-resume-go">Continue →</span>';
  main.insertBefore(a, main.firstChild);
}

if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot);else boot();
})();
