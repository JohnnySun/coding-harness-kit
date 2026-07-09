# Advisor Framework — dispatch-time tier consultation

> **Date:** 2026-07-09
> **Status:** implemented（P1 Claude B + Codex B 已實作；**P2 原生 advisor A、P3 Cursor 降級已落地**；兩項決策已鎖定）
> **Scope:** 設計 + 調查 + 實作（機制 A/B 接線、Cursor 降級文件化）。skill 建立/修改仍須經 `skill-creator`。
> **Related:** `docs/specs/20260709-prompt-skill-router/spec.md`（提示提交期 advisory 路由）
> **Skills SSOT:** `agent-kit/skills/skills/{model-tier-prompting,skill-creator}`

## 實作狀態（2026-07-09 更新）

- **P1（Claude B）已實作**：卡片產生器 `tools/harness/advisor-card.mjs`（純函式 +
  unit test）＋ Claude `PreToolUse` matcher `Task|Agent` 注入 `additionalContext`。
- **Codex B（原 P3）已坐实並實作（降級形態）**：Codex **無** `PreToolUse(Task)`
  ——其 `PreToolUse` 只攔 `Bash` / `apply_patch` / MCP，不攔子代理創建。子代理創建
  的表面是 **`SubagentStart`** 事件（fires「當子代理即將 spawn」；`matcher` 作用於
  `agent_type`），支援 `hookSpecificOutput.additionalContext`（注入為**子代理**的
  developer context），且 `continue:false` **不阻擋** spawn——與本卡片 advisory-only
  設計吻合。故 Codex 走 `SubagentStart` → `advisor-card.mjs`。**降級之處**：(1) 注入
  進「子代理」上下文而非 orchestrator 的 spawn 決策點（無法左右「spawn 成什麼形態/
  模型」，只能在子代理啟動時上桌層級卡片）；(2) `SubagentStart` payload **無任務
  文字**（無 `prompt`/`description`），故 Codex 得到的是**通用卡片**；(3) 無原生
  advisor（A，僅 Anthropic API）。→ 原 Open question #1 就此關閉。
- **P2（Claude A）已實作**：原生 `advisor` 經 **`advisorModel` settings 鍵**接線——落
  `agent-kit/hooks/clients/claude.settings.json`（`"advisorModel": "fable"`），
  `agent-kit.sh install` 時整份 settings.json 由 install.py materialize 到
  `.claude/settings.json`（見 install.py `write_json(... load_json(claude.settings.json))`）。
  文件三入口（`/advisor` 指令 / `advisorModel` settings / `--advisor` 旗標）中，
  **settings 鍵**是唯一能「不進互動 session、隨 install 落盤成預設」的路徑，故採之。
  選 `fable`（roster Index 60，frontier；alias 解析為最新 Fable）為**最強 tier alias**，
  符合 self-assess 決策「最強可用當 advisor」的錨點。約束（照文件）：(a) advisor 能力
  **必須 ≥ 主模型**否則**不掛載**（Fable > Opus/Sonnet，對任何 main 皆滿足配對）；
  (b) **僅 Anthropic API**（Bedrock/Vertex/Foundry 及非直連 gateway 無此工具）→ 於其他
  provider **靜默 no-op**；(c) **實驗性**，需 Claude Code **v2.1.98+**，`fable` 另需
  **v2.1.170+ 且組織開放 Fable 5 access**，否則該 alias 不生效／退回不掛載——此時
  **機制 B（dispatch 卡片）仍強制把層級查表上桌**，A 只是缺席的第二意見。
  A 與 B **互補不重疊**：B 每次 dispatch 確定性上桌層級卡片；A 由模型在決策點自行諮詢。
  契約：`checks.py check_hook_wiring` 斷言 `advisorModel` 為 tier alias／`claude-*` model id；
  `test_agent_kit_install.py::test_install_writes_claude_advisor_model` 斷言 install 落盤。
