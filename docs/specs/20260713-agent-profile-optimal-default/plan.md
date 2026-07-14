# Agent Profile：opinionated 最優預設實作方案

**狀態：** 已依本方案落地；本文保留交付契約、控制面邊界與驗收依據。

## 一頁摘要

安裝器的預設將從「只裝本地方法論，使用者另記得 `PLUGIN=…`」改為可重現的最優包：核心驗證／條件式 TDD／review、輕量意圖路由、使用者主動呼叫的 Matt skills，以及去除 bootstrap 的 SP 精選技能庫。`using-superpowers`、`brainstorming` 等會把每個回合變成流程閘的技能不再被安裝或註冊；既有 edit→verify、私有樹與 commit 閘保持不變。

活設定固定為 `.harness/agent-profile.yaml`，以內建預設、repo 設定、本機覆蓋三層合併。`process_scaffold` 立即影響 prompt router；`matt_skills` 與 `sp_library` 在下一次 install 時重算受管理技能；`reply_style` 可寫、可讀、可驗證，但 v1 不改變回覆行為。安裝器亦可將同一套 profile runtime、設定與接線片段帶到上游 subject；subject 升級必須跑 profile check，並由 `harness-builder`／`harness-operate` 明確列為完成條件。

## 已讀現況與設計依據

- `tools/harness/agent-kit.sh` 目前只把環境變數 `PLUGIN` 展成 `--with-optional-plugin`；沒有 profile 子命令，裸 `install` 不會帶插件。
- `agent-kit/install/install.py` 已是 install 的唯一 Python 入口；它能以 `OUTPUT_ROOT` 寫出目標樹，但目前把 client hooks 整份覆寫，且 optional plugin 會複製完整來源樹。
- `agent-kit/optional-plugins.json` 的 SP 宣告為 `"skills": "*"` 並含 `hooks` assets；這不足以保證 bootstrap 不被客戶端載入。`optional-plugins-lock.json` 已提供可重現來源版本。
- `agent-kit/manifest.json` 的 `harness-dev` profile 目前只有本地方法論 skills；`test_agent_kit_install.py` 也明確斷言 optional plugins 是 opt-in。
- 已安裝的 `using-superpowers` 要求任何回應前先查 skill；已安裝的 `brainstorming` 又要求設計核准後才能實作。這兩個全域流程閘與本方案的 lean 預設衝突。已安裝的 `grilling`／`implement` 適合保留為人類明示呼叫；`verification-before-completion` 與 `tdd` 是可按工作形狀建議的核心。
- `tools/harness/prompt-skill-router.mjs` 已證明「prompt submit → advisory context、session 去重、永不 deny」的可行形態，但目前只路由 `refine` 與 `model-tier-prompting`；三個 client 模板已接到此 router。
- `tools/harness/hook-router.mjs` 是另一條 edit→verify／commit 防線，不能因為移除 SP 過程閘而變弱。
- `agent-kit/skills/templates/harness-scaffold/` 已採「可攜腳本 + 各平台 wiring 範例」的 subject 輸出模式。`tools/sync/sync-subjects.sh` 只同步與 pin，不應被改成任意改寫 subject。
- `harness-builder`、`harness-operate` 是可輸出的技能 SSOT；`docs/README.md` 指定本計畫所在的 `docs/specs/YYYYMMDD-slug/`。

## 目標、邊界與不變量

### 目標

1. `CLIENT=<client> bash tools/harness/agent-kit.sh install` 在沒有 `PLUGIN` 的情況下產出最優預設包。
2. 安裝後的路由只在明確任務形狀下給出簡短建議；它不以「先讀 skill」「先 brainstorm」阻止普通回答或實作。
3. profile 是可追蹤、可本機覆蓋、可由 CLI 安全修改的設定，而不是散落環境變數。
4. 同一個 profile contract 能被 installer 輸出至 subject，並可被該 subject 的升級流程驗收。

### 保持不變

- `tools/harness/hook-router.mjs` 的可信集、私有樹、commit 與 Stop 防線仍然是硬閘；本案只撤除 SP 的全域流程接管。
- subject 的同步、pin 與 `harness-ready` 定義不擴張。profile 合規是「harness 升級完成」的額外檢查，不改寫既有 ready 判定。
- 客戶端樹仍是 install 產物且不進 git；profile repo 設定與可攜 runtime 則是 subject harness 表面的一部分。
- 不把 subject 真實 remote、pin、checkout 資訊或本機路徑寫入公開文件、fixture 或測試。

## 交付契約

### 1. Profile 設定與合併

新增下列 agent-kit SSOT：

