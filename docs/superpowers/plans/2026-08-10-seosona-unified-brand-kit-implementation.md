# SEOSONA Unified BrandKit V1 Implementation Plan

> **For Codex:** Use `superpowers:executing-plans` and implement every task with test-driven development. Work only in the three isolated worktrees named below. Do not edit the dirty product checkouts.

**Goal:** Publish one validated, versioned SEOSONA BrandKit in Video and make OS and Content consume the same version/digest when creating Facebook visual jobs.

**Architecture:** Video owns canonical design tokens and asset provenance. OS exposes only a portable logical reference plus SHA-256 digest. Content Companion resolves the physical BrandKit path from `SEOSONA_BRAND_KIT_FILE`, verifies the digest, freezes the visual subset into the immutable batch context, and builds a Flow prompt that requests text-free imagery. Flow remains unchanged and receives only the composed prompt.

**Tech Stack:** JSON Schema-style runtime validation in Node.js, Node built-in test runner, SHA-256 via `node:crypto`, existing Chrome extension modules, existing local Companion/MCP bridge.

**Worktrees:** Use the existing isolated worktrees on branches
`codex/seosona-brand-kit`, `codex/facebook-content-policy`, and
`codex/facebook-content-factory`. Discover their local locations with
`git worktree list`; never persist those machine-specific locations.

---

## Task 1: Canonical Video BrandKit contract and validator

**Files:**

- Create: `tests/brand-kit-contract.test.mjs`
- Create: `scripts/brand-kit/brand-kit-contract.mjs`
- Create: `scripts/brand-kit/validate-brand-kit.mjs`
- Create: `7_ASSETS/brand/SEOSONA/brand-kit.v1.json`
- Create: `7_ASSETS/brand/SEOSONA/asset-manifest.v1.json`
- Modify: `package.json`

### Step 1: Write failing contract tests

Test the public behavior of `validateBrandKit({ brandKitFile, manifestFile, repoRoot })`:

- Accept the approved identity colors, Be Vietnam Pro roles, visual modes, component families, and negative rules.
- Reject an asset manifest entry outside `7_ASSETS/brand/`.
- Reject any Academy asset in an `allow` usage class.
- Reject a missing asset, wrong dimensions, or SHA-256 mismatch.
- Reject a production typography role that does not resolve to a local Be Vietnam Pro file.

### Step 2: Run the tests and confirm RED

Run: `node --test tests/brand-kit-contract.test.mjs`

Expected: failure because `scripts/brand-kit/brand-kit-contract.mjs` does not exist.

### Step 3: Implement the minimum validator and CLI

Export:

```js
export async function validateBrandKit({ brandKitFile, manifestFile, repoRoot }) {
  // Return { valid, errors, brandKitDigest, manifestDigest, checkedAssets }.
}
```

The CLI must print a machine-readable JSON receipt and exit non-zero when invalid. It must resolve paths from the repository root and never persist machine-specific absolute paths.

### Step 4: Create canonical JSON artifacts

`brand-kit.v1.json` must encode the approved specification: version, identity, palette roles, typography, 1080 square layout, light/cobalt modes, eight component families, mascot rules, Flow boundary, and negative rules.

`asset-manifest.v1.json` must contain repo-relative paths, SHA-256, dimensions for raster images, asset kind, and one usage class from `allow`, `reference_only`, or `exclude`. Include the primary logo, Be Vietnam Pro production font files, named mascot catalog/assets, SEOSONA carousel references, and Academy reference-only assets.

### Step 5: Add the release gate and verify GREEN

Add `brand:validate` to `package.json`:

```json
"brand:validate": "node scripts/brand-kit/validate-brand-kit.mjs"
```

Run:

- `node --test tests/brand-kit-contract.test.mjs`
- `npm run brand:validate`

Expected: all tests pass and the receipt reports `valid: true` with zero errors.

## Task 2: Replace the conflicting human design guide

**Files:**

- Modify: `7_ASSETS/brand/SEOSONA/DESIGN.md`
- Test: `tests/brand-kit-contract.test.mjs`

### Step 1: Add a failing documentation consistency test

Assert that `DESIGN.md` names `brand-kit.v1.json` as canonical, uses Be Vietnam Pro, permits cobalt only for cover/CTA, identifies Academy assets as reference-only, and explicitly forbids Flow-rendered Vietnamese text/logos/statistics/citations.

### Step 2: Run the test and confirm RED

Run: `node --test tests/brand-kit-contract.test.mjs`

Expected: the legacy guide fails one or more consistency assertions.

### Step 3: Rewrite `DESIGN.md`

Keep it concise and human-facing. Link every color, typography, composition, component, mascot, and Flow rule back to the JSON source. Remove conflicting Poppins/Inter and blanket “dark mode forbidden” language.

### Step 4: Verify GREEN

Run:

- `node --test tests/brand-kit-contract.test.mjs`
- `npm run brand:validate`

Expected: documentation consistency and asset validation both pass.

## Task 3: Publish a portable BrandKit reference through SEOSONA OS

**Files:**

- Modify: `3_MEMORY/projects/seosona-content/facebook-group-factory/brand-profile.v1.json`
- Create: `3_MEMORY/projects/seosona-content/facebook-group-factory/brand-kit-reference.v1.json`
- Create: `3_MEMORY/projects/seosona-content/facebook-group-factory/validate-brand-reference.mjs`
- Create: `3_MEMORY/projects/seosona-content/facebook-group-factory/brand-reference.test.mjs`

