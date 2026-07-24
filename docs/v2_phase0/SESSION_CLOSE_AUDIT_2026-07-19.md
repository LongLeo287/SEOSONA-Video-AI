# SEOSONA Video AI V2 — Session-Close Audit (2026-07-19)

Four parallel evidence-based audits (render engines / director+craft / OS+agents+tests / branch hygiene).
Main tip green: **tsc exit 0, 1397/1397 tests** (when the factory loop is quiescent).

## THE UNIFYING FINDING
**"Built but NOT wired to the shipping path" is the dominant defect class.** Repeatedly, a correct capability
exists in a standalone script or a branch or a package, and the WIRED production engine / pipeline never calls it.
The no-orphan guarantee (the mechanism meant to prevent exactly this) has scope blind spots. Fixing V2 next
session is mostly WIRING, not building.

## HIGH

1. **Pixel-measurement discipline is not wired.** `scripts/lib/richness.py` correctly DECODES real frames
   (novelty vs frame−2s) — it's the CURE for the "measure the plan not the pixels" class — but has **ZERO
   callers**; `promo-v7-procedural.mjs` only ffprobes container metadata. `varietyGate` (director.mjs:1182)
   scores the PLAN object, never decoded pixels. And `CRAFT_STUDY.md` (the 62-video frame study) is **orphaned
   in the legacy repo — no V2 file references it**. FIX: call richness.py after mux() and fail on frozen_run>0;
   port CRAFT_STUDY into V2 as a tracked backlog; wire its 8 laws/constants into the director.

2. **Colour-correct encode + self-drawn-only are NOT on the WIRED engine.** `encode.mjs` (bt709 convert+tag)
   is imported only by standalone promo scripts; the production `nativeRenderAdapter.ts` encodes bare libx264
   with **no colorspace tags → ships `color_space=unknown`** (the exact CapCut wrong-colour bug we "fixed" —
   fixed only for the scripts). Same file still composites **real Pexels stock** (:2661) + user b-roll; the
   no-external-asset assert lives only in `full-film-engaging.mjs:200` (branch), and `proof-cut-engaging.mjs`
   still injects the user's E:\ 3D renders. FIX: run RGB→BT709 + tag in nativeRenderAdapter's encoders; add a
   self-drawn-only assert in `renderTimeline`; quarantine subjectComposite.mjs + proof-cut-engaging.mjs.

3. **~10 workers built + tested but dispatched by NOTHING.** `subtitleStylistWorker, scenePlannerWorker,
   templateArchetypeWorker, assetIndexWorker, assetSourcerWorker, musicSfxWorker(+emphasisPlanner),
   analyticsWorker, reporterWorker, packagingSpec` — each exported from `services/workers/src/index.ts` + its own
   test, zero runtime consumers; `compose.ts`/`buildTimeline`/`daemon` call none. The OODA Observe leg is the
   concrete casualty (nothing produces the snapshots `deriveLearnings` consumes). ROOT CAUSE: the no-orphan
   audit (`os-audit/registryAudit.ts`) checks registry membership + 6 named symbols, but **nothing audits worker
   DISPATCH**; dependency-cruiser treats barrel re-export as "reachable". FIX: add a Layer-2d worker-dispatch
   check; wire the intended stages into compose.ts or mark `planned`.

4. **The engaging-film capability + 3 more branches are stranded off main.** `git`: `claude/engaging-full-film`
   (+27/−3, the whole self-draw + glow + karaoke engine), `claude/integrated` (r-series superset), 
   `claude/cqa-voice-clone` (voice), `feat/phase-a-composition-root`. None on main. FIX (pause the factory loop
   first — no STOP present): consolidate the 4; then prune ~30 merged/dead branches + their worktrees.

## MEDIUM

5. **Roster overstates integration.** `roster.ts`: `seo_optimizer` "built" but 0 dispatch; `analytics_feedback`/
   `reporter` "partial" but 0 dispatch. `auditAgents` only checks the bound file EXISTS, not that it's called.
   Redefine "built" = "dispatched by a composition root", downgrade the three.

