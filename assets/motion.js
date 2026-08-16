/* Cauvery Peak — motion.
   Reveals on scroll, images that resolve rather than pop, and a masthead
   that condenses once. No dependencies. Everything degrades to "visible"
   if any of it fails. */
(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- what gets revealed ------------------------------------------
     Chosen rather than blanket-applied: a heading, a plate or a row of
     cards benefits; navigation, controls and anything already on screen
     at load does not. */
  var SEL = [
    '.ruled__mark', '.mark', '.d1', '.d2', '.eyebrow',
    '.lede', '.body', '.btns',
    '.ledger li', '.entry', '.cof', '.plate', '.section',
    '.flow__step', '.chap', '.cut', '.tl__i', '.person', '.brew',
    '.envcard', '.cafe', '.coffee', '.blend', '.pick', '.wl__i',
    '.cite', '.facts > div', '.tourfacts li', '.kv', '.stat', '.do', '.diff'
  ].join(',');

  function group(el) {
    // stagger siblings that arrive together, cap the delay so a long
    // list never feels like it is queueing
    var p = el.parentElement;
    if (!p) return 0;
    var kin = [].slice.call(p.children).filter(function (c) { return c.hasAttribute('data-rise'); });
    var i = kin.indexOf(el);
    return i > 0 ? Math.min(i, 5) * 60 : 0;
  }

  function reveal() {
    var els = [].slice.call(document.querySelectorAll(SEL));
    if (!els.length) return;
    var vh = innerHeight;
    els.forEach(function (el) {
      if (el.closest('.drawer,.cart,.top')) return;      // chrome never animates
      if (el.hasAttribute('data-rise')) return;
      el.setAttribute('data-rise', '');
      // anything already in view at load is shown immediately — a reveal
      // the visitor did not scroll to is just a flash
      if (el.getBoundingClientRect().top < vh * 0.92) {
        el.classList.add('is-in');
      }
    });

    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.style.setProperty('--d', group(e.target) + 'ms');
        e.target.classList.add('is-in');
        io.unobserve(e.target);                           // once, never again
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });

    els.forEach(function (el) {
      if (!el.classList.contains('is-in')) io.observe(el);
    });
  }

  /* ---- images resolve ---------------------------------------------- */
  function images() {
    [].slice.call(document.images).forEach(function (img) {
      if (img.closest('.top,.foot,.drawer,.cart')) return;   // chrome + logos
      if (img.hasAttribute('data-img')) return;
      img.setAttribute('decoding', 'async');
      // already painted (cached, or above the fold) — leave it alone
      if (img.complete && img.naturalWidth) return;
      img.setAttribute('data-img', '');
      var done = function () { img.classList.add('is-loaded'); };
      if (img.decode) { img.decode().then(done).catch(done); }
      else { img.addEventListener('load', done); img.addEventListener('error', done); }
    });
  }

  /* ---- masthead ----------------------------------------------------- */
  function masthead() {
    var top = document.querySelector('.top');
    if (!top) return;
    var ticking = false;
    function set() {
      top.classList.toggle('is-stuck', scrollY > 80);
      ticking = false;
    }
    addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(set); }
    }, { passive: true });
    set();
  }

  function boot() { reveal(); images(); masthead(); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }

  // pages arriving through a cross-document view transition re-run boot
  addEventListener('pageshow', function (e) { if (e.persisted) boot(); });
})();
