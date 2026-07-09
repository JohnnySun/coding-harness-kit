# coding-harness-kit 自身 Harness 設計

> 方法：`harness-builder` 工作流 A（評估）→ 工作流 B（從零構建）。  
> 日期：2026-07-09（rev.5 — 公開可信集脫敏：步1 僅公開 check IDs；本機 absorb → subject_ready）  
> 顯示名：**coding-harness-kit**（構建 / 迭代 coding harness 的工具倉）。  
> 對象：本工具倉（優化 / 迭代 / 比較各 subject harness），**不是** subject 業務倉。  
> 審查：`docs/harness/plan-review-2026-07-09.md`；決策採納：F5 **無逃生**；hook-router **vendor copy**。

---

## 0. 工程定位（影響落點選擇）

| 抽象角色 | 本倉填空 |
|---|---|
| 產品代碼 | 幾乎沒有；產物是 `tools/*`、`snapshots/`、`comparisons/`、`agent-kit` 蒸餾 |
| 「模組」 | 環1 暫單一 `harness-dev`（體量小）；日後可拆 `tools` / `agent-kit`（非本拍） |
| 可信集要證明什麼 | registry 合法、symlink 健康、默認 sync **不**拉業務樹、`default_submodules` 已到位、snapshot schema 合法、比較可復現（有 pin） |
| 進 prod | 無部署；「進歷史」= commit；「進結論」= `comparisons/` 報告被當 SSOT 引用 |
| 多平台 | Skills / hooks：經 `agent-kit.sh install` 寫入本機客戶端樹（不進 git）。Hooks SSOT：`agent-kit/hooks/clients/` |

抄拓撲不抄實現：環1 仍是 edit→verify→Stop/commit，但「verify」是 **harness 表面不變量**，不是業務測試。

---

## 1. 工作流 A — 現況評分

### 1.1 四層盤點

| 層 | 現況 | 強制力階梯 | 防線 |
|---|---|---|---|
| **約束** | `agent-kit` skills 已鏈到四平台；`README` 散文說明意圖；**無** `AGENTS.md`/`CLAUDE.md` | 散文 / 部分注入 | — |
| **強制** | 無 hook、無可信集命令、無 commit gate、無 ratchet | 無 | L0/L1/L2 全缺 |
| **回流** | inbox / 工單檔已 stub，無機器寫入 | 散文 | — |
| **進化** | 無週報消費協議 | 無 | — |

已有零件：`subjects/manifest.yaml` + `pin.json` + `tools/sync/sync-subjects.sh`；scaffold；`agent-kit` install 表面。

### 1.2 評分表（每層 0–2）

| 層 | 分 | 依據 |
|---|---|---|
| 約束 | 1 | 有方法論 skill，缺根指令檔與完成定義 |
| 強制 | 0 | 無 deny/exit 1 |
| 回流 | 0 | stub 無寫入端 |
| 進化 | 0 | 無消費協議 |
| **合計** | **1 / 8** | 約等於沒有 harness |

### 1.3–1.4 斷點與盲區

非 agent 路徑無 L1；無 pin / 空 `.claude` 仍可「比較」；回流尚無收集端。

### 1.5 本倉特有失敗模式

| ID | 失敗 | 為什麼致命 |
|---|---|---|
| F1 | 聲稱 sync 完成但 `default_submodules`（如 subject `.claude`）仍空 | 比較空 harness |
| F2 | 默認拉齊業務 submodule | 工具倉變第二 monorepo |
| F3 | 無 pin / pin 漂移仍 compare/score | 報告不可復現 |
| F4 | skill symlink 斷裂 | 約束層靜默失效 |
| F5 | `subjects/**`（除 example）、`snapshots/`、`comparisons/` 被 commit 進本倉 | 體積/權限/SSOT 污染；公開倉洩漏 subject |
| F6 | snapshot schema 分裂 | compare 無法通用 |
| F7 | subject 業務 skill 鏈進本倉 skills | 與方法論混載 |

---

## 2. 操作狀態機（sync → import → compare）

| 狀態 | 含義 | 允許的產品動作 |
|---|---|---|
| `absent` | 無 `checkout/` | 僅 `sync` |
| `shell` | 有 checkout，但某條 `default_submodules` 未到位 | 僅 `sync`（補 submodule）；**禁止** import/compare/score |
| `harness-ready` | checkout HEAD == `pin.sha`，且每個 `default_submodules` 路徑滿足「到位謂詞」（§2.1）；`pin.submodules[<path>]` 為非 null SHA 且與實際一致 | **允許** import / compare / score |
| `drifted` | checkout 存在但 HEAD ≠ `pin.sha`，或 submodule pin 為 null / 與實際不符 | **import/compare/score 一律 exit 1**（無逃生）。本機 absorb 檢查見 `tools/lib/subject_ready.py` / `check-local-absorb.sh`（**不**進公開可信集） |

