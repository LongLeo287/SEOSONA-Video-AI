# V2 OS (orchestrator) vs Loop Engineering — audit + hardening plan

The OS is the foundation: if the autonomous loop isn't world-class, the factory can't be. Loop
Engineering (cobusgreyling, MIT, ~7.9k★ — already ingested in legacy as `loop_guard` +
`LOOP_OPERATING_SOP` + `2_KNOWLEDGE/loop-engineering/`) is the discipline for reliable unattended
loops. This audits V2's `services/orchestrator` against its full principle set.

## Already COVERED in V2 (ported from the legacy ingest — the OS is not starting from zero)
| Loop Engineering principle | V2 orchestrator |
|---|---|
| Phased rollout L1→L2→L3 (report → assisted → unattended) | `policyEngine` autonomy L0–L3 ✅ |
| Ceilings / circuit breaker (stop runaway) | `circuitBreaker` (consecutive-failure / duration / spend) ✅ |
| Kill-switch | `FactoryPolicy.kill_switch` + STOP semantics ✅ |
| Per-item isolation + dead-letter | `queue` (`InboxQueue`) ✅ |
| Budget ceiling | `FactoryPolicy.budget.max_videos_per_day` ✅ |
| Human gates (approval) | Decision gate (release needs approval; core needs benchmark) ✅ |
| State/Memory (durable records outside chat) | `knowledge/memoryStore` + event ledger ✅ |
| OODA loop | `factoryTurn` ✅ |

## GAPS to close so the OS is XỊN (strengthening plan)
| Loop Engineering principle | Gap in V2 | To build |
|---|---|---|
| **Cost forecasting (`loop-cost`)** | V2 has budget CEILINGS but no pre-run token/GPU **cost estimate** or per-turn cost TRACKING | `costModel.ts`: estimate a turn's cost before running + track actual spend per turn; enforce against `FactoryPolicy.budget`; surface in the TurnReport |
| **Observability + readiness score + drift (`loop-audit`)** | `telemetry` is a no-op scaffold; no "is it safe to run unattended?" score, no output-quality drift detection | `loopAudit.ts`: a readiness score (ceilings sane · kill-switch reachable · checker wired · budget set) + drift detection over the metrics ledger (quality trending down → trip) |
| **Maker/checker sub-agent split (verification ownership)** | QA exists (evaluator/qaWorker) but the loop doesn't ENFORCE that every unattended output is independently verified before it counts | make the OODA `Act` require a checker pass (qaWorker) before a job is `done`; "unattended loops make unattended mistakes" — no self-approval |
| **Denylist/allowlist + scope restriction** | `FactoryPolicy` has no explicit action/tool/domain allowlist | add `policy.allow`/`policy.deny` (which actions the loop may take, which tools/domains) enforced in the turn |
| **Pre-run readiness gate (first-loop checklist)** | legacy had a manual checklist; V2 has no codified pre-unattended-run gate | `readinessGate.ts`: refuse to start an unattended run unless ceilings/kill-switch/cost-estimate/checker are all green (the checklist as code) |
| **Worktree isolation for parallel builds** | `runContext` isolates run dirs; no git-worktree isolation for parallel Builder runs | optional: worktree-per-build (defer; run-dir isolation suffices for v1) |

## Verdict on the repo itself
Loop Engineering = **REFERENCE/EXTRACT** (MIT). Already ingested in legacy; the V2 action is to
close the gaps above in `services/orchestrator`, not re-vendor. Its npm CLIs (`loop-cost`,
`loop-audit`) could be shell-out tools for the cost/observability gaps if reimplementing isn't worth
it — decide during the build (RAP-style: extract the principle, or adapt the CLI).

## Sequencing
Runs AFTER the RAP-hardening agent lands (both touch the same repo; no parallel commits). The
connectivity audit (task #16) and this OS hardening are the two things that make the OS trustworthy
enough for a real unattended factory.
