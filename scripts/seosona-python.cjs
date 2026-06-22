#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const repoRoot = process.cwd();

function expandHome(value) {
  if (!value || typeof value !== 'string') return value;
  const home = process.env.USERPROFILE || process.env.HOME;
  if (value === '~') return home || value;
  if (value.startsWith('~/') || value.startsWith('~\\')) {
    return home ? path.join(home, value.slice(2)) : value;
  }
  return value;
}

function expandVariables(value) {
  if (!value || typeof value !== 'string') return value;
  return value.replace(/\$\{([^}]+)\}/g, (_, name) => process.env[name] || '');
}

function hasOsAnchors(osRoot) {
  if (!osRoot) return false;
  return [
    '1_CORE/SOUL.md',
    '2_KNOWLEDGE/MASTER_INDEX.md',
    '1_CORE/scripts/seosona_capability_bridge.js',
  ].every((relativePath) => fs.existsSync(path.join(osRoot, relativePath)));
}

function readManifestOsRoot() {
  const manifestPath = path.join(repoRoot, 'seosona.project.json');
  if (!fs.existsSync(manifestPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(manifestPath, 'utf8')).osRoot || null;
  } catch {
    return null;
  }
}

function resolveCandidate(value) {
  if (!value || typeof value !== 'string') return null;
  const expanded = expandHome(expandVariables(value));
  if (!expanded || !expanded.trim()) return null;
  return path.resolve(repoRoot, expanded);
}

function resolveOsRoot() {
  const candidates = [
    process.env.SEOSONA_ROOT,
    readManifestOsRoot(),
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

function expandPortablePath(value) {
  if (!value || typeof value !== 'string') return value;
  if (value === '~/.seosona' || value.startsWith('~/.seosona/') || value.startsWith('~\\.seosona\\')) {
    const osRoot = resolveOsRoot();
    if (osRoot) {
      const suffix = value
        .replace(/^~[/\\]\.seosona[/\\]?/, '')
        .replace(/^~[/\\]\.seosona$/, '');
      return suffix ? path.join(osRoot, suffix) : osRoot;
    }
  }
  return expandHome(expandVariables(value));
}

function runtimeEnv() {
  const env = { ...process.env };
  env.PYTHONUTF8 = env.PYTHONUTF8 || '1';
  env.PYTHONIOENCODING = env.PYTHONIOENCODING || 'utf-8';
  try {
    const ffmpegPath = require('ffmpeg-static');
    let extraPaths = [];
    if (ffmpegPath) {
      env.FFMPEG_BINARY = ffmpegPath;
      env.IMAGEIO_FFMPEG_EXE = ffmpegPath;
      extraPaths.push(path.dirname(ffmpegPath));
    }
    try {
      const ffprobe = require('ffprobe-static');
      const ffprobePath = typeof ffprobe === 'string' ? ffprobe : ffprobe.path;
      if (ffprobePath) extraPaths.push(path.dirname(ffprobePath));
    } catch {
      // Optional; HyperFrames can still use a system ffprobe when available.
    }
    if (extraPaths.length) {
      const currentPath = env.PATH || env.Path || '';
      env.PATH = `${extraPaths.join(path.delimiter)}${path.delimiter}${currentPath}`;
      env.Path = env.PATH;
    }
  } catch {
    // ffmpeg-static is optional; external ffmpeg can still be on PATH.
  }
  return env;
}

function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: process.cwd(),
    encoding: 'utf8',
    stdio: options.stdio || ['ignore', 'pipe', 'pipe'],
  });
}

function findPython() {
  const candidates = [
    { command: path.join(process.cwd(), '.venv', 'Scripts', 'python.exe'), args: ['--version'] },
    { command: path.join(process.cwd(), '.venv', 'bin', 'python'), args: ['--version'] },
    { command: process.env.PYTHON, args: ['--version'] },
    { command: 'python', args: ['--version'] },
    { command: 'python3', args: ['--version'] },
    { command: 'py', args: ['-3', '--version'], prefixArgs: ['-3'] },
  ].filter((item) => item.command);

  for (const candidate of candidates) {
    const result = run(candidate.command, candidate.args);
    if (result.status === 0) {
      return {
        command: candidate.command,
        prefixArgs: candidate.prefixArgs || [],
        version: (result.stdout || result.stderr || '').trim(),
      };
    }
  }

  return null;
}

function main() {
  const python = findPython();
  if (!python) {
    process.stderr.write('No Python runtime found. Install Python or set PYTHON to an executable path.\n');
    process.exitCode = 1;
    return;
  }

  const args = process.argv.slice(2).map((arg, index) => (index === 0 ? expandPortablePath(arg) : arg));
  if (args[0] === '--which') {
    process.stdout.write(`${JSON.stringify(python, null, 2)}\n`);
    return;
  }

  if (process.env.SEOSONA_PYTHON_BOOTSTRAP === '1') {
    const doctorScript = path.join(process.cwd(), 'scripts', 'seosona_doctor.py');
    if (fs.existsSync(doctorScript)) {
      const doctorEnv = runtimeEnv();
      doctorEnv.SEOSONA_BOOTSTRAP_SILENT = '1';
      const docRes = spawnSync(python.command, [...python.prefixArgs, doctorScript], {
        cwd: process.cwd(),
        env: doctorEnv,
        stdio: 'inherit',
      });
      if (docRes.error || (docRes.status !== 0 && docRes.status !== null)) {
        process.stderr.write('Bootstrapper failed. Please check the logs.\n');
      }
    }
  }

  const result = spawnSync(python.command, [...python.prefixArgs, ...args], {
    cwd: process.cwd(),
    env: runtimeEnv(),
    stdio: 'inherit',
  });
  if (result.error) {
    process.stderr.write(`Python spawn failed: ${result.error.message}\n`);
    process.exitCode = 1;
    return;
  }
  process.exitCode = typeof result.status === 'number' ? result.status : 1;
}

main();
