#!/usr/bin/env node
// Harness-dev prompt-skill router — advisory UserPromptSubmit / beforeSubmitPrompt
// injection for model-tier-prompting + refine (intent rules ported from an
// upstream subject workspace, 2026-07-09). Does NOT deny; only suggests skills
// via context. Session-deduped via /tmp flag so we don't re-nag within the same
// shell tree.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, '../..');
// Methodology SSOT lives under agent-kit/skills/skills/ (submodule).
const SKILL_PREFIX = 'agent-kit/skills/skills';

export const skillCatalog = new Map([
  ['model-tier-prompting', {
    path: `${SKILL_PREFIX}/model-tier-prompting/SKILL.md`,
    reason: 'Tier-aware prompt design/rewrite: dispatch prompts, migrating prompts between models, prompt anti-pattern audit.',
  }],
  ['refine', {
    path: `${SKILL_PREFIX}/refine/SKILL.md`,
    reason: 'Expand a rough idea into a confirmable task brief before starting work.',
  }],
]);

function hasAny(text, patterns) {
  return patterns.some((re) => re.test(text));
}

function addSkill(selected, name) {
  if (selected.some((s) => s.name === name)) return;
  const entry = skillCatalog.get(name);
  if (!entry) return;
  selected.push({ name, path: entry.path, reason: entry.reason });
}

/**
 * Port of upstream applyPromptRules for model-tier-prompting + refine only.
 * @param {string} text
 * @param {string} eventName
 * @returns {{ name: string, path: string, reason: string }[]}
 */
export function selectPromptSkills(text = '', eventName = 'UserPromptSubmit') {
  const selected = [];
  const raw = String(text || '');

  // refine（B 顯式入口）
  if (/^\s*\/refine\b|需求寫清楚|需求写清楚|展開成(?:任務書|规格|規格|spec)|展开成(?:任务书|规格|spec)/i.test(raw)) {
    addSkill(selected, 'refine');
  }

  // refine（C 薄提示大任務啟發式）：僅 UserPromptSubmit / beforeSubmitPrompt
  if (/UserPromptSubmit|beforeSubmitPrompt/i.test(eventName)) {
    const trimmed = raw.trim();
    const isSlash = trimmed.startsWith('/');
    const followUp = /^(?:繼續|继续|好的?|ok(?:ay)?|go|do it|yes|嗯|對|对|不用|先這樣|先这样|commit|push|接著|接着|謝謝|谢谢|thanks)/i.test(trimmed);
    const buildIntent = /(?:實作|实作|實現|实现|開發|开发|做一個|做个|做一个|加一個|加個|加个|新增|支持|支援|重構|重构|修復|修复|implement|build a|add a|create a|refactor)/i.test(trimmed);
    const hasAcceptance = /(?:驗收|验收|測試|测试|期望|成功標準|成功标准|不做|邊界|边界|規格|规格|spec|acceptance|criteria)/i.test(trimmed);
    const promptDomain = /提示詞|提示词|prompt/i.test(trimmed);
    if (!isSlash && !followUp && trimmed.length >= 4 && trimmed.length <= 120
      && buildIntent && !hasAcceptance && !promptDomain) {
      addSkill(selected, 'refine');
    }
  }

  // model-tier-prompting：提示詞優化/設計/遷移、派工 prompt
  // `prompt(?:s)?(?![_a-z])` 守門：snake_case identifier 不誤射
  if (hasAny(raw, [/(?:提示詞|提示词|prompt)\s*(?:工程|engineering)|(?:優化|优化|改寫|改写|重寫|重写|遷移|迁移|審計|审计|設計|设计|rewrite|improve|optimi[sz]e|migrate)[^\n]{0,12}(?:提示詞|提示词|system prompt|prompt(?:s)?(?![_a-z]))|(?:提示詞|提示词|prompt(?:s)?(?![_a-z]))[^\n]{0,16}(?:優化|优化|改寫|改写|重寫|重写|遷移|迁移|反模式|派給|派给)|(?:派工|委派|子代理|subagent|dispatch)[^\n]{0,20}prompt(?:s)?(?![_a-z])|model[- ]tier|模型分層|模型分层/i])) {
    addSkill(selected, 'model-tier-prompting');
  }

  return selected;
}

export function buildAdditionalContext(selected, eventName = 'UserPromptSubmit') {
  if (!selected.length) return '';
  const skillLines = selected.map((s) => `- ${s.name}: ${s.path} (${s.reason})`);
  return [
    `Harness-dev Prompt Skill Router matched ${eventName}.`,
    'Before responding or editing, load and follow these SKILL.md files if they are not already active:',
    ...skillLines,
    'Usage rule: if there is even a 1% chance a matched skill applies, read it first and explicitly follow it.',
  ].join('\n');
}

