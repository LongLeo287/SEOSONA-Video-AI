# 🏭 SEOSONA Video — Autonomous Self-Improving Factory (NORTH-STAR)

*Created 2026-06-29. The single blueprint for turning SEOSONA Video from a video
**tool** into a video **factory** that runs unattended and gets better over time.*

> Companion docs: `MASTER_OPERATION.md` (production steps), `PRODUCT_ROADMAP.md`
> (phases), `SEOSONA_VIDEO_AUTONOMOUS_TEMPLATE_FACTORY.md` (HyperFrames production
> rules). This doc owns the **autonomy + self-improvement loop** they don't cover.

---

## 0. Vision & principles

A factory that: takes a goal → decides what to make → produces it → publishes →
measures real-world response → learns → makes the next batch better. No human in
the inner loop; humans set strategy + guardrails.

**Hard principles (do not violate):**
1. **ONE engine per job** — no parallel/overlapping systems (the rule that retired
   `pipeline_manager`). New machines *reuse* existing ones, never duplicate them.
2. **Closed loop or it doesn't count** — every output must produce a measurable
   signal that feeds the next decision. A report nobody acts on is dead weight.
3. **Guardrails before autonomy** — QA gate + publish approval + budget caps are
   mandatory; autonomy is *graduated*, not all-at-once.
4. **Real-world feedback drives change** — internal quality score is necessary but
   NOT sufficient; views / CTR / retention decide what wins.

---

## 1. The factory as a system

```
   ┌──────────────────────────── FACTORY BRAIN (orchestrator) ───────────────────────────┐
   │                                                                                       │
   │   PLAN ──▶ PRODUCE ──▶ QA ──▶ PUBLISH ──▶ MEASURE ──▶ LEARN ──┐                       │
   │    ▲                                                          │                       │
   │    └──────────────────────────────────────────────────────── ┘  (OODA, closed)       │
   └───────────────────────────────────────────────────────────────────────────────────-─┘
     OBSERVE        ORIENT            DECIDE              ACT
   real metrics   analyze+learn   pick topics/variants  enqueue+produce+publish
```

| Stage | What it does | Component (✅ built / ⚠️ needs creds) |
|---|---|---|
| **PLAN** | pick topics + template + variants for the next batch | ✅ `.agents/skills/factory-strategist` + trend_jacking/scraper |
| **PRODUCE** | render the videos | ✅ `video_engine → native_composer` (+ talking-head) |
| **QA** | gate quality before publish | ✅ `4_BRAIN/quality_scorer.py` |
| **PUBLISH** | post to YT/TikTok/FB/Drive | ⚠️ `publisher_agent` — built & gated, **needs creds (Phase 4)** |
| **MEASURE** | pull real performance back in | ✅ `analytics_feedback_agent/performance_ingest.py` (⚠️ live fetch needs creds) |
| **LEARN** | turn metrics into decisions | ✅ `factory_ledger.py` + `analytics_feedback_agent` (re-grounded) |
| **ORCHESTRATE** | run the whole loop unattended | ✅ `4_BRAIN/factory_brain.py` (cron-ready) |
| **TAG** | tie each video to its variant | ✅ `4_BRAIN/production_manifest.py` (keystone) |
| **QUEUE (reliability)** | batch with retry/timeout/idempotency | ✅ `scripts/queue_processor.py` |

> **Status 2026-06-29:** the loop is BUILT and runs end-to-end on the QA signal
> (`factory_brain.py --dry-run` verified). Two integrations remain credential-gated:
> live **PUBLISH** and live **MEASURE** (Phase 4 — add `1_CONFIG/credentials/*`).
> Until then the ledger learns from the QA score and auto-upgrades to real metrics
> the moment they land (no code change).

---

## 2. Current state — honest

**Works (production line is real):** `queue_processor.py` (crash-isolated batch),
both engines, `quality_scorer`, 11 agents, hermes telegram remote, 26 SOPs.

**Feedback — the accurate picture (corrected 2026-06-29):** what was retired is the
heavyweight `pipeline_manager` engine. `workflow_router` still wraps the NEW
`video_engine` in a *lightweight* `graph_executor.SuperGraph` whose `evaluate_node`
DOES call `analytics_feedback_agent.feedback_generator` — so a post-mortem already
runs for the `video:news` / `video:course` paths (it was never fully dead).
Two real gaps remained: (a) the GitHub one-shot `make:video` bypasses
`workflow_router`, so it got no feedback; (b) there was no cross-video LEARNING
(each post-mortem was standalone). This north-star fixes both: `feedback_generator`
now also accepts a produced project dir, and `factory_brain` tags every video
(`production_manifest`) + aggregates them (`factory_ledger`) regardless of entry path.
`factory_brain` is the consolidated loop going forward; `workflow_router.evaluate_node`
stays as the inline per-render hook.

**Now built (2026-06-29):** real-world performance ingest (creds-gated), the learning
ledger that biases production (`factory_ledger.py`), the orchestrator loop
(`factory_brain.py`), and graduated-autonomy guardrails (`factory_policy.yaml`).
What remains is **credentials** (live publish + metrics) and **cron** — see §7.

---

## 3. The self-improving loop (core design)

