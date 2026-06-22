#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const manifestPath = path.join(repoRoot, 'seosona.project.json');
const DEFAULT_BRIDGE_TIMEOUT_MS = Number(process.env.SEOSONA_BRIDGE_TIMEOUT_MS || 60000);

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

function parseJsonSafe(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function runBridge(command, args, options = {}) {
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
    timeout: options.timeoutMs || DEFAULT_BRIDGE_TIMEOUT_MS,
  });

  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.error && result.error.code === 'ETIMEDOUT') {
    process.stderr.write(`SEOSONA bridge command timed out after ${options.timeoutMs || DEFAULT_BRIDGE_TIMEOUT_MS}ms\n`);
    process.exitCode = 1;
    return;
  }
  process.exitCode = result.status || 0;
}

function doctor(args = []) {
  const status = projectStatus();
  const strict = args.includes('--strict');
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
      timeout: DEFAULT_BRIDGE_TIMEOUT_MS,
    });
    bridgeValidation = {
      ok: result.status === 0 && !(result.error && result.error.code === 'ETIMEDOUT'),
      exitCode: result.status,
      timedOut: Boolean(result.error && result.error.code === 'ETIMEDOUT'),
      stdout: parseJsonSafe(result.stdout),
      stderr: result.stderr || (result.error ? result.error.message : ''),
    };
  }

  const warnings = [];
  if (bridgeValidation && !bridgeValidation.ok) {
    warnings.push({
      name: 'SEOSONA OS strict validation',
      detail: 'Project anchors resolve, but the global OS bridge strict validate returned findings. Run npm run seosona:doctor -- --strict to fail on them.',
      bridgeValidation,
    });
  }

  const projectOk = checks.every((check) => check.ok);
  const output = {
    ok: projectOk && (!strict || !bridgeValidation || bridgeValidation.ok),
    projectOk,
    strict,
    status,
    checks,
    bridgeValidation,
    warnings,
  };
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
  if (!output.ok) process.exitCode = 1;
}

function intake(args) {
  const status = projectStatus();
  if (!status.ok) {
    process.stdout.write(`${JSON.stringify(status, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  const scriptPath = path.join(status.osRoot, '1_CORE', 'scripts', 'autonomous_activation_gate.py');
  if (!fs.existsSync(scriptPath)) {
    process.stdout.write(`${JSON.stringify({
      ok: false,
      error: 'Missing autonomous activation gate',
      script: '~/.seosona/1_CORE/scripts/autonomous_activation_gate.py',
    }, null, 2)}\n`);
    process.exitCode = 1;
    return;
  }

  const result = spawnSync(process.execPath, ['scripts/seosona-python.cjs', scriptPath, ...args], {
    cwd: repoRoot,
    encoding: 'utf8',
    stdio: 'inherit',
    timeout: Number(process.env.SEOSONA_INTAKE_TIMEOUT_MS || 120000),
  });
  if (result.error && result.error.code === 'ETIMEDOUT') {
    process.stderr.write('SEOSONA autonomy intake timed out.\n');
    process.exitCode = 1;
    return;
  }
  process.exitCode = result.status || 0;
}

function main() {
  const [command = 'doctor', ...args] = process.argv.slice(2);
  if (command === 'resolve') {
    process.stdout.write(`${JSON.stringify(projectStatus(), null, 2)}\n`);
  } else if (command === 'doctor') {
    doctor(args);
  } else if (command === 'intake') {
    intake(args);
  } else if (['manifest', 'route', 'validate', 'audit-portability'].includes(command)) {
    runBridge(command, args);
  } else {
    process.stderr.write(`Unknown command: ${command}\n`);
    process.exitCode = 1;
  }
}

main();
