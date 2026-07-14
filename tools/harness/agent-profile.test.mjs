#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';

import {
  checkProfile,
  exportProfile,
  loadProfile,
  parseFlatYaml,
  runCli,
  setProfileValue,
} from '../../agent-kit/profile/agent-profile.mjs';

function tempRoot() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'agent-profile-test-'));
}

test('profile merges built-in, repo, then local values', () => {
  const root = tempRoot();
  fs.mkdirSync(path.join(root, '.harness'), { recursive: true });
  fs.writeFileSync(
    path.join(root, '.harness', 'agent-profile.yaml'),
    'schema_version: 1\nprocess_scaffold: guided\nmatt_skills: disabled\n',
  );
  fs.writeFileSync(
    path.join(root, '.harness', 'agent-profile.local.yaml'),
    'process_scaffold: structured\nreply_style: concise\n',
  );

  const profile = loadProfile({ root });
  assert.deepEqual(profile.effective, {
    schema_version: 1,
    process_scaffold: 'structured',
    matt_skills: 'disabled',
    sp_library: 'enabled',
    reply_style: 'concise',
  });
  assert.equal(profile.sources.process_scaffold, 'local');
  assert.equal(profile.sources.matt_skills, 'repo');
  assert.equal(profile.sources.sp_library, 'built-in');
  assert.match(profile.notes.reply_style, /no behavior consumer/i);
  assert.equal(profile.reconcile_required, true);

  fs.writeFileSync(
    path.join(root, '.harness', 'agent-profile-state.json'),
    JSON.stringify({
      schema_version: 1,
      clients: {
        cursor: {
          libraries: {
            superpowers: 'enabled',
            matt: 'disabled',
          },
        },
      },
    }),
  );
  assert.equal(loadProfile({ root }).reconcile_required, false);
});

test('flat YAML rejects duplicate, unknown, nested, and invalid enum values', () => {
  assert.throws(
    () => parseFlatYaml('process_scaffold: lean\nprocess_scaffold: guided\n'),
    /duplicate/i,
  );
  assert.throws(() => parseFlatYaml('unknown: value\n'), /unknown/i);
  assert.throws(() => parseFlatYaml('nested:\n  value: x\n'), /flat|unknown/i);
  assert.throws(() => parseFlatYaml('process_scaffold: maximal\n'), /process_scaffold/i);
});

test('flat YAML accepts full-line and trailing comments', () => {
  assert.deepEqual(
    parseFlatYaml([
      '# Team profile',
      'schema_version: 1',
      'process_scaffold: guided # advisory density only',
      '',
    ].join('\n')),
    {
      schema_version: 1,
      process_scaffold: 'guided',
    },
  );
});

test('set writes canonical repo or local YAML atomically', () => {
  const root = tempRoot();
  setProfileValue({ root, key: 'process_scaffold', value: 'guided' });
  setProfileValue({ root, key: 'reply_style', value: 'concise', local: true });

  assert.equal(
    fs.readFileSync(path.join(root, '.harness', 'agent-profile.yaml'), 'utf8'),
    'schema_version: 1\nprocess_scaffold: guided\n',
  );
  assert.equal(
    fs.readFileSync(path.join(root, '.harness', 'agent-profile.local.yaml'), 'utf8'),
    'reply_style: concise\n',
  );
  assert.equal(fs.existsSync(path.join(root, '.harness', 'agent-profile.yaml.tmp')), false);
});

test('export is portable and never overwrites existing client hooks', () => {
  const root = tempRoot();
  const hooksPath = path.join(root, '.cursor', 'hooks.json');
  fs.mkdirSync(path.dirname(hooksPath), { recursive: true });
  fs.writeFileSync(hooksPath, '{"hooks":{"custom":[]}}\n');
  fs.writeFileSync(path.join(root, 'AGENTS.md'), '# Existing rules\n');

  const first = exportProfile({ root, client: 'cursor' });
  const second = exportProfile({ root, client: 'cursor' });

  assert.equal(fs.readFileSync(hooksPath, 'utf8'), '{"hooks":{"custom":[]}}\n');
  assert.equal(fs.readFileSync(path.join(root, 'AGENTS.md'), 'utf8'), '# Existing rules\n');
  assert.equal(first.hooks_overwritten, false);
  assert.equal(second.hooks_overwritten, false);
  assert.ok(fs.existsSync(path.join(root, '.harness', 'profile-runtime', 'agent-profile.mjs')));
  assert.ok(fs.existsSync(path.join(root, '.harness', 'profile-runtime', 'agent-profile-router.mjs')));
  assert.ok(fs.existsSync(path.join(root, '.harness', 'profile-wiring', 'cursor.json')));
  assert.match(fs.readFileSync(path.join(root, '.gitignore'), 'utf8'), /agent-profile\.local\.yaml/);
});

