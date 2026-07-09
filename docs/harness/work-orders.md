# Work orders

> 環3 合法產出登記處。完成改 `done(<證據>)`。

## WO-0001a — P0 可信集

- **狀態**：`done(bash tools/harness/test-harness.sh → ✔ 2026-07-09)`

## WO-0001b — P0 AGENTS.md

- **狀態**：`done(AGENTS.md + CLAUDE.md→AGENTS.md 2026-07-09)`

## WO-0002 — P1 環1 hooks

- **狀態**：`done(hook-smoke.md + 10/10 unit tests + Claude/Codex/Cursor wiring + L1 pre-commit 2026-07-09)`
- **證據**：`docs/harness/hook-smoke.md`；`tools/harness/hook-router.mjs`；`.claude/settings.json`；`.codex/hooks.json`；`.cursor/hooks.json`

## WO-0003 — P2 import / compare / score

- **目標**：`tools/import|compare|score`；`harness-ready` 閘；snapshot §5 schema。
- **狀態**：`done(import --all + compare + score 2026-07-09)`
- **證據**：本機 `snapshots/<id>@<sha>/`；本機 `comparisons/`（均不進公開 git）

## WO-0004 — P3 週報 + Cursor 佈線

- **目標**：週報腳本；Cursor hooks（硬 gate 在 shell）；更新債務。
- **狀態**：`done(weekly_report.py + .cursor/hooks.json；cursor-stop 按 workspace-shell 拓撲閉環：硬閘在 beforeShellExecution+L1，非待修債 2026-07-09)`
- **證據**：本機 `docs/harness/reports/`；`gates.json` `closed_debts`

## WO-0005 — 公開倉脫敏邊界

- **目標**：`subjects/` / `snapshots/` / `comparisons/` 本機化；`manifest.example.yaml`；F5+ L0/L1；可信集無私有 subject 仍綠。
- **狀態**：`done(2026-07-09)`
- **證據**：`.gitignore`；`subjects/manifest.example.yaml`；`hook-router` private-deny；`bash tools/harness/test-harness.sh`
