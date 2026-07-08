// capture_shot.js — screenshot a URL to a PNG for the `shot`/mockup component (real visuals).
// Best-effort: any failure (bad URL, 403, captcha, no browser) exits non-zero so the Python
// caller gracefully falls back (homepage → GitHub page → synthetic tiles).
// Uses Playwright with a SYSTEM browser channel (Edge/Chrome, always present on Win11) so no
// browser download is needed; falls back to Playwright's bundled chromium, then puppeteer-core.
// Usage: node scripts/capture_shot.js <url> <out.png>
const path = require("path");

async function launch() {
  // Try system browsers first (no download). Edge ships with Windows 11.
  try {
    const { chromium } = require("playwright");
    for (const opt of [{ channel: "msedge" }, { channel: "chrome" }, {}]) {
      try { return await chromium.launch({ headless: true, ...opt }); } catch (_) {}
    }
  } catch (_) {}
  const puppeteer = require("puppeteer");
  return await puppeteer.launch({ headless: "new", channel: "msedge", args: ["--no-sandbox"] });
}

async function shoot(url, out) {
  const browser = await launch();
  try {
    const page = await browser.newPage();
    if (page.setViewportSize) await page.setViewportSize({ width: 1280, height: 860 });
    else await page.setViewport({ width: 1280, height: 860, deviceScaleFactor: 2 });
    await page.goto(url, { waitUntil: "networkidle", timeout: 25000 }).catch(async () => {
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 25000 });
    });
    await new Promise((r) => setTimeout(r, 1400)); // let fonts / hero images settle
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1280, height: 860 } });
  } finally {
    try { await browser.close(); } catch (_) {}
  }
}

(async () => {
  const url = process.argv[2], out = process.argv[3];
  if (!url || !out) { console.error("usage: capture_shot.js <url> <out.png>"); process.exit(2); }
  try { await shoot(url, path.resolve(out)); process.exit(0); }
  catch (e) { console.error("capture failed:", e && e.message); process.exit(1); }
})();
