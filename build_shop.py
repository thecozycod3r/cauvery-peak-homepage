#!/usr/bin/env python3
"""Generate the commerce pages from the live catalogue.

Everything the store currently bakes into a JPEG — elevation, tasting
meters, brew recommendation, the weight x price grid — is emitted here as
real HTML instead. Prices and variant ids come straight from the store's
own products.json, so this build cannot drift out of step with it.

Nothing is written to the live store. "Add to cart" builds a Shopify cart
permalink against the real variant id, so the review build hands off to
their actual checkout rather than pretending to have one.
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_src_pages")
CAT = json.load(open(os.path.join(SRC, "catalog.json")))
BY = {p["handle"]: p for p in CAT}

STORE = "https://cauverypeakestate.com"

# the clean transparent pack renders, not the store's text-baked composites
PACK = {
    "coffee-powder-she":    ("p_sh.webp",      "#8E3A21", "est_sh.webp"),
    "coffee-powder-cp":     ("p_cp.webp",      "#324B50", "est_cp.webp"),
    "glenfell-4":           ("p_gf.webp",      "#00818C", "est_gf.webp"),
    "espresso-blend-5":     ("p_eb.webp",      "#3B2A1E", "cherries.webp"),
    "indian-filter-blend-5":("p_ib.webp",      "#7F3634", "leaves.webp"),
    "sample-pack":          ("p_sampler.webp", "#A98247", "land.webp"),
    "blend-sampler-pack-23":("p_blends.webp",  "#A98247", "shade.webp"),
}
# facts the store prints into its artwork; here they are data
ESTATE_FACTS = {
    "coffee-powder-she":     [("Elevation","1,450 m &middot; 4,800 ft"),("Acidity","Crisp"),("Body","Medium"),("Aftertaste","Distinct citrus"),("Aroma","Mild")],
    "coffee-powder-cp":      [("Elevation","1,400 m &middot; 4,600 ft"),("Acidity","Rich, low key"),("Body","Full"),("Aftertaste","Chocolate"),("Aroma","Sweetly round")],
    "glenfell-4":            [("Elevation","1,250 m &middot; 4,100 ft"),("Acidity","Low"),("Body","Full"),("Aftertaste","Exotic, spicy"),("Aroma","Fine")],
    "espresso-blend-5":      [("Made from","All three estates"),("Acidity","Good"),("Body","Medium"),("Best as","Espresso"),("Roast","Medium")],
    "indian-filter-blend-5": [("Made from","All three estates"),("Acidity","Medium"),("Body","Good decoction"),("Best as","Indian filter"),("Roast","Medium")],
}
SUBTITLE = {
    "coffee-powder-she":"Estate Reserve", "coffee-powder-cp":"Estate Heritage",
    "glenfell-4":"Estate Classic", "espresso-blend-5":"All three estates",
    "indian-filter-blend-5":"All three estates",
}
# indices of real photographs in each product's store gallery. The rest are
# composites with text painted in, which is the thing this build removes.
REAL_SHOTS = {
    "coffee-experience-tours-11":[2,3,5,6],
    "coffee-powder-she":[2,4,5,6],
    "glenfell-4":[2,3,4,5],
    "coffee-scrub":[1,2,3],
}
# where the store has no usable photograph, show the estate instead
FALLBACK_PLATES = {
    "coffee-powder-cp":      [("lake.webp","The estate lake"),("canopy.webp","Two-tier shade"),("terraces.webp","Drying terraces")],
    "espresso-blend-5":      [("roasting.webp","Roasting"),("sorting.webp","Grading by hand"),("millyard.webp","The mill yard")],
    "indian-filter-blend-5": [("roasting.webp","Roasting"),("cherrypour.webp","Pulping"),("channel.webp","Washing")],
    "sample-pack":           [("gate.webp","The estate gate"),("shade.webp","Under shade"),("lake.webp","The estate lake")],
    "blend-sampler-pack-23": [("roasting.webp","Roasting"),("millyard.webp","The mill yard"),("terraces.webp","Drying terraces")],
    "cauvery-peak-green-beans":[("terraces.webp","Drying terraces"),("sorting.webp","Grading"),("nursery.webp","The nursery")],
    "pepper":                [("shade.webp","Grown under shade"),("flora.webp","Estate flora"),("soil.webp","Estate soil")],
    "nutmeg-mace":           [("shade.webp","Grown under shade"),("flora.webp","Estate flora"),("soil.webp","Estate soil")],
    "clove":                 [("shade.webp","Grown under shade"),("flora.webp","Estate flora"),("soil.webp","Estate soil")],
    "honey":                 [("flora.webp","Estate flora"),("canopy.webp","The canopy"),("lake.webp","Water on the estate")],
}

GROUPS = [
    ("Single estates", "Grown, processed and roasted on one boundary.",
     ["coffee-powder-she","coffee-powder-cp","glenfell-4"]),
    ("Blends", "Drawn from all three estates, blended for a job rather than a place.",
     ["espresso-blend-5","indian-filter-blend-5"]),
    ("Sampler packs", "The way in, if you have not tasted them side by side.",
     ["sample-pack","blend-sampler-pack-23","cauvery-peak-green-beans"]),
    ("Spices &amp; honey", "Grown between the coffee, on the same land.",
     ["pepper","nutmeg-mace","clove","honey"]),
    ("Also from the estate", "",
     ["coffee-scrub","coffee-experience-tours-11"]),
]

def money(n):  return f"&#8377;{n:,.0f}"
def esc(s):    return html.escape(s, quote=True)

def img_for(p):
    """A clean pack render where we have one, else the store's photograph."""
    if p["handle"] in PACK:
        f, c, bg = PACK[p["handle"]]
        return f"assets/{f}", c, f"assets/{bg}"
    imgs = p["images"]
    src = f"assets/shop/{p['handle'][:24]}-{0}.webp"
    return src, "#A98247", None

