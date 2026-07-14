#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { loadProfile } from './agent-profile.mjs';

const LOCAL_SKILL_PREFIX = 'agent-kit/skills/skills';
const CLIENT_SKILL_PREFIX = '<client-skills>';

export const skillCatalog = new Map([
  ['model-tier-prompting', {
    path: `${LOCAL_SKILL_PREFIX}/model-tier-prompting/SKILL.md`,
    reason: 'The task concerns model-aware prompt design or subagent dispatch.',
  }],
  ['refine', {
    path: `${LOCAL_SKILL_PREFIX}/refine/SKILL.md`,
    reason: 'The request is a thin implementation idea whose boundaries may need clarification.',
  }],
  ['test-driven-development', {
    path: `${CLIENT_SKILL_PREFIX}/test-driven-development/SKILL.md`,
    reason: 'The task changes maintained behavior and can be specified with a failing test first.',
  }],
  ['systematic-debugging', {
    path: `${CLIENT_SKILL_PREFIX}/systematic-debugging/SKILL.md`,
    reason: 'The request asks for root-cause diagnosis of a reproducible failure.',
  }],
  ['code-review', {
    path: `${LOCAL_SKILL_PREFIX}/code-review/SKILL.md`,
    reason: 'The request is an explicit code or merge-readiness review.',
  }],
  ['verification-before-completion', {
    path: `${CLIENT_SKILL_PREFIX}/verification-before-completion/SKILL.md`,
    reason: 'The request is approaching a completion or commit claim where fresh evidence is useful.',
  }],
  ['harness-operate', {
    path: `${LOCAL_SKILL_PREFIX}/harness-operate/SKILL.md`,
    reason: 'The task changes a harness hook, gate, installer, or trusted-suite mechanism.',
  }],
  ['harness-builder', {
    path: `${LOCAL_SKILL_PREFIX}/harness-builder/SKILL.md`,
    reason: 'The task designs or assesses a coding harness control surface.',
  }],
]);

function hasAny(text, patterns) {
  return patterns.some((pattern) => pattern.test(text));
}

function addSkill(selected, name) {
  if (selected.length >= 2 || selected.some((skill) => skill.name === name)) return;
  const entry = skillCatalog.get(name);
  if (entry) selected.push({ name, ...entry });
}

function scaffoldValue(profile) {
  return profile?.process_scaffold || profile?.effective?.process_scaffold || 'lean';
}

