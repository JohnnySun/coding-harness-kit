#!/usr/bin/env node
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  analyzePromptSkillContext,
  buildHookResponse,
  selectPromptSkills,
} from './prompt-skill-router.mjs';

test('routes prompt-optimization / dispatch-prompt / prompt-migration intents to model-tier-prompting', () => {
  const hits = (prompt) => selectPromptSkills(prompt, 'UserPromptSubmit')
    .map((s) => s.name).includes('model-tier-prompting');

  assert.ok(hits('幫我優化這段提示詞，目標模型是 haiku'));
  assert.ok(hits('要派子代理跑批量任務，幫我把派工 prompt 寫好'));
  assert.ok(hits('migrate this system prompt to the new model'));
  assert.ok(hits('prompt engineering 有沒有分層的方法'));
  assert.ok(hits('這段 review prompt 遷移到新模型後召回率變低'));
});

test('snake_case prompt identifiers and unrelated asks do not misfire model-tier-prompting', () => {
  const miss = (prompt) => selectPromptSkills(prompt, 'UserPromptSubmit')
    .map((s) => s.name).includes('model-tier-prompting');

  assert.ok(!miss('命中率掉了，查一下 prompt_cache_key 的渠道親和'));
  assert.ok(!miss('看一下 prompt_strategy 的水位線邏輯'));
  assert.ok(!miss('幫我修一下登入頁的 bug'));
});

test('routes /refine and thin-big-task prompts to the refine skill', () => {
  const hits = (prompt) => selectPromptSkills(prompt, 'UserPromptSubmit')
    .map((s) => s.name).includes('refine');

  assert.ok(hits('/refine 做一個角色卡分享功能'));
  assert.ok(hits('幫我做一個角色收藏夾功能'));
  assert.ok(hits('加個深色模式'));
  assert.ok(hits('幫我把這個需求寫清楚'));
});

test('follow-ups, prompt-domain asks, and spec-complete asks do not misfire refine', () => {
  const hits = (prompt) => selectPromptSkills(prompt, 'UserPromptSubmit')
    .map((s) => s.name).includes('refine');

  assert.ok(!hits('繼續'));
  assert.ok(!hits('commit 一下'));
  assert.ok(!hits('幫我優化這段提示詞，目標模型是 haiku'));
  assert.ok(!hits('做一個匯出功能：驗收標準是 npm test 全綠、支援 csv 與 json 兩種格式，本次不做批量匯出'));
  assert.ok(!hits('這個 bug 是什麼原因？'));
});

test('analyzePromptSkillContext builds injectable additionalContext with Harness-dev skill paths', () => {
  const analysis = analyzePromptSkillContext({
    eventName: 'UserPromptSubmit',
    payload: { prompt: '幫我優化這段提示詞，目標模型是 haiku' },
  });
  assert.equal(analysis.shouldInject, true);
  assert.ok(analysis.skills.some((s) => s.name === 'model-tier-prompting'));
  assert.match(analysis.additionalContext, /model-tier-prompting/);
  assert.match(
    analysis.additionalContext,
    /agent-kit\/skills\/skills\/model-tier-prompting\/SKILL\.md/,
  );
  assert.match(analysis.additionalContext, /Harness-dev Prompt Skill Router/);
});

test('thin-task refine heuristic is prompt-submit-only', () => {
  const thin = '幫我做一個角色收藏夾功能';
  assert.ok(selectPromptSkills(thin, 'UserPromptSubmit').some((s) => s.name === 'refine'));
  assert.ok(selectPromptSkills(thin, 'beforeSubmitPrompt').some((s) => s.name === 'refine'));
  // PreToolUse with build verbs in command text must not trigger thin-task heuristic
  assert.ok(!selectPromptSkills('git add -A && git commit -m "add dark mode"', 'PreToolUse')
    .some((s) => s.name === 'refine'));
});

test('buildHookResponse uses Claude additionalContext shape for UserPromptSubmit', () => {
  const resp = buildHookResponse({
    eventName: 'UserPromptSubmit',
    payload: { prompt: '幫我優化這段提示詞' },
  });
  assert.ok(resp);
  assert.ok(resp.additionalContext);
  assert.equal(resp.hookSpecificOutput.hookEventName, 'UserPromptSubmit');
  assert.equal(resp.continue, undefined);
});

test('buildHookResponse uses Cursor continue+agent_message for beforeSubmitPrompt', () => {
  const resp = buildHookResponse({
    eventName: 'beforeSubmitPrompt',
    payload: { prompt: '幫我優化這段提示詞' },
  });
  assert.ok(resp);
  assert.equal(resp.continue, true);
  assert.match(resp.agent_message, /model-tier-prompting/);
});