6. **Brand palette duplicated in 4+ private literal copies past the guard.** `karaokeAss.mjs:75` inlines hexes
   (incl. non-brand navy `#0A2E7A`) with no brand.mjs import; `glowStage.mjs` inlines rgba() brand colours;
   card markup duplicated between fades-path and animated authors in nativeRenderAdapter. The guard only compares
   brand.mjs↔brandKit.ts. FIX: an rgba() helper from BRAND.*; import brand.mjs into karaokeAss; single shared
   card-markup builder.

7. **Beat→subject variety is HAND-AUTHORED, not engine-picked.** `pickDrawnSubject` (drawnSubjects.ts) is
   called only by its test; the film hardcodes subject.kind per scene in filmPlan.mjs. "The engine picks a varied
   style per beat" is NOT true yet — wire the director or state it's manual.

8. **`statement` still the universal failure sink** (mitigated not closed): every degrade collapses to statement;
   unreachable density floor only REPORTS rather than fails.

9. **Test suite non-deterministic under the live loop.** A run caught the loop mid-edit of `compositor.ts`
   (1 fail with escaped-comma source that exists nowhere); isolated re-run 10/10, full re-run 1397/1397. FIX:
   gate npm test/audits behind the loop STOP; commit/stash the compositor edit; remove stray `pl/` dir.

10. **`spec_lint` (the craft-pack enforcing gate) does not exist.** SAFE_ZONES ~14 rules TODO (the corrected
    9:16/16:9 boxes), COMPLIANCE loudness/AI-disclosure/no-fabrication all TODO; several "WIRED" seams point at
    legacy `scripts/lib/*.mjs`, not the V2 render path. The guardrails a shipped video relies on are docs, not
    code. FIX: minimal spec_lint pre-render gate in qaWorker (safe-zone + loudness first); re-point seams to V2.

## LOW
- Type-scale target 2.5 (director.mjs:761) vs CRAFT_STUDY measured **4–6:1** → engine can pass while flatter than every reference.
- Stale `glowStage.mjs:124` bakes FABRICATED specifics ("tăng traffic 300%") vs NO-FABRICATION (newer drawnSubjects softened).
- `drawnSubjects.mjs:161` ignores `spec.items` → silently drops director content (feedstack).
- `alignCaption.mjs:119` quietly interpolates meaningless caption times on empty ASR (return [] instead).
- richness.py docstring cites regression tests that don't exist; type-collision `\btin\b` substring risk if director activated; dead `brollProcedural` var; NATIVE_COLORS neutrals not shared tokens.
- Auto-update's asset "auto-land" path is never emitted by the CLI (only the test injects it) — reword or wire the sourcer land.

## GENUINELY SOUND (credit where due — verified, not issues)
- `seek_capture.py` (no N-identical stills, raises on empty), `sfxBed.mjs` (peak-align + probe-real-encode limiter + assertNoRepeats) — exemplary, fail-honest.
- **Auto-update code-apply boundary HOLDS and cannot be bypassed** — `assertBoundary` throws on code/policy+auto over every registry entry at load; CLI stops at a RAP-verdict proposal, never writes fetched code. 15 hermetic tests incl. the two refusals.
- **OS↔Factory maker/checker seam is real** — factoryTurn never imports the engine, records honest blocked_on, no render→done path skips the independent checker; compose builds maker+checker from different seams.
- **Live-leg tests render REAL mp4s** and assert audio-fingerprint preservation through re-encode — anti-"assert-the-plan" discipline present at the render boundary.
- `breakMonotony` no longer dead-by-construction; `assertOfferSurvives` checks substance; `validateAndRepair` refuses to pad; `plan_inputs_hash` cache-bust correctly wired.

## RESCUED THIS SESSION (don't lose)
- Newest full-bleed render → `store/MAU_DUNG_BRAND/full-film_fullbleed_NEW.mp4` (durable).
- Uncommitted full-bleed engine (composition.ts/.mjs framing-picker + edits) → commit `54dc9a1` on `claude/engaging-full-film-fullbleed`.
