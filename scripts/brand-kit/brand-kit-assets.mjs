import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const PRODUCTION_FONTS = [
  ["font.bevietnampro.regular", "BeVietnamPro-Regular.ttf"],
  ["font.bevietnampro.medium", "BeVietnamPro-Medium.ttf"],
  ["font.bevietnampro.semibold", "BeVietnamPro-SemiBold.ttf"],
  ["font.bevietnampro.bold", "BeVietnamPro-Bold.ttf"],
  ["font.bevietnampro.extrabold", "BeVietnamPro-ExtraBold.ttf"],
  ["font.bevietnampro.black", "BeVietnamPro-Black.ttf"],
];

function toPosix(filePath) {
  return filePath.split(path.sep).join("/");
}

function sha256(buffer) {
  return createHash("sha256").update(buffer).digest("hex");
}

function pngDimensions(buffer) {
  const pngSignature = "89504e470d0a1a0a";
  if (buffer.subarray(0, 8).toString("hex") !== pngSignature) return null;
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function jpegDimensions(buffer) {
  if (buffer[0] !== 0xff || buffer[1] !== 0xd8) return null;
  let offset = 2;
  while (offset + 8 < buffer.length) {
    if (buffer[offset] !== 0xff) {
      offset += 1;
      continue;
    }
    const marker = buffer[offset + 1];
    if (marker === 0xd9 || marker === 0xda) break;
    const segmentLength = buffer.readUInt16BE(offset + 2);
    if (
      [0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf].includes(marker)
    ) {
      return {
        width: buffer.readUInt16BE(offset + 7),
        height: buffer.readUInt16BE(offset + 5),
      };
    }
    if (segmentLength < 2) break;
    offset += 2 + segmentLength;
  }
  return null;
}

function imageDimensions(buffer) {
  return pngDimensions(buffer) ?? jpegDimensions(buffer);
}

async function describeAsset(repoRoot, definition) {
  const absolutePath = path.resolve(repoRoot, definition.path);
  const buffer = await readFile(absolutePath);
  const dimensions = imageDimensions(buffer);
  return {
    id: definition.id,
    path: toPosix(definition.path),
    kind: definition.kind,
    usage: definition.usage,
    sha256: sha256(buffer),
    bytes: buffer.byteLength,
    ...(dimensions ?? {}),
  };
}

async function listFiles(repoRoot, directory) {
  const entries = await readdir(path.resolve(repoRoot, directory), {
    withFileTypes: true,
  });
  return entries
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right, "vi"));
}

function slug(value) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export async function buildAssetManifest({ repoRoot }) {
  const definitions = [
    {
      id: "logo.primary",
      path: "7_ASSETS/brand/logos/Seosona_Logo.png",
      kind: "logo",
      usage: "allow",
    },
    ...PRODUCTION_FONTS.map(([id, filename]) => ({
      id,
      path: `7_ASSETS/brand/fonts/${filename}`,
      kind: "font",
      usage: "allow",
    })),
    {
      id: "mascot.catalog",
      path: "7_ASSETS/brand/SEOSONA/mascot_poses/named/catalog.json",
      kind: "catalog",
      usage: "allow",
    },
  ];

  const mascotDirectory = "7_ASSETS/brand/SEOSONA/mascot_poses/named";
  for (const filename of await listFiles(repoRoot, mascotDirectory)) {
    if (!filename.toLowerCase().endsWith(".png")) continue;
    definitions.push({
      id: `mascot.pose.${slug(path.parse(filename).name)}`,
      path: `${mascotDirectory}/${filename}`,
      kind: "mascot_pose",
      usage: "allow",
    });
  }

  for (const [directoryName, prefix] of [
    ["carousel SEOSONA", "reference.seosona.carousel"],
    ["carousel Chí Quyết Academy", "reference.academy.carousel"],
  ]) {
    const directory = `7_ASSETS/brand/SEOSONA/${directoryName}`;
    for (const filename of await listFiles(repoRoot, directory)) {
      if (!/\.(png|jpe?g)$/i.test(filename)) continue;
      definitions.push({
        id: `${prefix}.${slug(path.parse(filename).name)}`,
        path: `${directory}/${filename}`,
        kind: "visual_reference",
        usage: "reference_only",
      });
    }
  }

  const assets = [];
  for (const definition of definitions) {
    assets.push(await describeAsset(repoRoot, definition));
  }

  return {
    schemaVersion: "1.0",
    brandKitVersion: "1.0.0",
    pathPolicy: "repo_relative_posix",
    generatedFrom: [
      "7_ASSETS/brand/logos/Seosona_Logo.png",
      "7_ASSETS/brand/fonts/BeVietnamPro-*.ttf",
      "7_ASSETS/brand/SEOSONA/mascot_poses/named/",
      "7_ASSETS/brand/SEOSONA/carousel SEOSONA/",
      "7_ASSETS/brand/SEOSONA/carousel Chí Quyết Academy/",
    ],
    assets,
  };
}

export async function writeAssetManifest({ repoRoot, outputFile }) {
  const manifest = await buildAssetManifest({ repoRoot });
  await writeFile(outputFile, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  return manifest;
}

export { imageDimensions, pngDimensions, sha256 };
