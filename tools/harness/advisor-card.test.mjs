#!/usr/bin/env node
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  analyzeDispatchContext,
  buildHookResponse,
  generateAdvisorCard,
  isDispatchEvent,
} from './advisor-card.mjs';

test('generateAdvisorCard states the three tiers compactly', () => {
  const card = generateAdvisorCard({ taskText: '批量整理 changelog' });
  assert.match(card, /Frontier-agentic/);
  assert.match(card, /主力/);
  assert.match(card, /快速經濟/);
});

test('generateAdvisorCard carries the self-assess instruction (no harness allowlist)', () => {
  const card = generateAdvisorCard({ taskText: 'x' });
  assert.match(card, /self-assess/i);
  assert.match(card, /列出你此刻實際可選的模型選單/);
  assert.match(card, /Intelligence Index/);
  // Fallback-to-strongest-available is an instruction to the model.
  assert.match(card, /最強可用|次高可用/);
});

test('generateAdvisorCard points at the skill instead of inlining the roster', () => {
  const card = generateAdvisorCard({});
  assert.match(card, /agent-kit\/skills\/skills\/model-tier-prompting\/SKILL\.md/);
  assert.match(card, /references\/model-roster\.md/);
});

test('generateAdvisorCard hardcodes NO model names / allowlist (stays tool-agnostic)', () => {
  const card = generateAdvisorCard({ taskText: 'anything' });
  // Roster is volatile → must not be baked into the card.
  assert.doesNotMatch(card, /Opus|Sonnet|Haiku|Claude|GPT-|Grok|Fable|Gemini|Llama|Qwen|DeepSeek/i);
});

test('generateAdvisorCard recommends subagent form + prompt thickness per tier', () => {
  const card = generateAdvisorCard({ taskText: 'x' });
  assert.match(card, /拆腳手架/);
  assert.match(card, /加腳手架/);
  assert.match(card, /headless|fan-out|互動 session/);
});

test('generateAdvisorCard embeds the dispatch task text', () => {
  const card = generateAdvisorCard({ taskText: '幫我審查這個 PR 的安全性' });
  assert.match(card, /幫我審查這個 PR 的安全性/);
});

test('isDispatchEvent only fires on PreToolUse + Task/Agent tool', () => {
  assert.equal(isDispatchEvent('PreToolUse', 'Task'), true);
  assert.equal(isDispatchEvent('PreToolUse', 'Agent'), true);
  assert.equal(isDispatchEvent('PreToolUse', 'Bash'), false);
  assert.equal(isDispatchEvent('PreToolUse', 'Write'), false);
  assert.equal(isDispatchEvent('UserPromptSubmit', 'Task'), false);
  assert.equal(isDispatchEvent('SubagentStop', ''), false);
  assert.equal(isDispatchEvent('', ''), false);
});

test('analyzeDispatchContext injects on PreToolUse+Task and extracts tool_input.prompt', () => {
  const analysis = analyzeDispatchContext({
    eventName: 'PreToolUse',
    payload: { tool_name: 'Task', tool_input: { prompt: '跑批量 lint 修復', description: 'lint' } },
  });
  assert.equal(analysis.shouldInject, true);
  assert.equal(analysis.taskText, '跑批量 lint 修復');
  assert.match(analysis.additionalContext, /跑批量 lint 修復/);
  assert.match(analysis.additionalContext, /Frontier-agentic/);
});

test('analyzeDispatchContext falls back to tool_input.description when prompt absent', () => {
  const analysis = analyzeDispatchContext({
    eventName: 'PreToolUse',
    payload: { tool_name: 'Agent', tool_input: { description: '安全審查' } },
  });
  assert.equal(analysis.shouldInject, true);
  assert.equal(analysis.taskText, '安全審查');
});

test('analyzeDispatchContext no-ops on Bash / prompt-submit / empty', () => {
  const bash = analyzeDispatchContext({
    eventName: 'PreToolUse',
    payload: { tool_name: 'Bash', tool_input: { command: 'ls' } },
  });
  assert.equal(bash.shouldInject, false);
  assert.equal(bash.additionalContext, '');

  const prompt = analyzeDispatchContext({
    eventName: 'UserPromptSubmit',
    payload: { prompt: '做一個功能' },
  });
  assert.equal(prompt.shouldInject, false);

  const empty = analyzeDispatchContext({});
  assert.equal(empty.shouldInject, false);
});

test('buildHookResponse uses Claude PreToolUse additionalContext shape', () => {
  const resp = buildHookResponse({
    eventName: 'PreToolUse',
    payload: { tool_name: 'Task', tool_input: { prompt: '派工任務' } },
  });
  assert.ok(resp);
  assert.ok(resp.additionalContext);
  assert.equal(resp.hookSpecificOutput.hookEventName, 'PreToolUse');
  assert.match(resp.hookSpecificOutput.additionalContext, /Advisor Card/);
});

test('buildHookResponse returns null (no-op) on non-dispatch events', () => {
  assert.equal(
    buildHookResponse({ eventName: 'PreToolUse', payload: { tool_name: 'Bash' } }),
    null,
  );
  assert.equal(
    buildHookResponse({ eventName: 'UserPromptSubmit', payload: { prompt: 'x' } }),
    null,
  );
});
