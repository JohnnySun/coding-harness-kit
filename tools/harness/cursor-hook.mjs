#!/usr/bin/env node
// Cursor adapter: map camelCase events + permission field ↔ hook-router processEvent.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  processEvent,
  loadState,
  saveState,
  config,
} from './hook-router.mjs';

async function readPayload() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    return null;
  }
}

function toInternal(raw) {
  // Cursor may send event name in different fields
  const cursorEvent =
    raw.hook_event_name || raw.event || raw.event_name || '';
  const cmd = raw.command || (raw.tool_input && raw.tool_input.command) || '';
  const filePath = raw.file_path || (raw.tool_input && raw.tool_input.file_path);

  if (cursorEvent === 'beforeShellExecution' || cursorEvent === 'beforeMCPExecution') {
    return {
      hook_event_name: 'PreToolUse',
      tool_name: 'Bash',
      tool_input: { command: cmd },
      session_id: raw.session_id || raw.conversation_id,
    };
  }
  if (cursorEvent === 'afterFileEdit') {
    return {
      hook_event_name: 'PostToolUse',
      tool_name: 'Edit',
      tool_input: { file_path: filePath },
      session_id: raw.session_id || raw.conversation_id,
    };
  }
  if (cursorEvent === 'stop') {
    // informational only on Cursor — still update state / soft message
    return {
      hook_event_name: 'Stop',
      session_id: raw.session_id || raw.conversation_id,
      _cursorSoft: true,
    };
  }
  return null;
}

function toCursorResponse(internal, softStop) {
  const r = internal.response || {};
  const decision = r.hookSpecificOutput && r.hookSpecificOutput.permissionDecision;
  if (decision === 'deny') {
    const reason =
      r.hookSpecificOutput.permissionDecisionReason || 'denied by harness';
    return {
      permission: 'deny',
      user_message: reason,
      agent_message: reason,
    };
  }
  if (softStop && r.decision === 'block') {
    // Cursor stop cannot block — soft prompt only
    return {
      // no permission field for stop; message for agent if supported
      agent_message: r.reason || 'Run bash tools/harness/test-harness.sh before finishing.',
    };
  }
  return { permission: 'allow' };
}

async function main() {
  const raw = await readPayload();
  if (!raw) process.exit(0);
  const mapped = toInternal(raw);
  if (!mapped) {
    process.stdout.write(JSON.stringify({ permission: 'allow' }));
    return;
  }
  const sid = mapped.session_id;
  const state = loadState(sid);
  const result = processEvent(mapped, state);
  saveState(sid, result.state);
  const out = toCursorResponse(result, mapped._cursorSoft);
  process.stdout.write(JSON.stringify(out));
}

const isDirect =
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isDirect) main();
