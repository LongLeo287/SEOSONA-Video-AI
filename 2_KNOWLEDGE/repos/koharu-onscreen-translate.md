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

## How to use (license-safe)
**GPL-3.0 → isolate it.** Invoke koharu as a **separate CLI process** over frames/thumbnails;
do NOT statically link or embed it in the proprietary pipeline (running a separate GPL
binary keeps SEOSONA's own code clear of copyleft).

Integration: a new optional stage in the repurposer/localizer — for a source video with
burned-in foreign text, extract frames → koharu (OCR+translate+inpaint, target=vi) →
re-render Vietnamese in place. Pilot on hardsub removal + Vietnamese thumbnail re-text.

> Pairs with the localizer (audio dub) to cover BOTH axes (audio + on-screen text).
> Translation backend can be the local Gemma model. Triaged ADOPT (1,434-repo analysis).
