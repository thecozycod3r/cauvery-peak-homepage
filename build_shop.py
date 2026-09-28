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
    "drip-bags":             [("In the pack","6 sachets"),("Choose","Mixed, or one estate"),("Filter","Japanese, cornstarch bioplastic"),("You need","A mug and hot water")],
}
SUBTITLE = {
    "coffee-powder-she":"Estate Reserve", "coffee-powder-cp":"Estate Heritage",
    "glenfell-4":"Estate Classic", "espresso-blend-5":"All three estates",
    "indian-filter-blend-5":"All three estates",
    "drip-bags":"No equipment needed",
}
# indices of real photographs in each product's store gallery. The rest are
# composites with text painted in, which is the thing this build removes.
REAL_SHOTS = {
    "coffee-experience-tours-11":[2,3,5,6],
    "coffee-powder-she":[2,4,5,6],
    "glenfell-4":[2,3,4,5],
    "coffee-scrub":[1,2,3],
    # the store's four drip-bag images are all text composites; 0-2 are crops
    # of the photography inside them, and what the text said is below as HTML
    "drip-bags":[1,2],
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
    ("Samplers &amp; drip bags", "The way in, if you have not tasted them side by side.",
     ["sample-pack","blend-sampler-pack-23","drip-bags"]),
    ("Spices &amp; honey", "Grown between the coffee, on the same land.",
     ["pepper","nutmeg-mace","clove","honey"]),
    ("Also from the estate", "",
     ["cauvery-peak-green-beans","coffee-scrub","coffee-experience-tours-11"]),
]

# What the drip-bag artwork says, as text a customer can read at any size and
# a search engine can index. Wording is the store's own.
EXTRA = {
 "drip-bags": '''
<section>
  <div class="wrap">
    <h2 class="cgroup">Brew in minutes</h2>
    <ol class="steps4">
      <li><b class="num">01</b><h3>Open</h3><p>Tear open the sachet and unfold the filter.</p></li>
      <li><b class="num">02</b><h3>Place</h3><p>Secure the filter over your favourite mug.</p></li>
      <li><b class="num">03</b><h3>Pour</h3><p>Slowly add hot water and enjoy a freshly brewed cup.</p></li>
      <li><b class="num">04</b><h3>Add</h3><p>Add milk and sugar to taste.</p></li>
    </ol>
  </div>
</section>
<section>
  <div class="wrap">
    <h2 class="cgroup">Three estates, six cups</h2>
    <ul class="cof__specs trio">
      <li><span class="cof__k">Shevaroys Estate Reserve</span><span class="cof__lead"></span><span class="cof__v">1,450 m &middot; crisp acidity</span></li>
      <li><span class="cof__k">Cauvery Peak Estate Heritage</span><span class="cof__lead"></span><span class="cof__v">1,400 m &middot; medium acidity</span></li>
      <li><span class="cof__k">Glenfell Estate Classic</span><span class="cof__lead"></span><span class="cof__v">1,250 m &middot; low acidity</span></li>
    </ul>
    <p class="body" style="margin-top:1rem">Plant-based cornstarch filters and premium Japanese filter paper, for a clean extraction with no waxy or bitter aftertaste. <a href="coffee.html">Why the height changes the taste &rarr;</a></p>
  </div>
</section>''',
}

# Shipping, dispatch and damage terms are the store's own Shipping and Returns
# policies, stated where the decision is made instead of three clicks away.
TRUST = '''<ul class="assure">
        <li><b>Free shipping</b> anywhere in India</li>
        <li><b>Roasted after you order</b>, dispatched in 3&ndash;5 business days</li>
        <li><b>Arrived damaged?</b> We replace it or refund in full &mdash; <a href="returns.html">returns</a></li>
        <li><b>Secure checkout</b> on the estate&rsquo;s Shopify store</li>
      </ul>'''
TOUR_FACTS = '''<ul class="assure">
        <li><b>75 minutes</b>, in your own vehicle with a coffee guide</li>
        <li><b>Every day except Tuesday</b>, from the estate caf&eacute;, 7.30am&ndash;5pm</li>
        <li><b>Tour details</b> <a href="tel:+919487458387">+91 94874 58387</a></li>
      </ul>'''

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
    return f'''        <article class="cof" style="--c:{c}" data-price="{lo:.0f}" data-handle="{p['handle']}">
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
    out = ['''<header class="phero phero--shop">
  <img class="phero__img" src="assets/cherries.webp" alt="Ripe cherry on the estate" width="900" height="600" fetchpriority="high">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">The shop</p>
    <h1 class="d1">Everything here<br>grew on one estate.</h1>
    <p class="lede">Coffee, spices and honey from the same 150-year-old boundary in the Shevaroy Hills &mdash; and the tour, if you would rather come and see it.</p>
  </div>
