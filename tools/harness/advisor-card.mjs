#!/usr/bin/env node
// Harness-dev advisor card — dispatch-time tier consultation (mechanism B).
// On subagent creation this injects a TOOL-AGNOSTIC, SELF-ASSESS tier card as
// additionalContext so the model-tier lookup is on the table at dispatch time.
// The ONLY orchestrator-facing pre-spawn surface is:
//   - Claude Code: `PreToolUse` matcher Task/Agent (fires at the orchestrator's
//     spawn decision point BEFORE the spawn tool runs; task text via tool_input).
//     additionalContext returns to the ORCHESTRATOR so it can shape subagent
//     form / model / prompt-thickness.
// Codex/Cursor have NO orchestrator-facing pre-spawn hook (Codex `SubagentStart`
// delivers context to the CHILD post-decision; Cursor `preToolUse`/`subagentStart`
// are allow/deny only). Their advisor card rides the prompt-submit router instead
// (see prompt-skill-router.mjs dispatch-intent path), NOT this script.
// It carries NO per-client available-model list / allowlist: the executing model
// self-assesses its OWN menu against the model-tier-prompting roster ordering.
// Advisory only — never denies/blocks the dispatch. Always emitted on qualify.

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, '../..');
// Methodology SSOT lives under agent-kit/skills/skills/ (submodule).
const SKILL_DIR = 'agent-kit/skills/skills/model-tier-prompting';
const SKILL_MD = `${SKILL_DIR}/SKILL.md`;

/**
 * PURE. Build the advisor-card string to inject at dispatch time.
 * Tool-agnostic + self-assess: no hardcoded model names / per-client allowlist.
 * Points at the skill for the volatile roster instead of inlining it.
 * @param {{ taskText?: string }} [opts]
 * @returns {string}
 */
export function generateAdvisorCard({ taskText = '' } = {}) {
  const task = String(taskText || '').replace(/\s+/g, ' ').trim();
  const taskLine = task
    ? `本次子代理任務：${task.length > 200 ? `${task.slice(0, 200)}…` : task}`
    : '本次正在創建一個子代理（Task/Agent）。';

  return [
    'Harness-dev Advisor Card（dispatch-time tier consultation）。',
    taskLine,
    '在敲定「子代理形態 / 模型 / 提示厚度」前，先做一次層級自評（把 model-tier 查表強制上桌）。',
    '',
    '三層速查（排序依據見 skill roster，勿在此硬編任何模型清單）：',
    '- Frontier-agentic：最強推理 / 長程自主。用於開放式難題、需深度規劃。提示宜「拆腳手架」：給 why / 邊界 / 證據錨定，少步驟細節。',
    '- 主力（workhorse）：可靠執行主力。用於多數實作 / 重構 / 審查。提示中等：目標 + 關鍵約束 + 驗收標準。',
    '- 快速經濟：量大、格式固定、低歧義。提示宜「加腳手架」：明確步驟 / 格式契約 / few-shot，並配外置 verifier。',
    '',
    '自評步驟（self-assess；harness 不維護任何 per-client 可用模型清單）：',
    '1. 列出你此刻實際可選的模型選單（你比 harness 更清楚自己有什麼）。',
    '2. 依 roster 的模型名 + Intelligence Index 由高到低排序；名不在表上者，跑 SKILL.md 的歸層探針回填。',
    '3. 選當前最強可用者作 advisor / executor（原生 advisor 若客戶端支援，另要求 advisor 能力 ≥ 主模型；指定者不可用時回退到選單中次高可用者）。',
    '4. 依「任務難度 × roster 排序」為子代理選形態（一次性 headless 派工 / 互動 session / 平行 fan-out）＋ 對應提示厚度。',
    '',
    `深度依據（勿複製 volatile roster 進本卡片，避免過時）：${SKILL_MD}`,
    `（roster 排序見 ${SKILL_DIR}/references/model-roster.md；派工契約見 ${SKILL_DIR}/references/delegation-prompts.md）`,
  ].join('\n');
}

function isDispatchToolName(toolName = '') {
  // Claude documents the subagent-spawning tool as "Agent"; the conventional
  // tool_name is "Task". Accept either (unanchored, case-insensitive).
  return /task|agent/i.test(String(toolName || ''));
}

/**
 * Gate: only the orchestrator-facing pre-spawn event counts.
 * - Claude: `PreToolUse` + Task/Agent tool (orchestrator spawn decision point,
 *   BEFORE the spawn tool runs). This is the only true pre-spawn injection.
 * Codex `SubagentStart` (child-facing, post-decision) is intentionally NOT here.
 * @param {string} eventName
 * @param {string} toolName
 * @returns {boolean}
 */
export function isDispatchEvent(eventName = '', toolName = '') {
  const e = String(eventName);
  // Claude fires PreToolUse with the Task/Agent tool at the dispatch point.
  return e === 'PreToolUse' && isDispatchToolName(toolName);
}

function extractTaskText(payload = {}) {
  const ti = payload.tool_input ?? payload.toolInput ?? {};
  return (
    ti.prompt
    ?? ti.description
    ?? payload.prompt
    ?? payload.description
    ?? ''
  );
}

/**
 * @param {{ eventName?: string, payload?: object }} [opts]
 * @returns {{ shouldInject: boolean, eventName: string, taskText: string, additionalContext: string }}
 */
export function analyzeDispatchContext({ eventName = '', payload = {} } = {}) {
  const toolName = payload.tool_name ?? payload.toolName ?? '';
  const shouldInject = isDispatchEvent(eventName, toolName);
  const taskText = shouldInject ? extractTaskText(payload) : '';
  return {
    shouldInject,
    eventName,
    taskText,
    additionalContext: shouldInject ? generateAdvisorCard({ taskText }) : '',
  };
}

/**
 * @param {{ eventName?: string, payload?: object }} [opts]
 * @returns {object|null} Claude PreToolUse additionalContext shape (returned to
 *   the ORCHESTRATOR before the spawn tool runs), or null on non-dispatch.
 */
export function buildHookResponse({ eventName = '', payload = {} } = {}) {
  const analysis = analyzeDispatchContext({ eventName, payload });
  if (!analysis.shouldInject) return null;
  const additionalContext = analysis.additionalContext;
  // Only PreToolUse(Task|Agent) qualifies, so hookEventName is always PreToolUse.
  return {
    additionalContext,
    additional_context: additionalContext,
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      additionalContext,
    },
  };
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
  const eventName = payload.hook_event_name || payload.hookEventName || payload.event || '';
  const resp = buildHookResponse({ eventName, payload });
  if (!resp) {
    // Not a dispatch event — no-op.
    process.stdout.write('{}\n');
    return;
  }

  // Always emit on qualify: every dispatch decision should see the tier card
  // (no session dedup — re-injection at each spawn point is the point).
  process.stdout.write(`${JSON.stringify(resp)}\n`);
}

const isMain = process.argv[1]
  && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMain) {
  main().catch((err) => {
    process.stderr.write(`advisor-card failed: ${err.message}\n`);
    // advisory: never block the dispatch
    process.stdout.write('{}\n');
    process.exitCode = 0;
  });
}

void REPO_ROOT;