- **P3（Cursor 降級）已坐實並文件化**：Cursor hook 表面僅
  `beforeShellExecution` / `afterFileEdit` / `stop` / `beforeSubmitPrompt`
  （見 `agent-kit/hooks/clients/cursor.hooks.json`），**無 dispatch / 子代理創建事件**，
  故機制 B 的 dispatch 卡片（L1）**無法在 Cursor 觸發**，且無原生 advisor（A 不可用）。
  Cursor 的降級階梯就此**確定為**：**無 L1 dispatch 卡片 → L2 提示提交期 advisory
  （`beforeSubmitPrompt` → `prompt-skill-router.mjs`，命中 intent 時建議讀
  `model-tier-prompting`）→ L3 純 skill 描述觸發**（`model-tier-prompting` 已在
  profile，靠 description 召回）。此為**誠實的能力上限文件化**，非偽造 dispatch hook。
  L2 路徑**已就緒**：`cursor.hooks.json` 既有 `beforeSubmitPrompt` → `prompt-skill-router.mjs`
  接線（`checks.py` 已斷言），router 的 `model-tier-prompting` intent 規則已涵蓋
  「派工 / 子代理 / dispatch + prompt」語彙（見 `selectPromptSkills`），故 Cursor 使用者
  在提示提交時本就會被 nudge 去查層級。**本次 P3 為文件化 + 契約確認，未改 Cursor 程式碼**
  （不新增假的 dispatch 事件）。
- **Cursor 對 L1（dispatch 卡片）仍受阻**：無 dispatch / 子代理創建事件，維持 L2/L3（見上）。

## TL;DR

問題：`model-tier-prompting` 目前只在**人類提示提交**時被 advisory 注入，**沒有**在
**子代理創建（dispatch）**時被讀取。因此 orchestrator 決定「派什麼形態的子代理、
用哪個模型」時，層級指引不在上下文裡——這是本文要填的 GAP。

定案設計（**A + B 互補**，兩者皆採）：

- **機制 B（主軸，跨客戶端）**：在子代理創建事件上，把「任務 → 層級查表 →
  建議子代理形態 + 模型 + 提示厚度」注入為 additionalContext，**強制把層級查表
  上桌**。
- **機制 A（加值，僅 Claude Code）**：疊加原生 `advisor`，在決策點提供**第二意見**。

**可用模型來源（決策 2：self-assess）**：harness **不**維護任何 per-client
可用模型清單 / allowlist。advisor 卡片改為**指示執行中的模型自行**把它自己的
模型選單對照 roster（依模型名 + Intelligence Index）挑出**當前最強可用者**——
「最強可用當 advisor」的回退是**給模型的指令**，不是 harness 記帳。roster 因此
保持**工具無關**，只作為模型推理時的排序依據。

可行性**逐客戶端不同**：Claude Code 有原生 advisor 工具 + `Task` 可掛
`PreToolUse` → **可做（A+B）**；Codex 表面較窄 → **部分（B 降級）**；Cursor 無
dispatch 事件 → **受阻**，退化成提示提交期 advisory（L2/L3）。

## Q1 現況：層級指引在「子代理創建」時被讀了嗎？

**否（No）。** 層級指引只在**提示提交**時注入，不在 dispatch 時。

### 佈線圖（event → script → 注入什麼）

| 客戶端 | 事件 | 腳本 | 注入 / 行為 |
|---|---|---|---|
| Claude Code | `UserPromptSubmit` | `tools/harness/prompt-skill-router.mjs` | advisory 注入 `model-tier-prompting` / `refine`（依 intent 命中） |
| Claude Code | `SessionStart` | `tools/harness/hook-router.mjs` | 脫敏 advisory |
| Claude Code | `PreToolUse`（matcher **`Bash`**） | `hook-router.mjs` | 私有樹 / claimed-done 硬閘 |
| Claude Code | `PostToolUse`（`Write\|Edit\|…\|Bash`）、`Stop`、`SubagentStop` | `hook-router.mjs` | arm pending / 收環閘 |
| Codex | `UserPromptSubmit` | `prompt-skill-router.mjs` | 同上（advisory 注入） |
| Codex | `SessionStart` / `PreToolUse(Bash)` / `PostToolUse` / `Stop` / `SubagentStop` | `hook-router.mjs` | 同上 |
| Cursor | `beforeSubmitPrompt` | `prompt-skill-router.mjs` | advisory 注入（`continue:true` + `agent_message`） |
| Cursor | `beforeShellExecution` / `afterFileEdit` / `stop` | `tools/harness/cursor-hook.mjs` | 硬閘 / arm |

### 證據（file + event）

1. **只在 prompt-submit 觸發**：`tools/harness/prompt-skill-router.mjs`
   `isPromptSubmitEvent()`（第 113–119 行）只認 `UserPromptSubmit` /
   `userPromptSubmit` / `beforeSubmitPrompt`；`main()`（第 192–195 行）對**任何
   非 prompt-submit 事件直接 `{}` no-op**。→ 子代理創建不會走到注入路徑。