test('export requires an explicit subject root', () => {
  const previous = process.cwd();
  const root = tempRoot();
  process.chdir(root);
  try {
    assert.throws(
      () => runCli(['export', '--client', 'cursor']),
      /requires --root/i,
    );
  } finally {
    process.chdir(previous);
  }
});

test('profile check reports missing wiring and accepts complete portable surface', () => {
  const root = tempRoot();
  exportProfile({ root, client: 'cursor' });
  let report = checkProfile({ root, client: 'cursor' });
  assert.equal(report.ok, false);
  assert.ok(report.errors.some((error) => /wiring/i.test(error)));

  fs.mkdirSync(path.join(root, '.cursor'), { recursive: true });
  fs.writeFileSync(
    path.join(root, '.cursor', 'hooks.json'),
    '{"hooks":{"beforeSubmitPrompt":[{"command":"node .harness/profile-runtime/agent-profile-router.mjs"}]}}\n',
  );
  fs.writeFileSync(
    path.join(root, 'AGENTS.md'),
    [
      '# Agent profile',
      'Profile routing is lightweight and advisory, not a global process gate.',
      'Agents change profile settings through `agent-kit.sh profile set`, not direct edits.',
      '',
    ].join('\n'),
  );
  fs.writeFileSync(
    path.join(root, '.harness', 'agent-profile-state.json'),
    JSON.stringify({
      schema_version: 1,
      runtime_hash: report.runtime_hash,
      clients: {
        cursor: {
          managed_skills: [],
          managed_library_skills: [],
          library_skills: {
            superpowers: [],
            'mattpocock-skills': [],
          },
          libraries: { superpowers: 'enabled', matt: 'enabled' },
        },
      },
    }),
  );

  report = checkProfile({ root, client: 'cursor' });
  assert.equal(report.ok, false);
  assert.ok(report.errors.some((error) => /materialization/i.test(error)));

  const librarySkills = {
    superpowers: [
      'test-driven-development',
      'systematic-debugging',
      'verification-before-completion',
      'requesting-code-review',
      'receiving-code-review',
    ],
    'mattpocock-skills': ['grilling'],
  };
  for (const name of [...librarySkills.superpowers, ...librarySkills['mattpocock-skills']]) {
    const directory = path.join(root, '.cursor', 'skills', name);
    fs.mkdirSync(directory, { recursive: true });
    fs.writeFileSync(
      path.join(directory, 'SKILL.md'),
      name === 'grilling'
        ? '---\nname: grilling\ndisable-model-invocation: true\n---\n'
        : `---\nname: ${name}\n---\n`,
    );
  }
  const statePath = path.join(root, '.harness', 'agent-profile-state.json');
  const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  state.clients.cursor.library_skills = librarySkills;
  state.clients.cursor.managed_library_skills = [
    ...librarySkills.superpowers,
    ...librarySkills['mattpocock-skills'],
  ];
  fs.writeFileSync(statePath, JSON.stringify(state));

  report = checkProfile({ root, client: 'cursor' });
  assert.equal(report.ok, false);
  assert.ok(report.errors.some((error) => /Matt library materialization is incomplete/i.test(error)));

  const mattSkills = [
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
  for (const name of mattSkills) {
    const directory = path.join(root, '.cursor', 'skills', name);
    fs.mkdirSync(directory, { recursive: true });
    fs.writeFileSync(
      path.join(directory, 'SKILL.md'),
      `---\nname: ${name}\ndisable-model-invocation: true\n---\n`,
    );
  }
  state.clients.cursor.library_skills['mattpocock-skills'] = mattSkills;
  state.clients.cursor.managed_library_skills = [
    ...librarySkills.superpowers,
    ...mattSkills,
  ];
  fs.writeFileSync(statePath, JSON.stringify(state));

  report = checkProfile({ root, client: 'cursor' });
  assert.equal(report.ok, true, report.errors.join('; '));

  fs.rmSync(path.join(root, '.cursor', 'hooks.json'));
  report = checkProfile({ root });
  assert.equal(report.ok, false);
  assert.ok(report.errors.some((error) => /prompt wiring/i.test(error)));
});