export function selectPromptSkills(
  text = '',
  eventName = 'UserPromptSubmit',
  profile = { process_scaffold: 'lean' },
) {
  const selected = [];
  const raw = String(text || '');
  const trimmed = raw.trim();
  if (!/UserPromptSubmit|userPromptSubmit|beforeSubmitPrompt/.test(eventName)) return selected;

  const isSlash = trimmed.startsWith('/');
  const followUp = /^(?:繼續|继续|好的?|ok(?:ay)?|go|do it|yes|嗯|對|对|不用|先這樣|先这样|接著|接着|謝謝|谢谢|thanks)[.!。！\s]*$/i.test(trimmed);
  const questionOnly = /^(?:what|why|when|where|who|how|is|are|does|do|can|could|would|這|这|為什麼|为什么|什麼|什么|如何|哪)[^\n]*(?:\?|？)$/i.test(trimmed);
  if (!trimmed || followUp || questionOnly) return selected;

  if (/^\s*\/refine\b|需求寫清楚|需求写清楚|展開成(?:任務書|规格|規格|spec)|展开成(?:任务书|规格|spec)/i.test(raw)) {
    addSkill(selected, 'refine');
  }

  const buildIntent = /(?:實作|实作|實現|实现|開發|开发|做一個|做个|做一个|加一個|加個|加个|新增|支持|支援|重構|重构|修復|修复|implement|build a|add a|create a|refactor)/i.test(trimmed);
  const hasAcceptance = /(?:驗收|验收|測試|测试|tests?|期望|成功標準|成功标准|不做|邊界|边界|規格|规格|spec|acceptance|criteria)/i.test(trimmed);
  const promptDomain = /提示詞|提示词|system prompt|prompt(?:s)?(?![_a-z])/i.test(trimmed);
  if (!isSlash && trimmed.length >= 4 && trimmed.length <= 120
      && buildIntent && !hasAcceptance && !promptDomain) {
    addSkill(selected, 'refine');
  }

  if (hasAny(raw, [
    /(?:提示詞|提示词|prompt)\s*(?:工程|engineering)/i,
    /(?:優化|优化|改寫|改写|重寫|重写|遷移|迁移|審計|审计|設計|设计|rewrite|improve|optimi[sz]e|migrate)[^\n]{0,12}(?:提示詞|提示词|system prompt|prompt(?:s)?(?![_a-z]))/i,
    /(?:提示詞|提示词|prompt(?:s)?(?![_a-z]))[^\n]{0,16}(?:優化|优化|改寫|改写|重寫|重写|遷移|迁移|反模式|派給|派给)/i,
    /(?:派工|委派|子代理|subagent|dispatch)[^\n]{0,20}prompt(?:s)?(?![_a-z])/i,
    /model[- ]tier|模型分層|模型分层/i,
  ])) {
    addSkill(selected, 'model-tier-prompting');
  }

  const harnessIntent = /(?:coding[- ]?harness|harness|hook|gate|trusted suite|可信集|私有樹|私有树|edit.?verify|agent[- ]kit|profile)/i.test(trimmed);
  const harnessDesign = /(?:design|設計|设计|評估|评估|architecture|方案)/i.test(trimmed);
  if (harnessIntent) addSkill(selected, harnessDesign ? 'harness-builder' : 'harness-operate');

  const debugIntent = /(?:debug|diagnos|root cause|原因|崩潰|崩溃|crash|failing|failure|intermittent|broken|報錯|报错|回歸|回归)/i.test(trimmed);
  if (debugIntent) addSkill(selected, 'systematic-debugging');

  const reviewIntent = /(?:review (?:this |the )?(?:diff|code|pr)|code review|merge readiness|merge-ready|審查.*(?:代碼|代码|diff)|評審.*(?:代碼|代码|diff))/i.test(trimmed);
  if (reviewIntent) addSkill(selected, 'code-review');

  const closingIntent = /(?:implementation is complete|ready to commit|before (?:i )?commit|commit 一下|push 一下|完成聲明|完成声明|準備提交|准备提交|提交前|claimed.done|verify it before)/i.test(trimmed);
  if (closingIntent) addSkill(selected, 'verification-before-completion');

  const maintainedBehavior = buildIntent && hasAcceptance;
  if (maintainedBehavior && !debugIntent && !reviewIntent && !harnessIntent) {
    addSkill(selected, 'test-driven-development');
  }

  const scaffold = scaffoldValue(profile);
  if (scaffold === 'guided' && buildIntent && !hasAcceptance && selected.length < 2) {
    addSkill(selected, 'refine');
  }
  if (scaffold === 'structured'
      && /(?:完整流程|完整过程|step[- ]by[- ]step process|structured workflow)/i.test(trimmed)
      && selected.length < 2) {
    addSkill(selected, harnessIntent ? 'harness-builder' : 'refine');
  }
  return selected;
}

export function buildAdditionalContext(
  selected,
  eventName = 'UserPromptSubmit',
  { processMenu = false } = {},
) {
  if (!selected.length && !processMenu) return '';
  const skillLines = selected.map(
    (skill) => `- ${skill.name}: ${skill.reason} (${skill.path})`,
  );
  const lines = [
    `Advisory profile router observed a ${eventName} task shape.`,
    ...skillLines,
  ];
  if (processMenu) {
    lines.push(
      'Optional process menu: clarify scope if needed; use a failing test for maintained behavior; gather fresh verification and review evidence before closing.',
    );
  }
  lines.push('These skills and process options may help; use only what fits the task and current context.');
  return lines.join('\n');
}

function payloadText(payload) {
  return payload.prompt
    ?? payload.user_prompt
    ?? payload.message
    ?? payload.content
    ?? '';
}

