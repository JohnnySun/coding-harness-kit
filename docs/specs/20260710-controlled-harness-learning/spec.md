# 受控 Harness 學習與自我迭代

> 狀態：待 `plan-review`
>
> 日期：2026-07-10
>
> 方法：`harness-builder` 定義控制面，`harness-operate` 負責落地收環，
> `skill-creator` 建立並評測新的 `harness-learn` skill。

## 1. 問題

本倉目前能把上游 subject 的 harness 表面同步、匯入、比較並以四層 0–2 分做
描述性評分，但流程停在「看見差異」：

- `import` 只保存約束、強制、回流、進化四層證據。
- `compare` 只比較檔案清單與層級分數。
- `score` 明確聲明 0–8 是 surface inventory heuristic。
- `harness-operate` 能消費本倉既有反思，卻沒有受控入口接收從 subject 學到的
  通用機關。

因此本倉像一間會檢查車況、卻不會把修車經驗整理成新工具的汽修廠。更強的
subject 做法即使已被看到，也只能靠當次 Agent 臨場記住，無法穩定回流到本倉，
更無法在後續升級其他 subject 時複用。

## 2. 決策摘要

採用「受控自我迭代」，而不是直接自動吸收：

1. 新增 `harness-learn`，只做發現、證據整理、泛化與候選晉升。
2. 候選先寫入 gitignored 的 `comparisons/learning-candidates/`，保留來源證據但
   不進公開樹。
3. 候選只有通過 readiness、證據、泛化、脫敏、去重與覆核六道閘，才能以
   `source: subject-learning` 寫入既有 `docs/harness/retro-inbox.md`。
4. `harness-operate` 是唯一實作端：一次消費一條已晉升 insight，以 TDD、review
   與全量可信集把它轉成機關，或留下可查證的拒絕理由。
5. 學習流程沒有 `apply` 或直接 patch subject／本倉的入口。學到不等於採用，
   採用不等於未驗證地發布。

## 3. 目標與非目標

### 3.1 目標

- 從 harness-ready subject 的已匯入證據中辨認「比本倉目前更能預防某類失敗」
  的做法，而不是只列差異。
- 把 subject 專屬實作蒸餾成跨工程可理解的問題、機關、適用面與反例。
- 讓原始證據留在本機，公開樹只接收已脫敏、可泛化的 insight。
- 讓重複觀察冪等，不因多個 subject 有同一優點而灌爆 inbox。
- 讓每條 insight 有明確消費端，最後能進入本倉方法論、工具、模板或 gate，並在
  後續 subject 升級時被複用。

### 3.2 非目標

- 不把 0–8 描述性評分改成「誰比較先進」的總排名。
- 不從任意業務源碼、未 pin checkout、網路搜尋或未匯入路徑學習。
- 不把 subject 的原文、識別資訊、remote、pin 或本機路徑寫入公開樹。
- 不自動照抄 subject 的 hook、prompt、skill 或腳本。
- 不建立無消費端的新公開帳本。
- 不讓學習動作擴張目前任務的權限、外部副作用或破壞性操作邊界。

## 4. 「優點」的判定式

「不同」不等於「更好」。候選必須同時回答：

| 問題 | 必要答案 |
|---|---|
| 預防什麼 | 一個具體且可重現的失敗類型 |
| 現況缺口 | 本倉目前沒有攔截，或只在更晚、更弱的層級攔截 |
| 為何更強 | subject 的機關能更早、可執行或閉環地預防該失敗 |
| 為何可搬 | 原理不依賴單一產品、團隊、host、供應商或私有命名 |
| 搬去哪裡 | 本倉明確的 target surface：方法論、工具、模板、skill 或 gate |
| 何時不適用 | 至少一個反例、成本界線或不採用條件 |

證據分三級：

