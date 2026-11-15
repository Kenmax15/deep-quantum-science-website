/* Deep Quantum Science — shows where you are in the top navigation.
 * • Links to another page are marked when you are on that page (e.g. "Blog"
 *   on every article).
 * • Links to a section of the current page are marked while that section is
 *   on screen, and immediately when clicked.
 */
(function () {
  'use strict';
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav .links a'));
  if (!links.length) return;
  var here = location.pathname.replace(/\/index(\.html)?$/, '/').replace(/\.html$/, '');
  var sections = [];

  links.forEach(function (a) {
    var u = new URL(a.getAttribute('href'), location.href);
    var path = u.pathname.replace(/\/index(\.html)?$/, '/').replace(/\.html$/, '');
    if (u.hash && path === here) {
      var el = document.getElementById(decodeURIComponent(u.hash.slice(1)));
      if (el) sections.push({ a: a, el: el });
    } else if (!u.hash && path !== '/' && (here === path || (path.slice(-1) === '/' && here.indexOf(path) === 0))) {
      a.setAttribute('aria-current', 'page');
    }
  });
  if (!sections.length) return;

  var current = null;
  function mark(a) {
    if (current === a) return;
    sections.forEach(function (s) { s.a.classList.toggle('active', s.a === a); if (s.a === a) s.a.setAttribute('aria-current', 'location'); else s.a.removeAttribute('aria-current'); });
    current = a;
  }
  function update() {
    var line = window.innerHeight * 0.35, best = null;
    sections.forEach(function (s) {
      var r = s.el.getBoundingClientRect();
      if (r.top <= line && r.bottom > line) best = s.a;
    });
    // near the bottom of the page the last section wins
    if (!best && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) best = sections[sections.length - 1].a;
    mark(best);
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; update(); }); }
  }, { passive: true });
  window.addEventListener('resize', update);
  sections.forEach(function (s) { s.a.addEventListener('click', function () { mark(s.a); }); });
  update();
})();

/* Mobile menu for pages whose menu button carries data-menu="auto"
 * (blog and manuscript pages; the home page wires its own). */
(function () {
  'use strict';
  var nav = document.querySelector('.nav'), btn = document.getElementById('menu-toggle');
  if (!nav || !btn || btn.getAttribute('data-menu') !== 'auto') return;
  function set(o) { nav.classList.toggle('open', o); btn.setAttribute('aria-expanded', String(o)); }
  btn.addEventListener('click', function () { set(!nav.classList.contains('open')); });
  Array.prototype.forEach.call(document.querySelectorAll('#nav-links a'), function (a) { a.addEventListener('click', function () { set(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { set(false); btn.focus(); } });
  document.addEventListener('click', function (e) { if (nav.classList.contains('open') && !nav.contains(e.target)) set(false); });
  if (window.matchMedia) matchMedia('(min-width:1181px)').addEventListener('change', function (e) { if (e.matches) set(false); });
  var t2 = document.getElementById('theme-toggle-2'), t1 = document.getElementById('theme-toggle');
  if (t2 && t1) t2.addEventListener('click', function () { t1.click(); });
})();
