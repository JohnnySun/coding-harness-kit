#!/usr/bin/env node
// Vendored from agent-kit/skills/templates/harness-scaffold/hook-router.mjs
// Upstream sync is manual when the template changes.
// Harness-dev config: single module, test-harness.sh verify, HARNESS_SKIP escape,
// F5+ private absorb deny (no escape): subjects/** (except example),
// snapshots/**, comparisons/**. Repo-local gate-events.jsonl.
//
// Platforms: Claude Code / Codex use this file directly (PascalCase events).
// Cursor uses tools/harness/cursor-hook.mjs (camelCase + permission field).

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, '../..');

export const config = {
  // Code + harness surface that arms pending (design §3 步2).
  codeFilePattern:
    /\.(py|sh|mjs|js|ts|tsx|yaml|yml|json|md)$/i,
  armPathPattern:
    /^(tools\/|subjects\/manifest\.example\.yaml$|subjects\/manifest\.yaml$|agent-kit\/|docs\/|testdata\/|\.github\/|\.cursor\/skills\/|\.agents\/skills\/|\.claude\/skills\/|\.codex\/skills\/)/,
  moduleOf(_filePath) {
    return 'harness-dev';
  },
  verifyCommands: [
    {
      pattern: /(?:^|&&|;)\s*(?:bash\s+)?(?:\.\/)?tools\/harness\/test-harness\.sh\b/,
      modules: null,
    },
  ],
  escapeEnvVar: 'HARNESS_SKIP',
  eventLedger: path.join(REPO_ROOT, 'docs/harness/gate-events.jsonl'),
  stateDir: path.join(os.tmpdir(), 'harness-dev-hook'),
  // Private trees that must never enter git history (no HARNESS_SKIP escape).
  privateGitPathRe:
    /(?:^|[\s"'=])(?:\.\/)?(?:snapshots\/|comparisons\/|subjects\/(?!manifest\.example\.yaml(?:\s|$)))/,
};

export function logEvent(event, detail, ledgerPath = config.eventLedger) {
  try {
    fs.mkdirSync(path.dirname(ledgerPath), { recursive: true });
    fs.appendFileSync(
      ledgerPath,
      JSON.stringify({ ts: new Date().toISOString(), event, ...detail }) + '\n',
    );
  } catch {
    /* 帳本寫入失敗不阻斷主流程 */
  }
}

export function newState() {
  return { pending: {}, stopBlockedOnce: false };
}

function detectGitCommit(command) {
  return /(?:^|&&|;|\|)\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|\S*)\s+)*git\s+(?:-C\s+\S+\s+)?commit\b/.test(
    command,
  );
}

function commandTouchesPrivateGitPath(command) {
  if (!config.privateGitPathRe.test(command)) return false;
  return /(?:^|&&|;|\|)\s*(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|\S*)\s+)*git\s+(?:-C\s+\S+\s+)?(add|commit|rm|mv)\b/.test(
    command,
  );
}