| 級別 | 定義 | 能否晉升 |
|---|---|---|
| `prose` | 只有規則或設計敘述 | 否；保留為 hypothesis |
| `executable` | 有 gate、checker、test 或可重現命令之一 | 可以，但仍須證明本倉缺口 |
| `closed-loop` | 有寫入端、強制端、驗證端與消費端形成閉環 | 可以；仍須過其餘閘 |

檔案更多、文字更長、模型提示更嚴或分數更高，都不能單獨構成優點。

## 5. 邊界與角色分離

```text
harness-ready subject
        │
        ▼
imported snapshot ──► harness-learn ──► private candidate
                                            │
                       six gates + review ──┘
                                            ▼
                              retro-inbox (source: subject-learning)
                                            │
                                            ▼
                                    harness-operate
                                            │
                              TDD + review + trusted suite
                                            ▼
                                 reusable kit mechanism
                                            │
                                            ▼
                               later subject upgrades
```

### 5.1 `harness-learn`

負責：

- 確認 subject 與 snapshot 可作為證據。
- 把觀察整理成候選 schema。
- 區分差異、假說與可晉升優點。
- 執行機械驗證、產生穩定 fingerprint、脫敏並冪等晉升。

不負責：

- 修改本倉機關。
- 修改任何 subject。
- 宣稱候選已解決問題。
- 取代 `harness-builder` 的設計判斷或 `harness-operate` 的施工節拍。

### 5.2 `harness-operate`

沿用既有七步節拍，只擴充一個合法來源：

- 可認領 `source: subject-learning` 且 `status: new` 的條目。
- 先對齊本倉真實缺口，再決定 `converted`、`rejected` 或 `needs-decision`。
- 若轉成機關，必須 Red→Green、跑全量可信集、完成 code review，再收帳。

`harness-operate` 不回讀 private candidate 作為公開設計依據；公開條目本身必須有
足夠的泛化問題與機關描述，來源細節只用於本機查證。

## 6. 狀態機

```text
hypothesis ──補可執行證據──► eligible ──六閘通過──► promoted
    │                            │                         │
    ├──證據不足─────────────────┘                         ▼
    ├──只屬於單一 subject──► rejected                 consuming
    ├──與既有機關重複──────► rejected                    │
    └──涉及取捨/擴權───────► needs-decision              ├──► converted
                                                         ├──► rejected
                                                         └──► needs-decision
```

狀態含義：

- `hypothesis`：觀察成立，但只有 prose、缺本倉 gap 或缺反例。
- `eligible`：具備可執行／閉環證據，且所有必填泛化欄位完整。
- `promoted`：已冪等寫入 retro inbox；不代表已實作。
- `needs-decision`：會擴張權限、改變公開契約、引入重大成本或存在不可消解衝突。
- `rejected`：保留原因，避免後續 Agent 重付同一筆分析成本。

## 7. 深模組與外部介面

新增 `tools/lib/subject_learning.py` 作為學習深模組。它隱藏：

- readiness 與 exact pinned snapshot 驗證；不得沿用只按 mtime 選擇的
  `latest_snapshot()`。
- candidate schema 與狀態轉移。
- evidence path 必須位於該 snapshot 四層內的檢查。
- 公開／私有欄位分離與脫敏規則。
- generalized fingerprint 與 promotion orchestration。

另新增 `tools/lib/retro.py` 作為 retro 結構解析／rendering 深模組，由 learning promotion
與 `weekly_report.py` 共用。它只把真正的 entry heading 與 `status` 欄位算成條目，不以
全文字串計數；現況 `inbox_new_count()` 會把 legend 中的 `` `new` `` 誤算成 backlog，
本拍一併用回歸測試修正。

CLI adapter 為 `tools/learn/learn_subject.py`，P0 只提供三個動作：

```text
inspect <subject>              # read-only：確認 readiness、exact snapshot、證據層
record <subject> --input FILE  # 驗證並寫入固定 private candidate 路徑
promote <candidate.json>       # 六閘、去重後追加一條 public retro entry
```

刻意不提供：

