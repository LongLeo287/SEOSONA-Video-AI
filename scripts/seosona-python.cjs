#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');

function expandPortablePath(value) {
  if (!value || typeof value !== 'string') return value;
  const home = process.env.USERPROFILE || process.env.HOME;
  if (!home) return value;
  if (value === '~') return home;
  if (value.startsWith('~/') || value.startsWith('~\\')) {
    return path.join(home, value.slice(2));
  }
  return value;
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

  // >>> AUTO BOOTSTRAPPER HOOK <<<
  // Transparently run the doctor before executing the user's intended python script
  const doctorScript = path.join(process.cwd(), 'scripts', 'seosona_doctor.py');
  const fs = require('fs');
  if (fs.existsSync(doctorScript)) {
      const doctorEnv = runtimeEnv();
      doctorEnv.SEOSONA_BOOTSTRAP_SILENT = '1';
      const docRes = spawnSync(python.command, [...python.prefixArgs, doctorScript], {
        cwd: process.cwd(),
        env: doctorEnv,
        stdio: 'inherit',
      });
      if (docRes.error || (docRes.status !== 0 && docRes.status !== null)) {
         process.stderr.write(`Bootstrapper failed. Please check the logs.\n`);
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
