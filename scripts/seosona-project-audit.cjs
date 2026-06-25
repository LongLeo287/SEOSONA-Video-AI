#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), 'utf8'));
}

function run(command, args) {
  const executable = process.platform === 'win32' && command === 'npm' ? 'npm.cmd' : command;
  const result = spawnSync(executable, args, {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    timeout: Number(process.env.SEOSONA_AUDIT_COMMAND_TIMEOUT_MS || 90000),
  });
  return {
    ok: result.status === 0,
    exitCode: result.status,
    timedOut: Boolean(result.error && result.error.code === 'ETIMEDOUT'),
    stdout: (result.stdout || '').trim(),
    stderr: (result.stderr || result.error?.message || '').trim(),
  };
}

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function isGitIgnored(relativePath) {
  const git = process.platform === 'win32' ? 'git.exe' : 'git';
  const result = spawnSync(git, ['check-ignore', relativePath], {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  return result.status === 0;
}

function parseJsonSafe(value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function projectStatus() {
  const result = run(process.execPath, ['scripts/seosona-project-bridge.cjs', 'resolve']);
  return result.ok ? parseJsonSafe(result.stdout) : null;
}

function findPython() {
  const candidates = [
    { command: process.env.PYTHON, args: ['--version'] },
    { command: 'python', args: ['--version'] },
    { command: 'python3', args: ['--version'] },
    { command: 'py', args: ['-3', '--version'] },
  ].filter((item) => item.command);
  for (const candidate of candidates) {
    const result = run(candidate.command, candidate.args);
    if (result.ok) return { command: candidate.command, version: result.stdout || result.stderr };
  }
  return null;
}

function scanText(relativePath, patterns) {
  if (!exists(relativePath)) return [];
  const content = fs.readFileSync(path.join(root, relativePath), 'utf8');
  const findings = [];
  for (const pattern of patterns) {
    const regex = new RegExp(pattern.regex, 'gmi');
    let match;
    while ((match = regex.exec(content))) {
      const line = content.slice(0, match.index).split(/\r?\n/).length;
      findings.push({ file: relativePath, line, label: pattern.label });
    }
  }
  return findings;
}

function audit() {
  const packageJson = readJson('package.json');
  const manifest = readJson('seosona.project.json');
  const issues = [];
  const checks = [];
  const warnings = [];

  function check(name, ok, detail, severity = 'P2') {
    checks.push({ name, ok, detail });
    if (!ok) issues.push({ severity, name, detail });
  }

  function warn(name, ok, detail) {
    checks.push({ name, ok, detail, warning: true });
    if (!ok) warnings.push({ name, detail });
  }

  const requiredDirs = [
    '1_AGENTS',
    '2_KNOWLEDGE',
    '2_SKILLS',
    '3_MEMORY',
    '4_BRAIN',
    '5_FRAMEWORK',
    '6_SOP',
    '7_ASSETS',
    '8_WORKSPACE',
    'scripts',
  ];
  for (const dir of requiredDirs) check(`required dir: ${dir}`, exists(dir), dir);

  const requiredFiles = [
    'AGENTS.md',
    'GEMINI.md',
    'ARCHITECTURE.md',
    'system_config.yaml',
    'seosona.project.json',
    'package.json',
    'requirements.txt',
    '6_SOP/MASTER_OPERATION.md',
    '6_SOP/SEOSONA_WORKFLOW_BOUNDARY_MAP.md',
    '6_SOP/EXTERNAL_VIDEO_REPO_CAPABILITY_MAP.md',
    '6_SOP/HYPERFRAMES_INTEGRATION.md',
    '6_SOP/SEOSONA_VIDEO_AUTONOMOUS_TEMPLATE_FACTORY.md',
    '6_SOP/SEOSONA_VIDEO_RECONNECTION_MAP.md',
    '.agents/skills/seosona-video-operator/SKILL.md',
    '2_KNOWLEDGE/repos/yutu.md',
    '2_KNOWLEDGE/repos/obscura.md',
  ];
  for (const file of requiredFiles) check(`required file: ${file}`, exists(file), file);

  const requiredScripts = [
    'seosona:doctor',
    'seosona:route',
    'seosona:audit',
    'video:run',
    'template:clone',
    'post:image',
    'thumbnail:create',
    'video:news',
    'video:course',
  ];
  for (const script of requiredScripts) {
    check(`package script: ${script}`, Boolean(packageJson.scripts && packageJson.scripts[script]), script);
  }

  check('manifest uses portable OS root', manifest.osRoot === '~/.seosona', `osRoot=${manifest.osRoot}`);
  check('manifest memory namespace', manifest.memoryNamespace === 'seosona-video', `memoryNamespace=${manifest.memoryNamespace}`);

  check(
    'autonomy intake uses project bridge resolver',
    packageJson.scripts?.['autonomy:intake'] === 'node scripts/seosona-project-bridge.cjs intake',
    packageJson.scripts?.['autonomy:intake'],
    'P1',
  );

  const pythonWrapper = readText('scripts/seosona-python.cjs');
  check(
    'python wrapper bootstrap is opt-in',
    pythonWrapper.includes("SEOSONA_PYTHON_BOOTSTRAP === '1'") && !pythonWrapper.includes('AUTO BOOTSTRAPPER HOOK'),
    'Python commands must not install/update dependencies unless SEOSONA_PYTHON_BOOTSTRAP=1 is set',
    'P1',
  );

  const python = findPython();
  check('python runtime available', Boolean(python), python || 'No python/python3/py launcher found', 'P1');

  const logoFiles = [
    '7_ASSETS/brand/logos/Seosona_Logo.png',
    '7_ASSETS/brand/logos/Chi Quyet Academy Mascot Logo.png',
  ];
  for (const logo of logoFiles) check(`brand asset: ${logo}`, exists(logo), logo, 'P1');

  const status = projectStatus();
  check('project bridge resolves SEOSONA OS', Boolean(status && status.ok && status.osRoot), status, 'P1');
  const osRoot = status && status.osRoot ? status.osRoot : path.join(process.env.USERPROFILE || process.env.HOME || '', '.seosona');
  const osArtifacts = [
    {
      name: 'yutu ingestion artifact',
      alternatives: [
        '2_KNOWLEDGE/frameworks/multimedia_production/youtube_channel_operations_mcp/SKILL.md',
        '2_KNOWLEDGE/raw_data/ingested_data/yutu_youtube_toolkit/README.md',
      ],
    },
    {
      name: 'obscura ingestion artifact',
      alternatives: [
        '2_KNOWLEDGE/frameworks/browser_automation/obscura_headless_browser/SKILL.md',
        '2_KNOWLEDGE/raw_data/ingested_data/obscura_headless_browser/README.md',
      ],
    },
    {
      name: 'repo batch memory item',
      alternatives: [
        '3_MEMORY/knowledge_items/repo_batch_2026_06_19_yutu_obscura.md',
      ],
    },
  ];
  for (const artifact of osArtifacts) {
    const found = artifact.alternatives.find((relativePath) => fs.existsSync(path.join(osRoot, relativePath)));
    warn(`optional OS artifact: ${artifact.name}`, Boolean(found), found || artifact.alternatives);
  }

  const secretFindings = [
    ...scanText('.env.example', [
      { label: 'possible secret assignment', regex: "(api[_-]?key|secret|token)\\s*=\\s*[\"']?[A-Za-z0-9][^\\r\\n]+" },
    ]),
    ...scanText('system_config.yaml', [
      { label: 'hardcoded credential-like value', regex: "(api[_-]?keys?:|token:|secret:)\\s*[\"']?(?!\\$\\{)[A-Za-z0-9_\\-]{12,}" },
    ]),
  ];
  check('secret hygiene scan', secretFindings.length === 0, secretFindings, 'P1');

  const duplicateFunctionFindings = [];
  for (const file of ['4_BRAIN/pipeline_manager.py']) {
    if (!exists(file)) continue;
    const content = fs.readFileSync(path.join(root, file), 'utf8');
    const names = [...content.matchAll(/^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/gm)].map((match) => match[1]);
    const duplicates = names.filter((name, index) => names.indexOf(name) !== index);
    for (const name of [...new Set(duplicates)]) duplicateFunctionFindings.push({ file, name });
  }
  check('duplicate Python function definitions', duplicateFunctionFindings.length === 0, duplicateFunctionFindings, 'P2');

  const configText = readText('system_config.yaml');
  check(
    'local publishing disabled by default',
    /auto_upload_gdrive:\s*false\b/.test(configText),
    'features.auto_upload_gdrive must stay false unless a publish workflow is explicitly requested',
    'P2',
  );

  const runtimePathFiles = [
    'scripts/convert_to_9_16.py',
    'scripts/extract_frames.py',
    'scripts/preview_news_spatial.py',
    'scripts/inject_os_capabilities.py',
    '4_BRAIN/run_demo.py',
    '2_SKILLS/thumbnail_maker/thumbnail_generator.py',
  ];
  const localPathFindings = [];
  for (const file of runtimePathFiles) {
    if (!exists(file)) continue;
    const content = readText(file);
    const patterns = [
      /D:\\LongLeo\\SEOSONA AI\\SEOSONA Video/g,
      /D:\\SEOSONA Video/g,
      /C:\\Users\\R9000P 2021\.LONGLEO/g,
    ];
    for (const pattern of patterns) {
      let match;
      while ((match = pattern.exec(content))) {
        const line = content.slice(0, match.index).split(/\r?\n/).length;
        localPathFindings.push({ file, line, match: match[0] });
      }
    }
  }
  check('runtime scripts use portable paths', localPathFindings.length === 0, localPathFindings, 'P2');

  const requiredProductionAssets = [
    '7_ASSETS/brand/logos/Seosona_Logo.png',
    '7_ASSETS/brand/logos/Chi Quyet Academy Mascot Logo.png',
    '7_ASSETS/voice/profiles/seosona_male_southern.wav',
    '7_ASSETS/audio/bgm/bgm_tech_ambient.mp3',
    '7_ASSETS/audio/sfx/pops/pop_01.wav',
    '7_ASSETS/audio/sfx/transitions/whoosh_01.wav',
    '7_ASSETS/templates/loop-source-seosona-clone/template.json',
    '7_ASSETS/templates/loop-source-seosona-clone/index.html',
    '7_ASSETS/templates/loop-source-seosona-clone/hyperframes.json',
    '7_ASSETS/templates/loop-source-seosona-clone/production_manifest.json',
    '7_ASSETS/templates/loop-source-seosona-clone/sample.srt',
    '7_ASSETS/templates/loop-source-seosona-clone/thumbnail.png',
    '7_ASSETS/templates/loop-source-seosona-clone/assets/bgm_loop_96.mp3',
    '7_ASSETS/templates/loop-source-seosona-clone/assets/pop_01.wav',
    '7_ASSETS/templates/loop-source-seosona-clone/assets/whoosh_01.wav',
  ];
  const assetFindings = [];
  for (const asset of requiredProductionAssets) {
    if (!exists(asset)) assetFindings.push({ asset, issue: 'missing' });
    if (asset.match(/\.(mp3|wav)$/i) && isGitIgnored(asset)) {
      assetFindings.push({ asset, issue: 'gitignored despite being a required production input' });
    }
  }
  check('required production assets are restorable', assetFindings.length === 0, assetFindings, 'P1');

  const templateManifestPath = '7_ASSETS/templates/loop-source-seosona-clone/template.json';
  const templateFileFindings = [];
  if (exists(templateManifestPath)) {
    const template = readJson(templateManifestPath);
    for (const file of template.files || []) {
      const templateFile = path.posix.join('7_ASSETS/templates/loop-source-seosona-clone', file.replaceAll('\\', '/'));
      if (!exists(templateFile)) templateFileFindings.push(templateFile);
    }
  }
  check('LOOP clone template manifest files exist', templateFileFindings.length === 0, templateFileFindings, 'P1');

  // Voice contract: the rebuilt single-router system is the source of truth, and the
  // deprecated fish_audio adapter must NOT be resurrected to satisfy this check.
  const voiceRouterText = exists('2_SKILLS/voice_cloner/voice_router.py')
    ? readText('2_SKILLS/voice_cloner/voice_router.py')
    : '';
  const legacyFishGone = !exists('2_SKILLS/voice_cloner/fish_audio_api.py');
  const routerHasContract =
    voiceRouterText.includes('_edge_fallback') &&
    voiceRouterText.includes('vi-VN-NamMinhNeural') &&
    /fallback/i.test(voiceRouterText);
  check(
    'voice router has honest fallback contract (no legacy fish adapter)',
    routerHasContract && legacyFishGone,
    legacyFishGone
      ? 'voice_router.py must route VieNeu (clone > preset) -> honest edge-tts fallback to the approved male Vietnamese voice'
      : 'legacy 2_SKILLS/voice_cloner/fish_audio_api.py must not be resurrected — voice_router.py is the single source of truth',
    'P2',
  );

  const doctor = run(process.execPath, ['scripts/seosona-project-bridge.cjs', 'doctor']);
  check('SEOSONA doctor', doctor.ok, doctor.ok ? 'passed' : doctor.stderr || doctor.stdout, 'P1');

  const result = {
    ok: issues.length === 0,
    generatedAt: new Date().toISOString(),
    project: manifest.name,
    checks,
    warnings,
    issues,
  };

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (!result.ok) process.exitCode = 1;
}

audit();