### Step 1: Write failing reference tests

Assert that OS stores:

```json
{
  "ref": "seosona-brand://video/SEOSONA/brand-kit.v1.json",
  "version": "1.0.0",
  "sha256": "<64 lowercase hex characters>"
}
```

The test must reject absolute paths, digest drift, and a brand profile that omits the logical reference.

### Step 2: Run the test and confirm RED

Run: `node --test 3_MEMORY/projects/seosona-content/facebook-group-factory/brand-reference.test.mjs`

Expected: failure because the reference and validator are absent.

### Step 3: Implement reference validation and OS files

Copy only the Video BrandKit digest and portable logical reference into OS. Extend `brand-profile.v1.json` with the reference and the minimal visual policy used before Companion resolution. Do not duplicate the full asset manifest or use a drive-letter path.

### Step 4: Verify GREEN

Run:

- `node --test 3_MEMORY/projects/seosona-content/facebook-group-factory/brand-reference.test.mjs`
- `node 3_MEMORY/projects/seosona-content/facebook-group-factory/validate-brand-reference.mjs --brand-kit-file "$env:SEOSONA_BRAND_KIT_FILE"`

Expected: test passes and live validation confirms the exact Video digest.

## Task 4: Resolve and freeze BrandKit in Content Companion

**Files:**

- Modify: `scripts/companion/facebook-companion.mjs`
- Modify: `extension/lib/facebook-factory.js`
- Modify: `tests/facebook-context-resolution.test.mjs`
- Modify: `tests/facebook-contracts.test.mjs`
- Modify: `docs/facebook-group-factory-v1.md`

### Step 1: Write failing context-resolution tests

Add tests showing that Companion:

- Reads the physical file only from `SEOSONA_BRAND_KIT_FILE` or an injected `brandKitFile` test option.
- Matches OS `version` and SHA-256 before accepting it.
- Rejects a missing file, digest mismatch, version mismatch, or absolute path embedded in OS policy.
- Freezes a small `brandKitSnapshot` containing version, digest, palette roles, font family, visual modes, component allowlist, and negative rules.

### Step 2: Run the tests and confirm RED

Run: `node --test tests/facebook-context-resolution.test.mjs`

Expected: assertions fail because current resolution returns only the OS policy files.

### Step 3: Implement secure resolution

Change the context loader to:

```js
export async function loadOsContext(contextFile, { brandKitFile } = {}) {
  // Resolve OS sources, verify the external kit, and attach brandKitSnapshot.
}
```

The production entrypoint passes `process.env.SEOSONA_BRAND_KIT_FILE`. Keep binary assets out of extension storage and the OS repository.

### Step 4: Verify context GREEN

Run: `node --test tests/facebook-context-resolution.test.mjs`

Expected: all resolution and negative cases pass.

### Step 5: Write failing VisualJob/prompt tests

Assert that a `VisualJob` and its composed prompt include:

- `brandKitRef` with version and digest.
- Chosen `mode` and approved component family.
- Exact identity colors and `Be Vietnam Pro` as compositor guidance.
- The text-free Flow boundary.
- Negative rules prohibiting generated Vietnamese copy, logos/wordmarks, statistics, citations, Academy/coral styling, neon/cyberpunk, and unapproved fonts.

Also assert that the resulting `AssetReceipt` retains the BrandKit version and digest.

### Step 6: Run the tests and confirm RED

Run: `node --test tests/facebook-contracts.test.mjs`

Expected: prompt and receipt assertions fail against the existing minimal brand prompt.

### Step 7: Implement the minimal Content changes

Extend VisualJob validation and prompt composition without changing Flow MCP schema. Flow continues receiving the final prompt string and existing ratio/quality parameters. Extend the receipt provenance fields only; do not implement a deterministic compositor or Facebook publisher in this task.

### Step 8: Verify Content GREEN

Run:

- `npm test`
- `npm run seosona:doctor`

Expected: the complete Facebook Factory test suite and Content health gate pass.

## Task 5: Cross-repository release verification and receipts

**Files:**

- Modify: `docs/facebook-group-factory-v1.md`
- Create: `docs/verification/2026-08-10-brand-kit-v1-receipt.md` in the Video worktree

### Step 1: Run the full gates with fresh output

Run:

- Video: `npm run brand:validate` and `node --test tests/brand-kit-contract.test.mjs`
- OS: brand reference test and live validator command from Task 3
- Content: `npm test` and `npm run seosona:doctor`
- Flow unchanged checkout: its existing static/MCP contract gates only if required by Content regression scope

### Step 2: Inspect diffs and portability

Run path/secret scans over changed durable files. Confirm no drive-letter path was written to source/config/docs, no Academy asset is allowed for production, and no image binary was copied to OS or Content.

### Step 3: Write the verification receipt

Record exact BrandKit/version/digests, commands, exit codes, test counts, known scope exclusions, and the boundary that the deterministic compositor and live visual QA sample remain follow-up work.

### Step 4: Commit each isolated worktree

Create focused commits only after all fresh gates pass:

- Video: `feat(video): publish unified SEOSONA BrandKit v1`
- OS: `feat(os): reference SEOSONA BrandKit v1`
- Content: `feat(content): consume verified BrandKit in visual jobs`

Do not stage generated `node_modules`, unrelated changes, or files outside this plan.