### OBSERVE — performance ingest
Pull per-video metrics (views, CTR, avg-view-duration/retention, likes, comments)
from each platform's analytics API → write to `3_MEMORY/performance/<video_id>.json`.
Key: every produced video carries a stable `video_id` + its **variant tags**
(template, hook style, title pattern, thumbnail style, length bucket, voice).

### ORIENT — learning
Aggregate performance by variant tag → `3_MEMORY/learning/ledger.json`:
"which template / hook / title pattern / thumbnail style / length / topic wins,
by KPI, with confidence". This is the factory's memory of what works.

### DECIDE — strategy
A strategist turns the ledger into the next batch: topics worth making (trend ×
past performance), the template/variant mix (exploit winners + explore new), and
A/B variants to test. Writes to `0_INPUT_INBOX/production_queue.yaml`.

### ACT — produce & publish
`queue_processor.py` produces; `publisher_agent` publishes (behind the approval
gate); each output is registered with its variant tags so the loop can close.

---

## 4. Component blueprint (lean — reuse first)

| # | Machine | New artifact | Reuses | Role |
|---|---|---|---|---|
| 1 | **Factory Brain** | `4_BRAIN/factory_brain.py` | queue_processor, engines | Runs PLAN→…→LEARN unattended; cron-triggered |
| 2 | **Performance ingest** | extend `analytics_feedback_agent` (`performance_ingest.py`) | publisher creds | OBSERVE: metrics → `3_MEMORY/performance/` |
| 3 | **Learning ledger** | `3_MEMORY/learning/ledger.json` + `3_MEMORY/learning/template_weights.json` | quality_scorer history | ORIENT: variant → KPI memory |
| 4 | **Strategist** | `.agents/skills/factory-strategist/SKILL.md` | trend_jacking, scraper, ledger | DECIDE: next-batch plan → queue |
| 5 | **Variant tagging** | `production_manifest.json` per output | native_composer/make_video | Ties each video to its template/hook/thumbnail/length/voice |
| 6 | **Guardrails** | `1_CONFIG/factory_policy.yaml` | — | Approval gate, budget caps, kill switch |

No new render engine, no new queue, no new agent that duplicates an existing one.

---

## 5. How it actually learns (self-improvement mechanics)

- **Template selection** is weighted by `3_MEMORY/learning/template_weights.json`
  (winners get picked more; losers decay) — strategist reads it instead of round-robin.
- **Hook / title / thumbnail** run as tagged A/B variants; outcomes recorded by
  variant; winning patterns promoted into the default set, losers retired.
- **Length & pacing** tuned from retention curves (where viewers drop off).
- **Topic choice** = trend signal × past topic performance (exploit + explore).
- **Voice** (e.g. Chí Quyết clone vs others) compared by retention/engagement.
- **Explore/exploit**: a fixed % of each batch is exploration so the factory keeps
  discovering, not just over-fitting yesterday's winner.

---

## 6. Guardrails (graduated autonomy)

| Level | Publish | Human role |
|---|---|---|
| **L0 (now)** | nothing auto-publishes | review every output |
| **L1** | auto-produce + auto-QA; publish needs 1-click approve (telegram) | approve/reject |
| **L2** | auto-publish if QA score ≥ threshold AND within daily cap | spot-check + set strategy |
| **L3** | full loop incl. topic selection; human sets goals + guardrails only | strategy + audit |

Always-on: **QA gate must pass**; **budget/rate caps**; **no secrets in tracked
files**; **brand law** (light-mode, approved voice); **kill switch** (one flag halts
the loop); **every auto-action logged**.

---

## 7. Build plan (mapped to PRODUCT_ROADMAP phases)

| Step | Builds | Status |
|---|---|---|
| A | Variant tagging (manifest) + re-ground feedback on `video_engine` | ✅ DONE 2026-06-29 |
| B | Factory Brain orchestrator (`factory_brain.py`) + guardrails, L1 | ✅ DONE 2026-06-29 |
| C | Performance ingest (real metrics) | ⚠️ scaffold DONE; live fetch needs creds (Phase 4) |
| D | Strategist + learning ledger → template weighting | ✅ DONE 2026-06-29 |
| E | Dashboard observability + graduate to L2/L3 | ⬜ next |

**Remaining to "fully autonomous":**
1. **Credentials** (`1_CONFIG/credentials/*`) → flips on live PUBLISH + MEASURE so the
   ledger learns from real views/CTR/retention, not just QA.
2. **Cron** the loop (`4_BRAIN/factory_brain.py`) for unattended turns.
3. **Dashboard** (Step E) to watch cohorts improve + graduate L1→L2→L3.
4. **Strategist** runs each turn to fill the queue from ledger + trends (skill ready).

---

## 8. Success metrics (is the factory improving?)

Throughput (videos/day), QA pass-rate, **trend** of avg views / CTR / retention
per cohort, cost per published video, % autonomy (human touches per video → 0).
The factory is "self-improving" only when the performance trend rises across
cohorts with human touches falling.

---

## 9. Open decisions (need the user)

1. **Publish credentials** + which platforms first (gates OBSERVE).
2. **Autonomy level** to target first (recommend L1: auto-make, approve-to-publish).
3. **Analytics access** (YouTube Data/Analytics API, TikTok, FB) for real metrics.