- `apply`、`patch`、`sync-back` 或任何直接改碼動作。
- 任意 `--out`；private candidate 的落點由深模組決定。
- 跳過 readiness、snapshot、脫敏或覆核的 escape hatch。
- 從 live checkout 任意路徑讀取證據的選項。

CLI 的參數解析、檔案 I/O 與訊息輸出保持薄；學習判定集中在
`subject_learning.py`，retro 結構集中在 `retro.py`，讓單元測試可直接驗證同一份
規則，避免 CLI、weekly report 與 skill 各自發明語義。

exact snapshot 必須同時滿足：目錄名稱對應目前 pin、`manifest.subject` 對應目標、
`manifest.shell_sha` 等於完整目前 pin。snapshot 內證據以 `lstat` 判斷，遍歷不得
follow symlink；symlink 可以被列為 metadata，但不能作為可讀證據或被解引用到 snapshot
外。這一條專門封住匯入層目前會保存 resolved absolute symlink 的逃逸面。

## 8. Private candidate 契約

候選預設寫入：

```text
comparisons/learning-candidates/<fingerprint>.json
```

最小 schema：

```json
{
  "schema_version": 1,
  "status": "eligible",
  "source": {
    "subject": "<private-id>",
    "shell_sha": "<pinned-sha>",
    "snapshot": "snapshots/<private-ref>",
    "evidence": [
      {
        "layer": "gates",
        "path": "<snapshot-relative-path>",
        "level": "executable",
        "claim": "<what this artifact proves>"
      }
    ]
  },
  "generalization": {
    "failure_mode": "<failure prevented>",
    "current_gap": "<why the kit is weaker>",
    "mechanism": "<portable principle, not copied implementation>",
    "target_surfaces": ["<kit surface>"],
    "applies_when": ["<precondition for the mechanism>"],
    "not_applicable_when": ["<counterexample or cost boundary>"]
  },
  "review": {
    "decision": "passed",
    "rationale": "<evidence-backed second-pass conclusion>"
  }
}
```

約束：

- `claim` 只能描述證據作用，不能貼長段原文。
- `path` 必須是 snapshot 內相對路徑，不能是 home 或 checkout 絕對路徑。
- `target_surfaces` 使用公開、穩定的本倉 surface 類別，不接受任意私有路徑。
- fingerprint 只由規範化後的 `failure_mode + mechanism + target_surfaces +
  applies_when + not_applicable_when` 推導；不含 subject identity、日期或 evidence path，
  才能跨來源去重。
- private candidate 可以保留來源 id、pin 與 snapshot reference，且因此永不進 git。

## 9. 六道晉升閘

| 閘 | 失敗行為 |
|---|---|
| readiness | subject 非 harness-ready 或 pin 漂移：exit 1，不產候選 |
| evidence | snapshot 不存在、證據越界、僅 prose 或 claim 無法支持機關：不晉升 |
| generalization | 缺 failure、gap、mechanism、target 或反例：保留 hypothesis |
| privacy | public projection 含來源 identity、pin、remote、絕對路徑或 raw excerpt：exit 1 |
| dedupe | fingerprint 已在 inbox 或已 converted：冪等回報，不重複追加 |
| review | 沒有第二遍 evidence-backed 結論，或結論為 conflict：不晉升 |

「review」是語義品質閘，不冒充安全身分驗證。P0 由 `harness-learn` 要求 discoverer
之外的獨立 reviewer lane 重新檢查 evidence 與 kit gap；CLI 驗證 review 欄位與
決策完整，但不宣稱能從字串證明 reviewer 的真實身分。

promotion 以 `comparisons/` 下的私有 lock 搭配 OS advisory `flock` 串行化：取得 lock
後重新 parse inbox、再次檢查 fingerprint，再 append。若 inbox 已追加但 candidate
狀態更新前中斷，retry
必須以 fingerprint 發現既有 entry、補寫 candidate 的 `promoted` 狀態而不重複追加。
candidate 狀態以同目錄 temp + replace 原子更新；既有 inbox bytes 除尾端 append 外不得
重寫。process crash 會由 OS 釋放 lock，不留下需猜測是否 stale 的永久鎖。