</header>

<div class="wrap" style="padding-top:1.25rem">''' + TRUST.replace('class="assure"','class="assure assure--row"') + '''</div>
<section style="padding-top:1.5rem">
  <div class="wrap">''']
    for title, blurb, handles in GROUPS:
        items = [BY[h] for h in handles if h in BY]
        if not items: continue
        out.append(f'''    <h2 class="cgroup">{title}</h2>
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
    avail = [v for v in p["variants"] if v["av"]] or p["variants"]
    entry = min(avail, key=lambda v: v["p"])
    default = [entry["o1"], entry["o2"], entry["o3"]]
    for i, o in enumerate(axes, start=1):
        if single:
            break
        hint = ""
        if "grind" in o["name"].lower():
            hint = ('<p class="opts__hint">No grinder? Choose how you brew and we grind it to order. '
                    '<a href="grind.html">Which grind?</a></p>')
        opts = "\n".join(
            f'<label class="opt"><input type="radio" name="o{i}" value="{esc(v)}"'
            f'{" checked" if v == default[i-1] else ""}><span>{v.split(" (")[0]}</span>'
            + (f'<small>{v.split("(")[1].rstrip(")")}</small>' if "(" in v else "")
            + '</label>'
            for j, v in enumerate(o["values"]))
        ctrls += f'''      <fieldset class="opts">
        <legend class="cof__k">{o['name'].replace('Select ','')}</legend>
        {hint}
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
    <h2 class="cgroup">On the estate</h2>
    <div class="plates plates--3">
{figs}
    </div>
  </div>
</section>'''

    extra = EXTRA.get(p["handle"], "")
    return f'''<nav class="crumb" aria-label="Breadcrumb">
  <div class="wrap">
    <a href="shop.html">Shop</a><span aria-hidden="true">/</span><span aria-current="page">{p['title'].title()}</span>
  </div>
</nav>
<section class="pdp" style="--c:{c}" data-variants='{vjson}' data-handle="{p['handle']}" data-title="{esc(p['title'].title())}">
  <div class="wrap pdp__in">
    <figure class="pdp__fig">
      {f'<img class="pdp__bg" src="{bg}" alt="" loading="lazy">' if bg else ''}
      <img class="pdp__pack" src="{src}" alt="{esc(p['title'].title())}" loading="eager">
    </figure>
    <div class="pdp__buy">
      <p class="eyebrow">{sub}</p>
      <h1 class="d2">{p['title'].title()}</h1>
      {f'<ul class="cof__specs" style="margin-top:1.25rem">{factrows}</ul>' if factrows else ''}

      <form class="buy" onsubmit="return false">
{ctrls}
        <div class="buy__bar">
          <p class="buy__price num" data-price>{money(entry["p"])}</p>
          <button class="btn btn--gold" type="button" data-add>Add to cart</button>
          <button class="wish" type="button" data-wish="{p['handle']}" aria-pressed="false">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>
            <span data-wish-label>Save</span>
          </button>
        </div>
      </form>
      {TOUR_FACTS if p["handle"] == "coffee-experience-tours-11" else TRUST}
      {f'<div class="pdp__about"><h2 class="cof__k">About this {"tour" if p["handle"] == "coffee-experience-tours-11" else "product"}</h2><p class="body">{body}</p></div>' if body else ''}
    </div>
  </div>
</section>
{extra}
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
# the subscription's coffee names -> the single-bag product they correspond to,
# so the page can say what the term saves against buying the same bag monthly
SUB_SINGLES = {
    "Indian Filter Blend":"indian-filter-blend-5", "Espresso Blend":"espresso-blend-5",
    "Glenfell Classic":"glenfell-4", "Cauvery Peak Estate Heritage":"coffee-powder-cp",
    "Shevaroys Estate Reserve":"coffee-powder-she",
}
def singles():
    out = {}
    for name, h in SUB_SINGLES.items():
        row = {}
        for v in BY[h]["variants"]:
            m = re.search(r"(\d+)\s*(kg|gm)", v["t"], re.I)
            if m: row[f"{m.group(1)} {m.group(2).lower()}"] = v["p"]
        out[name] = row
    return out

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

<nav class="crumb" aria-label="Breadcrumb">
  <div class="wrap">
    <a href="shop.html">Shop</a><span aria-hidden="true">/</span><span aria-current="page">Subscription</span>
  </div>
</nav>
<section class="pdp" data-variants='{vjson}' data-singles='{json.dumps(singles(), separators=(",",":"))}' data-handle="coffee" data-title="Coffee subscription">
  <div class="wrap">
    <form class="buy buy--sub" onsubmit="return false">
{ctrls}
      <div class="buy__bar">
        <div>
          <p class="buy__price num" data-price>&#8377;3,132</p>
          <p class="buy__unit num" data-unit></p>
          <p class="buy__save" data-save></p>
        </div>
        <button class="btn btn--gold" type="button" data-add>Start the subscription</button>
      </div>
      <p class="buy__note">One pack a month for the term, billed once. Roasted to order before each despatch.</p>
      {TRUST}
    </form>
  </div>
</section>

<section class="band">
  <div class="wrap stack">
    <p class="eyebrow eyebrow--d">Why commit</p>
    <h2 class="d2">The longer the term,<br>the less you pay per kilo.</h2>
    <p class="lede">A subscription saves 10&ndash;15% against buying the same bag every month &mdash; the exact figure is shown above as you choose.</p>
    <ul class="ticks ticks--2" style="margin-top:1.5rem">
      <li><b>Mixed Bag</b> sends a different estate coffee with each delivery, for anyone who would rather taste all of them.</li>
      <li><b>A different rhythm?</b> Six, twelve and twenty-four months are the terms online. For any other frequency, <a href="contact.html">tell us</a> and the estate will arrange deliveries around you.</li>
    </ul>
  </div>
</section>'''

