#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const manifestPath = path.join(repoRoot, 'seosona.project.json');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function expandHome(value) {
  if (!value || typeof value !== 'string') return value;
  if (value === '~') return process.env.USERPROFILE || process.env.HOME || value;
  if (value.startsWith('~/') || value.startsWith('~\\')) {
    const home = process.env.USERPROFILE || process.env.HOME;
    return home ? path.join(home, value.slice(2)) : value;
  }
  return value;
}

function expandVariables(value) {
  if (!value || typeof value !== 'string') return value;
  return value.replace(/\$\{([^}]+)\}/g, (_, name) => process.env[name] || '');
}

function resolveCandidate(value) {
  if (!value || typeof value !== 'string') return null;
  const expanded = expandHome(expandVariables(value));
  if (!expanded.trim()) return null;
  return path.resolve(repoRoot, expanded);
}

function hasOsAnchors(osRoot) {
  if (!osRoot) return false;
  return [
    '1_CORE/SOUL.md',
    '2_KNOWLEDGE/MASTER_INDEX.md',
    '1_CORE/scripts/seosona_capability_bridge.js',
  ].every((relativePath) => fs.existsSync(path.join(osRoot, relativePath)));
}

function resolveOsRoot(manifest) {
  const candidates = [
    process.env.SEOSONA_ROOT,
    manifest.osRoot,
    '~/.seosona',
    '../SEOSONA OS',
    '../../SEOSONA OS',
  ].map(resolveCandidate).filter(Boolean);

  const seen = new Set();
  for (const candidate of candidates) {
    const normalized = path.resolve(candidate);
    if (seen.has(normalized)) continue;
    seen.add(normalized);
    if (hasOsAnchors(normalized)) return normalized;
  }

  return null;
}

function bridgePath(osRoot) {
  return path.join(osRoot, '1_CORE', 'scripts', 'seosona_capability_bridge.js');
}

function memoryPath(osRoot, manifest) {
  return path.join(osRoot, '3_MEMORY', 'projects', manifest.memoryNamespace || manifest.name);
}

function projectStatus() {
  const manifest = readJson(manifestPath);
  const osRoot = resolveOsRoot(manifest);
  const memoryNamespacePath = osRoot ? memoryPath(osRoot, manifest) : null;

  return {
    ok: Boolean(osRoot),
    projectRoot: repoRoot,
    manifest: path.relative(repoRoot, manifestPath).replace(/\\/g, '/'),
    project: manifest.name,
    memoryNamespace: manifest.memoryNamespace,
    osRoot,
    anchors: osRoot ? {
      soul: path.join(osRoot, '1_CORE', 'SOUL.md'),
      masterIndex: path.join(osRoot, '2_KNOWLEDGE', 'MASTER_INDEX.md'),
      capabilityBridge: bridgePath(osRoot),
      projectMemory: memoryNamespacePath,
    } : null,
    projectMemoryExists: memoryNamespacePath ? fs.existsSync(memoryNamespacePath) : false,
  };
}

function runBridge(command, args) {
  const status = projectStatus();
  if (!status.ok) {
    process.stdout.write(`${JSON.stringify(status, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  const result = spawnSync(process.execPath, [status.anchors.capabilityBridge, command, ...args], {
    cwd: repoRoot,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  process.exitCode = result.status || 0;
}

function doctor() {
  const status = projectStatus();
  const checks = [];

  checks.push({ name: 'project manifest', ok: fs.existsSync(manifestPath), path: manifestPath });
  checks.push({ name: 'SEOSONA OS root', ok: status.ok, path: status.osRoot });

  if (status.anchors) {
    for (const [name, filePath] of Object.entries(status.anchors)) {
      checks.push({ name, ok: fs.existsSync(filePath), path: filePath });
    }
  }

  let bridgeValidation = null;
  if (status.ok) {
    const result = spawnSync(process.execPath, [status.anchors.capabilityBridge, 'validate'], {
      cwd: repoRoot,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    bridgeValidation = {
      ok: result.status === 0,
      exitCode: result.status,
      stdout: result.stdout ? JSON.parse(result.stdout) : null,
      stderr: result.stderr,
    };
  }

  const output = {
    ok: checks.every((check) => check.ok) && (!bridgeValidation || bridgeValidation.ok),
    status,
    checks,
    bridgeValidation,
  };
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
  if (!output.ok) process.exitCode = 1;
}

function main() {
  const [command = 'doctor', ...args] = process.argv.slice(2);
  if (command === 'resolve') {
    process.stdout.write(`${JSON.stringify(projectStatus(), null, 2)}\n`);
  } else if (command === 'doctor') {
    doctor();
  } else if (['manifest', 'route', 'validate', 'audit-portability'].includes(command)) {
    runBridge(command, args);
  } else {
    process.stderr.write(`Unknown command: ${command}\n`);
    process.exitCode = 1;
  }
}

main();
