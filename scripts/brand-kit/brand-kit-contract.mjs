import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";

import { imageDimensions } from "./brand-kit-assets.mjs";

const EXPECTED_COLORS = {
  identityBlue: "#003CA6",
  heroBlueStart: "#182FB3",
  heroBlueEnd: "#1F31B7",
  identityGreen: "#00FF00",
};

const EXPECTED_COMPONENTS = [
  "cover_dark",
  "explain_light",
  "numbered_principle",
  "process_steps",
  "data_table",
  "comparison_split",
  "proof_cards",
  "mascot_callout",
];

function digest(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.keys(value).sort().reduce((output, key) => {
      output[key] = canonicalize(value[key]);
      return output;
    }, {});
  }
  return value;
}

function canonicalJsonDigest(buffer) {
  const value = JSON.parse(buffer.toString("utf8"));
  return digest(Buffer.from(JSON.stringify(canonicalize(value))));
}

function isPortableBrandPath(assetPath) {
  if (typeof assetPath !== "string") return false;
  if (path.isAbsolute(assetPath) || /^[a-zA-Z]:[\\/]/.test(assetPath)) return false;
  const normalized = assetPath.replace(/\\/g, "/");
  return (
    normalized.startsWith("7_ASSETS/brand/") &&
    !normalized.split("/").includes("..")
  );
}

export async function validateBrandKit({ brandKitFile, manifestFile, repoRoot }) {
  const errors = [];
  const brandKitBuffer = await readFile(brandKitFile);
  const manifestBuffer = await readFile(manifestFile);
  const brandKit = JSON.parse(brandKitBuffer.toString("utf8"));
  const manifest = JSON.parse(manifestBuffer.toString("utf8"));
  const assetById = new Map();
  let checkedAssets = 0;

  if (brandKit.version !== "1.0.0") errors.push("BrandKit version must be 1.0.0");
  if (brandKit.identity?.name !== "SEOSONA") errors.push("identity.name must be SEOSONA");
  if (brandKit.typography?.family !== "Be Vietnam Pro") {
    errors.push("Production typography family must be Be Vietnam Pro");
  }

  for (const [token, expected] of Object.entries(EXPECTED_COLORS)) {
    if (brandKit.palette?.[token] !== expected) {
      errors.push(`palette.${token} must equal ${expected}`);
    }
  }

  for (const component of EXPECTED_COMPONENTS) {
    if (!brandKit.components?.includes(component)) {
      errors.push(`missing approved component ${component}`);
    }
  }

  if (!brandKit.visualModes?.lightEditorial || !brandKit.visualModes?.cobaltHero) {
    errors.push("BrandKit must define lightEditorial and cobaltHero visual modes");
  }
  if (!Array.isArray(brandKit.negativeRules) || brandKit.negativeRules.length < 6) {
    errors.push("BrandKit must define at least six negative rules");
  }
  if (brandKit.assetManifest !== "asset-manifest.v1.json") {
    errors.push("assetManifest must be asset-manifest.v1.json");
  }

  if (!Array.isArray(manifest.assets)) {
    errors.push("asset manifest must contain an assets array");
  } else {
    for (const asset of manifest.assets) {
      assetById.set(asset.id, asset);
      if (!isPortableBrandPath(asset.path)) {
        errors.push(`${asset.id}: path is outside 7_ASSETS/brand`);
        continue;
      }
      if (!new Set(["allow", "reference_only", "exclude"]).has(asset.usage)) {
        errors.push(`${asset.id}: unsupported usage ${asset.usage}`);
      }
      if (/carousel Chí Quyết Academy/i.test(asset.path) && asset.usage === "allow") {
        errors.push(`${asset.id}: Academy asset cannot be production allowlisted`);
      }

      const absolutePath = path.resolve(repoRoot, asset.path);
      if (!absolutePath.startsWith(path.resolve(repoRoot, "7_ASSETS/brand") + path.sep)) {
        errors.push(`${asset.id}: resolved path is outside 7_ASSETS/brand`);
        continue;
      }

      let buffer;
      try {
        buffer = await readFile(absolutePath);
      } catch {
        errors.push(`${asset.id}: missing asset ${asset.path}`);
        continue;
      }
      checkedAssets += 1;
      if (digest(buffer) !== asset.sha256) {
        errors.push(`${asset.id}: SHA-256 mismatch`);
      }
      if (asset.width || asset.height) {
        const dimensions = imageDimensions(buffer);
        if (
          !dimensions ||
          dimensions.width !== asset.width ||
          dimensions.height !== asset.height
        ) {
          errors.push(`${asset.id}: dimension mismatch`);
        }
      }
    }
  }

  for (const assetId of Object.values(brandKit.typography?.assets ?? {})) {
    const asset = assetById.get(assetId);
    if (
      !asset ||
      asset.kind !== "font" ||
      asset.usage !== "allow" ||
      !/7_ASSETS\/brand\/fonts\/BeVietnamPro-.*\.ttf$/.test(asset.path)
    ) {
      errors.push(`Typography asset ${assetId} must resolve to a local Be Vietnam Pro file`);
    }
  }

  for (const assetId of [
    brandKit.identity?.logoAsset,
    brandKit.mascot?.catalogAsset,
    ...(brandKit.mascot?.allowedPoseAssets ?? []),
  ]) {
    if (!assetId) continue;
    const asset = assetById.get(assetId);
    if (!asset || asset.usage !== "allow") {
      errors.push(`Production asset ${assetId} is missing or not allowlisted`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    brandKitDigest: canonicalJsonDigest(brandKitBuffer),
    manifestDigest: canonicalJsonDigest(manifestBuffer),
    checkedAssets,
  };
}
