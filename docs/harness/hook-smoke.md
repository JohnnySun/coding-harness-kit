# Hook smoke evidence (WO-0002)

Date: 2026-07-09  
Method: stdin simulation against `tools/harness/hook-router.mjs` (same binary Claude/Codex wire to).  
Session id: `smoke-1`

| Step | Input | Result |
|------|-------|--------|
| 1 | PostToolUse Edit `tools/sync/sync-subjects.sh` | armed `pending[harness-dev]` |
| 2 | PreToolUse `git commit -m wip` | **deny** (commit-deny) |
| 3 | PreToolUse `git add subjects/demo-weak/checkout/x` | **deny** F5+ (private-deny, no escape) |
| 4 | PreToolUse `git add snapshots/x` / `comparisons/x` | **deny** F5+ |
| 5 | PostToolUse `bash tools/harness/test-harness.sh` | cleared pending |

Events append to local `docs/harness/gate-events.jsonl` (gitignored runtime).

Platform wiring present:

- Claude Code: `.claude/settings.json` → `hook-router.mjs`
- Codex: `.codex/hooks.json` + `config.toml` `[features] hooks=true` (TUI `/hooks` trust still required on first use)
- Cursor: `.cursor/hooks.json` → `cursor-hook.mjs`（`beforeShellExecution` 硬 deny；`stop` 僅軟提示 — workspace-shell 同構，硬閘不依賴 stop）
- L1: `core.hooksPath=tools/harness/git-hooks` → `pre-commit.sh`

Unit tests: `node --test tools/harness/hook-router.test.mjs`（計入可信集）。