def card(p):
    src, c, _ = img_for(p)
    lo = min(v["p"] for v in p["variants"])
    sub = SUBTITLE.get(p["handle"], p["type"] or "From the estate")
    facts = ESTATE_FACTS.get(p["handle"])
    rows = ""
    if facts:
        rows = "\n".join(
            f'<li><span class="cof__k">{k}</span><span class="cof__lead"></span>'
            f'<span class="cof__v">{v}</span></li>' for k, v in facts[:4])
    else:
        nv = len(p["variants"])
        rows = (f'<li><span class="cof__k">Options</span><span class="cof__lead"></span>'
                f'<span class="cof__v num">{nv}</span></li>')
    wide = " cof__pack--wide" if p["handle"] in ("sample-pack","blend-sampler-pack-23") else ""
    return f'''        <article class="cof" style="--c:{c}">
          <img class="cof__pack{wide}" src="{src}" alt="" loading="lazy">
          <h3 class="cof__n"><a class="cof__hit" href="p-{p['handle']}.html">{p['title'].title()}</a></h3>
          <p class="cof__t">{sub}</p>
          <ul class="cof__specs">
{rows}
          </ul>
          <p class="cof__price"><b class="num">From {money(lo)}</b><span class="cof__go">View &rarr;</span></p>
        </article>'''

# ---------------------------------------------------------------- shop
def shop_page():
    out = ['''<header class="phero">
  <img class="phero__img" src="assets/cherries.webp" alt="Ripe cherry on the estate" width="900" height="600" fetchpriority="high">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">The shop</p>
    <h1 class="d1">Everything here<br>grew on one estate.</h1>
    <p class="lede">Coffee, spices and honey from the same 150-year-old boundary in the Shevaroy Hills &mdash; and the tour, if you would rather come and see it.</p>
  </div>
</header>

<section>
  <div class="wrap">''']
    for title, blurb, handles in GROUPS:
        items = [BY[h] for h in handles if h in BY]
        if not items: continue
        out.append(f'''    <p class="cgroup">{title}</p>
    {f'<p class="body" style="margin:-.4rem 0 1.25rem">{blurb}</p>' if blurb else ''}
    <div class="coffees" style="margin:0 0 clamp(2.5rem,5vw,3.5rem)">
{chr(10).join(card(p) for p in items)}
    </div>''')
    out.append('''  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow--d">Subscriptions</p>
    <h2 class="d2">Coffee that arrives<br>before you run out.</h2>
    <p class="lede">Six, twelve or twenty-four months, any of the five coffees, any pack size. Roasted to order each time.</p>
    <div class="btns"><a class="btn btn--gold" href="subscribe.html">Build a subscription</a></div>
  </div>
</section>''')
    return "\n".join(out)