正交標記（**不是**互斥狀態，可與上表疊加）：

| 標記 | 含義 | 對產品動作 |
|---|---|---|
| `extras_present` | 曾用 `sync --with` 拉過非 default submodule | 若底態為 `harness-ready`，**仍允許** import/compare/score；import 只收 `harness_paths`，snapshot `extras_present: true`；不把業務樹寫入 snapshot |

Sync 旗標與狀態：

| 旗標 | 效果 | 對 pin / compare |
|---|---|---|
| （默認） | shell + `default_submodules` | 不改 pin；compare 仍看現有 pin |
| `--latest` | 重置到 `origin/<branch>` tip | 常導致 `drifted`，需再 `--pin` 才可 compare |
| `--pin` | 寫回 `pin.json`（含 submodule SHA） | 進入可復現基線 |
| `--with a,b` | 額外 init 業務 submodule | 打上 `extras_present`；**不**單獨取消 `harness-ready` |

### 2.1 「submodule 到位」謂詞（消滅 F1）

對 manifest 中每個 `default_submodules` 條目 `<path>`：

1. `subjects/<id>/checkout/<path>` 存在且為目錄；  
2. 其內存在 gitlink / `.git`；  
3. **最小 harness 標記**（按 path 類型，P0 寫死規則）：  
   - path 為 `.claude` 或含 `skills`：至少一個 `**/SKILL.md`，或存在 `hooks`/`settings.json` 之一；  
   - 其他 path：目錄非空（entry count ≥ 1）。  

不滿足 → 狀態不得標為 `harness-ready`（本機 absorb / `subject_ready` 紅）；公開可信集用 in-memory fixture 測同一謂詞。

---

## 3. 工作流 B — 從零構建

### 步 0 — 約束層最小集

- 根 `AGENTS.md`（`CLAUDE.md` → symlink）：定位、完成定義、黑名單、機關落點、帳本註冊表副本  
- `docs/harness/`：本設計 + 帳本

完成定義：

> 改了 `tools/**` 或 `subjects/manifest.yaml` 卻沒跑可信集 → **未完成**。  
> 對非 `harness-ready` 的 subject 跑 import/compare/score 或寫出 `comparisons/**` → **無效**（工具必須 exit 1）。  
> `subjects/**`（除 `manifest.example.yaml`）、`snapshots/**`、`comparisons/**` 進入 commit pathspec → **禁止**（無逃生，見步 2）。

### 步 1 — 公開可信集（P0）

命令：`bash tools/harness/test-harness.sh`（L2 CI 同構）。  
**不含**私有 `subjects/**` 的 pin / checkout / snapshot 狀態；那些走本機 absorb 入口（見下）。

| 檢查 ID | 失敗條件 | 測法約束 |
|---|---|---|
| `public-suite-decoupled` | 公開 `checks.py` 仍呼叫私有 pin/checkout/snapshot checker，或綁定私有 `manifest.yaml` | 靜態 grep |
| `manifest-schema` | example 缺 `remote` / `default_branch` / `harness_paths` / `default_submodules`；或有 `trusted_suite` 卻無 `fixture_root` | 讀 `manifest.example.yaml` + 負例 |
| `default-submodules-present` | §2.1 謂詞對 fixture 紅/綠不成立 | **強制 in-memory fixture**（不依賴真實 subject） |
| `symlink-health` | 本機已 install 時：四平台 `skills/*` 斷鏈，或非法指向 `subjects/**`；未 install → 提示跑 `agent-kit.sh install` | 本機 fs；允許 plugin flat-copy |
| `client-trees-ignored` | `.cursor`/`.agents`/`.claude`/`.codex` 未 ignore 或仍被 git 追蹤 | install 產物不得進公開 git |
| `no-business-default` | 默認將 init 的 submodule 集合 ⊈ `default_submodules` | **禁止真 clone**；契約綁 `planned_submodules` |
| `private-gitignore` | `.gitignore` 未覆蓋私有樹；或 `manifest.example.yaml` 被誤 ignore | F5+ |
| `ledger-registry` | 帳本檔與 §9 註冊表不一致 | live check |
| `docs-placement` | 設計文落在禁區（sentinel / 鬆散 `docs/*.md`） | 見 `docs/README.md` |
| `hook-wiring` | `agent-kit/hooks/clients/` 模板缺件或未指向 hook-router / cursor-hook | 靜態讀模板；已 install 時抽查本機樹 |
| `subject-gates-fixture` | example 綠 fixture 未過 / 紅 fixture 未紅；公開模式必須 `--fixture` | `testdata/subjects/**` |

窄跑（不算收環）：`node --test tools/sync/*.test.mjs`。

