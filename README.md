# Cauvery Peak — homepage direction

Review build for MSP Plantations. Not the live store.

    assets/      images, brand font, video, one shared stylesheet
    _src_pages/  page fragments + pages.json (the content)
    build.py     wraps each fragment in the shared head/header/footer
    run-audit.mjs  checks every page at 390px and 1440px

Rebuild with `python3 build.py`, then `node run-audit.mjs` with a server
running on the site root.

Café opening hours and telephone numbers are deliberately absent — the
current live site gives conflicting values and they need confirming.
