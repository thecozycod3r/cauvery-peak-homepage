// Page audit: run every page at phone and desktop width and report
// anything that would actually bother a visitor.
export default async function audit(page, url, label) {
  await page.goto(url, { waitUntil: 'networkidle' });
  return await page.evaluate((label) => {
    const vw = document.documentElement.clientWidth;
    const out = { label, vw, issues: [] };
    const add = (sev, what) => out.issues.push(`${sev} ${what}`);

    // 1. horizontal overflow — the classic mobile killer
    const wide = [];
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width > vw + 1 || r.right > vw + 1) {
        const scroller = el.closest('[style*="overflow"], .tablewrap, .rail');
        if (!scroller) wide.push((el.tagName + '.' + (el.className || '').toString().split(' ')[0]).slice(0, 40));
      }
    });
    if (document.documentElement.scrollWidth > vw + 1)
      add('FAIL', `page scrolls sideways (${document.documentElement.scrollWidth} > ${vw}) ${wide.slice(0,3).join(', ')}`);

    // 2. images that never decoded
    const broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0);
    if (broken.length) add('FAIL', `${broken.length} broken image(s): ${broken.map(i=>i.getAttribute('src')).slice(0,3)}`);

    // 3. images with no alt text
    const noAlt = [...document.images].filter(i => !i.hasAttribute('alt'));
    if (noAlt.length) add('WARN', `${noAlt.length} image(s) without alt`);

    // 4. tap targets that are too small to hit on a phone
    if (vw < 700) {
      const small = [...document.querySelectorAll('a, button')].filter(a => {
        const r = a.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0)) return false;
        const isIcon = !a.textContent.trim();
        return r.height < 40 || (isIcon && r.width < 40);
      });
      if (small.length) add('WARN', `${small.length} tap target(s) under 40px: ${small.slice(0,3).map(a=>(a.textContent||'').trim().slice(0,18))}`);
    }

    // 5. text spilling out of its box
    const clipped = [...document.querySelectorAll('h1,h2,h3,p,li,td,th')].filter(el =>
      el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === 'visible');
    if (clipped.length) add('WARN', `${clipped.length} element(s) with text wider than their box`);

    // 6. heading order
    const hs = [...document.querySelectorAll('h1,h2,h3,h4')].map(h => +h.tagName[1]);
    let jump = null;
    for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i-1] > 1) { jump = `h${hs[i-1]} → h${hs[i]}`; break; }
    if (jump) add('WARN', `heading level skips: ${jump}`);

    // 7. document essentials
    if (!document.querySelector('meta[name=viewport]')) add('FAIL', 'no viewport meta');
    if (!document.title) add('FAIL', 'no title');
    if (!document.querySelector('meta[name=description]')) add('WARN', 'no meta description');

    // 8. sticky chrome must not cover the sticky photo/nav
    const hdr = document.querySelector('.site');
    const sticky = [...document.querySelectorAll('*')].filter(e => getComputedStyle(e).position === 'sticky' && e !== hdr);
    sticky.forEach(e => {
      const t = parseFloat(getComputedStyle(e).top);
      if (hdr && !isNaN(t) && t < hdr.getBoundingClientRect().height - 1)
        add('WARN', `sticky ${e.className.split(' ')[0]} sits under the header (top:${t}px)`);
    });

    out.docH = document.documentElement.scrollHeight;
    out.imgs = document.images.length;
    return out;
  }, label);
}
