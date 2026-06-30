# LLM Coding Discipline — how the agent works on SEOSONA

Behavioral guardrails for any LLM (Claude here, or an agent) writing/editing SEOSONA code or
docs. Adopted from **multica-ai/andrej-karpathy-skills** (MIT), itself from Andrej Karpathy's
notes on LLM coding pitfalls. Reinforces the rules the team already enforces (no-bloat,
no-fakes, verify, surgical). Trades speed for caution — for trivial edits, use judgment.

## 1. Think before coding
Don't assume; don't hide confusion; surface trade-offs.
- State assumptions; if uncertain, ASK (don't pick an interpretation silently).
- If multiple readings exist, present them. If a simpler path exists, say so — push back when warranted.
- If something's unclear, STOP and name what's confusing.

## 2. Simplicity first
Minimum code that solves it. Nothing speculative.
- No features beyond what was asked; no abstractions for single-use code; no "flexibility" nobody requested.
- No error handling for impossible cases. 200 lines that could be 50 → rewrite.
- Test: "would a senior engineer call this overcomplicated?" → simplify. (This is the no-bloat rule.)

## 3. Surgical changes
Touch only what you must; clean up only your own mess.
- Don't "improve" adjacent code/comments/formatting; don't refactor what isn't broken; match existing style.
- Remove only the imports/vars/functions YOUR change orphaned. Pre-existing dead code → mention, don't delete (unless asked).
- Test: every changed line traces directly to the request.
- **Mark deliberate shortcuts** (from `DietrichGebert/ponytail`, MIT) with a greppable tag + upgrade trigger, e.g. `# TODO(seosona): naïve heuristic — profile before optimising`. A tagged shortcut is a tracked decision; an untagged one is silent debt that rots. Harvest with `grep -rn "TODO(seosona)"` into [`UPGRADE_BACKLOG.md`](UPGRADE_BACKLOG.md).

## 4. Goal-driven execution
Define success criteria; loop until verified.
- "Add X" → "write the check for X, then make it pass." Turn vague tasks into binary, verifiable goals.
- Multi-step → state a brief plan with a `verify:` per step. (This is our verify-before-claim rule —
  see [`SELF_IMPROVEMENT_LOOP.md`](SELF_IMPROVEMENT_LOOP.md) stage 7 + the persona Execution Contracts.)

> These pair with the persona **Execution Contracts** (researcher/scout/security-auditor/
> capability-analyst) and the SIL hard rules. When in doubt: think → simplest → surgical → verify.
