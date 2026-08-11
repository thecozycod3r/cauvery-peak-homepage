import { chromium } from 'playwright';
import audit from './audit.mjs';
import fs from 'fs';

const pages = JSON.parse(fs.readFileSync('pages/pages.json')).map(p => p.slug);
const base = 'http://localhost:8731/site/';
const browser = await chromium.launch();
let fails = 0, warns = 0;

for (const size of [{w:390,h:844,n:'phone'},{w:1440,h:900,n:'desktop'}]) {
  const ctx = await browser.newContext({ viewport:{width:size.w,height:size.h}, deviceScaleFactor:1 });
  const page = await ctx.newPage();
  const errs = [];
  page.on('console', m => { if (m.type()==='error') errs.push(m.text().slice(0,90)); });
  page.on('requestfailed', r => errs.push('REQ FAIL ' + r.url().split('/').pop()));
  console.log(`\n=== ${size.n} (${size.w}px) ===`);
  for (const slug of pages) {
    errs.length = 0;
    const r = await audit(page, base + slug, slug);
    const netErrs = errs.filter(e => !e.includes('favicon'));
    if (netErrs.length) r.issues.push('FAIL console/network: ' + netErrs.slice(0,2).join(' | '));
    fails += r.issues.filter(i=>i.startsWith('FAIL')).length;
    warns += r.issues.filter(i=>i.startsWith('WARN')).length;
    const tag = r.issues.length ? '' : '  ok';
    console.log(`  ${slug.padEnd(20)} ${String(r.docH).padStart(6)}px ${String(r.imgs).padStart(3)} img${tag}`);
    r.issues.forEach(i => console.log(`      ${i}`));
  }
  await ctx.close();
}
await browser.close();
console.log(`\nTOTAL  ${fails} fail, ${warns} warn`);