# ------------------------------------------------------------- product
def product_page(p):
    src, c, bg = img_for(p)
    facts = ESTATE_FACTS.get(p["handle"])
    sub = SUBTITLE.get(p["handle"], p["type"] or "From the estate")
    lo = min(v["p"] for v in p["variants"])
    axes = p["options"]
    vjson = json.dumps([{"id":v["id"],"p":v["p"],"o":[v["o1"],v["o2"],v["o3"]],"av":v["av"]}
                        for v in p["variants"]], separators=(",",":"))

    # the option controls — the 33 grind x weight combinations the store hides
    # behind two dropdowns, laid out so you can see all of them
    ctrls = ""
    # a single-variant product has nothing to choose; an empty fieldset with one
    # option in it is furniture, not a control
    single = len(p["variants"]) == 1
    for i, o in enumerate(axes, start=1):
        if single:
            break
        opts = "\n".join(
            f'<label class="opt"><input type="radio" name="o{i}" value="{esc(v)}"'
            f'{" checked" if j==0 else ""}><span>{v.split(" (")[0]}</span>'
            + (f'<small>{v.split("(")[1].rstrip(")")}</small>' if "(" in v else "")
            + '</label>'
            for j, v in enumerate(o["values"]))
        ctrls += f'''      <fieldset class="opts">
        <legend class="cof__k">{o['name'].replace('Select ','')}</legend>
        <div class="opts__row">
{opts}
        </div>
      </fieldset>
'''
    factrows = ""
    if facts:
        factrows = "\n".join(
            f'<li><span class="cof__k">{k}</span><span class="cof__lead"></span>'
            f'<span class="cof__v">{v}</span></li>' for k, v in facts)
    body = p["body"]
    if len(body) > 420:
        cut = body[:420]
        stop = max(cut.rfind(". "), cut.rfind("! "))
        body = (cut[:stop+1] if stop > 220 else cut[:cut.rfind(" ")] + "\u2026")

    gallery = ""
    idx = REAL_SHOTS.get(p["handle"])
    if idx:
        shots = [(f"assets/shop/{p['handle'][:24]}-{i}.webp", p["title"].title()) for i in idx[:3]]
    else:
        shots = [(f"assets/{f}", cap) for f, cap in FALLBACK_PLATES.get(p["handle"], [])[:3]]
    if shots:
        figs = "\n".join(
            f'      <figure class="plate"><img src="{src}" alt="{esc(cap)}" loading="lazy">'
            f'<figcaption><span class="plate__n num">{i+1:02d}</span><span>{cap}</span></figcaption></figure>'
            for i, (src, cap) in enumerate(shots))
        gallery = f'''
<section>
  <div class="wrap">
    <p class="cgroup">On the estate</p>
    <div class="plates plates--3">
{figs}
    </div>
  </div>
</section>'''

    return f'''<section class="pdp" style="--c:{c}" data-variants='{vjson}' data-handle="{p['handle']}" data-title="{esc(p['title'].title())}">
  <div class="wrap pdp__in">
    <figure class="pdp__fig">
      {f'<img class="pdp__bg" src="{bg}" alt="" loading="lazy">' if bg else ''}
      <img class="pdp__pack" src="{src}" alt="{esc(p['title'].title())}" loading="eager">
    </figure>
    <div class="pdp__buy">
      <p class="eyebrow">{sub}</p>
      <h1 class="d2">{p['title'].title()}</h1>
      {f'<p class="body" style="margin-top:1rem">{body}</p>' if body else ''}
      {f'<ul class="cof__specs" style="margin-top:1.5rem">{factrows}</ul>' if factrows else ''}

      <form class="buy" onsubmit="return false">
{ctrls}
        <div class="buy__bar">
          <p class="buy__price num" data-price>{money(lo)}</p>
          <button class="btn btn--gold" type="button" data-add>Add to cart</button>
        </div>
        <p class="buy__note">Roasted after your order is placed. Checkout is handled by the estate&rsquo;s own store.</p>
      </form>
    </div>
  </div>
</section>
{gallery}

<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow--d">Grower to connoisseur</p>
    <h2 class="d2">Nine stages,<br>one boundary.</h2>
    <p class="lede">Every stage of this coffee happened on the estate &mdash; nursery to roast.</p>
    <div class="btns"><a class="btn btn--ghost" href="estate.html">See how it is made</a></div>
  </div>
</section>'''

