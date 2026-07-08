// capture_scroll.js <url> <out.webm> [seconds]
// Records a SLOW auto-scroll of a real web page → webm (real "screen-recording" footage for the mockup
// scene, vs a static screenshot). Uses Playwright with a system browser channel (no download), falling
// back to bundled chromium. Best-effort: prints "OK <path>" on success, exits non-zero on failure so the
// caller keeps the static screenshot. (2026-07-03 — density study "real footage, not a static shot")
const path = require("path");
const fs = require("fs");

async function launch() {
  const { chromium } = require("playwright");
  for (const opt of [{ channel: "msedge" }, { channel: "chrome" }, {}]) {
    try { return await chromium.launch({ headless: true, args: ["--no-sandbox"], ...opt }); } catch (_) {}
  }
  throw new Error("no chromium/edge/chrome available");
}

(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  const secs = Math.max(2, parseFloat(process.argv[4] || "6"));
  if (!url || !out) { console.error("usage: capture_scroll.js <url> <out.webm> [seconds]"); process.exit(2); }
  const dir = path.dirname(out);
  fs.mkdirSync(dir, { recursive: true });
  let browser;
  try { browser = await launch(); } catch (e) { console.error("launch failed:", e.message); process.exit(2); }
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1,
    recordVideo: { dir, size: { width: 1280, height: 800 } },
  });
  const page = await ctx.newPage();
  let ok = true;
  try {
    await page.goto(url, { waitUntil: "load", timeout: 30000 });
    await page.waitForTimeout(1100);                       // let hero/above-the-fold settle
    await page.evaluate(async (secs) => {                  // smooth 60fps auto-scroll to the bottom
      const h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
      const dist = Math.max(0, h - window.innerHeight);
      const steps = Math.max(1, Math.round(secs * 60));
      for (let i = 0; i <= steps; i++) {
        window.scrollTo(0, (dist * i) / steps);
        await new Promise((r) => setTimeout(r, 1000 / 60));
      }
    }, secs);
    await page.waitForTimeout(500);
  } catch (e) { console.error("nav/scroll failed:", e.message); ok = false; }
  const video = page.video();
  await ctx.close();                                       // finalizes the .webm
  await browser.close();
  if (video && ok) {
    const p = await video.path();
    try { fs.renameSync(p, out); } catch (_) { try { fs.copyFileSync(p, out); } catch (_) {} }
    if (fs.existsSync(out) && fs.statSync(out).size > 10000) { console.log("OK " + out); process.exit(0); }
  }
  process.exit(2);
})();