# --------------------------------------------------------- collections
# The live store has a page per collection. These keep that — each is a real,
# linkable URL the old collection addresses can 301 to — but reuse the shop's
# cards. The store's filters ("in stock", a price slider) are dropped: with
# three to eight products every one is already in view. Sort stays.
COLLECTIONS = [
    ("shop-coffee.html", "Coffee", "Estate coffee",
     "Three single estates, two blends.",
     "Each single estate is one named property at one elevation. The blends draw on all three. Every bag is roasted and ground to order.",
     ["coffee-powder-she","coffee-powder-cp","glenfell-4","espresso-blend-5","indian-filter-blend-5","sample-pack","blend-sampler-pack-23","drip-bags","cauvery-peak-green-beans"],
     "cherries.webp", "Estate coffee from Cauvery Peak, Yercaud: three single estates at 1,250–1,450 m, two blends, samplers and drip bags. Roasted to order."),
    ("shop-spices-honey.html", "Spices &amp; honey", "Grown between the coffee",
     "Spice and honey from the same boundary.",
     "Pepper vines climb the shade trees. Cloves and nutmeg are inter-planted with the coffee at Glenfell. The hives sit among all of it.",
     ["pepper","clove","nutmeg-mace","honey"],
     "shade.webp", "Pepper, cloves, nutmeg, mace and honey grown among the coffee on the Cauvery Peak estates in the Shevaroy Hills, Yercaud."),
    ("shop-samplers.html", "Samplers &amp; drip bags", "The way in",
     "Taste the three estates side by side.",
     "If you have not had them before, start here. The sampler packs put the estates next to each other; the drip bags need nothing but a mug.",
     ["sample-pack","blend-sampler-pack-23","drip-bags"],
     "land.webp", "Cauvery Peak sampler packs and single-estate drip bags: the easiest way to taste the three Shevaroy Hills estates side by side."),
]

SORT = '''    <div class="sortbar">
      <p class="sortbar__n num" data-count></p>
      <label class="sortbar__l">Sort
        <select data-sort>
          <option value="">Featured</option>
          <option value="lo">Price, low to high</option>
          <option value="hi">Price, high to low</option>
        </select>
      </label>
    </div>'''

def collection_page(slug, title, eyebrow, head, lede, handles, img):
    items = [BY[h] for h in handles if h in BY]
    others = " &middot; ".join(f'<a href="{s}">{t}</a>' for s, t, *_ in COLLECTIONS if s != slug)
    return f'''<header class="phero phero--shop">
  <img class="phero__img" src="assets/{img}" alt="" width="900" height="600" fetchpriority="high">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">{eyebrow}</p>
    <h1 class="d1">{head}</h1>
    <p class="lede">{lede}</p>
  </div>
</header>

<nav class="crumb" aria-label="Breadcrumb">
  <div class="wrap">
    <a href="shop.html">Shop</a><span aria-hidden="true">/</span><span aria-current="page">{title}</span>
  </div>
</nav>
<div class="wrap" style="padding-top:.5rem">{TRUST.replace('class="assure"','class="assure assure--row"')}</div>
<section style="padding-top:1rem">
  <div class="wrap">
{SORT}
    <h2 class="sr">Products</h2>
    <div class="coffees" data-sortable style="margin-top:1.25rem">
{chr(10).join(card(p) for p in items)}
    </div>
    <p class="closer__or" style="margin-top:2rem">Also in the shop: {others} &middot; <a href="shop.html">everything</a>.</p>
  </div>
</section>'''