# --------------------------------------------------------- subscription
def subscribe_page():
    p = BY["coffee"]
    vjson = json.dumps([{"id":v["id"],"p":v["p"],"o":[v["o1"],v["o2"],v["o3"]],"av":v["av"]}
                        for v in p["variants"]], separators=(",",":"))
    axes = p["options"]
    ctrls = ""
    for i, o in enumerate(axes, start=1):
        opts = "\n".join(
            f'<label class="opt"><input type="radio" name="o{i}" value="{esc(v)}"'
            f'{" checked" if j==0 else ""}><span>{v}</span></label>'
            for j, v in enumerate(o["values"]))
        ctrls += f'''      <fieldset class="opts">
        <legend class="cof__k">{i:02d} &middot; {o['name']}</legend>
        <div class="opts__row">
{opts}
        </div>
      </fieldset>
'''
    return f'''<header class="phero">
  <img class="phero__img" src="assets/lake.webp" alt="The estate lake" width="900" height="600" fetchpriority="high">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">Subscriptions</p>
    <h1 class="d1">Pick three things.<br>We do the rest.</h1>
    <p class="lede">Fifty-four combinations, which is why the store currently shows you a photograph of a price table. Here they are as three choices.</p>
  </div>
</header>

<section class="pdp" data-variants='{vjson}' data-handle="coffee" data-title="Coffee subscription">
  <div class="wrap">
    <form class="buy buy--sub" onsubmit="return false">
{ctrls}
      <div class="buy__bar">
        <div>
          <p class="buy__price num" data-price>&#8377;3,132</p>
          <p class="buy__unit num" data-unit></p>
        </div>
        <button class="btn btn--gold" type="button" data-add>Start the subscription</button>
      </div>
      <p class="buy__note">Billed once for the full term. Roasted to order before each despatch. Checkout is handled by the estate&rsquo;s own store.</p>
    </form>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow--d">Why commit</p>
    <h2 class="d2">The longer the term,<br>the less you pay per kilo.</h2>
    <p class="lede">The price per kilogram is shown above as you choose, because that is the number that actually tells you whether this is worth it.</p>
  </div>
</section>'''

# ------------------------------------------------------------------ run
def main():
    pages = json.load(open(os.path.join(SRC, "pages.json")))
    pages = [p for p in pages if not p["slug"].startswith(("p-", "shop.", "subscribe."))]

    open(os.path.join(SRC, "shop.html"), "w").write(shop_page())
    pages.append({"file":"shop.html","slug":"shop.html",
                  "title":"Shop — Cauvery Peak","og":"og-coffee.jpg",
                  "desc":"Estate coffee, spices and honey from a 150-year-old plantation in the Shevaroy Hills, Yercaud. Roasted to order."})

    open(os.path.join(SRC, "subscribe.html"), "w").write(subscribe_page())
    pages.append({"file":"subscribe.html","slug":"subscribe.html",
                  "title":"Coffee subscription — Cauvery Peak","og":"og-coffee.jpg",
                  "desc":"Six, twelve or twenty-four months of single-estate coffee, roasted to order before each despatch."})

    made = 0
    for p in CAT:
        # the subscription has a purpose-built page; a generic PDP would be a
        # second, worse copy of it
        if p["handle"] == "coffee":
            continue
        frag = product_page(p)
        f = f"p-{p['handle']}.html"
        open(os.path.join(SRC, f), "w").write(frag)
        pages.append({"file":f, "slug":f, "og":"og-coffee.jpg",
                      "title":f"{p['title'].title()} — Cauvery Peak",
                      "desc":(p["body"][:150] or f"{p['title'].title()} from Cauvery Peak estate, Yercaud.")})
        made += 1

    json.dump(pages, open(os.path.join(SRC, "pages.json"), "w"), indent=1, ensure_ascii=False)
    print(f"shop.html, subscribe.html and {made} product pages -> pages.json ({len(pages)} total)")

if __name__ == "__main__":
    main()