function relPath(filePath) {
  const abs = path.isAbsolute(filePath) ? filePath : path.resolve(REPO_ROOT, filePath);
  if (abs.startsWith(REPO_ROOT + path.sep)) {
    return abs.slice(REPO_ROOT.length + 1).split(path.sep).join('/');
  }
  return filePath.replace(/^\.\//, '');
}

function shouldArm(filePath) {
  const rel = relPath(filePath);
  // Never arm private absorb trees (local-only).
  if (
    rel.startsWith('snapshots/') ||
    rel.startsWith('comparisons/') ||
    (rel.startsWith('subjects/') &&
      rel !== 'subjects/manifest.yaml' &&
      rel !== 'subjects/manifest.example.yaml')
  ) {
    return false;
  }
  return config.armPathPattern.test(rel) && config.codeFilePattern.test(rel);
}

function extractEditedFiles(payload) {
  const input = payload.tool_input || payload || {};
  const files = [];
  if (input.file_path) files.push(input.file_path);
  if (payload.file_path) files.push(payload.file_path);
  if (Array.isArray(input.edits)) {
    for (const e of input.edits) if (e.file_path) files.push(e.file_path);
  }
  return files;
}

function denyPreTool(reason) {
  return {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  };
}

/** Advisory only — employer/org brand bans live in AGENTS.md, not as string scanners. */
export const DESENSITIZE_ADVISORY = [
  'Harness-dev public-tree desensitize reminder:',
  'Before writing tools/docs/agent-kit public content, scrub private absorb details:',
  'no home absolute paths, no real subject id/remote/pin, no internal forge hostnames,',
  'no employer/org brand names — use generic wording (upstream subject, example remote).',
  'Do not implement brand bans as source-code string matchers (that re-leaks the token).',
  'See AGENTS.md blacklist + docs/specs/20260709-desensitize-public-tree/spec.md.',
].join(' ');

export function processEvent(payload, state, env = process.env) {
  const event = payload.hook_event_name;

  if (event === 'SessionStart') {
    return {
      state: newState(),
      response: {
        additionalContext: DESENSITIZE_ADVISORY,
        additional_context: DESENSITIZE_ADVISORY,
        hookSpecificOutput: {
          hookEventName: 'SessionStart',
          additionalContext: DESENSITIZE_ADVISORY,
        },
      },
    };
  }

  if (event === 'PostToolUse') {
    const tool = payload.tool_name || '';
    if (/^(Write|Edit|MultiEdit|NotebookEdit|apply_patch)$/.test(tool)) {
      for (const f of extractEditedFiles(payload)) {
        if (shouldArm(f)) {
          state.pending[config.moduleOf(f)] = true;
          state.stopBlockedOnce = false;
        }
      }
    }
    if (tool === 'Bash') {
      const cmd = (payload.tool_input && payload.tool_input.command) || '';
      for (const vc of config.verifyCommands) {
        if (vc.pattern.test(cmd)) {
          if (vc.modules === null) state.pending = {};
          else for (const m of vc.modules) delete state.pending[m];
        }
      }
    }
    return { state, response: {} };
  }

  if (event === 'PreToolUse' && payload.tool_name === 'Bash') {
    const cmd = (payload.tool_input && payload.tool_input.command) || '';

    // F5+: private absorb into git history — no escape
    if (commandTouchesPrivateGitPath(cmd)) {
      logEvent('private-deny', { command: cmd.slice(0, 200) });
      return {
        state,
        response: denyPreTool(
          '禁止將 subjects/**（除 manifest.example.yaml）、snapshots/**、comparisons/** 納入 git（F5+，無逃生）。僅本機產物。',
        ),
      };
    }

    if (detectGitCommit(cmd) && Object.keys(state.pending).length > 0) {
      const escape =
        new RegExp(`${config.escapeEnvVar}=`).test(cmd) || env[config.escapeEnvVar];
      const mods = Object.keys(state.pending).join(', ');
      if (escape) {
        logEvent('verify-skip', { modules: mods, command: cmd.slice(0, 200) });
        return { state, response: {} };
      }
      logEvent('commit-deny', { modules: mods });
      return {
        state,
        response: denyPreTool(
          `模組 [${mods}] 有未跑可信集的改動。先跑：bash tools/harness/test-harness.sh；` +
            `或顯式逃生：${config.escapeEnvVar}="<原因>" git commit …（自動記帳，按次）。`,
        ),
      };
    }
    return { state, response: {} };
  }

  if (event === 'Stop' || event === 'SubagentStop') {
    if (payload.stop_hook_active) return { state, response: {} };
    const mods = Object.keys(state.pending);
    if (mods.length > 0 && !state.stopBlockedOnce) {
      state.stopBlockedOnce = true;
      logEvent('stop-block', { modules: mods.join(', ') });
      return {
        state,
        response: {
          decision: 'block',
          reason:
            `以下模組改了 harness 表面但還沒跑可信集：${mods.join(', ')}。` +
            `請執行：bash tools/harness/test-harness.sh`,
        },
      };
    }
    return { state, response: {} };
  }

  return { state, response: {} };
}

function statePath(sessionId) {
  return path.join(config.stateDir, `${sessionId || `ppid-${process.ppid}`}.json`);
}

export function loadState(sessionId) {
  try {
    return JSON.parse(fs.readFileSync(statePath(sessionId), 'utf8'));
  } catch {
    return newState();
  }
}

export function saveState(sessionId, state) {
  try {
    fs.mkdirSync(config.stateDir, { recursive: true });
    fs.writeFileSync(statePath(sessionId), JSON.stringify(state));
  } catch {
    /* state 壞掉不阻斷 CLI */
  }
}

async function main() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  let payload;
  try {
    payload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    process.exit(0);
  }
  const state = loadState(payload.session_id);
  const { state: next, response } = processEvent(payload, state);
  saveState(payload.session_id, next);
  if (response && Object.keys(response).length > 0) {
    process.stdout.write(JSON.stringify(response));
  }
}

const isDirect =
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isDirect) {
  main();
}
