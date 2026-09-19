#!/usr/bin/env python3
"""Import the store's policy pages into the review build.

The four policies are the client's own legal text, so they are copied, never
retyped: this script pulls each one from the live Shopify store, keeps the
text verbatim, and changes only structure —

  - strips Shopify's inline style/class/id/data attributes
  - shifts headings so each document starts at h2 (the page has its own h1)
  - points links between the policies at the local copies, so reading the
    Terms does not throw you onto the old site

Run it whenever the client edits a policy in Shopify, then `python3 build.py`.
"""
import os, re, sys, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "_src_pages")
STORE = "https://cauverypeakestate.com/policies/"

POLICIES = {                      # store handle -> (local page, page title)
    "privacy-policy":   ("privacy.html",  "Privacy Policy"),
    "terms-of-service": ("terms.html",    "Terms of Service"),
    "shipping-policy":  ("shipping.html", "Shipping Policy"),
    "refund-policy":    ("returns.html",  "Return and Refund Policy"),
}

def fetch(handle):
    req = urllib.request.Request(STORE + handle, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def body(page):
    m = re.search(r'<div[^>]*class="[^"]*shopify-policy__body[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</main>', page, re.S)
    if not m:
        sys.exit("policy body not found — the store's theme markup has changed")
    inner = m.group(1)
    rte = re.search(r'<div[^>]*class="[^"]*rte[^"]*"[^>]*>(.*?)</div>\s*$', inner.strip(), re.S)
    return (rte.group(1) if rte else inner).strip()

def clean(html):
    html = re.sub(r'\s(style|class|id|data-[\w-]+)="[^"]*"', '', html)
    html = re.sub(r'<meta[^>]*>', '', html)
    # Shift headings so the document opens at h2 under the page's h1. Key it
    # off the FIRST heading, not the shallowest: the refund policy opens on
    # h3 sections and only reaches h2 at the very end, so "shallowest" left
    # h1 -> h3 skips in place. Anything that would rise above h2 is clamped.
    levels = [int(n) for n in re.findall(r'<h([1-6])[\s>]', html)]
    if levels:
        shift = 2 - levels[0]
        html = re.sub(r'<(/?)h([1-6])([\s>])',
                      lambda m: f'<{m.group(1)}h{min(6, max(2, int(m.group(2)) + shift))}{m.group(3)}', html)
    # links between policies stay on this site
    for handle, (local, _) in POLICIES.items():
        html = re.sub(r'href="(?:https?://(?:www\.)?cauverypeakestate\.com)?/policies/%s/?"' % re.escape(handle),
                      f'href="{local}"', html)
    return re.sub(r'\n{3,}', '\n\n', html)

def page(title, doc):
    return f'''<header class="phero phero--doc">
  <div class="wrap phero__in stack">
    <p class="eyebrow eyebrow--d">Policies</p>
    <h1 class="d1">{title}</h1>
    <p class="lede">The terms below are the ones that apply to your order. They are the same policies that govern checkout on the estate store.</p>
  </div>
</header>

<section>
  <div class="wrap">
    <div class="doc">
{doc}
    </div>
    <p class="closer__or" style="margin-top:2rem">Questions about any of this? <a href="contact.html">Talk to the estate</a>.</p>
  </div>
</section>
'''

if __name__ == "__main__":
    for handle, (local, title) in POLICIES.items():
        doc = clean(body(fetch(handle)))
        with open(os.path.join(SRC, local), "w") as f:
            f.write(page(title, doc))
        words = len(re.sub(r"<[^>]+>", " ", doc).split())
        print(f"  {local:14} {words:>5} words  <- {STORE}{handle}")