export function analyzePromptSkillContext({
  eventName = 'UserPromptSubmit',
  payload = {},
} = {}) {
  const text = payload.prompt
    ?? payload.user_prompt
    ?? payload.message
    ?? payload.content
    ?? '';
  const selected = selectPromptSkills(text, eventName);
  const additionalContext = buildAdditionalContext(selected, eventName);
  return {
    shouldInject: selected.length > 0,
    eventName,
    skills: selected,
    additionalContext,
  };
}

function isCursorPromptEvent(eventName) {
  // Case-sensitive: /userPromptSubmit/i would also match Claude's UserPromptSubmit.
  return eventName === 'beforeSubmitPrompt' || eventName === 'userPromptSubmit';
}

function isPromptSubmitEvent(eventName) {
  return (
    eventName === 'UserPromptSubmit'
    || eventName === 'userPromptSubmit'
    || eventName === 'beforeSubmitPrompt'
  );
}

export function buildHookResponse({ eventName = 'UserPromptSubmit', payload = {} } = {}) {
  const analysis = analyzePromptSkillContext({ eventName, payload });
  if (!analysis.shouldInject) return null;
  const additionalContext = analysis.additionalContext;
  if (isCursorPromptEvent(eventName)) {
    // Cursor beforeSubmitPrompt: continue + agent_message (advisory; never block).
    return {
      continue: true,
      agent_message: additionalContext,
      additionalContext,
      additional_context: additionalContext,
    };
  }
  return {
    additionalContext,
    additional_context: additionalContext,
    hookSpecificOutput: {
      hookEventName: eventName || 'UserPromptSubmit',
      additionalContext,
    },
  };
}

function sessionFlagPath(payload = {}) {
  const sid = payload.session_id ?? payload.sessionId ?? process.ppid ?? 'anon';
  return path.join(os.tmpdir(), `harness-dev-prompt-skill-${sid}.json`);
}

function loadInjected(flagPath) {
  try {
    return JSON.parse(fs.readFileSync(flagPath, 'utf8'));
  } catch {
    return { injected: {} };
  }
}

function saveInjected(flagPath, state) {
  try {
    fs.writeFileSync(flagPath, JSON.stringify(state));
  } catch {
    // best-effort; advisory only
  }
}

function filterAlreadyInjected(selected, state, now = Date.now()) {
  const TTL = 2 * 60 * 60 * 1000;
  return selected.filter((s) => {
    const prev = state.injected[s.name];
    return !(typeof prev === 'number' && now - prev < TTL);
  });
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks).toString('utf8');
}

async function main() {
  let payload = {};
  const raw = await readStdin();
  if (raw.trim()) {
    try {
      payload = JSON.parse(raw);
    } catch {
      process.stdout.write('{}\n');
      return;
    }
  }
  const eventName = payload.hook_event_name || payload.hookEventName || payload.event || 'UserPromptSubmit';
  // Only act on prompt-submit events (Claude/Codex PascalCase + Cursor camelCase).
  if (raw.trim() && eventName && !isPromptSubmitEvent(eventName)) {
    process.stdout.write('{}\n');
    return;
  }

  const normalizedEvent = isCursorPromptEvent(eventName) ? eventName : 'UserPromptSubmit';
  const analysis = analyzePromptSkillContext({ eventName: normalizedEvent, payload });
  if (!analysis.shouldInject) {
    // Cursor beforeSubmitPrompt still needs continue:true when we no-op.
    if (isCursorPromptEvent(eventName)) {
      process.stdout.write(JSON.stringify({ continue: true }) + '\n');
      return;
    }
    process.stdout.write('{}\n');
    return;
  }

  const flagPath = sessionFlagPath(payload);
  const state = loadInjected(flagPath);
  const now = Date.now();
  const fresh = filterAlreadyInjected(analysis.skills, state, now);
  if (fresh.length === 0) {
    if (isCursorPromptEvent(eventName)) {
      process.stdout.write(JSON.stringify({ continue: true }) + '\n');
      return;
    }
    process.stdout.write('{}\n');
    return;
  }
  for (const s of fresh) state.injected[s.name] = now;
  saveInjected(flagPath, state);

  // Rebuild with fresh-only skills (session dedupe may have dropped some).
  const additionalContext = buildAdditionalContext(fresh, normalizedEvent);
  const out = isCursorPromptEvent(eventName)
    ? {
        continue: true,
        agent_message: additionalContext,
        additionalContext,
        additional_context: additionalContext,
      }
    : {
        additionalContext,
        additional_context: additionalContext,
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext,
        },
      };
  process.stdout.write(`${JSON.stringify(out)}\n`);
}

const isMain = process.argv[1]
  && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMain) {
  main().catch((err) => {
    process.stderr.write(`prompt-skill-router failed: ${err.message}\n`);
    // advisory: never block the prompt
    process.stdout.write('{}\n');
    process.exitCode = 0;
  });
}

void REPO_ROOT;