2. **沒有 dispatch/Task 事件被掛**：`agent-kit/hooks/clients/*` 三個模板裡，
   `PreToolUse` 的 matcher 只有 **`Bash`**（Claude `claude.settings.json` 第 29 行；
   Codex `codex.hooks.json` 第 27 行）。全樹 grep `Task|subagent|dispatch` 只命中
   **`SubagentStop`**（`claude.settings.json:65`、`codex.hooks.json:60`）。
3. **`SubagentStop` ≠ 創建**：`SubagentStop` 在子代理**結束後**才 fire
   （`hook-router.mjs` 第 198–215 行，處理 Stop/SubagentStop 的收環閘），
   對「創建時選形態/選模型」的決策無用。

**結論**：`model-tier-prompting` 在**人類提示提交**時被 advisory 注入，
**不在子代理 spawn（Task / MoE / sub 派工）時**被讀取。使用者的假設**成立**。

### GAP

Orchestrator 在呼叫 `Task`（或等價子代理創建）那一刻，上下文裡**沒有**
層級查表結果，因此「用哪種子代理形態、指派哪個模型、提示要多厚」全憑模型
即興判斷，`model-tier-prompting` 的 roster / 三層速查沒有在**決策點**被強制上桌。

## Q2 Advisor 文件摘要

> 來源：<https://code.claude.com/docs/en/advisor>（WebFetch，2026-07-09）

- **是什麼**：`advisor` 是 Claude Code 的**實驗性 server 工具**（需 v2.1.98+，
  **僅 Anthropic API**；Bedrock / Vertex / Foundry 不支援）。讓主模型在關鍵時刻
  諮詢**第二個、通常更強**的模型；advisor 收到**完整對話**（含每個 tool call
  與結果），回傳指引供主模型套用後再繼續。
- **何時被叫**：**由主模型自行決定**時機——傾向在「敲定方案前 / 反覆同一錯誤時 /
  宣稱完成前」諮詢；規則是**模型驅動非硬規則**。使用者可在提示裡要求
  「consult the advisor before you continue」，但沒有強制/上限設定。
- **設定面**：三種入口——`/advisor` 指令（存成預設）、settings 的
  `advisorModel`、啟動旗標 `--advisor`。alias `opus` / `sonnet` / `fable` 解析為
  各家最新版；也可給完整 model id（如 `claude-opus-4-8`）。關閉：`/advisor off`
  或 `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1`。
- **配對規則（關鍵）**：**advisor 能力必須 ≥ 主模型**。若 advisor 較弱則**不
  掛載**；若被組織 `availableModels` allowlist 排除則不被呼叫；子代理**繼承**
  所設 advisor，並對**自己的模型**重跑同一配對檢查。
- **成本 / 快取**：每次 advisor call 按 advisor 費率吃整段對話 token；主模型
  prompt cache 不因開關 advisor 失效；advisor 自身讀對話**不快取**。
- **解決什麼問題**：長、多步任務中「多數回合例行、但方案品質決定成敗」的情境
  ——用快主模型跑例行、在決策點升級到強模型把關，通常比全程跑強模型便宜。
  文件明確與 `opusplan` / subagents(`model` set) / `/model` 對比：advisor 是
  **決策點 mid-task 的第二意見**，由 Claude 自行呼叫。

## Q3 提案：Advisor Framework（dispatch-time tier consultation）

目標：在**子代理創建**時，讓 orchestrator 諮詢層級指引，選出**最適子代理形態 +
模型 + 提示厚度**，並帶「最強可用模型當 advisor」的（模型自評）回退。**定案採
A + B 互補**，兩者職責分明：

- **機制 B — Harness 自有的 dispatch advisor（主軸，跨客戶端目標）**：在子代理
  創建事件（如 Claude `PreToolUse` matcher `Task`）掛一個 hook，注入
  **tier-lookup 卡片**當 additionalContext。這是本 harness 要**新增**的表面，
  負責把層級查表**強制上桌**——涵蓋 A 到不了的 Codex/Cursor。
- **機制 A — 原生 advisor 工具（加值，僅 Claude Code）**：疊加 `advisorModel`，
  讓主模型在「決策點」諮詢更強模型（含「該不該 spawn 子代理、spawn 成什麼」）。
  這是**現成能力**、零程式碼，但時機由模型決定、且僅 Anthropic API。

