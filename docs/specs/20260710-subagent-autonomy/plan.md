# Autonomous Subagent Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 明確授權本倉 Agent 自主派出子代理，並把這項授權與後續 subject 升級規則納入公開可信集。

**Architecture:** 根 `AGENTS.md` 是本倉 Agent 行為 SSOT，`CLAUDE.md` 透過 symlink 共用同一內容。`tools/harness/checks.py` 的既有 cross-client dispatch 規則檢查擴充為授權契約；不新增 hook、skill、模板或自動 subject patch。

**Tech Stack:** Markdown Agent 規則、Python 公開可信集、Bash 全量驗證。

---

## File map

- `AGENTS.md`：保存自主派工授權、安全邊界、層級 advisory 與後續 subject 升級規則。
- `CLAUDE.md`：既有 symlink；不直接編輯，可信集以它驗證跨客戶端可見性。
- `tools/harness/checks.py`：驗證兩份實際生效規則都含自主授權契約。
- `docs/specs/20260710-subagent-autonomy/spec.md`：記錄實作狀態與驗證證據。
- `docs/specs/20260710-subagent-autonomy/plan.md`：本計畫與執行勾選紀錄。

### Task 1: 用可信集鎖定自主派工契約

**Files:**
- Modify: `tools/harness/checks.py:501`
- Test: `tools/harness/checks.py`

- [ ] **Step 1: 擴充規則檢查，先製造 Red**

把既有單一判斷：

```python
if "派工前先查層級" not in rules_text or "model-tier-prompting" not in rules_text:
    fail(cid, f"{rules_name} must carry the dispatch-consult pointer "
              "(派工前先查層級 → model-tier-prompting)")
```

替換為：

```python
required_dispatch_rules = {
    "## 子代理自主派工": "autonomous dispatch heading",
    "不需要使用者主動要求或逐次批准": "no per-dispatch user approval",
    "不擴張任務範圍或操作權限": "scope and permission boundary",
    "沒有等價授權": "future subject upgrade propagation",
    "派工前先查層級": "dispatch tier consultation",
    "model-tier-prompting": "model-tier guidance",
}
for marker, description in required_dispatch_rules.items():
    if marker not in rules_text:
        fail(cid, f"{rules_name} missing {description}: {marker}")
```

- [ ] **Step 2: 執行公開可信集，確認因規則尚未加入而失敗**

Run: `python3 tools/harness/checks.py`

Expected: exit 1，`AGENTS.md` 與 `CLAUDE.md` 至少回報缺少 `## 子代理自主派工`；
其他既有檢查維持通過。

### Task 2: 加入本倉自主派工規則並轉 Green

**Files:**
- Modify: `AGENTS.md:83`
- Test: `tools/harness/checks.py`

- [ ] **Step 1: 以核准文本取代現有派工段落**

將現有 `## 派工前先查層級（advisory）` 段落替換為：

```markdown
## 子代理自主派工

本倉明確允許並授權 Agent 自主使用子代理。只要工作仍在使用者原始任務範圍內，且 Agent 判斷委派、平行處理或上下文隔離能提升品質、速度或可靠性，就可以直接派出子代理；不需要使用者主動要求或逐次批准。不得把「使用者未明示要求使用子代理」當成不派工的理由。

這項授權不擴張任務範圍或操作權限。子代理繼承本倉規則及既有 permission / approval 邊界；破壞性操作、外部副作用或實質範圍變更，仍須依原規則取得授權。主 Agent 對任務拆分、結果整合與最終驗證負責，不得把子代理的完成聲明直接當成驗證證據。這是允許自主判斷，不是要求每個任務都必須派工；緊密耦合、無法獨立驗收或派工成本高於收益的工作，可由主 Agent 直接完成。

### 派工前先查層級（advisory）

決定派工後，先諮詢 `model-tier-prompting`（`agent-kit/skills/skills/model-tier-prompting/`）做層級自評：依 roster 的 Intelligence Index 排序當前可用模型，再按任務難度選擇子代理形態、模型與提示厚度。這是派工品質指引，不是使用子代理的許可閘。

### 後續 subject 升級

使用本倉為其他 subject 導入、同步或升級 harness 時，必須檢查目標倉實際生效的 Agent 規則。已有語義等價的自主派工授權則不重複添加；沒有等價授權則把本節的授權與安全邊界納入該次升級；已有明確且更嚴格的限制則不靜默覆寫，保留限制並向使用者報告差異。
```

- [ ] **Step 2: 執行公開可信集，確認契約轉 Green**

Run: `python3 tools/harness/checks.py`

Expected: exit 0，輸出包含 `ok    [hook-wiring]` 與最終
`✔ harness 公開可信集通過`。

- [ ] **Step 3: 提交行為與可信集變更**

```bash
git add AGENTS.md tools/harness/checks.py
git commit -m "feat(harness): authorize autonomous subagent dispatch"
```

### Task 3: 更新設計證據並完成全量收環

**Files:**
- Modify: `docs/specs/20260710-subagent-autonomy/spec.md:3`
- Modify: `docs/specs/20260710-subagent-autonomy/plan.md`
- Test: `tools/harness/test-harness.sh`

- [ ] **Step 1: 更新 spec 狀態與實作證據**

把狀態改為：

```markdown
> 狀態：已實作
```

在文件末尾加入：

```markdown
## 實作證據

- 根 `AGENTS.md` 已加入自主派工授權、既有權限邊界及後續 subject 升級規則；`CLAUDE.md` 透過 symlink 同步生效。
- `tools/harness/checks.py` 會拒絕缺少授權標題、免逐次批准、權限邊界、subject 傳播規則或 `model-tier-prompting` advisory 的規則檔。
- Red：規則文本尚未加入時，公開可信集因 `AGENTS.md` / `CLAUDE.md` 缺少自主派工標記而失敗。
- Green：`bash tools/harness/test-harness.sh` 通過。
```

- [ ] **Step 2: 勾選已完成的計畫步驟**

將本文件所有已執行的 `- [ ]` 改為 `- [x]`，保留命令與預期輸出作為可重跑紀錄。

- [ ] **Step 3: 執行全量可信集與 diff 檢查**

Run: `bash tools/harness/test-harness.sh`

Expected: exit 0，輸出以 `✔ harness 公開可信集通過` 結束。

Run: `git diff --check HEAD`

Expected: exit 0，無輸出。

- [ ] **Step 4: 依 `code-review` 做一次獨立 inline review**

Review scope: `HEAD^..working-tree` 中的 `AGENTS.md`、`tools/harness/checks.py`、
本 spec 與 plan。確認沒有把自主派工誤寫成強制派工、沒有擴張操作權限、沒有立即
修改 subject，也沒有把 `model-tier-prompting` 變成許可閘。發現 blocker 時先修復並
重跑全量可信集。

- [ ] **Step 5: 提交文件證據**

```bash
git add docs/specs/20260710-subagent-autonomy/spec.md docs/specs/20260710-subagent-autonomy/plan.md
git commit -m "docs(spec): record subagent autonomy verification"
```

- [ ] **Step 6: 最終狀態核對**

Run: `git status --short --branch`

Expected: 工作樹乾淨；目前分支只比 `origin/main` 超前本任務的本地 commits，未自動 push。
