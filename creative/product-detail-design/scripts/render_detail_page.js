// render_detail_page.js — Render an e-commerce detail-page HTML prototype to
// platform-ready PNGs (full long-image + per-module slices).
//
// Usage:  copy this file into the prototype folder, edit the 3 constants below,
//         then run:  node render_detail_page.js
//
// Requires:  npm install puppeteer-core   (run once in this folder)
// Chrome:    uses the Chrome cached by the anygen/Puppeteer setup. Adjust
//            CHROME_PATH if your version folder differs.

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

// ── Edit these three constants per project ───────────────────────────────
const HTML_FILE   = 'index.html';                       // prototype in same folder
const OUT_DIR     = '成品图';                            // output subfolder
const CHROME_PATH = 'C:/Users/win10/.cache/puppeteer/chrome/win64-150.0.7871.24/chrome-win64/chrome.exe';
// ─────────────────────────────────────────────────────────────────────────

(async () => {
  const here = __dirname;
  const htmlPath = 'file:///' + path.join(here, HTML_FILE).replace(/\\/g, '/');

  if (!fs.existsSync(path.join(here, OUT_DIR))) fs.mkdirSync(path.join(here, OUT_DIR), { recursive: true });

  console.log('Launching Chrome...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--force-color-profile=srgb']
  });

  const page = await browser.newPage();
  // 750px design width × 2 DPI = crisp 1500px output
  await page.setViewport({ width: 750, height: 1334, deviceScaleFactor: 2 });
  await page.goto(htmlPath, { waitUntil: 'networkidle0', timeout: 60000 });
  await new Promise(r => setTimeout(r, 3000)); // let images settle

  console.log('Taking full page screenshot...');
  await page.screenshot({
    path: path.join(here, OUT_DIR, '全图.png'),
    fullPage: true
  });

  // Per-module slices for single-image platform upload
  const blocks = await page.$$('.section, .hero, .full-img, .brand-block, .cta-block, .footer-block');
  console.log(`Found ${blocks.length} blocks`);
  for (let i = 0; i < blocks.length; i++) {
    await blocks[i].screenshot({
      path: path.join(here, OUT_DIR, `P${String(i + 1).padStart(2, '0')}.png`)
    }).catch(e => console.log(`P${i + 1} failed: ${e.message}`));
  }

  await browser.close();
  console.log('Done →', path.join(here, OUT_DIR));
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
