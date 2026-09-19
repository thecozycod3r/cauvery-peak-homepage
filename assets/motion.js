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
    '.ledger li', '.entry', '.cof', '.section',
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
      if (el.hasAttribute('data-rise') || el.hasAttribute('data-lines')) return;
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


  /* ---- hero headline: each line rises out of its own mask ----------
     The h1 is split on its <br>s. Each line sits in a clip, so the type
     appears to come up out of the page rather than fading on top of it. */
  function lines() {
    [].slice.call(document.querySelectorAll('.hero .d1, .phero .d1')).forEach(function (h) {
      if (h.hasAttribute('data-lines')) return;
      h.setAttribute('data-lines', '');
      var parts = h.innerHTML.split(/<br\s*\/?>/i);
      h.innerHTML = parts.map(function (t, i) {
        return '<span class="ln"><span class="ln__i" style="--i:' + i + '">' + t.trim() + '</span></span>';
      }).join('');
      // two frames so the start state is painted before the end state
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { h.classList.add('is-in'); });
      });
    });
  }

  /* ---- photographs wipe open ---------------------------------------
     The documentary plates open from the bottom edge like a print being
     pulled, rather than fading. Only figures that are scrolled to. */
  var FIG = '.plate, .entry__fig, .flow__fig, .tourcard, .person__fig';
  function wipes() {
    var figs = [].slice.call(document.querySelectorAll(FIG)).filter(function (f) {
      return !f.closest('.top,.drawer,.cart') && !f.hasAttribute('data-wipe');
    });
    if (!figs.length) return;
    var vh = innerHeight;
    figs.forEach(function (f) {
      f.setAttribute('data-wipe', '');
      if (f.getBoundingClientRect().top < vh * 0.92) f.classList.add('is-wiped');
    });
    if (!('IntersectionObserver' in window)) {
      figs.forEach(function (f) { f.classList.add('is-wiped'); }); return;
    }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-wiped'); io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.01 });
    figs.forEach(function (f) { if (!f.classList.contains('is-wiped')) io.observe(f); });
  }

  /* ---- the record counts itself in ---------------------------------
     Every number in a ledger value counts up once when scrolled to.
     The final width is reserved first so nothing beside it moves. */
  function counters() {
    var vals = [].slice.call(document.querySelectorAll('.ledger__v'));
    if (!vals.length || reduce) return;
    var items = [];
    vals.forEach(function (v) {
      var walker = document.createTreeWalker(v, NodeFilter.SHOW_TEXT);
      var nodes = [], n;
      while ((n = walker.nextNode())) if (/\d/.test(n.nodeValue)) nodes.push(n);
      nodes.forEach(function (node) {
        var frag = document.createDocumentFragment();
        node.nodeValue.split(/([\d,]+)/).forEach(function (part) {
          if (/\d/.test(part)) {
            var end = parseInt(part.replace(/,/g, ''), 10);
            var sp = document.createElement('span');
            sp.className = 'count';
            sp.textContent = part;
            sp.setAttribute('data-end', end);
            sp.setAttribute('data-comma', part.indexOf(',') > -1 ? '1' : '');
            frag.appendChild(sp);
            items.push(sp);
          } else if (part) frag.appendChild(document.createTextNode(part));
        });
        node.parentNode.replaceChild(frag, node);
      });
    });
    // reserve the settled width of each number before it starts from zero
    // A fixed width, not a minimum: Fraunces' figures are not truly
    // tabular, so an in-between value like 1788 can be wider than 1867 and
    // would nudge its neighbours sideways. The box never changes size.
    items.forEach(function (sp) { sp.style.width = sp.getBoundingClientRect().width + 'px'; });

    function run(sp) {
      var end = +sp.getAttribute('data-end'), comma = sp.getAttribute('data-comma');
      // a year counts up from a century earlier; a quantity from zero
      var start = end > 1500 && end < 2100 && !comma ? end - 160 : 0;
      var t0 = null, dur = 1400;
      function fmt(x) { return comma ? x.toLocaleString('en-IN') : String(x); }
      function step(t) {
        if (t0 === null) t0 = t;
        var k = Math.min(1, (t - t0) / dur);
        var e = 1 - Math.pow(1 - k, 4);            // ease-out quart
        sp.textContent = fmt(Math.round(start + (end - start) * e));
        if (k < 1) requestAnimationFrame(step);
      }
      sp.textContent = fmt(start);
      requestAnimationFrame(step);
    }
    if (!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        [].slice.call(e.target.querySelectorAll('.count')).forEach(run);
        io.unobserve(e.target);
      });
    }, { threshold: 0.6 });
    vals.forEach(function (v) {
      // one already on screen at load keeps its final value — no flash
      if (v.getBoundingClientRect().top < innerHeight * 0.9) return;
      io.observe(v);
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

  function boot() { lines(); reveal(); wipes(); counters(); images(); masthead(); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }

  // pages arriving through a cross-document view transition re-run boot
  addEventListener('pageshow', function (e) { if (e.persisted) boot(); });
})();
