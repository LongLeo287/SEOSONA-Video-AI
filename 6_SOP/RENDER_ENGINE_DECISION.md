# Render Engine Decision — HyperFrames (2026-06-23)

**Decision: HyperFrames is the SOLE render engine. Remotion is ELIMINATED.**

Remotion was evaluated for reference only. It is **source-available with a paid
company license** ($100/mo minimum + $0.01/render for an autonomous commercial
factory). Per the rule "if it charges a fee, drop it," **Remotion is ruled out** —
no further Remotion work, no `@remotion/*` dependency anywhere in SEOSONA Video.
HyperFrames (Apache-2.0, free) carries the entire render path.

## Why

Both engines share the **same render core** — seek each frame in headless Chromium, encode with FFmpeg, deterministic output. So render *quality* is not the deciding factor. The differences:

| | HyperFrames (heygen-com/hyperframes) | Remotion (remotion-dev/remotion) |
|---|---|---|
| Authoring | HTML/CSS + GSAP (what SEOSONA already builds) | React components (frame-driven) |
| License | **Apache-2.0 — free, no thresholds** | Source-available; **paid for 4+ employee companies** → autonomous factory = "Automators" tier **$100/mo min + $0.01/render** |
| Agent fit | Built for agents; LLMs emit HTML easily | React frame-driven is harder for LLMs |
| Captions | DIY (we use faster-whisper already) | Built-in Whisper word-timed captions |
| Migration | already integrated | **rewrite all HTML/GSAP scenes → React** (weeks) |

Migrating would mean **paying a license + a multi-week React rewrite for a render core we already have.** Not justified. If we ever want Remotion's captions, we already have `faster-whisper` (used in the repurpose SRT path) — no license exposure.

## Adopted hardening (done 2026-06-23, commit c9e9140)
1. **Killed the `npx --yes hyperframes@0.6.112` network dependency** — render now prefers the local `node_modules/.bin/hyperframes` binary (pinned in package.json); falls back to npx with a warning only if not installed. Run `npm install` to materialize it. *(Was: every render downloaded from npm mid-pipeline — an npm hiccup killed a run.)*
2. **Untracked the vendored `5_FRAMEWORK/hf_engine/`** (54MB, never executed by the render path) — kept on disk as reference, gitignored.

## Open recommendations (need an A/B render check before applying)
- **Upgrade 0.6.112 → 0.7.4** — newer line fixes real render bugs (timed descendants staying visible after a parent clip ends; sub-composition duration). No breaking changes reported. Re-pin in package.json + pipeline_manager `_HF_VERSION` after one comparison render.
- **Use the programmatic `@hyperframes/producer` API** (HTTP server / `createRenderJob`) instead of CLI subprocess — streaming progress, render queue, no per-video process spawn.
- **Adopt `@hyperframes/shader-transitions`** (13 WebGL transitions) + quality flags (`--quality high`, `--fps 60`, `--resolution 4k`, `--workers 4`).
- **For scale:** `--docker` (byte-identical reproducible renders → content-hash + skip-rebuild caching) and `@hyperframes/aws-lambda` / `gcp-cloud-run` to fan out many renders.

## Sources
- https://github.com/heygen-com/hyperframes (Apache-2.0, "Write HTML. Render video. Built for agents.")
- https://registry.npmjs.org/hyperframes (latest 0.7.4; pinned 0.6.112)
- https://www.remotion.dev/docs/license · https://remotion.pro/license (company-size license)
- https://github.com/remotion-dev/remotion