**本機 absorb（非公開可信集）**：`bash tools/harness/check-local-absorb.sh --all`（或 `python3 tools/lib/subject_ready.py`）。  
pin / checkout / `harness-ready` 由 `subject_ready.require_ready` 閘住 import/compare/score；**無**公開套件逃生變數。

### 步 2 — 環 1

| 抽象 | 本倉落點 |
|---|---|
| 編輯偵測 | `tools/**`、`subjects/manifest.example.yaml`（及本機 `manifest.yaml`）、`agent-kit/skills/**`、四平台 skills 連結、`docs/harness/**` → `pending[harness-dev]` |
| 驗證偵測 | 僅 `bash tools/harness/test-harness.sh` 全綠 |
| Stop | block-once + 列出可信集命令 |
| commit deny（pending） | 上述路徑有 pending → DENY；逃生：`HARNESS_SKIP="<原因>"` → 放行**一次** + 寫入 `gate-events.jsonl` |
| commit deny（private） | pathspec 命中 `subjects/**`（除 `manifest.example.yaml`）、`snapshots/**`、`comparisons/**` → **DENY，無逃生變數**（F5+）。L0 PreToolUse + L1 pre-commit |

**Hook SSOT（定案）**：從  
`agent-kit/skills/templates/harness-scaffold/hook-router.mjs`（及 test）  
**vendor copy** 到 `tools/harness/`，檔頭註明上游路徑與「上游變更需人工同步」義務。不 symlink 回 templates（避免本倉 config 與通用模板耦死）。

**P1 佈線範圍**：Claude Code + Codex 調用同一 `tools/harness/hook-router.mjs`。Cursor / CLI hook：**不宣稱已接**；掛 `gates.json` 債務（§8）。

**P1 驗收（證明打響，防靜默失效）**：

1. 改 `tools/sync/sync-subjects.sh` 一行註釋 → 不跑可信集 → 在 **已佈線的一個平台** 觸發 Stop 或 `git commit`，必須被攔；  
2. 將結果（平台名、事件、是否 deny）記入 `docs/harness/hook-smoke.md` 或 gate-events；  
3. 未完成實測不得關閉 P1 工單。

防線：L0 先上；L1 pre-commit = 可信集 + 私有樹拒收；L2 = `.github/workflows/harness-trusted.yml`（公開可信集，`submodules: true`）。

### 步 3 — 帳本三件套

| 帳本 | 路徑（SSOT） | 寫入 | 消費 |
|---|---|---|---|
| 事件帳本 | `docs/harness/gate-events.jsonl`（上線即進 repo，不搞本機雙寫） | deny / `HARNESS_SKIP` | 週報 |
| 反思 inbox | `docs/harness/retro-inbox.md` | Stop 反思 | SessionStart + 一拍一條 |
| 債務 ledger | `docs/harness/gates.json` | 掛帳 / 平台債務 | ratchet + 償還 |
| 偏差登記 | `docs/harness/deviation-log.md` | 當輪糾偏；**compare 結論被人工推翻時必寫** | 週報 |
| 工單 | `docs/harness/work-orders.md` | 環3 | SessionStart 發牌 |

規則：新帳本無消費端不許上線；上線必須同步改 §9 註冊表（由 `ledger-registry` 檢查強制）。

### 步 4–5 — 環 3 / 環 2

同前：週報歸因三選一；環2 等兩週數據。關鍵路徑 manifest 示例保留。

---

## 4. 產品面與 Harness 面

```
產品線（對 subject）          harness 線（對本倉自己）
  sync / import                 test-harness.sh
  snapshot / compare / score     hook-router + 帳本
  comparisons/ 報告             retro → 工單
```

- subject harness 弱 → `comparisons/` + subject 側跟進，**非**本倉債務。  
- 本倉在非 `harness-ready` 仍出報告 → F3，本倉債。  

**產品閘（寫進 import/compare/score CLI，非 hook）**：

- 默認要求目標 subject ∈ `harness-ready`（§2）；否則 **import / compare / score** 均 exit 1。  
- 不讀 `HARNESS_ALLOW_DRIFT`。  
- import **必須**以 `subjects/manifest.yaml` 的 `harness_paths` 為唯一收錄清單（可加工具倉內部元數據檔）；禁止 ad-hoc 路徑列表。  
- `extras_present` 不放寬 ready 閘；僅影響 snapshot 元數據。

---

## 5. Snapshot 契約（凍結最小 schema）

路徑：`snapshots/<subject-id>@<shell-sha>/`

```text
manifest.json          # 必填，見下
constraints/           # 約束層摘錄（CLAUDE/AGENTS、skill 目錄清單等）
gates/                 # hooks / ratchet / 可信集入口引用
feedback/              # inbox/ledger 結構摘錄（可空目錄+README）
evolution/             # retro/工單/週報消費點摘錄（可空）
```