涉及以下情況一律 `needs-decision`，不由自我迭代自行決定：

- 擴張任務或工具權限。
- 新增外部寫入、網路、憑證、裝置或破壞性操作。
- 改變公開兼容契約或大幅增加所有 subject 的固定成本。
- 兩個可泛化原則互相衝突，且沒有客觀 gate 可以裁決。

## 10. Public promotion 契約

不新增公開帳本。`promote` 只把下列 projection 追加到
`docs/harness/retro-inbox.md`：

```markdown
## new — <date> — <generalized title>

- **status**: `new`
- **source**: `subject-learning`
- **fingerprint**: `<stable digest>`
- **failure-mode**: <generalized failure>
- **current-gap**: <kit gap>
- **mechanism**: <portable mechanism>
- **target-surfaces**: <public kit surfaces>
- **applies-when**: <preconditions>
- **not-applicable-when**: <counterexample/cost boundary>
- **evidence-level**: `executable` | `closed-loop`
```

公開 projection 不含 subject 名、來源路徑、SHA、remote、原始摘錄或 reviewer 身分。
如需追查，只能在本機以 fingerprint 對應 private candidate。

## 11. Skill 設計

新增 `agent-kit/skills/skills/harness-learn/SKILL.md`，並由 `skill-creator` 建立與
評測。skill 應在以下情境觸發：

- compare/import 後詢問「別的工程有什麼值得學」。
- 要本倉從 subject 優點自我迭代、吸收、蒸餾或回流。
- 發現 subject 有更強 gate／hook／閉環，想判斷是否應成為通用能力。

skill 輸出不是 patch，而是以下三種之一：

- `eligible candidate`：附 evidence pointer、泛化內容與覆核結論。
- `hypothesis`：列明還缺哪一級證據。
- `rejected / needs-decision`：列明不可泛化、重複、洩密或取捨衝突原因。

`agent-kit/manifest.json` 與 skills README 同步註冊。skill 不複製 `harness-operate`
的 TDD 施工流程，只在晉升後明確 handoff 給它。

## 12. Skill eval 與反過擬合

依 `skill-creator` 建立 `evals/evals.json`，至少覆蓋：

1. subject 有可執行、且本倉缺少的早期 gate：應形成 eligible candidate。
2. subject 只是文件較多或命名不同：應判為 difference，不得晉升。
3. 機關綁定單一產品／host：應 rejected 或要求重新泛化。
4. 輸入要求把來源原文與路徑寫進公開文件：應拒絕洩漏。
5. 同一機關由第二個 subject 再次出現：應 dedupe。
6. 只有 prose、沒有可執行證據：應保留 hypothesis。
7. 候選會擴張權限或外部副作用：應 `needs-decision`。
8. 一般業務功能開發或單純 compare/score：不應誤觸發本 skill。

with-skill 與 baseline 同拍執行；使用客觀 assertions 評測是否區分 difference / advantage、
是否保持 private/public 邊界、是否錯誤直接改碼。生成 static eval viewer 供人工抽查，
並做 held-out trigger set，避免 description 只記住測試關鍵字。

`agent-kit/skills/` 不在父倉通用 public-tree 脫敏掃描的覆蓋面內，因此 eval 與 skill
必須有自己的安全 assertion；只提交通用 prompts、assertions 與必要 benchmark，原始
run transcript 不得進公開樹。

## 13. TDD 實作順序

每個 capability 都先看見正確 RED，再寫最小 GREEN：

