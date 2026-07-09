# Plan Review Report — `docs/harness/design.md`

## Summary

| Reviewer | Role | Final |
|----------|------|-------|
| A | Architecture & Feasibility | blockers resolved |
| B | Completeness & Risk | blockers resolved |
| C | Quality & Conventions | blockers resolved |
| F | Blind-Spot Reconstruction | blockers resolved |
| D / E | — | deactivated |

**Overall Result**: APPROVED（無 open critical / major）  
**Review Iterations**: 4（discovery → rev.2 → rev.3 → rev.4）  
**Harness Status**: `passed`  
**Budget used**: 4 / 5 sweeps  

## Decisions locked

1. F5：`checkout/**` commit → **DENY，無逃生**  
2. hook-router → **vendor copy** 進 `tools/harness/`  
3. P1 hooks：Claude Code + Codex；Cursor/CLI → `gates.json` 債務  

## Revision changelog

| Rev | Closed |
|-----|--------|
| rev.2 | 原 11 confirmed（F1 到位檢查、F5 措辭、fixture 測法、snapshot 契約、drift/compare、WO+AGENTS、vendor、smoke、狀態機、註冊表、平台債務） |
| rev.3 | F1 真空綠、`pin.submodules` 套件、no-business 入口綁定 |
| rev.4 | sample 門檻語義、drift 範圍自洽、`extras_present` 正交、import 納入 ready 閘 |

## Non-blocking leftovers

- WO-0001a 驗收句可補一句「不授權 import/score」（design §4 已寫死）  
- 環1 日後可拆 `pending[tools]` / `pending[agent-kit]`  

## Final recommendation

設計可開工：**WO-0001a**（可信集）+ **WO-0001b**（AGENTS.md）。