**互補分工（避免雙重注入噪音）**：B 保證**每次 dispatch** 都有層級查表在上下文；
A 只在模型判斷需要第二意見時、於決策點介入。B 是**確定性的資訊上桌**，A 是
**選擇性的品質把關**。兩者不重疊：B 不諮詢模型、A 不查 roster 卡片。

### B 注入什麼（advisor 卡片內容）

dispatch 事件觸發時，卡片注入的是**給執行中模型的指示 + roster 摘要**（不含任何
harness 側維護的模型清單），要模型自評並產出：

1. **層級查表（self-assess）**：卡片附 roster 的層級/Index 摘要，並**指示模型**
   把它自己選單裡的候選模型對照 `references/model-roster.md`（模型名 + Intelligence
   Index）→ 歸 frontier-agentic / 主力 / 快速經濟。名不在表上 → 依卡片指示跑
   SKILL.md [歸層探針](../../../agent-kit/skills/skills/model-tier-prompting/SKILL.md)。
2. **建議子代理形態**：一次性 headless 派工 vs 互動 session vs 平行 fan-out
   （對照 `references/delegation-prompts.md` 的派工契約）。
3. **建議模型**：指示模型以「任務難度 × roster 排序」自選一檔（例：開放式難推理 →
   當前最強可用者；量大格式固定 → 經濟層 + 外置 verifier）。
4. **提示厚度**：frontier → 拆腳手架（why/邊界/證據錨定）；經濟 → 加腳手架
   （步驟/格式契約/few-shot）。即 `model-tier-prompting` 三層速查的方向指引。

> 卡片是**無狀態的指示 + roster 排序依據**；判斷「哪些模型當前可用」永遠是**模型
> 自評自己的選單**，harness 不記帳。這保住 roster 工具無關。

### 「最強可用模型當 advisor」選擇 / 回退邏輯（決策 2：self-assess，指令化）

不再由 harness 維護 `availableModels` / allowlist。fallback 是**寫進卡片的一段
指令**，要執行中模型對**自己的**模型選單這樣推理：

1. **列自己的選單**：模型枚舉它當前實際可選的模型（它比 harness 更清楚自己有什麼）。
2. **依 roster 排序**：對照 roster Index 由高到低排（Fable 5=60 > Opus 4.8=56 >
   GPT-5.5=55 > Grok 4.5=54 > Sonnet 5=53 …）；表上無 Index 者標「（啟發式）」殿後。
   roster 只提供**排序這一件事**，供模型推理，不作 harness 側比對。
3. **選最強可用**：取自己選單中 roster 排序最高、且滿足所在客戶端配對約束者當
   advisor。
   - Claude 原生 advisor 另要求 **advisor ≥ 主模型**（此約束由 Claude 端強制，
     非 harness）。
   - 指定 advisor（如 `fable`）**不可用**時（Fable 5 觸發 guardrail 自動 fallback、
     或未開放）→ 模型**自行回退到選單中次高可用者**（實務上多為 Opus 4.8，
     「當前最強**可用**」）。這即使用者要的 fallback，只是判斷主體從 harness 移到
     模型。
4. **錨定約束**：roster 已載明「最強可用 ≠ frontier」——Opus 4.8 是**主力之首**。
   「用最強可用當 advisor」是**選 advisor 模型**的策略，**不**改變被建議子代理該用
   哪種**提示厚度**（那由子代理自己的層級決定）。兩者不可混淆。

### 優雅降級階梯（A + B 皆在 scope 下的完整定義）

既然 A（Claude 原生 advisor）與 B（dispatch 卡片）都採，降級階梯明確如下——
**B 是主軸階梯、A 是可疊加的最上層加值**：

| 層 | 手段 | 覆蓋客戶端 |
|---|---|---|
| **L1+A**（最佳，僅 Claude Code） | B 的 dispatch 卡片（強制層級查表上桌）**＋** 原生 `advisor` 決策點第二意見 | Claude Code |
| **L1**（B 主軸） | dispatch 事件 hook 注入 advisor 卡片（機制 B），無原生 advisor | Claude Code（若不開 A）、Codex（若表面坐實） |
| **L2** | 提示提交期 advisory（現有 `prompt-skill-router`）+ SessionStart 提醒「派子代理前先查層級」 | Cursor；Codex 若 dispatch 表面不可 hook |
| **L3** | 純 skill 描述觸發（`model-tier-prompting` 已在 profile）+ orchestrator 的 system/AGENTS 指引「dispatch 前查 roster」 | 全客戶端保底 |

