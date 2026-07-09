// Harness-dev hook-router tests (vendored scaffold adapted).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { processEvent, newState, config } from './hook-router.mjs';

const edit = (file) => ({
  hook_event_name: 'PostToolUse',
  tool_name: 'Edit',
  tool_input: { file_path: file },
});
const bash = (event, command) => ({
  hook_event_name: event,
  tool_name: 'Bash',
  tool_input: { command },
});

test('編輯 tools 下腳本武裝 harness-dev', () => {
  const { state } = processEvent(edit('tools/sync/sync-subjects.sh'), newState());
  assert.deepEqual(Object.keys(state.pending), ['harness-dev']);
});

test('編輯無關路徑不武裝', () => {
  const { state } = processEvent(edit('README.md'), newState());
  assert.deepEqual(state.pending, {});
});

test('可信集命令清除 pending', () => {
  let { state } = processEvent(edit('tools/harness/checks.py'), newState());
  ({ state } = processEvent(
    bash('PostToolUse', 'bash tools/harness/test-harness.sh'),
    state,
  ));
  assert.deepEqual(state.pending, {});
});

test('有 pending 時 git commit 被 deny', () => {
  const { state } = processEvent(edit('tools/sync/foo.py'), newState());
  const { response } = processEvent(bash('PreToolUse', 'git commit -m "wip"'), state, {});
  assert.equal(response.hookSpecificOutput.permissionDecision, 'deny');
});

test('正向對照：無 pending 時 git commit 放行', () => {
  const { response } = processEvent(bash('PreToolUse', 'git commit -m "ok"'), newState(), {});
  assert.deepEqual(response, {});
});

test('HARNESS_SKIP 逃生放行且不清 pending', () => {
  const { state } = processEvent(edit('tools/sync/foo.py'), newState());
  const { response, state: after } = processEvent(
    bash('PreToolUse', `${config.escapeEnvVar}="hotfix" git commit -m "x"`),
    state,
    {},
  );
  assert.deepEqual(response, {});
  assert.deepEqual(Object.keys(after.pending), ['harness-dev']);
});

test('F5+：git add subjects checkout 路徑無條件 deny', () => {
  const { response } = processEvent(
    bash('PreToolUse', 'git add subjects/demo-weak/checkout/CLAUDE.md'),
    newState(),
    {},
  );
  assert.equal(response.hookSpecificOutput.permissionDecision, 'deny');
  assert.match(response.hookSpecificOutput.permissionDecisionReason, /F5/);
});

test('F5+：git add snapshots 無條件 deny', () => {
  const { response } = processEvent(
    bash('PreToolUse', 'git add snapshots/demo-weak@abc/manifest.json'),
    newState(),
    {},
  );
  assert.equal(response.hookSpecificOutput.permissionDecision, 'deny');
});

test('F5+：git add comparisons 無條件 deny', () => {
  const { response } = processEvent(
    bash('PreToolUse', 'git add comparisons/report.md'),
    newState(),
    {},
  );
  assert.equal(response.hookSpecificOutput.permissionDecision, 'deny');
});

test('F5+：無逃生 — HARNESS_SKIP 不能放行 private path', () => {
  const { response } = processEvent(
    bash(
      'PreToolUse',
      'HARNESS_SKIP=nope git add subjects/demo-weak/checkout/foo',
    ),
    newState(),
    { HARNESS_SKIP: 'nope' },
  );
  assert.equal(response.hookSpecificOutput.permissionDecision, 'deny');
});

test('公開 example manifest 可 add（不觸發 private-deny）', () => {
  const { response } = processEvent(
    bash('PreToolUse', 'git add subjects/manifest.example.yaml'),
    newState(),
    {},
  );
  assert.deepEqual(response, {});
});

test('Stop block-once', () => {
  let { state } = processEvent(edit('docs/harness/design.md'), newState());
  let r = processEvent({ hook_event_name: 'Stop' }, state);
  assert.equal(r.response.decision, 'block');
  r = processEvent({ hook_event_name: 'Stop' }, r.state);
  assert.deepEqual(r.response, {});
});

test('提及 git commit 字樣不 deny', () => {
  const { state } = processEvent(edit('tools/a.py'), newState());
  const { response } = processEvent(
    bash('PreToolUse', 'grep -rn "git commit" docs/'),
    state,
    {},
  );
  assert.deepEqual(response, {});
});
