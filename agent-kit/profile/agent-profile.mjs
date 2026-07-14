#!/usr/bin/env node
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const MODULE_DIR = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_FILE = path.join(MODULE_DIR, 'agent-profile.default.yaml');
const TEMPLATE_FILE = path.join(MODULE_DIR, 'agent-profile.template.yaml');
const ROUTER_FILE = path.join(MODULE_DIR, 'agent-profile-router.mjs');

export const PROFILE_KEYS = [
  'schema_version',
  'process_scaffold',
  'matt_skills',
  'sp_library',
  'reply_style',
];

const ALLOWED = {
  schema_version: new Set([1]),
  process_scaffold: new Set(['lean', 'guided', 'structured']),
  matt_skills: new Set(['enabled', 'disabled']),
  sp_library: new Set(['enabled', 'disabled']),
  reply_style: new Set(['default', 'concise', 'detailed']),
};

const BUILT_IN = {
  schema_version: 1,
  process_scaffold: 'lean',
  matt_skills: 'enabled',
  sp_library: 'enabled',
  reply_style: 'default',
};

const REQUIRED_SP_SKILLS = [
  'test-driven-development',
  'systematic-debugging',
  'verification-before-completion',
  'requesting-code-review',
  'receiving-code-review',
];

const REQUIRED_MATT_SKILLS = [
  'ask-matt',
  'codebase-design',
  'diagnosing-bugs',
  'domain-modeling',
  'grill-me',
  'grill-with-docs',
  'grilling',
  'implement',
  'improve-codebase-architecture',
  'prototype',
  'research',
  'resolving-merge-conflicts',
  'setup-matt-pocock-skills',
  'tdd',
  'teach',
  'to-spec',
  'to-tickets',
  'triage',
  'wayfinder',
  'writing-great-skills',
];

function normalizedRoot(root) {
  return path.resolve(root || process.env.AGENT_PROFILE_ROOT || process.cwd());
}