落點：**Claude Code → L1+A**（完整 A+B）；**Codex → L1 或 L2**（視 dispatch 表面
是否可 hook 而定，無 A）；**Cursor → L2/L3**（無 dispatch hook、無 A）。A 永遠是
**Claude Code 專屬的最上層加值**，不是任何客戶端的保底層——保底永遠由 B/L2/L3
（跨客戶端）承擔。

## 可行性判定（逐客戶端）

| 客戶端 | 判定 | 理由（一行） |
|---|---|---|
| **Claude Code** | **可做（can-do，A+B）** | `PreToolUse` matcher **`Task`** 可注入 dispatch 卡片（B），再疊原生 `advisor`（A）於決策點；alias 提供「最新版」解析。可用模型由**模型自評**，harness 不需 allowlist。 |
| **Codex** | **部分（partial，B 降級）** | 有 `PreToolUse` hook 機制，但目前只掛 `Bash`；能否精確匹配子代理創建工具、子代理表面語意需先坐實；無原生 advisor（A 不可用）。可做 B 降級版，時機/覆蓋不如 Claude。 |
| **Cursor** | **受阻（blocked，for L1）** | hook 表面僅 `beforeShellExecution` / `afterFileEdit` / `stop` / `beforeSubmitPrompt`，**無 dispatch / PreToolUse(Task) 事件**，也無 A；只能退化到 L2/L3。 |

**總判定：可行，但非齊頭並進**——Claude Code 完整落地（L1+A），Codex 部分
（L1 或 L2，無 A），Cursor 僅降級（L2/L3）。跨客戶端一致的載體是**與工具無關的
roster + 一份 self-assess 式 advisor 卡片產生器**：卡片只帶指示與排序依據，
「當前可用模型」永遠由執行中模型自評，各客戶端按表面能力接入對應層。

## 若涉及建立 / 修改任何 skill：必經 skill-creator

本框架若需**新增或修改任何 skill**（例：把 advisor 決策協定封裝成一個
`dispatch-advisor` skill，或擴充 `model-tier-prompting` 的 dispatch reference），
**一律必須經 `skill-creator` skill 操作**，不得手搓：

- 讀並遵循 `.cursor/skills/skill-creator/SKILL.md`
  （SSOT 源：`agent-kit/skills/skills/skill-creator/SKILL.md`）。
- 交由 skill-creator 把關：**SKILL.md 結構**、**description 觸發品質**（讓
  dispatch 場景能正確召回）、**reference-file 慣例**、**eval harness**（用
  variance 分析驗證觸發率與行為）。
- 任何 skill 的最終落點仍是 `agent-kit/skills/skills/`（SSOT submodule），
  再經 `agent-kit.sh install` 暴露到各客戶端；客戶端樹不進 git。

## 已鎖定的決策

- **決策 1（機制）**：**A + B 互補**，兩者皆採。B 為跨客戶端主軸（強制層級查表
  上桌）；A 為 Claude Code 專屬加值（決策點第二意見）。原本「A/B 是否重疊」的
  open question 就此定案為**互補、不重疊**（B 不諮詢模型、A 不查卡片）。
- **決策 2（可用模型來源）**：**self-assess**。harness **不**維護 per-client 清單
  / allowlist；「最強可用當 advisor」是**寫進卡片、交給執行中模型自評自己選單**
  的指令。原本「候選模型清單來源」的 open question 就此關閉——roster 保持工具無關，
  只當模型推理時的排序依據。

## Open questions / risks

1. ~~**Codex 子代理表面未坐實**~~ **（已關閉，見「實作狀態」）**：Codex 無
   `PreToolUse(Task)`，但有 **`SubagentStart`** 事件支援 `additionalContext` 注入
   （降級 B：注入進子代理上下文、無任務文字）。Codex 落 **L1（降級）**，已實作。
2. **Cursor dispatch 事件缺口**：是否有（或未來會有）`beforeSubagent` / Task 類
   事件？無則 Cursor 長期只能 L2/L3。
3. **self-assess 的可靠度**：模型自評「自己有哪些模型可用」可能不準（不知道
   完整選單、或誤判 Index）。卡片需明確要求「不確定就跑歸層探針」，並接受
   偶發次優選擇作為換取工具無關的代價。
