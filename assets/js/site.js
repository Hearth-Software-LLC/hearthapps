// Hearth — small progressive enhancements. The site works without this file.
(function () {
  var doc = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile menu
  var nav = document.querySelector('.nav');
  var btn = document.querySelector('.menu-btn');
  if (nav && btn) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    nav.querySelectorAll('.sheet a').forEach(function (a) {
      a.addEventListener('click', function () {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        btn.setAttribute('aria-label', 'Open menu');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        btn.focus();
      }
    });
  }

  // Light / dark appearance. The <head> script already set data-theme before paint.
  var themeBtn = document.querySelector('.theme-btn');
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function savedTheme() { try { return localStorage.getItem('hearth-theme'); } catch (e) { return null; } }
  function applyTheme(t) {
    doc.setAttribute('data-theme', t);
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) { m.setAttribute('content', t === 'dark' ? '#000000' : '#FBFBFD'); });
    if (themeBtn) themeBtn.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
  applyTheme(doc.getAttribute('data-theme') || (mq && mq.matches ? 'dark' : 'light'));
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', function (e) { if (!savedTheme()) applyTheme(e.matches ? 'dark' : 'light'); });
  }
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = doc.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('hearth-theme', next); } catch (e) {}
      if (!document.startViewTransition || reduce) { applyTheme(next); return; }
      var r = themeBtn.getBoundingClientRect();
      var x = r.left + r.width / 2, y = r.top + r.height / 2;
      var end = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
      var vt = document.startViewTransition(function () { applyTheme(next); });
      vt.ready.then(function () {
        doc.animate({ clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + end + 'px at ' + x + 'px ' + y + 'px)'] },
          { duration: 650, easing: 'cubic-bezier(.2, .8, .2, 1)', pseudoElement: '::view-transition-new(root)' });
      });
    });
  }

  if (!('IntersectionObserver' in window)) return;

  // Scroll reveals: fall back to IntersectionObserver where CSS scroll-driven
  // animations aren't supported.
  var native = window.CSS && CSS.supports && CSS.supports('animation-timeline: view()');
  if (!native && !reduce) {
    doc.classList.add('js-io');
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in-view'); revealIO.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
    document.querySelectorAll('.reveal, .reveal-zoom, .tile, .pr, .doc section').forEach(function (el) { revealIO.observe(el); });
  }

  // Rings and bars in the phone mockups fill when they come into view.
  var fillIO = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('in-view'); fillIO.unobserve(en.target); }
    });
  }, { threshold: 0.35 });
  document.querySelectorAll('.stage').forEach(function (el) { fillIO.observe(el); });

  // Highlight the current section in legal-page tables of contents.
  var toc = document.querySelector('.toc');
  if (toc) {
    var links = {};
    toc.querySelectorAll('a[href^="#"]').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
    var tocIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && links[en.target.id]) {
          Object.keys(links).forEach(function (k) { links[k].classList.remove('active'); });
          links[en.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('.doc section[id]').forEach(function (s) { tocIO.observe(s); });
  }
})();
