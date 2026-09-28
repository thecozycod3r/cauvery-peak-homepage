#!/usr/bin/env python3
"""Refresh _src_pages/catalog.json from the live store's products.json.

Prices, variant ids and availability must match the store exactly: the basket
hands off to Shopify with /cart/<variant id>:<qty>, and a stale id sends the
visitor to an empty or wrong cart. Nothing is written to the store.

Run it when the client adds a product or changes a price, then
`python3 build_shop.py && python3 build.py`. New products also need a
product image in assets/shop/ — see fetch_images() below.
"""
import html, json, os, re, subprocess, sys, tempfile, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(HERE, "_src_pages", "catalog.json")
SHOP = os.path.join(HERE, "assets", "shop")
STORE = "https://cauverypeakestate.com"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def text(body_html):
    t = re.sub(r"<[^>]+>", " ", body_html or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def shape(p):
    return {
        "body": text(p["body_html"]),
        "handle": p["handle"],
        "images": [i["src"].split("/")[-1].split("?")[0] for i in p["images"]],
        "options": [{"name": o["name"], "values": o["values"]} for o in p["options"]],
        "tags": p["tags"],
        "title": p["title"],
        "type": p["product_type"],
        "variants": [{"av": v["available"], "id": v["id"], "o1": v["option1"],
                      "o2": v["option2"], "o3": v["option3"],
                      "p": float(v["price"]), "t": v["title"]} for v in p["variants"]],
    }

def fetch_images(p, keep=4):
    """Download a product's store images as assets/shop/<handle[:24]>-<n>.webp,
    only where the file does not exist yet (existing crops are hand-checked)."""
    for n, img in enumerate(p["images"][:keep]):
        out = os.path.join(SHOP, f"{p['handle'][:24]}-{n}.webp")
        if os.path.exists(out):
            continue
        src = img["src"] + ("&" if "?" in img["src"] else "?") + "width=1200"
        with tempfile.NamedTemporaryFile(suffix=".img") as f:
            f.write(get(src)); f.flush()
            subprocess.run(["cwebp", "-quiet", "-q", "80", "-resize", "1200", "0", f.name, "-o", out], check=True)
        print("  image", os.path.relpath(out, HERE))

if __name__ == "__main__":
    live = json.loads(get(STORE + "/products.json?limit=250"))["products"]
    old = {p["handle"]: p for p in json.load(open(CAT))} if os.path.exists(CAT) else {}
    # keep the existing order, append anything new at the end
    order = list(old) + [p["handle"] for p in live if p["handle"] not in old]
    by = {p["handle"]: p for p in live}
    cat = [shape(by[h]) for h in order if h in by]
    for h in order:
        if h not in by: print("  removed from store:", h)
        elif h not in old: print("  new product:", h); fetch_images(by[h])
    json.dump(cat, open(CAT, "w"), indent=1, ensure_ascii=False)
    print(f"catalog.json: {len(cat)} products")
