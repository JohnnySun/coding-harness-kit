# Retro inbox

> 寫入：Stop 反思 gate / 人工登記。消費：SessionStart 提醒 + 一拍一條（harness-operate）。  
> 狀態：`new` → `consuming` → `converted(<證據>)` | `rejected(<原因>)`

## converted — 2026-07-14 — rename to Los Santos Customs

- **status**: `converted(display name + GitHub slug los-santos-customs 2026-07-14)`
- **summary**: 顯示名改為 **Los Santos Customs**（LSC / 洛聖都改車王）；公開 GitHub repo 改為 `JohnnySun/los-santos-customs`。
- **follow-up**: 無。

## converted — 2026-07-09 — product naming

- **status**: `converted(README+AGENTS display name coding-harness-kit 2026-07-09)`
- **summary**: 顯示名定為 **coding-harness-kit**——構建 / 迭代 coding harness 的工具倉（meta harness）。舊候選 Keel / Coderig / Belay / harness-bench 不採。
- **follow-up**: 已於 2026-07-14 改為 Los Santos Customs / `los-santos-customs`。

- **follow-up**: 硬 rename 本機目錄可另拍；公開 GitHub repo 名用 `coding-harness-kit`。

## consuming — 2026-07-12 — review revision scope growth

- **status**: `consuming(2026-07-12)`
- **summary**: plan-review 為修補本拍 finding，連續把「全 client 可發現性」擴成持久 install transaction，新增 state、fsync、migration、concurrency 邊界後反覆生成 blocker；主 Agent 沒有執行既有「修訂不得擴 scope」規則。
- **failure-class**: review-revision-scope-growth
- **current-gap**: review ledger 能分類 late finding，卻沒有強迫每次 material revision 比對 original acceptance boundary；建議修法可能悄悄新增子系統責任。
- **mechanism**: revision 前產生 scope delta；若新增 persisted state、外部副作用、權限、public API 或新的 lifecycle owner，必須轉 needs-decision/deferred work，不得直接留在原 loop 修訂。
- **applies-when**: adversarial review、plan revision、Reviewer F coverage finding。
- **not-applicable-when**: 修訂只補齊原 acceptance 已明列的 schema、測試或錯誤語義。
- **evidence-level**: closed-loop
- **follow-up**: 本拍以縮小 P0 spec 作 dogfood；plan-review skill 加 scope-delta checkpoint 與真實 bad-case eval。

## new — 2026-07-15 — same-source skill propagation

- **status**: `new`
- **summary**: `plan-review` 與 `model-tier-prompting` 是上游 subject、factory source 與未來 consumer repo 之間的多倉同源 skills；任一副本出現分檔、輸出契約、角色路由或其他結構性改造時，不能只在單倉封閉演進。
- **mechanism**: 修改任一同源副本時，先盤點其餘副本與各倉實際治理規則；評估是否同步、泛化或明確拒絕，並把結果留在該次工單。factory 版本保持 project-agnostic，subject 專屬 overlay 留在 consumer 側。
- **applies-when**: 同源 skill 的結構、eval、輸出 schema、review profile、模型派工檔位或角色憲章變更。
- **not-applicable-when**: 純文字修正且不改變 skill 行為、觸發、契約或派工結果。
- **evidence-level**: policy-recorded
- **follow-up**: 後續升級其他 subject 時比照辦理；有等價機關則不重複添加，有更嚴格治理則保留並回報差異。