| 拍 | RED | 最小 GREEN |
|---|---|---|
| 1 | non-ready、缺 snapshot 或 snapshot SHA 不符仍可 inspect/record | readiness + exact pinned snapshot fail-closed |
| 2 | evidence symlink 被解引用到 snapshot 外 | `lstat` + no-follow traversal |
| 3 | schema 缺 gap/適用條件/反例、evidence 越界仍被接受 | `subject_learning.py` validator |
| 4 | public projection 洩漏來源欄位 | allowlist renderer + privacy rejection |
| 5 | 同一 generalized mechanism 可重複追加 | stable fingerprint + locked inbox idempotency |
| 6 | append 後狀態更新失敗導致 retry 重複 | fingerprint-based recovery |
| 7 | retro legend 被 weekly report 算成 new entry | structural retro parser |
| 8 | promote 可繞過 evidence/review 狀態 | 狀態轉移與六閘 |
| 9 | CLI 與 library 語義分裂 | thin CLI contract tests |
| 10 | skill 把候選直接變 patch 或混同差異/優點 | skill eval + 修訂 |
| 11 | 新能力未進公開可信集 | `test-harness.sh` 顯式註冊 fixture tests |

公開測試只用 `testdata/` fixture；不得依賴真實 subject、private manifest、snapshot 或
comparison。實作若改動 `tools/**` 或 `agent-kit/**`，最終必跑
`bash tools/harness/test-harness.sh`。

## 14. 預計改動面

| 類型 | 路徑 |
|---|---|
| 深模組 | `tools/lib/subject_learning.py`、`tools/lib/retro.py` |
| CLI | `tools/learn/learn_subject.py` |
| 單元／契約測試 | `tools/harness/test_subject_learning.py`、`tools/harness/test_weekly_report.py` |
| 可信集 | `tools/harness/test-harness.sh`、必要的 `checks.py` ratchet |
| skill | `agent-kit/skills/skills/harness-learn/` |
| skill 註冊 | `agent-kit/manifest.json`、`agent-kit/skills/README.md`、根 `AGENTS.md` |
| install ratchet | `tools/harness/test_agent_kit_install.py` 的 local skill 契約 |
| 長期 SSOT | `docs/harness/design.md` |
| 既有消費端 | `agent-kit/skills/skills/harness-operate/SKILL.md` |

若實作發現可用更小表面達成同一契約，可以在 plan 中縮小路徑數；不得省略六閘、
private/public 分界、無 direct apply、skill eval 或全量可信集。

## 15. 驗收標準

1. 對非 harness-ready subject 的任何學習動作都 fail closed，且不寫候選／inbox。
2. 只有 executable 或 closed-loop evidence 能進入 eligible。
3. 「不同但不更好」、subject-specific、證據不足與權限擴張案例不會被誤晉升。
4. private candidate 保留可追查 evidence；public entry 經 allowlist projection 後不含
   subject identity、pin、remote、絕對路徑或 raw excerpt。
5. 同一 generalized fingerprint 重跑 promote 不會重複寫入。
6. 學習流程沒有直接修改本倉或 subject 的介面。
7. `harness-operate` 能消費 `source: subject-learning` 條目並以既有狀態收帳。
8. 新 skill 經 with-skill/baseline eval、held-out trigger eval 與 static viewer 檢查。
9. learning 只接受 exact pinned snapshot，且任何 snapshot symlink 都不會被解引用。
10. weekly report 只計算結構化 `status: new` entry，不計 legend 或 converted/rejected。
11. 新 Python tests 已顯式註冊；公開 fixture 測試與 `bash tools/harness/test-harness.sh` 全綠。
12. 正式 `plan-review` 無未解 blocker，實作後 `code-review` 收斂為 `passed`。

## 16. Submodule 交付邊界

`agent-kit/skills` 是獨立 submodule。實作時先在 skill submodule 完成測試與 commit，
再更新父倉 manifest、測試與 gitlink。若未獲 push 授權，保持 local-only 並在交付時
明確報告；不得把父倉 gitlink 的本機可見誤稱為其他 clone 已可取得。

## 17. Review 記錄

待正式 `plan-review` 後寫入同目錄 `plan-review.md`，並把本文件狀態更新為
`reviewed`。任何 verified blocker 必須先修訂本 spec，再進 implementation plan。