`manifest.json` 最小欄位：

```json
{
  "schema_version": 1,
  "subject": "<id>",
  "shell_sha": "<pin.sha>",
  "submodules": { "<path>": "<sha>" },
  "harness_paths": ["..."],
  "imported_at": "YYYY-MM-DD",
  "extras_present": false
}
```

- `harness_paths` 必須等於（或為其解析結果）manifest 註冊表中該 subject 的列表。  
- P0：無 `snapshots/` 子目錄 → 跳過；存在任一 snapshot 目錄但缺 `manifest.json` / 缺四層目錄 / `schema_version`≠1 → 可信集紅。  
- P2：`tools/import` 實現寫入；契約測試進可信集。

---

## 6. 目標目錄

```text
Harness-dev/
├── AGENTS.md
├── CLAUDE.md → AGENTS.md
├── agent-kit/skills/          # submodule → JohnnySun/skills
├── subjects/manifest.example.yaml   # 公開範本
├── subjects/manifest.yaml           # 本機（gitignore）
├── subjects/<id>/{pin.json,checkout/}  # 本機
├── tools/
│   ├── sync/
│   ├── import|compare|score/
│   └── harness/
├── snapshots/                 # 本機 absorb
├── comparisons/               # 本機 absorb
└── docs/harness/
```

---

## 7. 補強清單

| 優先 | 項 | 消滅 |
|---|---|---|
| P0 | `test-harness.sh`（含 §3 步1 全表） | F1–F5、F6 雛形、註冊表 |
| P0 | `AGENTS.md` + `CLAUDE.md` symlink | 約束真空 |
| P1 | vendor hook-router；**Claude+Codex** 佈線；hook smoke 實測 | 聲稱完成；靜默失效 |
| P1 | L1 pre-commit：可信集 + **無逃生**拒私有樹 | F5+、非 agent 路徑 |
| P2 | 帳本三件套機器寫入；`tools/import` 按 `harness_paths` | 回流、F6 |
| P2 | `tools/import|compare|score` 均強制 `harness-ready`；import 按 `harness_paths` | F3、F6 |
| P3 | 週報；Cursor/CLI hook 償還；L2 CI | 環3、平台債務 |
| P4 | 環2 償還隊列 | 延後 |

---

## 8. 已知債務（預掛，上線 `gates.json` 時落入）

| ID | class | reason | 計劃 |
|---|---|---|---|
| `l2-ci` | env-dependent | 本倉尚無遠端 CI | 有 remote 後接同一 `test-harness.sh` |

**已關閉**：`cursor-stop-soft-only` — 對齊 workspace-shell：Cursor `stop` 平台無法硬攔屬 residual，不是待修債；硬閘落在 `beforeShellExecution` commit-deny + L1 `pre-commit`（已佈線）。

---

## 9. 帳本註冊表（目標態；`ledger-registry` 檢查對象）

| 帳本 | 路徑 | 寫入端 | 消費端 | 節奏 | 狀態 |
|---|---|---|---|---|---|
| gate-events | `docs/harness/gate-events.jsonl` | hook / HARNESS_SKIP | 週報 | 週 | ✓ runtime（**gitignore**） |
| retro-inbox | `docs/harness/retro-inbox.md` | Stop 反思 | SessionStart + operate | 日 | ⚠→✓ |
| gates.json | `docs/harness/gates.json` | 掛帳 | ratchet | 日 | ✓ |
| deviation-log | `docs/harness/deviation-log.md` | 糾偏；compare 推翻 | 週報 | 週 | ⚠ |
| work-orders | `docs/harness/work-orders.md` | 環3 | SessionStart | 週 | ⚠（正文勿貼私有路徑） |
| comparisons/ | `comparisons/` | score | 人 / subject 工單 | 按次 | 本機產物（**gitignore**） |

---

## 10. 本拍邊界與設計驗收

**做了**：A 評分 + B 構建序 + 狀態機 + snapshot 契約 + 審查修訂。  
**不做**：實作 hook/可信集/import（下一拍按 WO 施工）。

設計驗收：

- [x] F1 有獨立檢查 + **空 `.claude` fixture** + **至少一 checkout 樣本**（防真空綠）  
- [x] `pin.submodules` 納入可信集，與 `harness-ready` 對齊  
- [x] `no-business-default`：單一 lib + 入口綁定檢查，禁止真 clone  
- [x] F5 無逃生、措辭無矛盾  
- [x] snapshot schema + `harness_paths` 消費義務  
- [x] drift vs compare 分離  
- [x] hook vendor SSOT + P1 smoke + 平台債務顯式  
- [x] 操作狀態機覆蓋 `--latest`/`--pin`/`--with`  
- [x] 帳本註冊表納入可信集  