- `agent-kit/profile/agent-profile.default.yaml`：內建最優預設；
- `agent-kit/profile/agent-profile.template.yaml`：供首次 materialize 與 subject export；
- `agent-kit/profile/agent-profile.schema.json`：機器可讀 schema；
- `agent-kit/profile/agent-profile.mjs`：唯一的解析、合併、驗證與 CLI 實作；
- `agent-kit/profile/agent-profile-router.mjs`：可輸出的 advisory router runtime。

v1 schema 是刻意扁平的 YAML，避免把配置語言本身變成新的依賴面：

```yaml
schema_version: 1
process_scaffold: lean
matt_skills: enabled
sp_library: enabled
reply_style: default
```

合併順序為 **內建 < `.harness/agent-profile.yaml` < `.harness/agent-profile.local.yaml`**；v1 只接受 flat `key: scalar`、空白行與註解，未知 key、重複 key、錯誤 enum 或其他 YAML 結構均為設定錯誤。local 檔不存在時不報錯。repo 檔是版本控制的團隊預設；local 檔與 install state 加入根 `.gitignore`，但不忽略整個 `.harness/`。

`process_scaffold` 值為 `lean`、`guided`、`structured`，預設 `lean`。它只增加 advisory 的密度與任務提醒：即使 `structured`，也不得重新安裝或模擬 `using-superpowers` 的「每回合查 skill」、設計核准、強制 worktree 或全域 brainstorming gate。`matt_skills`／`sp_library` 為 `enabled|disabled`；變更後由下一次 install reconcile 受管理技能。`reply_style` 接受 `default|concise|detailed`，`show` 必須標示「v1 已識別、尚無行為 consumer」，不可假裝已改變回覆。

### 2. CLI 是唯一寫入者

新增頂層命令面，`tools/harness/agent-kit.sh` 只轉交，不自行改 YAML：

```text
agent-kit.sh profile show [--root <repo>] [--json]
agent-kit.sh profile get <key> [--root <repo>]
agent-kit.sh profile set <key> <value> [--root <repo>] [--local]
agent-kit.sh profile check [--root <repo>] [--client <client>]
agent-kit.sh profile export --root <subject-root> --client <client>
```

`set` 以原子寫入輸出 canonical flat YAML（不承諾保留使用者註解）；agent 要調整設定只能呼叫此 CLI，不能直接 edit YAML。`install --process-scaffold <value>` 是安裝時便利入口，但必須委派同一 profile module 寫入，再執行 install；不能形成第二套設定邏輯。`show` 同時回報來源層、有效值與是否需要 reconcile。

### 3. 最優預設包與 SP 隔離

裸 install 自動解析 profile，預設 materialize：

- 核心 SP allowlist：`test-driven-development`、`systematic-debugging`、`verification-before-completion`、`requesting-code-review`、`receiving-code-review`；
- 既有 harness 本地方法論（特別是 `harness-builder`、`harness-operate`、`code-review`、`model-tier-prompting`、`refine`）；
- 現有 Matt allowlist，作為使用者明示的 `/grilling`、`/implement` 等能力；router 不會自動挑選 Matt skills；
- profile-aware 輕量 router。

SP 與 Matt 都改以 **library materialization** 安裝：從 lock 指定來源取得檔案，只複製 allowlist skill tree 到 client skill 目錄，並寫入受管理 state。不得把完整 vendor plugin、其 `hooks` 目錄、plugin manifest 的 hook 宣告或未列入的 skills 放進 client plugin 目錄。這解決目前 `"skills": "*"` 加完整 asset copy 造成的 bootstrap 漏網問題，也使 allowlist 能在沒有 upstream manifest `skills` array 時以明示 `skill_root` 驗證路徑。

人控指「Harness 不會自動路由 Matt」；若客戶端支援 `disable-model-invocation`，materializer 應保留或補上此 metadata。對不支援該 metadata 的客戶端，文件要誠實表述為「不由 harness 主動注入」，而不是聲稱能限制底層模型自行發現 skill。

為使舊工程直接遷到預設，install 要讀取受管理 state 與 lock 對應 hash，安全移除已知的完整 SP plugin、vendor hook 註冊與 `using-superpowers`／`brainstorming`／`writing-plans` 等舊 bootstrap materialization，再寫入 allowlist。無法證明歸 installer 所有的同名目錄不得刪除；命令以非零結果列出 `manual_cleanup_required`，而非靜默吞掉使用者內容。

### 4. 三個控制面：發現、提示、強制

路由不是「同一支 regex 的 soft／hard 兩個 mode」。三個控制面有不同輸入、責任與失敗語義，實作與測試必須保持分離：

