# Loop Engineering — knowledge + SEOSONA self-audit

Ingested 2026-06-29 from **mduongvandinh.github.io/loop-engineering-phan-tich** (Addy
Osmani / Boris Cherny / Peter Steinberger synthesis). The discipline of building a
**self-operating system that prompts the agent**, instead of prompting it yourself — and
doing so without letting unattended loops amplify errors. Directly governs SEOSONA's
Phase 3–6 loop (queue → daily → feedback).

## The framework (cheat-sheet)

**Four-layer stack** (error cost multiplies upward): Prompt → Context → Harness → **Loop**.

**Five-move pattern** every iteration: ① Scheduling → ② Discovery → ③ Handoff →
④ Verification → ⑤ State persistence. Skip one = the loop breaks.

**Six components:** Automations · Worktrees (isolation) · Skills (permanent
knowledge) · Connectors (MCP) · Sub-agents (generator≠evaluator) · Memory (state on disk).

**Five anti-patterns** (= skipping a move): Nodding loop (no verify) · Amnesiac (no state) ·
Manual (no schedule) · Blind (no discovery) · Tangled (no isolation).

**Generator / Evaluator (maker-checker):** the writer can't fairly judge its own work
("nodding loop" bias). An *independent, skeptical* evaluator assumes the output is broken,
judges **behavior not intent**, and validates by *execution*. A smaller/faster model decides
success — never the generator.

**Four silent debts:** Verification debt · Comprehension rot · Cognitive surrender ·
**Token blowout** (a bug → runaway retries → huge bill).

**Three disciplines:** read a representative SAMPLE daily (explain each change) · set hard
CEILINGS before shipping (circuit breakers, not cost-saving) · leave a DOOR open (a
structural human-review checkpoint).

**First-loop checklist (6):** discovery source · state file · evaluator that can say "no" ·
isolation per parallel task · token ceiling · human-review step. *First two make it run;
the other four stop it causing harm. Add parallelism only after a single agent can be
stopped by the evaluator.*

> Closing law: "the loop mirrors its builder — bring understanding, it amplifies
> understanding; bring negligence, it amplifies negligence."

## SEOSONA self-audit (where we stand · 2026-06-29)

Our loop = `scripts/daily_production.py` → `scripts/queue_processor.py` → `9_DASHBOARD/feedback_loop.py`.

| Checklist item | SEOSONA today | Gap |
|---|---|---|
| ① Scheduling | ✅ daily_production + schtasks + autostart | — |
| ② Discovery | ⚠️ queue is human-filled (+ `--news` file) | no auto-discovery skill |
| ③ Handoff | ✅ queue per-item | sequential (no worktree — OK while single-threaded) |
| ④ Verification | ⚠️ `quality_scorer` (technical integrity, in-process) | **not an independent, skeptical evaluator** |
| ⑤ State | ✅ `.processed_ledger`, `events.jsonl`, `run.jsonl`, `feedback_state.json` | — |
| Token/cost ceiling | ❌ retries+timeout exist, but **no run/day budget or kill-switch** | **biggest safety gap** |
| Human-review door | ✅ publish is opt-in (`SEOSONA_PUBLISH`); nothing auto-publishes | keep it |

**Silent-debt exposure:** Token-blowout = free/local so cost≈0, but **render-time runaway /
infinite-retry IS a real risk** → needs a circuit breaker. Verification-debt = the scorer
isn't an independent skeptic → an evaluator gate would harden it.

## What we're building from this (priority)
1. **Circuit breaker** (`scripts/loop_guard.py`) — bounded risk: max items/run, max retries/day,
   max wall-time, kill-switch file. *(ceiling + token-blowout guard)*  → **built**, see SOP.
2. **Operating SOP** (`6_SOP/LOOP_OPERATING_SOP.md`) — the three disciplines applied. → built.
3. *Next:* independent **evaluator** gate (moderation — skeptical, judges the actual MP4) +
   auto-**discovery** skill (scan sources) + content-moderation (no fabricated claims/brand-safe).

Related: [[product-roadmap]] · [[design-system-and-craft]] · `9_DASHBOARD/README.md`
