#!/usr/bin/env python3
"""Assemble the Cauvery Peak review site.

Pages are content fragments in _src_pages/. This wraps each one in the shared
document, header, mobile drawer and footer so there is exactly one copy of the
chrome. Assets are real files, not data URIs, so the browser caches them across
pages.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
SRC = os.path.join(HERE, "_src_pages")

# where this build is actually served from — used for canonical + og:url
BASE = "https://thecozycod3r.github.io/cauvery-peak-homepage"

NAV = [
    ("Coffee",   "coffee.html"),
    ("Visit",    "visit.html"),
    ("The estate", "estate.html"),
    ("Learn",    "brewing.html"),
    ("Shop",     "shop.html"),
]

FOOT = [
    ("Coffee", [("Single estates","shop.html"),("Blends","shop.html"),
                ("Subscriptions","subscribe.html"),("Spices &amp; honey","shop.html")]),
    ("Visit",  [("Estate tour","visit.html"),("Estate caf&eacute;","cafes.html"),
                ("Lake View Village","cafes.html"),("Glenfell kiosk","cafes.html")]),
    ("The estate", [("Grower to Connoisseur","estate.html"),("Our story","story.html"),
                    ("History","history.html"),("The environment","environment.html")]),
    ("Learn",  [("Brewing guide","brewing.html"),("Grind guide","grind.html"),
                ("In the press","press.html"),("Contact","contact.html")]),
]

# real destinations on the live store — no placeholder hrefs anywhere on the site
LEGAL = [
    ("Privacy",  "https://cauverypeakestate.com/policies/privacy-policy"),
    ("Terms",    "https://cauverypeakestate.com/policies/terms-of-service"),
    ("Shipping", "https://cauverypeakestate.com/policies/shipping-policy"),
    ("Returns",  "https://cauverypeakestate.com/policies/refund-policy"),
]

# Instagram is confirmed. Facebook and WhatsApp are omitted rather than linked
# to "#" — the WhatsApp number is one of the disputed ones (see README).
SOCIAL = [("Instagram", "https://www.instagram.com/cauverypeakcoffee/")]

PLACES = [
    ("cp", "Cauvery Peak Estate Caf&eacute;", "On the plantation, 15 km from Yercaud town."),
    ("sh", "Lake View Village Caf&eacute;",   "Yercaud Main Road. Parking available."),
    ("gf", "Glenfell Kiosk",                  "17th hairpin bend, Salem&ndash;Yercaud ghat road."),
]

IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c0 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2 0-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c0-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 3.2A6.6 6.6 0 1 0 18.6 12 6.6 6.6 0 0 0 12 5.4zm0 10.9A4.3 4.3 0 1 1 16.3 12 4.3 4.3 0 0 1 12 16.3zm6.9-11.1a1.5 1.5 0 1 1-1.6-1.6 1.5 1.5 0 0 1 1.6 1.6z"/></svg>'
SOCIAL_SVG = {"Instagram": IG}


def header(active):
    links = "\n".join(
        f'      <a href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for label, href in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="top__in">
    <a href="index.html" class="top__home" aria-label="Cauvery Peak, home">
      <img class="top__logo" src="assets/logo_dark.webp" alt="Cauvery Peak" width="300" height="239" fetchpriority="high">
    </a>
    <nav class="top__nav" aria-label="Main">
{links}
    </nav>
    <button class="burger" type="button" id="burger" aria-expanded="false" aria-controls="sitemenu">
      <span class="burger__box" aria-hidden="true"><i></i><i></i><i></i></span>
      <span class="burger__t">Menu</span>
    </button>
    <button class="cartbtn" type="button" id="cartbtn" hidden>Basket <b class="num">0</b></button>
  </div>
</header>'''


def drawer(active):
    groups = "\n".join(
        '      <div class="dnav__g">\n        <h2 class="dnav__h">%s</h2>\n        <ul class="dnav__l">\n%s\n        </ul>\n      </div>' % (
            title,
            "\n".join(
                '          <li><a href="%s"%s>%s</a></li>' % (
                    h, ' aria-current="page"' if h.split("#")[0] == active else "", t)
                for t, h in items))
        for title, items in FOOT)
    return f'''<div class="drawer" id="sitemenu">
  <div class="drawer__scrim" data-close hidden></div>
  <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Site menu">
    <div class="drawer__head">
      <a href="index.html" class="drawer__home">Cauvery Peak</a>
      <button class="drawer__x" type="button" data-close aria-label="Close menu">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="1.6" fill="none"/></svg>
      </button>
    </div>
    <nav class="dnav" aria-label="All pages">
{groups}
    </nav>
    <div class="drawer__cta">
      <a class="btn btn--gold" href="visit.html">Book the tour</a>
      <a class="btn btn--ink" href="coffee.html">Shop coffee</a>
    </div>
    <p class="drawer__meta">MSP Plantations &middot; Yercaud, Tamil Nadu</p>
  </div>
</div>'''


def footer():
    cols = "\n".join(
        '        <div>\n          <h2 class="foot__h">%s</h2>\n          <ul class="foot__l">\n%s\n          </ul>\n        </div>' % (
            title, "\n".join(f'            <li><a href="{h}">{t}</a></li>' for t, h in items))
        for title, items in FOOT)
    places = "\n".join(
        f'''      <div class="foot__place" style="--c:var(--{c})">
        <h2 class="foot__pn">{name}</h2>
        <p class="foot__pd">{desc}</p>
        <a class="foot__pl" href="cafes.html">More &rarr;</a>
      </div>''' for c, name, desc in PLACES)
    legal = "".join(f'<li><a href="{h}" rel="noopener">{t}</a></li>' for t, h in LEGAL)
    social = "\n".join(
        f'        <a href="{h}" aria-label="{n}" rel="me noopener" target="_blank">{SOCIAL_SVG[n]}</a>'
        for n, h in SOCIAL)
    return f'''<footer class="foot">
  <div class="sheet">
    <div class="foot__grid">
      <div>
        <img class="foot__logo" src="assets/logo_light.webp" alt="Cauvery Peak" width="300" height="239" loading="lazy">
        <p class="mark mark--d" style="margin-top:1rem">Growing since 1867</p>
        <p class="body" style="color:var(--onDark-2); margin-top:.6rem; max-width:32ch">A working coffee estate in the Shevaroy Hills, farmed by the same family for five generations.</p>
      </div>
      <nav class="foot__cols" aria-label="Footer">
{cols}
      </nav>
    </div>
    <div class="foot__places">
{places}
    </div>
    <div class="foot__bar">
      <ul class="foot__legal">{legal}</ul>
      <div class="foot__social">
{social}
      </div>
      <span class="num">11&deg;46&prime;N 78&deg;12&prime;E &middot; 4,100&ndash;4,800 FT</span>
      <span class="foot__credit">Roasting photograph: <a href="https://commons.wikimedia.org/wiki/File:Genio_dsc02968.jpg" rel="noopener">Wikimedia Commons</a>, CC BY-SA 4.0 &mdash; placeholder</span>
    </div>
  </div>
</footer>'''



CART = '''<div class="cart" id="cart">
  <div class="cart__scrim" data-cclose hidden></div>
  <div class="cart__panel" role="dialog" aria-modal="true" aria-label="Your basket">
    <div class="cart__head">
      <p class="mark" style="margin:0">Your basket</p>
      <button class="drawer__x" type="button" data-cclose aria-label="Close basket">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="1.6" fill="none"/></svg>
      </button>
    </div>
    <div class="cart__body" data-clines></div>
    <div class="cart__foot">
      <p class="cart__sum"><span>Total</span><b class="num" data-ctotal>&#8377;0</b></p>
      <a class="btn btn--gold" data-ccheckout href="https://cauverypeakestate.com/collections/all">Checkout on the estate store</a>
      <p class="buy__note" style="margin:0">You will finish on cauverypeakestate.com, where the order is actually taken.</p>
    </div>
  </div>
</div>'''

STICKY = '''<div class="sticky">
  <a class="btn btn--gold" href="visit.html">Book the tour</a>
  <a class="btn btn--ghost" href="coffee.html">Shop coffee</a>
</div>'''

# Small enough to inline. Runs on every page; the drawer is inert until opened.

SHOP_JS = r"""<script>
(function(){
  var KEY='cp-basket', STORE='https://cauverypeakestate.com';
  var read=function(){ try{ return JSON.parse(localStorage.getItem(KEY))||[] }catch(e){ return [] } };
  var write=function(v){ localStorage.setItem(KEY, JSON.stringify(v)); paint(); };
  var inr=function(n){ return '\u20B9'+n.toLocaleString('en-IN'); };

  // ---- product / subscription forms -------------------------------
  document.querySelectorAll('.pdp[data-variants]').forEach(function(scope){
    var vs, form=scope.querySelector('.buy');
    try{ vs=JSON.parse(scope.getAttribute('data-variants')) }catch(e){ return }
    if(!form||!vs) return;
    var out=scope.querySelector('[data-price]'), unit=scope.querySelector('[data-unit]');
    var handle=scope.getAttribute('data-handle'), title=scope.getAttribute('data-title');
    function chosen(){
      return [1,2,3].map(function(i){
        var el=form.querySelector('input[name="o'+i+'"]:checked');
        return el?el.value:null;
      });
    }
    function match(){
      var c=chosen();
      return vs.filter(function(v){
        return c.every(function(x,i){ return x===null || v.o[i]===x; });
      })[0];
    }
    function kilos(s){
      if(!s) return 0;
      var m=/([\d.]+)\s*kg/i.exec(s); if(m) return parseFloat(m[1]);
      m=/([\d.]+)\s*(gm|g)\b/i.exec(s); if(m) return parseFloat(m[1])/1000;
      return 0;
    }
    function months(s){ var m=/(\d+)\s*month/i.exec(s||''); return m?parseInt(m[1],10):0; }
    function paintPrice(){
      var v=match(); if(!v) return;
      out.textContent=inr(v.p);
      if(unit){
        var c=chosen(), kg=kilos(c[2]), mo=months(c[0]);
        unit.textContent = (kg&&mo) ? inr(Math.round(v.p/(kg*mo)))+' per kg · '+mo+' months' : '';
      }
      // strike through combinations the store has no variant for
      form.querySelectorAll('.opt').forEach(function(l){
        var inp=l.querySelector('input'), i=parseInt(inp.name.slice(1),10)-1;
        var probe=chosen(); probe[i]=inp.value;
        var ok=vs.some(function(v){ return probe.every(function(x,j){ return x===null||v.o[j]===x }) });
        if(ok) l.removeAttribute('data-out'); else l.setAttribute('data-out','');
      });
    }
    form.addEventListener('change', paintPrice);
    paintPrice();
    var add=form.querySelector('[data-add]');
    if(add) add.addEventListener('click', function(){
      var v=match(); if(!v) return;
      var b=read(), hit=b.filter(function(l){ return l.id===v.id })[0];
      if(hit) hit.q++; else b.push({id:v.id,q:1,p:v.p,t:title,o:chosen().filter(Boolean).join(' · '),h:handle});
      write(b); open();
    });
  });

  // ---- basket ------------------------------------------------------
  var cart=document.getElementById('cart'); if(!cart) return;
  var lines=cart.querySelector('[data-clines]'), total=cart.querySelector('[data-ctotal]');
  var go=cart.querySelector('[data-ccheckout]'), scrim=cart.querySelector('.cart__scrim');
  var btn=document.getElementById('cartbtn'), count=btn?btn.querySelector('b'):null, last=null;
  function paint(){
    var b=read(), sum=0;
    lines.innerHTML = b.length ? '' : '<p class="cart__empty">Nothing in the basket yet.</p>';
    b.forEach(function(l,i){
      sum += l.p*l.q;
      var el=document.createElement('div'); el.className='cart__line';
      el.innerHTML='<p class="cart__t">'+l.t+'</p><p class="cart__p num">'+inr(l.p*l.q)+'</p>'
        +'<p class="cart__o">'+(l.o||'')+(l.q>1?' · x'+l.q:'')+'</p>';
      var rm=document.createElement('button');
      rm.type='button'; rm.className='cart__rm'; rm.textContent='Remove';
      rm.addEventListener('click', function(){ var c=read(); c.splice(i,1); write(c); });
      el.appendChild(rm); lines.appendChild(el);
    });
    total.textContent=inr(sum);
    if(btn){ btn.hidden = !b.length; if(count) count.textContent=b.reduce(function(n,l){return n+l.q},0); }
    // Shopify takes a cart permalink, so the real checkout gets the real ids
    go.setAttribute('href', b.length
      ? STORE+'/cart/'+b.map(function(l){ return l.id+':'+l.q }).join(',')
      : STORE+'/collections/all');
  }
  function open(){ last=document.activeElement; scrim.hidden=false; cart.classList.add('is-open');
    document.documentElement.classList.add('no-scroll');
    (cart.querySelector('button,a')||cart).focus(); document.addEventListener('keydown',key,true); }
  function close(){ cart.classList.remove('is-open');
    document.documentElement.classList.remove('no-scroll');
    document.removeEventListener('keydown',key,true); if(last) last.focus();
    var ms=matchMedia('(prefers-reduced-motion:reduce)').matches?0:260;
    setTimeout(function(){ if(!cart.classList.contains('is-open')) scrim.hidden=true; },ms); }
  function key(e){ if(e.key==='Escape'){ e.preventDefault(); close(); } }
  cart.addEventListener('click', function(e){ if(e.target.closest('[data-cclose]')) close(); });
  if(btn) btn.addEventListener('click', open);
  paint();
})();
</script>"""

MENU_JS = '''<script>
(function(){
  var b=document.getElementById('burger'), d=document.getElementById('sitemenu');
  if(!b||!d) return;
  var panel=d.querySelector('.drawer__panel'), scrim=d.querySelector('.drawer__scrim'), last=null;
  var Q='a[href],button:not([disabled])';
  function open(){
    last=document.activeElement;
    scrim.hidden=false;
    d.classList.add('is-open'); b.setAttribute('aria-expanded','true');
    document.documentElement.classList.add('no-scroll');
    (panel.querySelector(Q)||panel).focus();
    document.addEventListener('keydown',key,true);
  }
  function close(){
    d.classList.remove('is-open'); b.setAttribute('aria-expanded','false');
    document.documentElement.classList.remove('no-scroll');
    document.removeEventListener('keydown',key,true);
    if(last) last.focus();
    // keep the scrim in the tree until the panel has travelled back out
    var ms=matchMedia('(prefers-reduced-motion:reduce)').matches?0:260;
    setTimeout(function(){ if(!d.classList.contains('is-open')) scrim.hidden=true; },ms);
  }
  function key(e){
    if(e.key==='Escape'){ e.preventDefault(); close(); return; }
    if(e.key!=='Tab') return;
    var f=[].slice.call(panel.querySelectorAll(Q)).filter(function(el){return el.offsetParent!==null});
    if(!f.length) return;
    var first=f[0], lastEl=f[f.length-1];
    if(e.shiftKey && document.activeElement===first){ e.preventDefault(); lastEl.focus(); }
    else if(!e.shiftKey && document.activeElement===lastEl){ e.preventDefault(); first.focus(); }
  }
  b.addEventListener('click',function(){ d.classList.contains('is-open')?close():open(); });
  d.addEventListener('click',function(e){ if(e.target.closest('[data-close]')) close(); });
  // a viewport that grows past the breakpoint must not leave the drawer stuck open
  matchMedia('(min-width:760px)').addEventListener('change',function(e){ if(e.matches) close(); });
})();
</script>'''


def jsonld(slug, title, desc, og):
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Cauvery Peak",
        "legalName": "MSP Plantations",
        "url": BASE + "/",
        "logo": BASE + "/assets/logo_dark.webp",
        "foundingDate": "1867",
        "sameAs": [h for _, h in SOCIAL] + ["https://cauverypeakestate.com"],
        "address": {"@type": "PostalAddress", "addressLocality": "Yercaud",
                    "addressRegion": "Tamil Nadu", "addressCountry": "IN"},
    }
    blocks = [org]
    if slug == "index.html":
        blocks.append({"@context": "https://schema.org", "@type": "WebSite",
                       "name": "Cauvery Peak", "url": BASE + "/"})
    else:
        blocks.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": re.sub(r"\s+—.*$", "", title),
                 "item": f"{BASE}/{slug}"},
            ]})
    if slug in ("cafes.html", "visit.html", "contact.html"):
        blocks.append({
            "@context": "https://schema.org", "@type": "TouristAttraction",
            "name": "Cauvery Peak Estate", "url": f"{BASE}/visit.html",
            "description": "A working 150-year-old coffee plantation in the Shevaroy Hills, open for guided tours.",
            "image": f"{BASE}/assets/{og}",
            "address": {"@type": "PostalAddress", "addressLocality": "Yercaud",
                        "addressRegion": "Tamil Nadu", "addressCountry": "IN"},
            "geo": {"@type": "GeoCoordinates", "latitude": 11.7753, "longitude": 78.2095},
        })
    return "\n".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(b, separators=(",", ":"))
        for b in blocks)


def document(slug, title, desc, og, body):
    canonical = f"{BASE}/" if slug == "index.html" else f"{BASE}/{slug}"
    return f'''<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#16261C">
<script>document.documentElement.className="js"</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Cauvery Peak">
<meta property="og:locale" content="en_IN">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}/assets/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{desc[:110]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/estate.css">
{jsonld(slug, title, desc, og)}
</head>
<body>
{header(slug)}
{drawer(slug)}
<main id="main">
{body}
</main>
{footer()}
{STICKY}
{CART}
{MENU_JS}
{SHOP_JS}
<script src="assets/motion.js" defer></script>
</body>
</html>
'''


def build():
    pages = json.load(open(os.path.join(SRC, "pages.json")))
    made = []
    for p in pages:
        frag = open(os.path.join(SRC, p["file"])).read()
        html = document(p["slug"], p["title"], p["desc"], p.get("og", "og-default.jpg"), frag)
        out = os.path.join(OUT, p["slug"])
        open(out, "w").write(html)
        made.append((p["slug"], os.path.getsize(out)))
    return made


if __name__ == "__main__":
    for slug, size in build():
        print(f"  {slug:22} {size/1024:6.1f} KB")
