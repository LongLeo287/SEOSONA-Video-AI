// Skip Puppeteer's bundled-Chrome download. SEOSONA points puppeteer at an
// existing Chrome (system/Playwright) via PUPPETEER_EXECUTABLE_PATH — see
// 5_FRAMEWORK/hf_producer_render.mjs. Makes @hyperframes/producer install cleanly.
module.exports = { skipDownload: true };
