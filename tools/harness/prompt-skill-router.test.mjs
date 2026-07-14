#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  analyzePromptSkillContext,
  buildAdditionalContext,
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
  assert.match(analysis.additionalContext, /Advisory profile router/);
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

test('advisory copy is optional, specific, and contains no bootstrap poison', () => {
  const selected = selectPromptSkills(
    '幫我優化這段提示詞，目標模型是 haiku',
    'UserPromptSubmit',
  );
  const context = buildAdditionalContext(selected, 'UserPromptSubmit');
  assert.match(context, /observed|觀察/i);
  assert.match(context, /may help|可能有用|consider/i);
  assert.doesNotMatch(context, /before responding|回覆前|回复前|must follow|1%|不得繼續|不得继续/i);
});

test('lean routes maintained behavior, debugging, review, closing, and harness work', () => {
  const names = (prompt) => selectPromptSkills(prompt, 'UserPromptSubmit', {
    process_scaffold: 'lean',
  }).map((skill) => skill.name);

  assert.ok(names('新增匯出功能並補 integration tests').includes('test-driven-development'));
  assert.ok(names('debug this intermittent crash and find the root cause').includes('systematic-debugging'));
  assert.ok(names('review this diff for merge readiness').includes('code-review'));
  assert.ok(names('implementation is complete; verify it before I commit').includes('verification-before-completion'));
  assert.ok(names('調整 harness hook 與 gate 的行為').includes('harness-operate'));
});

test('Matt skills are never selected automatically', () => {
  const mattSkills = new Set([
    'grilling',
    'implement',
    'ask-matt',
    'prototype',
    'wayfinder',
  ]);
  for (const prompt of [
    'grill this plan',
    'implement this feature',
    'ask Matt how to model this domain',
    'prototype the UI',
  ]) {
    const selected = selectPromptSkills(prompt, 'UserPromptSubmit');
    assert.equal(selected.some((skill) => mattSkills.has(skill.name)), false);
  }
});

test('plain questions and follow-ups stay ritual-free', () => {
  for (const prompt of [
    'what does this function return?',
    '繼續',
    '謝謝',
    '這個設定值是什麼？',
  ]) {
    assert.deepEqual(selectPromptSkills(prompt, 'UserPromptSubmit'), []);
  }
});

test('explicit closing follow-up offers verification without refine ritual', () => {
  const selected = selectPromptSkills('commit 一下', 'UserPromptSubmit');
  assert.ok(selected.some((skill) => skill.name === 'verification-before-completion'));
  assert.equal(selected.some((skill) => skill.name === 'refine'), false);
});

test('all scaffold levels remain advisory and never emit deny', () => {
  for (const process_scaffold of ['lean', 'guided', 'structured']) {
    const response = buildHookResponse({
      eventName: 'beforeSubmitPrompt',
      payload: {
        prompt: '請用完整流程規劃並實作一個大型功能',
        profile: { process_scaffold },
      },
    });
    if (response) {
      assert.equal(response.continue, true);
      assert.equal(response.permissionDecision, undefined);
      assert.doesNotMatch(JSON.stringify(response), /"deny"/i);
    }
  }
});

test('guided increases advisory density for long under-specified build tasks', () => {
  const prompt = `請實作一個跨多個模組的匯出功能，${'需要協調資料來源與多個介面，'.repeat(12)}`;
  const lean = selectPromptSkills(prompt, 'UserPromptSubmit', {
    process_scaffold: 'lean',
  });
  const guided = selectPromptSkills(prompt, 'UserPromptSubmit', {
    process_scaffold: 'guided',
  });
  assert.equal(lean.some((skill) => skill.name === 'refine'), false);
  assert.equal(guided.some((skill) => skill.name === 'refine'), true);
});

test('structured emits an optional process menu only on explicit process requests', () => {
  const structured = analyzePromptSkillContext({
    eventName: 'UserPromptSubmit',
    payload: {
      prompt: '請用完整流程規劃並實作一個大型功能',
      profile: { process_scaffold: 'structured' },
    },
  });
  const lean = analyzePromptSkillContext({
    eventName: 'UserPromptSubmit',
    payload: {
      prompt: '請用完整流程規劃並實作一個大型功能',
      profile: { process_scaffold: 'lean' },
    },
  });
  assert.match(structured.additionalContext, /optional process menu/i);
  assert.doesNotMatch(lean.additionalContext, /optional process menu/i);
});

test('behavior eval: repeated route does not create a per-turn ritual', () => {
  const sessionId = `router-eval-${process.pid}-${Date.now()}`;
  const payload = JSON.stringify({
    hook_event_name: 'beforeSubmitPrompt',
    session_id: sessionId,
    prompt: 'debug this intermittent crash and find the root cause',
  });
  const directory = path.dirname(fileURLToPath(import.meta.url));
  const router = path.join(directory, 'prompt-skill-router.mjs');
  const invoke = () => spawnSync(process.execPath, [router], {
    cwd: path.resolve(directory, '../..'),
    input: payload,
    encoding: 'utf8',
  });
  try {
    const first = invoke();
    const second = invoke();
    assert.equal(first.status, 0, first.stderr);
    assert.equal(second.status, 0, second.stderr);
    assert.match(JSON.parse(first.stdout).agent_message, /systematic-debugging/);
    assert.deepEqual(JSON.parse(second.stdout), { continue: true });
  } finally {
    fs.rmSync(
      path.join(os.tmpdir(), `agent-profile-advisory-${sessionId}.json`),
      { force: true },
    );
  }
});
