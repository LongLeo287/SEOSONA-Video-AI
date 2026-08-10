import assert from "node:assert/strict";
import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import { validateBrandKit } from "../scripts/brand-kit/brand-kit-contract.mjs";

const repoRoot = path.resolve(import.meta.dirname, "..");
const brandKitFile = path.join(
  repoRoot,
  "7_ASSETS/brand/SEOSONA/brand-kit.v1.json",
);
const manifestFile = path.join(
  repoRoot,
  "7_ASSETS/brand/SEOSONA/asset-manifest.v1.json",
);

async function validateCanonical() {
  return validateBrandKit({ brandKitFile, manifestFile, repoRoot });
}

async function validateWithManifestMutation(mutate) {
  const tempRoot = await mkdtemp(path.join(tmpdir(), "seosona-brand-kit-"));
  const manifest = JSON.parse(await readFile(manifestFile, "utf8"));
  mutate(manifest);
  const mutatedManifestFile = path.join(tempRoot, "asset-manifest.v1.json");
  await writeFile(mutatedManifestFile, `${JSON.stringify(manifest, null, 2)}\n`);
  return validateBrandKit({ brandKitFile, manifestFile: mutatedManifestFile, repoRoot });
}

async function validateWithBrandMutation(mutate) {
  const tempRoot = await mkdtemp(path.join(tmpdir(), "seosona-brand-kit-"));
  const brandKit = JSON.parse(await readFile(brandKitFile, "utf8"));
  mutate(brandKit);
  const mutatedBrandKitFile = path.join(tempRoot, "brand-kit.v1.json");
  await writeFile(mutatedBrandKitFile, `${JSON.stringify(brandKit, null, 2)}\n`);
  return validateBrandKit({
    brandKitFile: mutatedBrandKitFile,
    manifestFile,
    repoRoot,
  });
}

test("canonical BrandKit validates approved tokens and assets", async () => {
  const result = await validateCanonical();

  assert.equal(result.valid, true, result.errors.join("\n"));
  assert.match(result.brandKitDigest, /^[a-f0-9]{64}$/);
  assert.match(result.manifestDigest, /^[a-f0-9]{64}$/);
  assert.ok(result.checkedAssets >= 10);
});

test("BrandKit digest is invariant to JSON formatting and line endings", async () => {
  const canonical = await validateCanonical();
  const tempRoot = await mkdtemp(path.join(tmpdir(), "seosona-brand-kit-format-"));
  const parsed = JSON.parse(await readFile(brandKitFile, "utf8"));
  const reformattedFile = path.join(tempRoot, "brand-kit.v1.json");
  const reformatted = `${JSON.stringify(parsed, null, 4)}\n`.replace(/\n/g, "\r\n");
  await writeFile(reformattedFile, reformatted, "utf8");

  const result = await validateBrandKit({
    brandKitFile: reformattedFile,
    manifestFile,
    repoRoot,
  });

  assert.equal(result.valid, true, result.errors.join("\n"));
  assert.equal(result.brandKitDigest, canonical.brandKitDigest);
});

test("manifest rejects a path outside the brand asset root", async () => {
  const result = await validateWithManifestMutation((manifest) => {
    manifest.assets[0].path = "package.json";
  });

  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.includes("outside 7_ASSETS/brand")));
});

test("Academy assets can never be production allowlisted", async () => {
  const result = await validateWithManifestMutation((manifest) => {
    const academyAsset = manifest.assets.find((asset) =>
      asset.path.includes("carousel Chí Quyết Academy"),
    );
    assert.ok(academyAsset, "canonical manifest must inventory Academy references");
    academyAsset.usage = "allow";
  });

  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.includes("Academy asset")));
});

test("manifest rejects missing files and checksum drift", async () => {
  const missing = await validateWithManifestMutation((manifest) => {
    manifest.assets[0].path = "7_ASSETS/brand/logos/missing.png";
  });
  assert.ok(missing.errors.some((error) => error.includes("missing asset")));

  const drifted = await validateWithManifestMutation((manifest) => {
    manifest.assets[0].sha256 = "0".repeat(64);
  });
  assert.ok(drifted.errors.some((error) => error.includes("SHA-256 mismatch")));
});

test("manifest rejects wrong raster dimensions", async () => {
  const result = await validateWithManifestMutation((manifest) => {
    const image = manifest.assets.find((asset) => asset.width && asset.height);
    assert.ok(image, "canonical manifest must contain a raster image");
    image.width += 1;
  });

  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.includes("dimension mismatch")));
});

test("production typography resolves only to local Be Vietnam Pro files", async () => {
  const result = await validateWithBrandMutation((brandKit) => {
    brandKit.typography.family = "Poppins";
  });

  assert.equal(result.valid, false);
  assert.ok(result.errors.some((error) => error.includes("Be Vietnam Pro")));
});

test("human design guide agrees with the canonical machine contract", async () => {
  const guide = await readFile(
    path.join(repoRoot, "7_ASSETS/brand/SEOSONA/DESIGN.md"),
    "utf8",
  );

  assert.match(guide, /brand-kit\.v1\.json/);
  assert.match(guide, /Be Vietnam Pro/);
  assert.match(guide, /cover.*CTA/is);
  assert.match(guide, /Academy.*reference-only/is);
  assert.match(guide, /Flow.*Vietnamese text.*logo.*statistics.*citations/is);
});