# ------------------------------------------------------------ wishlist
def wish_data():
    """Just enough per product to draw a saved-item card without a server."""
    out = {}
    for p in CAT:
        if p["handle"] == "coffee":
            continue
        src, c, _ = img_for(p)
        out[p["handle"]] = {"t": p["title"].title(), "s": SUBTITLE.get(p["handle"], p["type"] or "From the estate"),
                            "p": min(v["p"] for v in p["variants"]), "i": src, "c": c}
    return out

def wishlist_page():
    return f'''<header class="phero phero--doc">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">Saved</p>
    <h1 class="d1">Your wishlist</h1>
    <p class="lede">Things you saved for later. They stay in this browser &mdash; no account needed.</p>
  </div>
</header>
<section>
  <div class="wrap">
    <div class="coffees" data-wishlist data-wishdata=\'{json.dumps(wish_data(), separators=(",",":"), ensure_ascii=False).replace("'", "&#39;")}\'></div>
    <div class="wl-empty" data-wish-empty hidden>
      <p class="body">Nothing saved yet. Tap <b>Save</b> on any product and it will wait here.</p>
      <div class="btns" style="margin-top:1.25rem"><a class="btn btn--gold" href="shop.html">Shop Coffee</a></div>
    </div>
  </div>
</section>'''

