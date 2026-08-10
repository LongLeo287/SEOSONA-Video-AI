import path from "node:path";
import { fileURLToPath } from "node:url";

import { validateBrandKit } from "./brand-kit-contract.mjs";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDirectory, "../..");
const result = await validateBrandKit({
  repoRoot,
  brandKitFile: path.join(repoRoot, "7_ASSETS/brand/SEOSONA/brand-kit.v1.json"),
  manifestFile: path.join(
    repoRoot,
    "7_ASSETS/brand/SEOSONA/asset-manifest.v1.json",
  ),
});

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
if (!result.valid) process.exitCode = 1;