1. **Description 發現面（主路由）**：以 skill frontmatter 的名稱與 description 判別度為主要發現機制，讓模型按任務語義選中能力；應優先投資 description 的正例、反例與邊界，而不是持續擴張 prompt regex。Matt skills 是使用者主動呼叫的 library，不進 harness 的自動建議；若客戶端支援 `disable-model-invocation`，materializer 保留或補上該 metadata。
2. **情境提示／advisory hook（補充路由）**：與現有 `prompt-skill-router` 同平面，僅補足 description 難以表達的時機與顯著性。提示必須窄、可跳過、低頻，以 session／route 去重守住信任預算；注入語氣固定為「觀察到的任務形狀＋具名 skill＋為何可能有用＋由 agent 選擇是否採用」。禁止「回覆前必讀」「1% must follow」「未先執行某流程不得繼續」或等價祈使／硬閘語義。此平面永遠 fail-open、永不 deny，也不攔回覆、edit、commit 或完成聲明。
3. **硬閘／enforcement hook（機器不變量）**：只守可機器證明的不變量，例如私有樹不得進 commit、edit→verify、claimed-done 與既有 commit 防線；它不推薦 skill、不讀 `process_scaffold` 調整強度，且所有 profile 下語義一致。現有 `tools/harness/hook-router.mjs` 與其可信集屬此平面，本方案不得削弱或混入 advisory 決策。

advisory router 以現有 `tools/harness/prompt-skill-router.mjs` 的跨 client event shape 與 session TTL 為基礎，改為讀取有效 profile。工作中只在高信號形狀命中時建議至多兩個技能：維護行為實作→條件式 TDD、debug→systematic debugging、review→review、提交／完成聲明→verification、harness 變更→builder/operate、prompt／dispatch→model-tier；`/refine` 與薄需求啟發式保留，但完整規格、跟進語與純問答仍不觸發。

`process_scaffold` **只調 advisory 密度，永不升級成閘**：`lean` 僅保留高信號且每個 route key session 去重；`guided` 可對大型但邊界不足的任務多給一個可選規劃建議；`structured` 只在使用者明示要求流程時提供較完整的可選流程選單。三檔都受相同信任預算、fail-open 與非阻斷契約約束。

### 5. Subject 輸出與升級完成條件

`profile export` 以既有 scaffold 模式輸出可攜 profile runtime、router、repo config、local-ignore 規則與 client wiring fragment 到目標 subject。它不得覆蓋 subject 既有 hooks；subject 的升級工作把 fragment 接到它實際生效的 prompt-submit 路徑，然後跑 `profile check`。

`profile check` 驗證：設定三層合併、可攜 runtime 版本／hash、受管理核心與 library materialization、至少一個實際 client prompt hook 接入 router、以及 subject 規則含「輕路由、非全域流程閘、agent 用 CLI 改 profile」的簡明契約。它的失敗代表本次 harness 升級尚未完成，但不影響既有 `harness-ready`、sync、import 或 pin。

在 `harness-builder` 的「從零構建／升級」清單與 `harness-operate` 的「定位／收環」清單加入同一條：只要工程使用 agent-kit profile，交付前必須 export 或 upgrade、接線、跑 profile check；已存在語義等價 profile 時可驗證後跳過，不可重複覆寫。這讓手藝存在可輸出的表面，而非只留在本倉操作記憶。

## 實作任務切分

| 任務 | 主要落點 | 依賴 | 驗收 |
|---|---|---|---|
| A. Profile kernel 與 CLI | `agent-kit/profile/*`、`tools/harness/agent-kit.sh` | 無 | 三層合併、schema 錯誤、`show/get/set`、原子寫入與 reply-style 佔位均有正反測試。 |
| B. Default package materialization | `agent-kit/install/install.py`、`optional-plugins*.json`、install unit tests | A | 不設 `PLUGIN` 的 dry-run 顯示核心 SP、Matt 與 router；輸出不含 SP bootstrap、vendor hook 或未 allowlist skill。 |
| C. Profile-aware light router | `tools/harness/prompt-skill-router.mjs` 與 `.test.mjs`、client templates | A | 三 client 的 prompt hook 仍可 advisory 注入；無毒性祈使語；正負 fixture 與多回合行為 eval 證明 lean 不會把工作儀式化。 |
| D. 可攜 subject exporter/checker | `agent-kit/profile/*`、installer、public fixture 與 subject-gate tests | A、B、C | export 不覆蓋既有 subject hook，check 能分別拒絕漏設定、漏接線、遺留 bootstrap 與不完整 materialization。 |
| E. 舊安裝遷移與文件 | installer migration、`README.md`、`agent-kit/README.md`、onboarding、規則範例 | B、C | 已知受管理的雙包舊輸出可一輪遷移到預設；不明所有權檔案安全失敗且提供可執行升級說明。 |
| F. 可輸出方法論與可信集 | `agent-kit/skills/skills/{harness-builder,harness-operate}`、`tools/harness/test_agent_kit_install.py`、`tools/harness/checks.py`、`test-harness.sh` | A–E | 兩個方法論 skill 都把 profile upgrade 列為完成檢查，公開可信集涵蓋 source、install、router、wiring 與 public fixture 合約。 |

