/* Deep Quantum Science — consent banner and audience measurement.
 *
 * Audience measurement uses Cloudflare Web Analytics (no cookies, no
 * fingerprinting, no cross-site tracking). It is loaded only after the visitor
 * agrees. The choice is stored in this browser (localStorage "dqs-consent") and
 * can be changed at any time with the "Cookie settings" link in the footer.
 * Strictly necessary storage (language and light/dark choice) needs no consent.
 */
(function () {
  'use strict';
  var KEY = 'dqs-consent';
  var VERSION = 1;
  var CF_TOKEN = 'c0181811eba64e97a756df4ae46c578c';   // public site token, not a secret
  var root = document.documentElement;
  var prefix = (document.currentScript && document.currentScript.getAttribute('data-root')) || '/';

  var T = {
    en: {
      title: 'Your privacy',
      text: 'We would like to count visits anonymously with Cloudflare Web Analytics to improve this site. It uses no cookies and does not track you across websites. Do you agree?',
      accept: 'Accept statistics', reject: 'Only necessary', more: 'Privacy policy', settings: 'Cookie settings'
    },
    de: {
      title: 'Ihre Privatsphäre',
      text: 'Wir möchten Besuche mit Cloudflare Web Analytics anonym zählen, um diese Website zu verbessern. Dabei werden keine Cookies gesetzt und Sie werden nicht über Websites hinweg verfolgt. Sind Sie einverstanden?',
      accept: 'Statistik erlauben', reject: 'Nur notwendige', more: 'Datenschutzerklärung', settings: 'Cookie-Einstellungen'
    }
  };
  function lang() { return (root.dataset.lang || root.lang || 'en').slice(0, 2) === 'de' ? 'de' : 'en'; }

  function read() {
    try { var v = JSON.parse(localStorage.getItem(KEY) || 'null'); return v && v.v === VERSION ? v : null; }
    catch (e) { return null; }
  }
  function save(stats) {
    try { localStorage.setItem(KEY, JSON.stringify({ v: VERSION, stats: !!stats, at: new Date().toISOString() })); } catch (e) {}
  }

  var loaded = false;
  function loadAnalytics() {
    if (loaded || !CF_TOKEN) return;
    loaded = true;
    var s = document.createElement('script');
    s.defer = true;
    s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    s.setAttribute('data-cf-beacon', JSON.stringify({ token: CF_TOKEN }));
    document.head.appendChild(s);
  }

  var css = '' +
    '#dqs-consent{position:fixed;z-index:1000;left:16px;right:16px;bottom:16px;max-width:560px;margin-inline:auto;' +
    'background:var(--panel,#fff);color:var(--text,#15113a);border:1px solid var(--rule,#d8dbeb);border-radius:16px;' +
    'padding:18px 20px;box-shadow:0 18px 50px -20px rgba(0,0,0,.45);font:400 15px/1.55 var(--sans,system-ui,sans-serif)}' +
    '#dqs-consent h2{font:600 16px/1.3 var(--sans,system-ui,sans-serif);margin:0 0 6px;color:inherit}' +
    '#dqs-consent p{margin:0 0 14px;color:var(--text-2,#34375a)}' +
    '#dqs-consent a{color:inherit;text-decoration:underline}' +
    '#dqs-consent .row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}' +
    '#dqs-consent button{flex:1 1 160px;min-height:44px;border-radius:999px;font:600 15px/1 var(--sans,system-ui,sans-serif);' +
    'cursor:pointer;border:1px solid var(--rule,#d8dbeb);background:transparent;color:inherit;padding:0 18px}' +
    '#dqs-consent button:focus-visible{outline:2px solid var(--mint,#0a7462);outline-offset:3px}' +
    '#dqs-consent button[data-k="accept"]{background:var(--text,#15113a);color:var(--panel,#fff);border-color:var(--text,#15113a)}' +
    '@media print{#dqs-consent{display:none}}';

  var box = null;
  function render() {
    var t = T[lang()];
    box.innerHTML = '<h2 id="dqs-consent-title"></h2><p></p><div class="row">' +
      '<button type="button" data-k="reject"></button><button type="button" data-k="accept"></button></div>';
    box.querySelector('h2').textContent = t.title;
    var p = box.querySelector('p');
    p.textContent = t.text + ' ';
    var a = document.createElement('a');
    a.href = prefix + 'datenschutz';
    a.textContent = t.more;
    p.appendChild(a);
    box.querySelector('[data-k="reject"]').textContent = t.reject;
    box.querySelector('[data-k="accept"]').textContent = t.accept;
  }
  function open() {
    if (!box) {
      var st = document.createElement('style');
      st.textContent = css;
      document.head.appendChild(st);
      box = document.createElement('section');
      box.id = 'dqs-consent';
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-labelledby', 'dqs-consent-title');
      box.addEventListener('click', function (e) {
        var k = e.target && e.target.getAttribute && e.target.getAttribute('data-k');
        if (!k) return;
        save(k === 'accept');
        close();
        if (k === 'accept') loadAnalytics();
        else if (loaded) location.reload();   // stop measurement that already started
      });
    }
    render();
    if (!box.isConnected) document.body.appendChild(box);
  }
  function close() { if (box && box.isConnected) box.remove(); }

  function addFooterLink() {
    var host = document.querySelector('footer .legal') || document.querySelector('footer');
    if (!host || document.getElementById('dqs-consent-open')) return;
    var a = document.createElement('a');
    a.href = '#';
    a.id = 'dqs-consent-open';
    a.addEventListener('click', function (e) { e.preventDefault(); open(); });
    host.appendChild(a);
    function label() { a.textContent = T[lang()].settings; }
    label();
    new MutationObserver(function () { label(); if (box && box.isConnected) render(); })
      .observe(root, { attributes: true, attributeFilter: ['data-lang', 'lang'] });
  }

  function init() {
    addFooterLink();
    var c = read();
    if (!c) open();
    else if (c.stats) loadAnalytics();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
  window.dqsConsent = { open: open };
})();
