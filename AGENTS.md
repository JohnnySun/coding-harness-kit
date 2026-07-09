# coding-harness-kit

本倉是 **coding-harness 工具倉**（顯示名 coding-harness-kit）：用來構建 / 迭代各業務倉（subject）的 coding harness——導入 / 同步 / 比較 / 評價。  
業務源碼不是一等公民；工作對象是 harness 表面。方法論見 `agent-kit/`；自身設計見 `docs/harness/design.md`。

## 公開 / 本機邊界（脫敏）

| 層 | 路徑 | 進 git？ |
|---|---|---|
| 公開 | `tools/`、`docs/`（`README` + `specs/` + `harness/` 帳本）、`agent-kit/`（含 `hooks/clients/` 模板）、`subjects/manifest.example.yaml`、`testdata/` | ✓ |
| 本機私有 | `subjects/**`（含真實 `manifest.yaml` / pin / checkout）、`snapshots/`、`comparisons/`、`docs/harness/gate-events.jsonl`、`docs/harness/reports/` | ✗（gitignore + L0/L1 無逃生） |
| 本機安裝產物 | `.cursor/` / `.agents/` / `.claude/` / `.codex/`（skills、hooks、plugins） | ✗（gitignore；由 `agent-kit.sh install` 再生） |

```bash
git submodule update --init --recursive
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 填入本機 subject remote 後：
bash tools/sync/sync-subjects.sh
```

## 完成定義（判定式）

- 改了 `tools/**`、`agent-kit/**`（install/manifest/locks）或 `subjects/manifest.example.yaml`（或本機 `manifest.yaml`）卻沒跑 `bash tools/harness/test-harness.sh` → **未完成**。
- 對非 `harness-ready` 的 subject 跑 import/compare/score 或寫出 `comparisons/**` → **無效**（工具必須 exit 1）。
- `subjects/**`（除 `manifest.example.yaml`）、`snapshots/**`、`comparisons/**` 進入 commit pathspec → **禁止**（無逃生）。

`harness-ready`：checkout HEAD == `pin.sha`，且每個 `default_submodules` 滿足 design §2.1，且 `pin.submodules` 非 null 且與實際一致。

## 黑名單

- 默認 `sync` 拉業務 submodule（server/desktop/`repos/*` 等）——只用 `--with` 顯式加。
- 把 subject 業務 skill symlink 進本倉 `.cursor/.agents/.claude/.codex/skills`。
- 無 pin / pin 漂移仍產出比較報告。
- 用窄測代替 `tools/harness/test-harness.sh` 宣稱收環。
- 把真實 subject remote / pin / snapshot / 比較報告提交進本倉。
- 把 `.cursor` / `.agents` / `.claude` / `.codex` 客戶端安裝樹提交進本倉（一律走 `agent-kit.sh install`）。
- 設計文檔寫進 `docs/harness/`、根 `specs/`、`docs/superpowers/`、`docs/technical-design/`，或鬆散的 `docs/*.md`——一律進 `docs/specs/YYYYMMDD-slug/`（見 `docs/README.md`）。
- **公開樹正文脫敏（AI 行為閘）**：寫入 `tools/` / `docs/` / `agent-kit/` 等公開 pathspec 時，禁止寫特定僱主／組織品牌名、內部 forge 實名、本機絕對路徑、真實 subject id／remote／pin；用「上游 subject」「內部 forge」「example remote」等通用指代。此條**不是**程式碼禁詞掃描——在閘裡嵌入禁詞會再污染公開樹。可執行互補閘只攔通用形態（home 絕對路徑、`subjects/*/checkout` 絕對路徑、本機 manifest 的 id／remote）。

## 常用命令

```bash
bash tools/sync/sync-subjects.sh              # harness 表面（需本機 manifest.yaml）
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/test-harness.sh            # 公開可信集（收環 / L2 同構；不含私有 pin）
bash tools/harness/check-local-absorb.sh --all  # 本機 absorb：harness-ready（非公開套件）
# 等價：python3 tools/lib/subject_ready.py --all
bash tools/harness/agent-kit.sh validate
CLIENT=cursor bash tools/harness/agent-kit.sh install
# 可選：CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

## 機關落點

| 規則 | 落點 | 狀態 |
|---|---|---|
| 可信集不變量 | `tools/harness/test-harness.sh` | ✓ |
| agent-kit install 契約 | `test_agent_kit_install.py` + `agent-kit.sh`；客戶端樹 gitignore | ✓ |
| 文檔落點 | `docs/README.md` + sentinel + L1 pre-commit + `docs-placement` | ✓ |
| 私有樹拒進 git | L0 hook + L1 `pre-commit.sh`（無逃生） | ✓ |
| edit→verify 環1 | `tools/harness/hook-router.mjs`；模板在 `agent-kit/hooks/clients/` | ✓ |
| Cursor claimed-done | `stop` 軟提示；硬閘 = `beforeShellExecution` + L1 | ✓ 已閉環 |
| L2 CI | `.github/workflows/harness-trusted.yml`（公開可信集） | ✓ |

## 帳本註冊表

| 帳本 | 路徑 | 寫入端 | 消費端 | 節奏 | 進 git |
|---|---|---|---|---|---|
| gate-events | `docs/harness/gate-events.jsonl` | hook / HARNESS_SKIP | 週報 | 週 | ✗ runtime |
| retro-inbox | `docs/harness/retro-inbox.md` | Stop 反思 | SessionStart + operate | 日 | ✓ 結構 |
| gates.json | `docs/harness/gates.json` | 掛帳 | ratchet | 日 | ✓ |
| deviation-log | `docs/harness/deviation-log.md` | 糾偏；compare 推翻 | 週報 | 週 | ✓ 結構 |
| work-orders | `docs/harness/work-orders.md` | 環3 | SessionStart | 週 | ✓（勿貼私有路徑正文） |
| comparisons/ | `comparisons/` | score | 人 / subject 工單 | 按次 | ✗ 本機 |

## Skills

方法論 skills 經 `bash tools/harness/agent-kit.sh install` 暴露於本機 `.cursor` / `.agents` / `.claude` / `.codex` `/skills/`，源在 `agent-kit/skills/skills/`（submodule → `github.com/JohnnySun/skills`）。客戶端樹不進 git。external skills / optional plugins 走 lock 檔；插件需 `PLUGIN=…`。優先：`harness-builder`、`harness-operate`、`plan-review`、`model-tier-prompting`。

## 派工前先查層級（advisory）

派子代理 / 委派 / fan-out 前，先諮詢 `model-tier-prompting`（`agent-kit/skills/skills/model-tier-prompting/`）做一次層級自評：依 roster 的 Intelligence Index 給你當前可用模型排序、挑最強可用者，再按任務難度選子代理形態與提示厚度。理由：dispatch 決策點若沒把層級查表上桌，形態/模型/提示厚度全憑即興。此為**指引非硬閘**。