export function analyzePromptSkillContext({
  eventName = 'UserPromptSubmit',
  payload = {},
  profile,
} = {}) {
  const text = payloadText(payload);
  const activeProfile = profile ?? payload.profile;
  const selected = selectPromptSkills(text, eventName, activeProfile);
  const processMenu = scaffoldValue(activeProfile) === 'structured'
    && /(?:完整流程|完整过程|step[- ]by[- ]step process|structured workflow)/i.test(text);
  return {
    shouldInject: selected.length > 0 || processMenu,
    eventName,
    skills: selected,
    processMenu,
    additionalContext: buildAdditionalContext(selected, eventName, { processMenu }),
  };
}

function isCursorPromptEvent(eventName) {
  return eventName === 'beforeSubmitPrompt' || eventName === 'userPromptSubmit';
}

function isPromptSubmitEvent(eventName) {
  return ['UserPromptSubmit', 'userPromptSubmit', 'beforeSubmitPrompt'].includes(eventName);
}

export function buildHookResponse({
  eventName = 'UserPromptSubmit',
  payload = {},
  profile,
} = {}) {
  const analysis = analyzePromptSkillContext({ eventName, payload, profile });
  if (!analysis.shouldInject) return null;
  const { additionalContext } = analysis;
  if (isCursorPromptEvent(eventName)) {
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
  const sessionId = payload.session_id ?? payload.sessionId ?? process.ppid ?? 'anon';
  return path.join(os.tmpdir(), `agent-profile-advisory-${sessionId}.json`);
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
    // Advisory state is best-effort and never blocks prompts.
  }
}

function filterAlreadyInjected(selected, state, now = Date.now()) {
  const ttl = 2 * 60 * 60 * 1000;
  return selected.filter((skill) => {
    const previous = state.injected[skill.name];
    return !(typeof previous === 'number' && now - previous < ttl);
  });
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));
  return Buffer.concat(chunks).toString('utf8');
}

function effectiveProfile(payload) {
  try {
    const root = payload.cwd ?? payload.workspace_root ?? process.env.AGENT_PROFILE_ROOT ?? process.cwd();
    return loadProfile({ root }).effective;
  } catch (error) {
    process.stderr.write(`profile router advisory config ignored: ${error.message}\n`);
    return { process_scaffold: 'lean' };
  }
}

export async function main() {
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
  if (raw.trim() && eventName && !isPromptSubmitEvent(eventName)) {
    process.stdout.write('{}\n');
    return;
  }
  const normalizedEvent = isCursorPromptEvent(eventName) ? eventName : 'UserPromptSubmit';
  const analysis = analyzePromptSkillContext({
    eventName: normalizedEvent,
    payload,
    profile: effectiveProfile(payload),
  });
  if (!analysis.shouldInject) {
    process.stdout.write(isCursorPromptEvent(eventName) ? '{"continue":true}\n' : '{}\n');
    return;
  }

  const flagPath = sessionFlagPath(payload);
  const state = loadInjected(flagPath);
  const now = Date.now();
  const fresh = filterAlreadyInjected(analysis.skills, state, now);
  const menuPrevious = state.injected['process-menu'];
  const freshProcessMenu = analysis.processMenu
    && !(typeof menuPrevious === 'number' && now - menuPrevious < 2 * 60 * 60 * 1000);
  if (!fresh.length && !freshProcessMenu) {
    process.stdout.write(isCursorPromptEvent(eventName) ? '{"continue":true}\n' : '{}\n');
    return;
  }
  for (const skill of fresh) state.injected[skill.name] = now;
  if (freshProcessMenu) state.injected['process-menu'] = now;
  saveInjected(flagPath, state);
  const additionalContext = buildAdditionalContext(
    fresh,
    normalizedEvent,
    { processMenu: freshProcessMenu },
  );
  const response = isCursorPromptEvent(eventName)
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
  process.stdout.write(`${JSON.stringify(response)}\n`);
}

const isMain = process.argv[1]
  && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  main().catch((error) => {
    process.stderr.write(`profile router advisory failed open: ${error.message}\n`);
    process.stdout.write('{}\n');
    process.exitCode = 0;
  });
}
