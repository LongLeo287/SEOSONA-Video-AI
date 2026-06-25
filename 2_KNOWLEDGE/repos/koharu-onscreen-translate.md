# koharu — on-screen / hardsub text translation + inpainting (the missing axis)

Source: [mayocream/koharu](https://github.com/mayocream/koharu) (**GPL-3.0**, Rust, local,
v0.61.2, very active). "ML-powered manga translator": **detect text → OCR → translate →
inpaint the original out → re-render the translation in place.**

## Why it fills a real gap
SEOSONA Video's audio axis is covered: PhoWhisper (ASR) → translate → VieNeu (dub). But
nothing handles **text burned into the image**: foreign title cards, on-screen captions,
hardsubs, signage, thumbnails. koharu's detect→OCR→**inpaint**→re-render loop is exactly
that — and the inpainting (FLUX.2 Klein 4B / lama-manga) is the hard part the pipeline
lacks. It also ships a local-LLM translation hook (Gemma/Qwen → see `2_KNOWLEDGE/...local-llm-gemma`).

## ⚠️ Reality check (2026-06-25): koharu is a GUI DESKTOP app
koharu ships only desktop installers (`x64-setup.exe` / `.msi` / `.AppImage` — a Tauri app),
**no headless CLI**. So it CANNOT be auto-wired as a batch pipeline stage — it's a **manual
tool**: install it, open a thumbnail/frame, translate+inpaint by hand. The on-screen-text
axis is real, but koharu fills it manually, not automatically.

**The automation point still exists, tool-agnostic:** `1_AGENTS/repurposer_agent/
onscreen_translate.py` invokes whatever headless OCR→translate→inpaint binary `KOHARU_BIN`
points at. If/when a headless tool exists (a koharu CLI build, or an alternative like a
manga-image-translator CLI), it plugs straight in — no code change. GPL-3.0 → keep any such
binary isolated as a separate process.

Manual use now: install koharu desktop → translate foreign title cards / hardsub frames /
thumbnails → drop the re-rendered image back into the render. Automatic: pending a headless tool.

> Pairs with the localizer (audio dub) to cover BOTH axes (audio + on-screen text).
> Translation backend can be the local Gemma model. Triaged ADOPT (1,434-repo analysis).
