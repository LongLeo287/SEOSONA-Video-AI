#!/usr/bin/env node
/**
 * SEOSONA Video — HyperFrames Producer render helper.
 *
 * Programmatic render via @hyperframes/producer (streaming progress + structured
 * errors), an opt-in alternative to the CLI subprocess. Enabled from the Python
 * pipeline when SEOSONA_HF_PRODUCER=1.
 *
 * The producer pulls full `puppeteer`, whose bundled Chrome download is unreliable
 * in some environments. This helper sidesteps that by pointing puppeteer at an
 * EXISTING Chrome via PUPPETEER_EXECUTABLE_PATH (system Chrome / Playwright
 * Chromium / Edge), so no Chrome download is needed at install or render time.
 * Install the package once with: PUPPETEER_SKIP_DOWNLOAD=1 npm install
 *
 * Usage: node hf_producer_render.mjs <projectDir> <outputPath> [fps] [quality]
 * Emits lines: `HF_PROGRESS <pct> <stage>` and final `HF_DONE <path>` / `HF_ERROR <msg>`.
 */

import fs from "node:fs";
import path from "node:path";

function findChrome() {
  // 1) explicit override
  const envPath = process.env.PUPPETEER_EXECUTABLE_PATH || process.env.SEOSONA_CHROME_PATH;
  if (envPath && fs.existsSync(envPath)) return envPath;

  const candidates = [];
  // 2) system Chrome (Win)
  for (const base of [process.env["ProgramFiles"], process.env["ProgramFiles(x86)"], process.env["LOCALAPPDATA"]]) {
    if (base) candidates.push(path.join(base, "Google", "Chrome", "Application", "chrome.exe"));
  }
  // 3) Playwright Chromium
  const ms = process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, "ms-playwright");
  if (ms && fs.existsSync(ms)) {
    for (const d of fs.readdirSync(ms)) {
      if (d.startsWith("chromium-")) candidates.push(path.join(ms, d, "chrome-win64", "chrome.exe"));
    }
  }
  // 4) Microsoft Edge (Chromium) as last resort
  for (const base of [process.env["ProgramFiles(x86)"], process.env["ProgramFiles"]]) {
    if (base) candidates.push(path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"));
  }
  // 5) POSIX fallbacks
  candidates.push("/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium");

  return candidates.find((c) => c && fs.existsSync(c)) || null;
}

async function main() {
  const [projectDir, outPath, fpsArg, qualityArg] = process.argv.slice(2);
  if (!projectDir || !outPath) {
    console.error("HF_ERROR usage: hf_producer_render.mjs <projectDir> <outputPath> [fps] [quality]");
    process.exit(2);
  }

  const chrome = findChrome();
  if (chrome) {
    process.env.PUPPETEER_EXECUTABLE_PATH = chrome;
    console.error(`[hf-producer] using Chrome: ${chrome}`);
  } else {
    console.error("[hf-producer] WARNING: no existing Chrome found; producer may try to download one.");
  }

  let producer;
  try {
    producer = await import("@hyperframes/producer");
  } catch (e) {
    console.log(`HF_ERROR @hyperframes/producer not installed (PUPPETEER_SKIP_DOWNLOAD=1 npm install): ${e.message}`);
    process.exit(3);
  }
  const { createRenderJob, executeRenderJob, resolveConfig, createConsoleLogger } = producer;

  const job = createRenderJob({
    fps: fpsArg ? Number(fpsArg) : 30,
    quality: qualityArg || "high",
    format: "mp4",
    entryFile: "index.html",
    logger: createConsoleLogger("warn"),
    producerConfig: resolveConfig({ browserGpuMode: "auto" }),
  });

  try {
    await executeRenderJob(job, projectDir, outPath, (j) => {
      if (j.progress != null) {
        console.log(`HF_PROGRESS ${Math.floor(j.progress * 100)} ${j.currentStage || ""}`);
      }
    });
    console.log(`HF_DONE ${outPath}`);
  } catch (e) {
    console.log(`HF_ERROR ${e && e.message ? e.message : e}`);
    process.exit(1);
  }
}

main();