4. **roster 時效**：Index 是拋棄式快照；模型推理排序依賴它，需綁定「過時就跑
   歸層探針回填」的既有規則，否則自評排序會錯。
5. **advisor 成本（A）**：原生 advisor 每次 call 吃整段對話 token；dispatch 密集的
   fan-out 場景若頻繁諮詢，成本需上限或節流策略。
6. **雙重注入噪音**：Claude L1+A 下，B 卡片與 A 指引可能在相近時點都出現；需在
   卡片措辭上分工清楚（B=資訊上桌、A=第二意見），避免互相覆蓋。

## 分階段下一步（actionable）

**P0（前置調查，不寫碼，≤ 半天）**：只坐實 P1 需要的一件事——實測 Claude
`PreToolUse` matcher `Task` 的 hook payload：拿得到**任務描述**嗎？能回傳
`additionalContext` 注入子代理上下文嗎？（Codex/Cursor 表面留到 P3 再測，不擋 P1。）

**P1（先原型這個 → 最小可用切片）**：**Claude Code 上的 B**——一條垂直切片，
把「卡片產生器 + dispatch-hook」在**唯一表面已就緒的客戶端**打通：

- **產物 1｜卡片產生器（工具無關純函式）**：輸入=任務描述（+ 卡片自帶的 roster
  排序摘要）；輸出=一段 **self-assess 卡片文字**——指示模型自評選單→歸層→選
  形態/模型/提示厚度/advisor+fallback。**純函式、可 unit test、不含任何可用模型
  清單、不掛 hook**。
- **產物 2｜Claude `PreToolUse(Task)` 接線**：把產生器輸出當 `additionalContext`
  注入（沿用 `hook-router.mjs` 的注入慣例）。
- **收環**：新增 unit test + 跑 `bash tools/harness/test-harness.sh`；改了 hook
  模板則 `for c in cursor claude codex; do CLIENT=$c bash tools/harness/agent-kit.sh install; done`。
- **此步不涉及 skill。** A（原生 advisor）此階段**先不接**，避免雙重注入干擾
  B 的驗證。

**P2（疊加 A + 觀察）✅ 已完成**：在 P1 之上，於 Claude Code 疊原生 `advisor`——
經 `advisorModel: "fable"` settings 鍵落 `claude.settings.json`，install materialize
到 `.claude/settings.json`。純配置 + 文件 + 契約斷言，無新運行程式。L1+A 分工：
B 每次 dispatch 確定性上桌卡片、A 決策點選擇性第二意見（見「實作狀態 · P2」）。
雙重注入噪音由措辭分工（B=資訊上桌、A=第二意見）緩解，屬 Open question #6 的持續觀察項。

**P3（Codex/Cursor 降級接入）✅ 已完成**：Codex 走 `SubagentStart` → `advisor-card.mjs`
（B 降級版，見「實作狀態」）；**Cursor 落 L2/L3**——無 dispatch hook，維持
`beforeSubmitPrompt` → `prompt-skill-router.mjs`（L2）+ skill 描述召回（L3），
文件化為誠實能力上限（見「實作狀態 · P3」）。未偽造 Cursor dispatch 事件。

**P4（若要沉澱為 skill → 必經 `skill-creator`）**：若決定把 dispatch 決策協定
封裝成 skill（或擴充 `model-tier-prompting` 的 dispatch reference），**一律用
`skill-creator`** 產出 SKILL.md + references + eval，落 `agent-kit/skills/skills/`
再 `agent-kit.sh install`。**不得手搓 skill。**

> 全程 design → 原型 → 收環；**任何 skill 建立/修改一律走 skill-creator**
> （見上節）。

## 建議的第一步（可直接批准）

**先做 P1 在 Claude Code 上的垂直切片**：一個**工具無關的 self-assess 卡片產生器
（純函式 + unit test）**，接到 **Claude `PreToolUse(Task)`** 用 `additionalContext`
注入。理由：Claude 是**唯一 dispatch 表面已就緒**的客戶端，能最快證明「dispatch
時把層級查表強制上桌」這條核心價值；卡片走 self-assess 故**不需任何可用模型清單**；
先不接原生 advisor（A）以隔離驗證 B。P0 只需先確認該 hook payload 拿得到任務描述。
**批准後才動工；本步不涉及 skill，也不 commit/push。**
