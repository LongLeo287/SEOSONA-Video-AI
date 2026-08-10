# SEOSONA Unified BrandKit V1 Verification Receipt

**Date:** 2026-08-10

**BrandKit version:** 1.0.0

**Logical reference:** `seosona-brand://video/SEOSONA/brand-kit.v1.json`

## Provenance

- Canonical BrandKit SHA-256: `4ecb0a7ac2d49c65d96739f2fa31492863c716b477868b130142c482d289a927`
- Canonical asset manifest SHA-256: `0cf49d370c9fc30fba29954458d7a25d5efbd48b6de640336500d424612b14cc`
- Verified assets: 48
- Inventory: primary logo, six Be Vietnam Pro production fonts, named mascot
  catalog and 20 pose files, 15 SEOSONA carousel references, and five Chí
  Quyết Academy reference-only carousel files.

All manifest paths are repository-relative. Academy assets are inventory-only
and cannot enter the production allowlist.

## Verification gates

| Surface | Command | Result |
|---|---|---|
| Video contract | `node --test tests/brand-kit-contract.test.mjs` | PASS — 7/7 |
| Video asset gate | `npm run brand:validate` | PASS — 48 assets, zero errors |
| Video project connection | `npm run seosona:doctor` | PASS |
| OS reference contract | `node --test 3_MEMORY/projects/seosona-content/facebook-group-factory/brand-reference.test.mjs` | PASS — 5/5, including live Video file |
| OS live digest | `node 3_MEMORY/projects/seosona-content/facebook-group-factory/validate-brand-reference.mjs --brand-kit-file "$env:SEOSONA_BRAND_KIT_FILE"` | PASS |
| OS project connection | `npm run seosona:doctor` | PARTIAL — capability bridge, manifest, memory, portable `AGENTS.md`, Git remote, and npm script pass; pre-existing `.clauderules` and `.cursorrules` are absent |
| Content Factory | `npm test` | PASS — 23/23 |
| Content dependency audit | `npm audit --omit=dev` | PASS — 0 vulnerabilities |
| Content project connection | `npm run seosona:doctor` | PASS |
| Flow static gate | `npm run check:static` | PASS — 540 JavaScript and 22 JSON files plus HTML resources |
| Flow MCP contracts | `node --test mcp-local/contracts/integration.test.mjs mcp-local/contracts/persist.test.mjs mcp-local/contracts/quality-backfill.test.mjs` | PASS — 3/3 |
| Flow project connection | `npm run seosona:doctor` | PASS |

The Flow MCP contract fixtures intentionally run on loopback without a token
and print a warning. Production Content Companion startup still requires
`SEOSONA_LOCAL_MCP_TOKEN`.

## Negative and portability checks

- Wrong SHA-256, wrong version, wrong dimensions, missing assets, directory
  escape, and machine-specific OS references are rejected by tests.
- No machine-specific absolute path was found in changed durable files.
- No AWS, OpenAI-style, GitHub-style, or private-key secret pattern was found.
- No image binary was copied into OS or Content.
- `git diff --check` is clean in Video, OS, and Content worktrees.
- Content stores only the small BrandKit snapshot and provenance receipt; image
  binary remains in the local Content Library.

## Runtime contract delivered

1. Video owns `brand-kit.v1.json`, `asset-manifest.v1.json`, and the aligned
   `DESIGN.md`.
2. OS owns the portable logical reference, version, digest, group policy, and
   evidence packet.
3. Content Companion resolves `SEOSONA_BRAND_KIT_FILE`, verifies version/hash,
   and freezes the approved visual subset into the batch context.
4. Content creates a VisualJob with BrandKit provenance, mode, component,
   explicit Flow asset allowlist, and negative rules.
5. Flow receives only a composed text-free image prompt. The asset receipt
   retains BrandKit version and digest.

## Explicitly outside this delivery

- Deterministic text/logo compositor.
- Live visual QA exports for all eight component families.
- Live image-provider acceptance batch.
- Facebook OAuth, scheduling, or publishing.

These exclusions do not weaken the BrandKit/data contract; they are separate
runtime and creative acceptance phases.