A 可先行；B 與 C 可平行；D 依賴兩者的穩定輸出；E 可與 D 並行；F 最後收束。`agent-kit/skills` 是 submodule，實作者必須先確認其工作樹與 gitlink 狀態，不能把既有無關修改混入這次更新。

## 測試與遷移矩陣

- **profile unit**：預設、repo 覆蓋、local 覆蓋、非法 YAML／enum、`--local`、install option 委派與 reply-style 無 consumer 的透明回報。
- **library materialization**：allowlist 正向、未列 skill／hook／完整 plugin 不存在、來源缺少 allowlist skill 時失敗、collision 不覆寫、disabled library reconcile 移除受管理內容。
- **description discovery**：核心 skill descriptions 有可區分的正例／must-not 邊界；Matt skills 不進 harness 自動 route，支援 metadata 的客戶端保留人控標記。
- **router unit**：每種 task shape 的正例、純問答／跟進／完整規格的負例、session 去重、三個 `process_scaffold` 的 advisory 密度差異、永不輸出 bootstrap／毒性祈使文字、永不 deny。
- **router 行為 eval**：不只量開火率；以多回合 fixture 檢查 must-not、重複 nag、每回合先讀 skill／先報流程等儀式化行為，以及 agent 是否仍能直接回答或實作。任何「更常開火但信任預算下降」都算 regression。
- **enforcement regression**：profile 與 `process_scaffold` 的所有組合都跑既有 `hook-router.mjs` 防線，證明私有樹、edit→verify、claimed-done 與 commit gate 未被 advisory 改動。
- **client install contract**：擴充 `tools/harness/test_agent_kit_install.py`，覆蓋五 client 的預設 targets、profile report、Cursor/Claude/Codex 接線與 legacy migration；更新既有「optional plugins opt-in only」斷言為最優預設契約。
- **subject export**：使用公開 demo fixture，驗證 export 的冪等、既有 hook 未被覆蓋、接線 fragment 可被 check 辨識，以及缺任一 profile 面即 red。
- **suite wiring**：把新增 Node／Python 測試接入 `tools/harness/test-harness.sh`，並在 `checks.py` 只檢查公開 source／fixture，不讀本機 manifest、pin 或 checkout。

舊工程升級入口是正常 `install`（先 `DRY_RUN=1` 顯示遷移計畫，再實際 install），而非要求使用者先卸載 plugin。安裝報告必須列出移除的受管理 bootstrap、保留的使用者檔案、有效 profile、待 re-run 的 client 與 `profile check` 結果。文件把舊 `PLUGIN='superpowers mattpocock-skills'` 範例改為「預設已包含；用 profile 調整」；保留 `PLUGIN` 僅作相容的顯式擴充，不再是推薦路徑。

## 非目標

- 不把 SP 全庫、`using-superpowers`、`brainstorming` 或任何等價全域 bootstrap 改名後重新啟用。
- 不把 `process_scaffold` 做成硬 gate、回覆格式強制器或 per-turn skill 掃描。
- 不維護各客戶端可用模型清單，也不改變既有 model-tier self-assess 原則。
- 不把 generic exporter 變成會盲覆寫任意 subject 的 hooks、規則或業務設定。
- 不把 profile 合規塞進既有 pin／submodule 的 `harness-ready` 語義。
- v1 不實作 `reply_style` 的語義行為，也不新增雲端 profile、使用者全域 profile 或 telemetry。

## 最終驗收

1. 裸 `install` 的 dry-run 與實際輸出都顯示最優包，無需使用者記憶 `PLUGIN`。
2. SP 保持精選 library，但 client tree 與可見技能中沒有 bootstrap hard-gate 與 vendor hook 接管。
3. 四個設定鍵可由唯一 CLI 顯示、讀取、寫入並按 local > repo > built-in 合併；local／state 不進 git。
4. 三控制面分離：description 是主發現面；router 已由三個 client prompt event 消費，預設 lean、advisory、去重且無毒性祈使；`hook-router.mjs` enforcement 對所有 profile 保持不變。
5. Matt 不被 router 自動注入；SP 核心覆蓋 verification、TDD 意圖與 review。
6. profile export/check 可用於公開 fixture 與實際 subject；builder／operate 的升級清單把缺 profile 視為未完成。
7. 舊雙包安裝有安全、可觀察、冪等的直接遷移路徑。
8. `bash tools/harness/test-harness.sh` 通過，並在最終 diff 上執行 `git diff --check` 與公開樹脫敏檢查。
