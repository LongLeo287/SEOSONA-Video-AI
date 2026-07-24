# Talking-Head Craft Study — 22 reels (2026-07-16)

Deep frame-level analysis of `D:\SEOSONA AI\data\video talking heads` (22 videos, 3 analyst passes + main-agent frame verification). Parts: `TH_CRAFT_part1/2/3.md`. Frames: `scratchpad/th_frames/` (150 frames + contact sheets). Goal: extract the REAL talking-head edit craft → a brand-adapted MODE LIBRARY for the V2 native renderer.

## The single biggest correction to our V2 samples
Our first V2 samples used a **frosted lower-third** caption. The real high-craft VN reels DON'T: the dominant caption sits **at chest/mic level (~y 55-62%)**, 2 lines, **line-1 white + line-2 accent**, heavy black outline, **no box** — deliberately at the torso so it never collides with the face/mouth/mic. This is the #1 portable pattern and should be the DEFAULT talking-head caption. (The real reels highlight in yellow/mint/green per creator; we translate the STRUCTURE to brand coral/blue.)

## Verified craft (main-agent confirmed by eye)
- **Chest-level 2-line karaoke** (g1_1 Khánh): white line + accent line, bold condensed, thick outline, no box, at the mic.
- **Top-headroom bracket card + bottom highlighter-box karaoke** (g1_2 Hermes): neon corner-bracket title card in the headroom; caption = black pill with ONE keyword in a filled accent box.
- **Shrink-speaker-to-inset + numbered checklist/progress-bar on a brand stage** (g2_3 CEO AGENT): speaker boxed into a rounded inset; structured graphics live above; graphics never touch the face.
- **Speaker-in-a-framed-card on a solid color stage** (g3 UUID set): captions structurally collision-proof.

## CRITICAL foundation — subject auto-reframe (user requirement 2026-07-16)
Source talking-head footage rarely has the subject centered (e.g. `front_916.mp4` = speaker frame-RIGHT). V2 MUST **detect the subject and reframe** so the person sits where the mode wants — **centered by default**, or deliberately off-center (leaving the opposite side clear) for card/bignum modes. Method: rembg subject matte → bounding box → compute a crop+scale+pan transform to the mode's target x, applied via ffmpeg (stable center; if the subject drifts, sample the matte a few times and use a smoothed center, never a per-frame jitter). This runs BEFORE compositing overlays. Without it the whole layout system breaks (captions/cards are placed relative to a subject that isn't where the layout assumes).

## Cross-cutting principles (all 22)
0. **Subject centered/placed first** (see above) — reframe before anything else.
1. **Face band is sacred** — every good reel keeps a clean zone over face/mouth/mic. Three solutions: caption-at-chest, graphics-in-headroom, or shrink-speaker-to-inset.
2. **Exactly ONE accent keyword per caption cue** — the most templatable discipline (creator signature: yellow / mint / orange / green). → V2 = coral (or blue) on one keyword.
3. **Three legibility substrates, pick by background busyness**: no-box + heavy outline/shadow (clean bg) · dark frosted scrim pill (medium) · filled highlighter box on keyword (busy/loud).
4. **Topic-matched prop/icon per beat** — keyword→icon mapping makes it feel produced (toggles=hand-tracking, gauge=speed, atom=physics, ✓/✗ tiles for yes/no).
5. **Structured info-graphics** replace b-roll for "technical" credibility: numbered checklist + progress bar, icon-tile bulleted panels, spec tables, data-readout HUD.
6. **Big-word kinetic** for a single key token (oversized two-tone number + underline); behind-speaker occlusion looks premium but COSTS readability — use sparingly, or off-center the speaker.

## Proposed V2 talking-head MODE LIBRARY (brand-adapted: Be Vietnam Pro + #2A5BDA/#E2724D)
| Mode | Structure (learned) | Brand adaptation | Face-safe by |
|---|---|---|---|
| **TH-Chest** (DEFAULT) | 2-line chest karaoke, white + accent line, no box | coral accent line; Be Vietnam Pro Black | caption at chest |
| **TH-TopCard** | headroom bracket/step card + clean face + chest karaoke | blue card + coral tick; frosted not neon | card in headroom |
| **TH-Highlighter** | black caption pill + one keyword in filled box | coral filled box on keyword | at chest |
| **TH-Inset** | shrink speaker → rounded inset on brand stage + checklist/progress above | blue/coral stage, coral progress | speaker boxed |
| **TH-Stage** | speaker framed on solid brand color stage + props | brand stage + brand props | speaker framed |
| **TH-Bignum** | oversized two-tone number + ✓/✗ icon-tiles for a stat beat | blue number + coral underline | off-center speaker |
| **News-Stack** (faceless) | full-screen b-roll + kicker pill → headline → numbered list → caption | one coral accent, blue structure | no face (faceless) |
| **Tutorial-Split** | full-width screen-rec band OR 40/60 split, caption on top | brand chrome around screen-rec | screen band separate |

These BLEND per beat within one reel (hook=Bignum/TopCard, tips=Chest, list=Inset, stat=Bignum) — the "phối nhiều kiểu" the user asked for. Every mode: Be Vietnam Pro + brand colors ONLY; ≤2-word (or 2-line) captions; one accent keyword; face band protected.

## Honest notes
- The UUID clips (g3 + g2 V4-7) are a "one script → many looks" showcase / AI-styled b-roll, not all authored reels — high value as look-references, flagged in the parts.
- Real reels use yellow/mint/green highlights; we deliberately re-map to brand coral/blue (learn craft, keep brand — per the user rule "màu + font = brand").
- Behind-speaker occlusion (balloon/rotoscope/bigword) = premium but readability-costly; gate it to short hook beats.
