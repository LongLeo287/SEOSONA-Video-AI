import path from "node:path";
import { fileURLToPath } from "node:url";

import { writeAssetManifest } from "./brand-kit-assets.mjs";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDirectory, "../..");
const outputFile = path.join(
  repoRoot,
  "7_ASSETS/brand/SEOSONA/asset-manifest.v1.json",
);

const manifest = await writeAssetManifest({ repoRoot, outputFile });
process.stdout.write(
  `${JSON.stringify({ output: "7_ASSETS/brand/SEOSONA/asset-manifest.v1.json", assets: manifest.assets.length })}\n`,
);