# -------------------------------------------------------------- search
def search_page(pages):
    idx = []
    # curated keywords and a weight, so "coffee" finds the coffees before the
    # coffee scrub, and "spices" finds pepper without the word being in its name
    coffees = {"coffee-powder-she","coffee-powder-cp","glenfell-4","espresso-blend-5","indian-filter-blend-5"}
    KW = {"pepper":"spice spices","clove":"spice spices","nutmeg-mace":"spice spices","honey":"honey",
          "drip-bags":"coffee drip bag sachet","sample-pack":"coffee sampler","blend-sampler-pack-23":"coffee sampler",
          "cauvery-peak-green-beans":"coffee green beans","coffee-experience-tours-11":"tour visit estate booking"}
    order = sorted((p for p in CAT if p["handle"] != "coffee"), key=lambda p: p["handle"] not in coffees)
    for p in order:
        h = p["handle"]
        body = p["body"][:160]
        if len(p["body"]) > 160: body = body[:body.rfind(" ")] + "\u2026"
        idx.append({"t": p["title"].title(), "u": f"p-{h}.html", "k": "Product", "d": body,
                    "w": 2 if h in coffees else (1 if h in KW else 0),
                    "x": " ".join([p["type"] or "", SUBTITLE.get(h, ""), "coffee beans ground" if h in coffees else "", KW.get(h, "")]),
                    "o": " ".join(o for x in p["options"] for o in x["values"])[:400]})
    idx.append({"t": "Coffee subscription", "u": "subscribe.html", "k": "Product",
                "d": "Six, twelve or twenty-four months of estate coffee, roasted to order.", "x": "coffee subscribe subscription monthly", "w": 1, "o": ""})
    for p in pages:
        if p["slug"].startswith("p-") or p["slug"] in ("search.html", "wishlist.html", "subscribe.html"):
            continue
        idx.append({"t": re.sub(r"\s+—.*$", "", p["title"]), "u": p["slug"], "k": "Page", "d": p["desc"], "x": "", "w": 0, "o": ""})
    data = json.dumps(idx, separators=(",",":"), ensure_ascii=False).replace("</", "<\\/")
    return f'''<header class="phero phero--doc">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">Search</p>
    <h1 class="d1">Search the estate</h1>
    <form class="sbox" role="search" action="search.html" method="get">
      <label class="sr" for="q">Search products and pages</label>
      <input id="q" name="q" type="search" autocomplete="off" placeholder="Try &ldquo;filter&rdquo;, &ldquo;pepper&rdquo; or &ldquo;tour&rdquo;">
      <button class="btn btn--gold" type="submit">Search</button>
    </form>
    <p class="sbox__pop">Popular: <a href="search.html?q=coffee">Coffee</a> &middot; <a href="search.html?q=spices">Spices</a> &middot; <a href="search.html?q=tour">Tour</a> &middot; <a href="search.html?q=filter">Filter</a></p>
  </div>
</header>
<section>
  <div class="wrap">
    <p class="sortbar__n num" data-sres-n aria-live="polite"></p>
    <ol class="sres" data-sres></ol>
  </div>
</section>
<script type="application/json" id="sidx">{data}</script>
<script>
(function(){{
  var idx=JSON.parse(document.getElementById('sidx').textContent);
  var input=document.getElementById('q'), list=document.querySelector('[data-sres]'), n=document.querySelector('[data-sres-n]');
  var SYN={{cafe:'caf',beans:'bean whole'}};
  function norm(s){{ return (s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'') }}
  function esc(s){{ var d=document.createElement('div'); d.textContent=s; return d.innerHTML }}
  function run(q){{
    q=norm(q).trim(); list.innerHTML=''; if(!q){{ n.textContent=''; return }}
    var terms=q.split(/\\s+/);
    var hits=idx.map(function(r){{
      // title 4, curated keyword 3, description or option 1, plus the item's weight
      var t=norm(r.t), kw=norm(r.x), all=norm(r.d)+' '+norm(r.o), score=0;
      var ok=terms.every(function(w){{
        var alts=[w].concat((SYN[w]||'').split(' ').filter(Boolean));
        return alts.some(function(a){{
          if(t.indexOf(a)>-1){{ score+=4; return true }}
          if(kw.indexOf(a)>-1){{ score+=3; return true }}
          if(all.indexOf(a)>-1){{ score+=1; return true }}
          return false }});
      }});
      score+=r.w||0;
      return ok?{{r:r,s:score}}:null;
    }}).filter(Boolean).sort(function(a,b){{ return b.s-a.s }});
    n.textContent = hits.length ? hits.length+' result'+(hits.length>1?'s':'')+' for \u201c'+q+'\u201d' : 'Nothing matches \u201c'+q+'\u201d. Try a shorter word.';
    hits.forEach(function(h){{
      var li=document.createElement('li'); li.className='sres__i';
      li.innerHTML='<p class="sres__k">'+h.r.k+'</p><h2 class="sres__t"><a href="'+h.r.u+'">'+esc(h.r.t)+'</a></h2><p class="sres__d">'+esc(h.r.d)+'</p>';
      list.appendChild(li);
    }});
  }}
  var q0=new URLSearchParams(location.search).get('q')||'';
  input.value=q0; run(q0);
  input.addEventListener('input',function(){{
    run(input.value);
    var u=new URL(location.href); if(input.value) u.searchParams.set('q',input.value); else u.searchParams.delete('q');
    history.replaceState(null,'',u);
  }});
  input.form.addEventListener('submit',function(e){{ e.preventDefault(); run(input.value) }});
}})();
</script>'''

# ------------------------------------------------------------------ run
def main():
    pages = json.load(open(os.path.join(SRC, "pages.json")))
    pages = [p for p in pages if not p["slug"].startswith(("p-", "shop.", "shop-", "subscribe.", "wishlist.", "search."))]

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

    for slug, title, eb, head, lede, handles, img, desc in COLLECTIONS:
        open(os.path.join(SRC, slug), "w").write(collection_page(slug, title, eb, head, lede, handles, img))
        pages.append({"file":slug, "slug":slug, "og":"og-coffee.jpg",
                      "title":f"{html.unescape(title)} — Cauvery Peak", "desc":desc})

    open(os.path.join(SRC, "wishlist.html"), "w").write(wishlist_page())
    pages.append({"file":"wishlist.html","slug":"wishlist.html","og":"og-default.jpg",
                  "title":"Wishlist — Cauvery Peak","desc":"Products you have saved for later at Cauvery Peak."})

    # search indexes every other page, so it is written last
    pages.append({"file":"search.html","slug":"search.html","og":"og-default.jpg",
                  "title":"Search — Cauvery Peak","desc":"Search Cauvery Peak's coffee, spices, honey, the estate tour and every page on the site."})
    open(os.path.join(SRC, "search.html"), "w").write(search_page(pages))

    json.dump(pages, open(os.path.join(SRC, "pages.json"), "w"), indent=1, ensure_ascii=False)
    print(f"shop.html, subscribe.html and {made} product pages -> pages.json ({len(pages)} total)")

if __name__ == "__main__":
    main()
