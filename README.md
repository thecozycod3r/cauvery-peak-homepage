# Cauvery Peak — homepage direction

Review build for MSP Plantations. Not the live store.

    assets/      images, brand font, video, one shared stylesheet
    _src_pages/  page fragments + pages.json (the content)
    build.py     wraps each fragment in the shared head/header/footer
    run-audit.mjs  checks every page at 390px and 1440px

Rebuild with `python3 build.py`, then `node run-audit.mjs` with a server
running on the site root.

Café opening hours and telephone numbers are deliberately absent — the
current live site gives conflicting values and they need confirming. The
WhatsApp and Facebook links are omitted for the same reason: the number is
one of the disputed pair, and no Facebook page has been confirmed. Nothing
on the site points at `#`.

Under 760px the inline nav is replaced by a drawer holding the whole site
map. It traps focus, closes on Escape and on the scrim, returns focus to the
button, and collapses to a cross-fade under `prefers-reduced-motion`.

Two photographs carried a marketing caption burnt into the frame and several
were video stills with letterbox bars; both are cropped out. Three homepage
process stages showed the wrong subject (cherries for washing, drying
parchment for roasting, the lake for despatch) and now match the estate page.
The Shevaroys card previously showed an open-cast bauxite excavation; it now
shows the ridge. Roasting still has no photograph and says so.
