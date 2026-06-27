# Motion Recipes for SEOSONA components (re-skinned from Open Design templates)

Three production HyperFrames templates from Open Design (`prompt-templates/video/`)
were dark-mode/neon. Below: their **motion ideas extracted and re-skinned to SEOSONA
light + brand palette**, mapped onto the 14 components in `native_composer.py`.

Brand constants used here: blue `#2A5BDA`, coral `#E2724D`, green `#16A34A`, ink
`#0F172A`, surface `#FFFFFF`/`#F8FAFC`. `acc` = the scene's rotated accent.
All examples are 9:16 (1080×1920) and respect the bottom ~160px safe zone.

---

## Recipe 1 — Money-Counter → enrich `bignum`

**Source:** `hyperframes-money-counter-hype` (deep-emerald, neon counter, money burst).
**Re-skin:** white canvas, accent-tinted radial glow, brand-color flash on landing.

The big number should not just fade in — it should **tick + pop + flash**:

```js
// counter ticks then pops on landing (replaces a plain fade)
const obj = { v: 0 };
tl.to(obj, { v: TARGET, duration: 1.6, ease: "power2.inOut",
             onUpdate: () => bignumEl.textContent = format(obj.v) }, st + 0.3);
tl.to("#bignum", { scale: 1.04, duration: 0.18, ease: "back.out(2)" }, st + 1.9);  // +4% pop
tl.to("#bignum", { scale: 1.0, duration: 0.4, ease: "power2.out" }, st + 2.1);
// brand-color flash on the landing frame (NOT neon — use the scene accent)
tl.to("#bignum", { color: acc, duration: 0.25, ease: "power2.out" }, st + 1.9);
tl.to("#bignum", { color: "#0F172A", duration: 0.6, ease: "power2.out" }, st + 2.2);
```

- **Visual weight** (`data-in-motion.md`): pair the number with a presence element —
  an accent-tinted radial glow behind it that grows `opacity 0.10 → 0.18` on landing,
  or a fill bar. A number alone "floats in empty space."
- Use `font-variant-numeric: tabular-nums slashed-zero` so digits don't jitter while ticking.
- **SFX:** keep the existing `impact_deep` cue on the landing frame (`st+1.9`), not the entrance.

---

## Recipe 2 — Social-Overlay-Stack → enrich multi-item components (`steps` / `feature` / `badges` / `stats` / `compare`)

**Source:** `hyperframes-social-overlay-stack` (4 cards entering in sequence).
**Key idea:** consecutive items must **NOT all enter the same way**. The template
alternates direction + ease per card. This is the fix for "everything slides up the same".

Re-skinned entrance choreography for a list of `.ritem`s (apply per index, not uniform):

```js
const ENTRANCES = [
  { x: -340, ease: "expo.out",     dur: 0.55 },  // from left, confident
  { y:   80, ease: "power3.out",   dur: 0.50 },  // from below
  { x: +340, ease: "expo.out",     dur: 0.55 },  // from right
  { scale: 0.9, opacity: 0, ease: "back.out(1.4)", dur: 0.6 }, // scale-pop
];
items.forEach((el, i) => {
  const e = ENTRANCES[i % ENTRANCES.length];
  tl.from(el, { ...e, opacity: 0 }, revealTimes[i]);   // revealTimes from _reveal_plan
});
```

- **Beat grid:** the template lands each card on a beat (90 BPM = 666ms). Our
  `_reveal_plan` interval (0.22–0.55s) already approximates this — keep reveal
  intervals on a consistent grid within a scene so reveals feel rhythmic, not random.
- **Readability scrim:** over busy backgrounds the template drops a 38%-opacity scrim
  on the bottom 32%. SEOSONA is light, so instead use a soft white card
  (`background:#FFFFFF; box-shadow: 0 8px 40px rgba(15,23,42,.10)`) behind list items.
- **Choreography = hierarchy** (`motion-principles.md`): order reveals by *importance*,
  not DOM order. The first item to move reads as most important.
- Keep the per-item `ui_pop` SFX already wired in `_sfx_cues` — one pop per reveal.

---

## Recipe 3 — TikTok-Karaoke → enrich karaoke + `talking_head` captions

**Source:** `hyperframes-tiktok-karaoke-talking-head` (word-synced captions, marker pop).
**Re-skin:** brand accent instead of `#ff5e3a`; white pill instead of dark.

Word-level treatment (improves on a plain karaoke fill):

```js
// chunk = 2–3 words, ≤28 chars/line, sits at y≈78% (above the 300px karaoke safe zone)
// each word enters, then the ACTIVE word color-flips on its own start frame:
words.forEach(w => {
  tl.from(w.el, { y: 24, opacity: 0, duration: 0.18, ease: "power3.out" }, w.start - 0.18);
  tl.set(w.el, { color: acc }, w.start);          // flip to accent exactly when spoken
  tl.set(w.el, { color: "#0F172A" }, w.end);      // back to ink when passed
});
// exit the whole chunk by clip-path inset wipe right before the next chunk
tl.to(chunkEl, { clipPath: "inset(0 0 0 100%)", duration: 0.12, ease: "power2.in" }, chunkEnd);
```

- **Emphasis words** (numbers, the one key term): use a marker-highlight from
  `css-patterns.md` — the **highlight sweep** re-skinned to an accent-tinted bar
  (`background: acc; opacity:.18`) sweeping `scaleX 0→1`. Cycle modes every 3–4 chunks
  for variety (highlight → circle → sweep), per `css-patterns.md`.
- **Numbers** get a clip-path "slam" instead of a fade — reads as impact.
- **Lower-third name plate** (the `yt-lower-third` idea): a brand pill that slides in
  `x:-360→0 expo.out 0.7s` mid-clip to show "SEOSONA · <topic>", holds 4s, exits. Good
  for the talking-head engine's speaker label.
- **Non-negotiable from the template:** captions never overlap and never run off-frame.
  This matches our existing single-track-3 karaoke rule ([[master-video-spec]]).

---

## Cross-cutting upgrades (from `motion-principles.md` + `house-style.md`)

Apply to **every** scene, not just the three above:

1. **Never start at t=0** — offset the first tween 0.1–0.3s (zero-delay = jump cut).
2. **Vary the ease** — no more than 2 tweens share an ease per scene. `.out` for
   entrances, `.in` for exits, `.inOut` for moves-between.
3. **Asymmetry** — entrances ~0.4s, exits ~0.25s (faster). Our transition exit at
   `nxt-0.33` already does this; keep it.
4. **Background depth** — every light scene still needs 2–3 ambient decoratives:
   accent-tinted radial glow (low opacity, breathing scale), oversized ghost word at
   4–6% opacity drifting, a hairline rule pulsing. Static = "nothing loaded".
5. **Two focal points minimum** — never a single text block centered in empty space;
   anchor content to an edge + add an accent element (label, data bar, divider).
6. **Build / breathe / resolve** — stagger reveals in the first 30%, ONE ambient motion
   in the middle 40%, decisive exit in the last 30%. Don't dump everything at once.

Related: [[master-video-spec]] · `SEOSONA-INDEX.md` · `7_ASSETS/brand/SEOSONA/DESIGN.md`
