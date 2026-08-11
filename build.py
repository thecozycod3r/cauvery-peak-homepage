#!/usr/bin/env python3
"""Assemble the Cauvery Peak review site.

Pages are content fragments in pages/. This wraps each one in the shared
document, header and footer so there is exactly one copy of the chrome.
Assets are real files, not data URIs, so the browser caches them across pages.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE

NAV = [
    ("Coffee",   "coffee.html"),
    ("Visit",    "visit.html"),
    ("The estate", "estate.html"),
    ("Learn",    "brewing.html"),
]

FOOT = [
    ("Coffee", [("Single estates","coffee.html"),("Blends","coffee.html#blends"),
                ("Subscriptions","coffee.html"),("Spices &amp; honey","coffee.html")]),
    ("Visit",  [("Estate tour","visit.html"),("Estate caf&eacute;","cafes.html"),
                ("Lake View Village","cafes.html"),("Glenfell kiosk","cafes.html")]),
    ("The estate", [("Grower to Connoisseur","estate.html"),("Our story","story.html"),
                    ("History","history.html"),("The environment","environment.html")]),
    ("Learn",  [("Brewing guide","brewing.html"),("Grind guide","grind.html"),
                ("In the press","press.html"),("Contact","contact.html")]),
]

PLACES = [
    ("cp", "Cauvery Peak Estate Caf&eacute;", "On the plantation, 15 km from Yercaud town."),
    ("sh", "Lake View Village Caf&eacute;",   "Yercaud Main Road. Parking available."),
    ("gf", "Glenfell Kiosk",                  "17th hairpin bend, Salem&ndash;Yercaud ghat road."),
]

IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.05 1.8.25 2.2.42.6.22 1 .48 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c0 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2 0-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c0-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 3.2A6.6 6.6 0 1 0 18.6 12 6.6 6.6 0 0 0 12 5.4zm0 10.9A4.3 4.3 0 1 1 16.3 12 4.3 4.3 0 0 1 12 16.3zm6.9-11.1a1.5 1.5 0 1 1-1.6-1.6 1.5 1.5 0 0 1 1.6 1.6z"/></svg>'
FB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8.5V7c0-.7.5-.9.8-.9h2V3.2h-2.7C11 3.2 10.3 5.4 10.3 6.8v1.7H8.5v3h1.8V21H14v-9.5h2.4l.3-3H14z"/></svg>'
WA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15l-1.3 4.7 4.8-1.3A10 10 0 1 0 12 2zm5.6 14.2c-.2.6-1.3 1.2-1.8 1.3-.5.1-1.1.1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.7-1.2-4.5-3.9-4.6-4-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.3.5-.3.7-.3h.5c.2 0 .4-.1.6.5.2.5.8 1.9.8 2s.1.3 0 .5c-.1.2-.2.3-.3.5l-.4.5c-.1.1-.3.3-.1.6.2.3.7 1.1 1.5 1.8 1 .9 1.9 1.2 2.2 1.3.3.1.4.1.6-.1.2-.2.7-.8.9-1.1.2-.3.4-.2.6-.1.2.1 1.6.7 1.8.9.2.1.4.2.5.3.1.1.1.6-.1 1.3z"/></svg>'


def header(active):
    links = "\n".join(
        f'      <a href="{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a>'
        for label, href in NAV)
    return f'''<header class="site">
  <div class="site__in">
    <a href="index.html" class="site__home" aria-label="Cauvery Peak, home">
      <img class="site__logo" src="assets/logo_dark.webp" alt="Cauvery Peak" width="900" height="718">
    </a>
    <nav class="site__nav" aria-label="Main">
{links}
    </nav>
  </div>
</header>'''


def footer():
    cols = "\n".join(
        '        <div>\n          <h2 class="foot__h">%s</h2>\n          <ul class="foot__list">\n%s\n          </ul>\n        </div>' % (
            title, "\n".join(f'            <li><a href="{h}">{t}</a></li>' for t, h in items))
        for title, items in FOOT)
    places = "\n".join(
        f'''      <div class="foot__place" style="--c:var(--{c})">
        <h2 class="foot__pn">{name}</h2>
        <p class="foot__pd">{desc}</p>
        <a class="foot__pl" href="cafes.html">More &rarr;</a>
      </div>''' for c, name, desc in PLACES)
    return f'''<footer class="foot">
  <div class="foot__in">
    <div class="foot__top">
      <div class="foot__brand">
        <img class="foot__logo" src="assets/logo_light.webp" alt="Cauvery Peak" width="900" height="718">
        <p class="foot__tag">Growing since 1867</p>
        <p class="foot__blurb">A working coffee estate in the Shevaroy Hills, farmed by the same family for five generations.</p>
      </div>
      <nav class="foot__cols" aria-label="Footer">
{cols}
      </nav>
    </div>
    <div class="foot__places">
{places}
    </div>
    <div class="foot__bar">
      <ul class="foot__legal">
        <li><a href="#">Privacy</a></li><li><a href="#">Terms</a></li>
        <li><a href="#">Shipping</a></li><li><a href="#">Returns</a></li>
        <li><a href="#">Careers</a></li>
      </ul>
      <div class="foot__social">
        <a href="#" aria-label="Instagram">{IG}</a>
        <a href="#" aria-label="Facebook">{FB}</a>
        <a href="#" aria-label="WhatsApp">{WA}</a>
      </div>
      <p class="foot__co">MSP Plantations &middot; Yercaud, Tamil Nadu</p>
    </div>
  </div>
</footer>'''


STICKY = '''<div class="sticky">
  <a class="btn btn--gold" href="visit.html">Book the tour</a>
  <a class="btn btn--ghost" href="coffee.html">Shop coffee</a>
</div>'''


def document(slug, title, desc, body):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#00313B">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
{header(slug)}
{body}
{footer()}
{STICKY}
</body>
</html>
'''


def build():
    pages = json.load(open(os.path.join(HERE, "pages", "pages.json")))
    made = []
    for p in pages:
        frag = open(os.path.join(HERE, "pages", p["file"])).read()
        html = document(p["slug"], p["title"], p["desc"], frag)
        out = os.path.join(OUT, p["slug"])
        open(out, "w").write(html)
        made.append((p["slug"], os.path.getsize(out)))
    return made


if __name__ == "__main__":
    for slug, size in build():
        print(f"  {slug:22} {size/1024:6.1f} KB")