function scalarValue(key, raw, lineNumber) {
  const value = raw.replace(/\s+#.*$/, '').trim();
  if (!value || /^[[{>|&*!]/.test(value) || value.includes('#')) {
    throw new Error(`line ${lineNumber}: profile accepts only unquoted flat scalar values`);
  }
  const parsed = key === 'schema_version'
    ? (/^\d+$/.test(value) ? Number(value) : value)
    : value;
  if (!ALLOWED[key].has(parsed)) {
    throw new Error(`${key}: invalid value ${JSON.stringify(parsed)}`);
  }
  return parsed;
}

export function parseFlatYaml(text, source = 'profile') {
  const parsed = {};
  for (const [index, line] of String(text).split(/\r?\n/).entries()) {
    const lineNumber = index + 1;
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    if (/^\s/.test(line)) {
      throw new Error(`${source}:${lineNumber}: nested YAML is not supported; use flat key: value`);
    }
    const match = /^([a-z_][a-z0-9_]*):\s*(.*?)\s*$/.exec(line);
    if (!match) {
      throw new Error(`${source}:${lineNumber}: expected flat key: value`);
    }
    const [, key, raw] = match;
    if (!Object.hasOwn(ALLOWED, key)) {
      throw new Error(`${source}:${lineNumber}: unknown profile key ${key}`);
    }
    if (Object.hasOwn(parsed, key)) {
      throw new Error(`${source}:${lineNumber}: duplicate profile key ${key}`);
    }
    parsed[key] = scalarValue(key, raw, lineNumber);
  }
  return parsed;
}

function readLayer(file) {
  if (!fs.existsSync(file)) return {};
  return parseFlatYaml(fs.readFileSync(file, 'utf8'), file);
}

export function loadProfile({ root } = {}) {
  const repoRoot = normalizedRoot(root);
  const builtIn = fs.existsSync(DEFAULT_FILE) ? readLayer(DEFAULT_FILE) : { ...BUILT_IN };
  const repoFile = path.join(repoRoot, '.harness', 'agent-profile.yaml');
  const localFile = path.join(repoRoot, '.harness', 'agent-profile.local.yaml');
  const repo = readLayer(repoFile);
  const local = readLayer(localFile);
  const effective = { ...builtIn, ...repo, ...local };
  for (const key of PROFILE_KEYS) {
    if (!Object.hasOwn(effective, key)) {
      throw new Error(`effective profile is missing ${key}`);
    }
    if (!ALLOWED[key].has(effective[key])) {
      throw new Error(`${key}: invalid effective value ${JSON.stringify(effective[key])}`);
    }
  }
  const sources = {};
  for (const key of PROFILE_KEYS) {
    sources[key] = Object.hasOwn(local, key)
      ? 'local'
      : Object.hasOwn(repo, key)
        ? 'repo'
        : 'built-in';
  }
  const stateFile = path.join(repoRoot, '.harness', 'agent-profile-state.json');
  let reconcileRequired = true;
  if (fs.existsSync(stateFile)) {
    try {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      const clients = Object.values(state.clients || {});
      reconcileRequired = clients.length === 0 || clients.some((client) => (
        client?.libraries?.superpowers !== effective.sp_library
        || client?.libraries?.matt !== effective.matt_skills
      ));
    } catch {
      reconcileRequired = true;
    }
  }
  return {
    root: repoRoot,
    files: { built_in: DEFAULT_FILE, repo: repoFile, local: localFile },
    layers: { built_in: builtIn, repo, local },
    effective,
    sources,
    reconcile_required: reconcileRequired,
    notes: {
      reply_style: 'Recognized in v1; no behavior consumer is installed.',
      process_scaffold: 'Adjusts advisory density only; never enforcement.',
    },
  };
}

function canonicalYaml(values) {
  return PROFILE_KEYS
    .filter((key) => Object.hasOwn(values, key))
    .map((key) => `${key}: ${values[key]}`)
    .join('\n') + '\n';
}

function atomicWrite(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp`;
  fs.writeFileSync(temporary, text);
  fs.renameSync(temporary, file);
}

export function setProfileValue({ root, key, value, local = false }) {
  if (!Object.hasOwn(ALLOWED, key)) throw new Error(`unknown profile key ${key}`);
  const parsedValue = scalarValue(key, String(value), 1);
  const repoRoot = normalizedRoot(root);
  const file = path.join(
    repoRoot,
    '.harness',
    local ? 'agent-profile.local.yaml' : 'agent-profile.yaml',
  );
  const current = readLayer(file);
  if (!local && !Object.hasOwn(current, 'schema_version')) current.schema_version = 1;
  current[key] = parsedValue;
  atomicWrite(file, canonicalYaml(current));
  return { file, key, value: parsedValue, local };
}

function sha256Files(files) {
  const digest = crypto.createHash('sha256');
  for (const file of files) digest.update(fs.readFileSync(file));
  return digest.digest('hex');
}

function runtimeFiles(root) {
  const runtime = path.join(root, '.harness', 'profile-runtime');
  return [
    path.join(runtime, 'agent-profile.mjs'),
    path.join(runtime, 'agent-profile-router.mjs'),
  ];
}

function activeRuntimeFiles(root) {
  const portable = runtimeFiles(root);
  if (portable.every((file) => fs.existsSync(file))) return portable;
  const source = [
    path.join(root, 'agent-kit', 'profile', 'agent-profile.mjs'),
    path.join(root, 'agent-kit', 'profile', 'agent-profile-router.mjs'),
  ];
  return source.every((file) => fs.existsSync(file)) ? source : portable;
}

function wiringFragment(client) {
  const command = 'node .harness/profile-runtime/agent-profile-router.mjs';
  if (client === 'cursor' || client === 'cursor-cli') {
    return { hooks: { beforeSubmitPrompt: [{ command }] } };
  }
  if (client === 'claude') {
    return {
      hooks: {
        UserPromptSubmit: [{
          hooks: [{ type: 'command', command: 'node', args: ['.harness/profile-runtime/agent-profile-router.mjs'] }],
        }],
      },
    };
  }
  if (client === 'codex') {
    return {
      hooks: {
        UserPromptSubmit: [{
          hooks: [{ type: 'command', command, timeout: 5 }],
        }],
      },
    };
  }
  if (client === 'codex-native') {
    return { note: 'This client has no supported prompt-submit hook; description discovery remains active.' };
  }
  throw new Error(`unsupported client: ${client}`);
}

function appendIgnoreRules(root) {
  const file = path.join(root, '.gitignore');
  const required = [
    '.harness/agent-profile.local.yaml',
    '.harness/agent-profile-state.json',
  ];
  const current = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '';
  const missing = required.filter((line) => !current.split(/\r?\n/).includes(line));
  if (!missing.length) return;
  const prefix = current && !current.endsWith('\n') ? '\n' : '';
  fs.appendFileSync(file, `${prefix}${missing.join('\n')}\n`);
}

export function exportProfile({ root, client }) {
  const repoRoot = normalizedRoot(root);
  const harnessDir = path.join(repoRoot, '.harness');
  const runtimeDir = path.join(harnessDir, 'profile-runtime');
  const wiringDir = path.join(harnessDir, 'profile-wiring');
  fs.mkdirSync(runtimeDir, { recursive: true });
  fs.mkdirSync(wiringDir, { recursive: true });

  const repoProfile = path.join(harnessDir, 'agent-profile.yaml');
  if (!fs.existsSync(repoProfile)) {
    const template = fs.existsSync(TEMPLATE_FILE)
      ? fs.readFileSync(TEMPLATE_FILE, 'utf8')
      : canonicalYaml(BUILT_IN);
    atomicWrite(repoProfile, template);
  }

  const copies = [
    [fileURLToPath(import.meta.url), path.join(runtimeDir, 'agent-profile.mjs')],
    [ROUTER_FILE, path.join(runtimeDir, 'agent-profile-router.mjs')],
    [DEFAULT_FILE, path.join(runtimeDir, 'agent-profile.default.yaml')],
  ];
  for (const [source, target] of copies) {
    if (path.resolve(source) !== path.resolve(target)) fs.copyFileSync(source, target);
  }
  atomicWrite(
    path.join(wiringDir, `${client}.json`),
    JSON.stringify({
      merge_manually: true,
      overwrites_existing_hooks: false,
      fragment: wiringFragment(client),
    }, null, 2) + '\n',
  );
  const contractText = [
    '# Agent profile contract',
    '',
    '- Profile routing is lightweight and advisory, not a global process gate.',
    '- Agents change profile settings through `agent-kit.sh profile set`, not direct edits.',
    '- Enforcement hooks protect machine-checkable invariants and do not recommend skills.',
    '',
  ].join('\n');
  atomicWrite(path.join(harnessDir, 'agent-profile-rules.md'), contractText);
  const hasRules = ['AGENTS.md', 'CLAUDE.md']
    .some((name) => fs.existsSync(path.join(repoRoot, name)));
  if (!hasRules) atomicWrite(path.join(repoRoot, 'AGENTS.md'), contractText);
  appendIgnoreRules(repoRoot);
  const runtimeHash = sha256Files(runtimeFiles(repoRoot));
  return {
    root: repoRoot,
    client,
    runtime_hash: runtimeHash,
    hooks_overwritten: false,
    rules_overwritten: false,
    required_actions: [
      `merge .harness/profile-wiring/${client}.json into the active client hook configuration`,
      'copy the profile contract into an always-loaded agent rules file',
      `run profile check --root <repo> --client ${client}`,
    ],
  };
}

function clientHookFile(root, client) {
  if (client === 'cursor' || client === 'cursor-cli') return path.join(root, '.cursor', 'hooks.json');
  if (client === 'claude') return path.join(root, '.claude', 'settings.json');
  if (client === 'codex') return path.join(root, '.codex', 'hooks.json');
  return null;
}

function clientSkillDirectory(root, client) {
  if (client === 'cursor' || client === 'cursor-cli') return path.join(root, '.cursor', 'skills');
  if (client === 'claude') return path.join(root, '.claude', 'skills');
  if (client === 'codex') return path.join(root, '.agents', 'skills');
  if (client === 'codex-native') return path.join(root, '.codex', 'skills');
  return null;
}

export function checkProfile({ root, client } = {}) {
  const repoRoot = normalizedRoot(root);
  const errors = [];
  let profile;
  try {
    profile = loadProfile({ root: repoRoot });
  } catch (error) {
    errors.push(`profile config: ${error.message}`);
  }
  const files = activeRuntimeFiles(repoRoot);
  const runtimePresent = files.every((file) => fs.existsSync(file));
  const runtimeHash = runtimePresent ? sha256Files(files) : null;
  if (!runtimePresent) errors.push('portable profile runtime is missing; run profile export');

  if (client && client !== 'codex-native') {
    const hookFile = clientHookFile(repoRoot, client);
    const hookText = hookFile && fs.existsSync(hookFile) ? fs.readFileSync(hookFile, 'utf8') : '';
    if (!/agent-profile-router\.mjs|prompt-skill-router\.mjs/.test(hookText)) {
      errors.push(`${client} prompt wiring is missing the profile router`);
    }
  } else if (!client) {
    const wired = ['cursor', 'claude', 'codex'].some((candidate) => {
      const hookFile = clientHookFile(repoRoot, candidate);
      const hookText = hookFile && fs.existsSync(hookFile) ? fs.readFileSync(hookFile, 'utf8') : '';
      return /agent-profile-router\.mjs|prompt-skill-router\.mjs/.test(hookText);
    });
    if (!wired) errors.push('at least one active client prompt wiring must include the profile router');
  }

  const rulesText = ['AGENTS.md', 'CLAUDE.md']
    .map((name) => path.join(repoRoot, name))
    .filter((file) => fs.existsSync(file))
    .map((file) => fs.readFileSync(file, 'utf8'))
    .join('\n');
  if (!/lightweight and advisory|輕量.*advisory|轻量.*advisory/i.test(rulesText)
      || !/not a global process gate|非全域流程閘|非全局流程闸/i.test(rulesText)
      || !/agent-kit\.sh profile set/.test(rulesText)) {
    errors.push('agent rules are missing the lightweight profile and CLI-only mutation contract');
  }

  const stateFile = path.join(repoRoot, '.harness', 'agent-profile-state.json');
  let state = null;
  if (fs.existsSync(stateFile)) {
    try {
      state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    } catch (error) {
      errors.push(`managed state is invalid JSON: ${error.message}`);
    }
  } else {
    errors.push('managed profile state is missing; run agent-kit install');
  }
  if (state && runtimeHash && state.runtime_hash !== runtimeHash) {
    errors.push('portable runtime hash does not match managed state');
  }
  if (state && client && !state.clients?.[client]) {
    errors.push(`managed materialization state is missing client ${client}`);
  }
  if (state && client && profile) {
    const clientState = state.clients?.[client] || {};
    const libraries = clientState.libraries || {};
    if (libraries.superpowers !== profile.effective.sp_library) {
      errors.push('superpowers library materialization does not match effective profile');
    }
    if (libraries.matt !== profile.effective.matt_skills) {
      errors.push('Matt library materialization does not match effective profile');
    }
    const librarySkills = clientState.library_skills || {};
    const spSkills = librarySkills.superpowers || [];
    const mattSkills = librarySkills['mattpocock-skills'] || [];
    if (profile.effective.sp_library === 'enabled') {
      const missingCore = REQUIRED_SP_SKILLS.filter((name) => !spSkills.includes(name));
      if (missingCore.length) {
        errors.push(`superpowers materialization is incomplete: ${missingCore.join(', ')}`);
      }
    } else if (spSkills.length) {
      errors.push('superpowers materialization remains present while disabled');
    }
    if (profile.effective.matt_skills === 'enabled') {
      const missingMatt = REQUIRED_MATT_SKILLS.filter((name) => !mattSkills.includes(name));
      if (missingMatt.length) {
        errors.push(`Matt library materialization is incomplete: ${missingMatt.join(', ')}`);
      }
    } else if (profile.effective.matt_skills === 'disabled' && mattSkills.length) {
      errors.push('Matt library materialization remains present while disabled');
    }
    const skillRoot = clientSkillDirectory(repoRoot, client);
    for (const name of [...spSkills, ...mattSkills]) {
      if (!skillRoot || !fs.existsSync(path.join(skillRoot, name, 'SKILL.md'))) {
        errors.push(`${name} materialization is missing SKILL.md`);
      }
    }
    for (const name of mattSkills) {
      const skillFile = skillRoot && path.join(skillRoot, name, 'SKILL.md');
      const text = skillFile && fs.existsSync(skillFile) ? fs.readFileSync(skillFile, 'utf8') : '';
      if (!/^disable-model-invocation:\s*true\s*$/m.test(text)) {
        errors.push(`${name} is missing user-invoked metadata`);
      }
    }
    for (const bootstrap of ['using-superpowers', 'brainstorming', 'writing-plans']) {
      if (skillRoot && fs.existsSync(path.join(skillRoot, bootstrap))) {
        errors.push(`legacy bootstrap materialization remains: ${bootstrap}`);
      }
    }
  }
  return {
    ok: errors.length === 0,
    root: repoRoot,
    client: client || null,
    effective: profile?.effective || null,
    runtime_hash: runtimeHash,
    errors,
  };
}

function optionValue(args, name, fallback = undefined) {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
}

function withoutOptions(args, optionsWithValues, flags = []) {
  const result = [];
  for (let index = 0; index < args.length; index += 1) {
    if (optionsWithValues.includes(args[index])) {
      index += 1;
    } else if (!flags.includes(args[index])) {
      result.push(args[index]);
    }
  }
  return result;
}

export function runCli(argv = process.argv.slice(2)) {
  const [command, ...args] = argv;
  const root = optionValue(args, '--root', process.cwd());
  if (command === 'show') {
    const report = loadProfile({ root });
    if (args.includes('--json')) console.log(JSON.stringify(report, null, 2));
    else {
      for (const key of PROFILE_KEYS) {
        console.log(`${key}: ${report.effective[key]} (${report.sources[key]})`);
      }
      console.log(`reply_style note: ${report.notes.reply_style}`);
    }
    return 0;
  }
  if (command === 'get') {
    const positional = withoutOptions(args, ['--root']);
    const key = positional[0];
    if (!PROFILE_KEYS.includes(key)) throw new Error(`unknown profile key ${key}`);
    console.log(loadProfile({ root }).effective[key]);
    return 0;
  }
  if (command === 'set') {
    const positional = withoutOptions(args, ['--root'], ['--local']);
    if (positional.length !== 2) throw new Error('usage: profile set <key> <value> [--root <repo>] [--local]');
    console.log(JSON.stringify(setProfileValue({
      root,
      key: positional[0],
      value: positional[1],
      local: args.includes('--local'),
    }), null, 2));
    return 0;
  }
  if (command === 'export') {
    if (!args.includes('--root')) throw new Error('profile export requires --root <subject-root>');
    const client = optionValue(args, '--client');
    if (!client) throw new Error('profile export requires --client <client>');
    console.log(JSON.stringify(exportProfile({ root, client }), null, 2));
    return 0;
  }
  if (command === 'check') {
    const report = checkProfile({ root, client: optionValue(args, '--client') });
    console.log(JSON.stringify(report, null, 2));
    return report.ok ? 0 : 1;
  }
  throw new Error('usage: profile {show|get|set|check|export}');
}

const isMain = process.argv[1]
  && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  try {
    process.exitCode = runCli();
  } catch (error) {
    console.error(error.message);
    process.exitCode = 2;
  }
}
