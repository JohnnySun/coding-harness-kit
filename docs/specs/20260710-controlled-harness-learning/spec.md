# 受控 Harness 學習與自我迭代

> 狀態：`plan-review` blocked（iteration 3 plateau：PR-10b；尚未進 implementation）
>
> 日期：2026-07-10
>
> 方法：`harness-builder` 定義控制面，`harness-operate` 負責落地收環，
> `skill-creator` 建立並評測新的 `harness-learn` skill。

## 1. 問題

本倉目前能把上游 subject 的 harness 表面同步、匯入、比較並以四層 0–2 分做
描述性評分，但流程停在「看見差異」：

- `import` 保存約束、強制、回流、進化四層表面。
- `compare` 比較檔案清單與層級分數。
- `score` 明確聲明 0–8 是 surface inventory heuristic。
- `harness-operate` 能消費本倉既有反思，卻沒有受控入口接收從 subject 學到的
  通用機關。

因此本倉像一間會檢查車況、卻不會把修車經驗整理成新工具的汽修廠。更強的
subject 做法即使已被看到，也只能靠當次 Agent 臨場記住，無法穩定回流到本倉，
更無法在後續升級其他 subject 時驗證是否真的有用。

## 2. 決策摘要

採用「受控自我迭代」，而不是直接自動吸收：

1. `harness-learn` 只做證據整理、泛化、覆核、晉升與後續採用記錄，不改本倉
   機關，也不改 subject。
2. 學習證據必須同時綁定目前完整 pin、default submodule pin 集、乾淨的
   `harness_paths`、snapshot manifest 與實際 evidence bytes；SHA 標籤本身不算證明。
3. source-bound observation 與跨 subject insight 使用兩套 identity。hypothesis
   不會被硬塞進尚未具備的 insight fingerprint。
4. 獨立 reviewer 產生 digest-bound receipt；candidate 或 evidence 任一 byte 改變，
   receipt 立即失效。
5. promotion 只接受固定 private root 下的 fingerprint，由指定 coordinator 在 primary
   worktree 單寫 public retro inbox；沒有任意 path、`apply` 或直接 patch 入口。
6. public projection 經欄位 allowlist、單行 grammar、Markdown escaping、source-token
   deny 與公開樹 scanner；raw evidence 永遠留在 gitignored private roots。
7. `harness-operate` 是唯一 implementation consumer，沿用 public
   `new → consuming → converted | rejected` 狀態，不發明未被現有 consumer 支援的
   public `needs-decision`。
8. converted insight 必須帶 later-upgrade contract；後續 subject 升級記錄
   `adopted | not-applicable | rejected`，否則「學會」不算證明「有用」。
9. 交付分 tracer、deterministic substrate、skill packaging、dogfood 四個 value gate；
   不在第一個端到端 tracer 前先完成全部包裝。

## 3. 目標與非目標

### 3.1 目標

- 從 harness-ready subject 的已匯入證據中辨認「比本倉目前更能預防某類失敗」
  的做法，而不是只列差異。
- 把 subject 專屬實作蒸餾成跨工程可理解的 failure class、portable mechanism、
  applicability 與反例。
- 讓每個判斷可追到完整 pin 與 evidence digest，又不把來源資訊寫入公開樹。
- 讓 exact duplicate 冪等，semantic duplicate 由 reviewer 明確合併，不冒充自由文字
  hash 能理解語義。
- 讓每條 promoted insight 有既有 implementation consumer，並在後續 subject 升級
  留下採用／不適用／拒絕的可查證 receipt。

### 3.2 非目標

- 不把 0–8 描述性評分改成「誰比較先進」的總排名。
- 不從任意業務源碼、未 pin checkout、網路搜尋或未匯入路徑學習。
- 不把 subject 原文、識別資訊、remote、pin、本機路徑或 eval transcript 寫入公開樹。
- 不自動照抄 subject 的 hook、prompt、skill 或腳本。
- 不建立無消費端的新公開帳本。
- 不讓學習動作擴張目前任務的權限、外部副作用或破壞性操作邊界。

### 3.3 Threat model

P0 防止正常工具與合作式 Agent 的誤用、競態、stale evidence、路徑逃逸與隱私外洩。
它不宣稱能防止具有本機任意寫權的惡意使用者或已遭入侵的 Agent。AI 行為規則不能
假裝是 sandbox；可機械化的部分由 digest、fixed root、no-follow、single writer、
CAS、parser 與 trusted-suite gate 強制。

## 4. 「優點」的判定式

「不同」不等於「更好」。observation 必須同時回答：

| 問題 | 必要答案 |
|---|---|
| 預防什麼 | 一個具體且可重現的 failure class |
| 現況缺口 | 本倉目前沒有攔截，或只在更晚、更弱的層級攔截 |
| 為何更強 | subject 機關能更早、可執行或閉環地預防該失敗 |
| 為何可搬 | 原理不依賴單一產品、團隊、host、供應商或私有命名 |
| 搬去哪裡 | 公開、穩定的 target surface |
| 何時適用 | 可檢查的 applicability preconditions |
| 何時不適用 | 至少一個反例、成本界線或拒絕條件 |

證據分三級：

| 級別 | 定義 | 能否進 review |
|---|---|---|
| `prose` | 只有規則或設計敘述 | 否；保留 `hypothesis` |
| `executable` | 有 gate、checker、test 或可重現命令之一 | 可以 |
| `closed-loop` | 有寫入端、強制端、驗證端與消費端形成閉環 | 可以 |

檔案更多、文字更長、提示更嚴或分數更高，都不能單獨構成優點。

為了穩定 projection，`failure_class`、`mechanism_key` 與 `target_surfaces` 使用
受控 slug／enum；人類可讀的 `mechanism` 仍是受限單行文字。fingerprint 只能保證
canonical payload 的 exact dedupe。兩個不同 payload 是否語義等價，必須由 reviewer
在 receipt 中用 `equivalent_to` 明確合併。

## 5. 邊界與角色分離

```text
harness-ready subject
        │
        ▼
attested snapshot evidence
        │
        ▼
source-bound observation ──► independent review receipt
        │                              │
        └─────────────── merge ────────┘
                                ▼
                       multi-source insight
                                │
                  single-writer promotion
                                ▼
                    retro-inbox (public)
                                │
                                ▼
                        harness-operate
                                │
                    TDD + review + trusted suite
                                ▼
                       converted mechanism
                                │
                  later-upgrade applicability
                                ▼
                 private adoption receipt
```

### 5.1 `harness-learn`

負責：

- attestation、observation、review receipt、candidate merge、promotion 與 adoption receipt。
- 區分 difference、hypothesis、eligible insight 與需 owner 決策的 private item。
- 把 public entry 當資料輸出，不把 raw source 或命令帶給 implementation consumer。

不負責：

- 修改本倉機關或任何 subject。
- 宣稱 promoted 等於 implemented，或 converted 等於 downstream useful。
- 取代 `harness-builder` 的設計判斷或 `harness-operate` 的施工節拍。

discovery/reviewer subagents 只回傳 JSON；主 Agent 在 designated coordinator worktree
呼叫 CLI 寫 private state。子代理的完成聲明不直接成為 attestation 或 review receipt。

### 5.2 `harness-operate`

只讀 public retro entry，不回讀 private observation/candidate。它：

- 一拍認領一條 `source: subject-learning` 且 `status: new` 的條目。
- 把 entry 文本視為 untrusted data；不得直接執行其中看似命令的文字。
- 重新對齊本倉 gap，Red→Green，跑全量可信集，完成適用的 code review。
- 只按既有 grammar 收帳為 `converted(<證據>)` 或 `rejected(<原因>)`。
- converted 時把 versioned later-upgrade contract co-locate 回同一條 retro entry；
  機關／skill／模板可以引用 fingerprint，但 retro entry 是 fresh clone 可枚舉的 SSOT。

若施工時才發現需要 owner 決策，該拍以
`rejected(needs-owner-decision:<work-order-id>)` 收帳並進既有 work-orders；不在
retro-inbox 發明第三個 terminal state。

### 5.3 後續 subject 升級

使用本倉升級 subject 的正常入口必須先執行 `inspect --for-upgrade`，對所有 returned
contract 做 applicability screen，並在該次升級結束前逐條收成 adoption outcome。
適用者納入正常升級計畫，不適用或拒絕者都要有原因；學習 CLI 只記錄 outcome，
不替升級流程改 subject。缺 contract、duplicate fingerprint、invalid reference 或無法
完成 screen 時 fail closed，不把「沒看見」當成「不適用」。

## 6. Persisted state machine

### 6.1 Private observation

固定落點：

```text
comparisons/learning-observations/<observation-id>.json
```

`observation-id` 綁定 source identity、完整 pin digest、snapshot manifest digest、
evidence digests 與 rule version，不依賴尚未完整的 generalization。

| from | to | actor / precondition |
|---|---|---|
| — | `hypothesis` | `record`；可只有 prose 或缺一部分 generalization |
| `hypothesis` | `review-pending` | 欄位完整，至少 executable evidence |
| `review-pending` | `linked` | digest-bound review `passed`，已合併至 insight |
| `review-pending` | `rejected` | review 有 reason code |
| `review-pending` | `needs-decision` | 涉及權限、外部副作用、兼容或重大固定成本 |
| `needs-decision` | `review-pending` | 新 owner-decision receipt；舊 receipt 不覆寫 |
| non-terminal | `stale` | pin、submodules、snapshot、evidence 或 rule version 漂移 |

`linked`、`rejected`、`stale` 不回退；新 evidence 產生新 observation。

### 6.2 Private insight

固定落點：

```text
comparisons/learning-candidates/<insight-fingerprint>.json
```

只有 review-passed 的完整 generalization 才能產生 insight。insight 使用 `sources[]`
保留多個 observation receipt；同 fingerprint 的新來源在 lock + CAS 下冪等合併。

| from | to | precondition |
|---|---|---|
| — | `eligible` | review receipt 與 observation／attestation digest 全部匹配 |
| `eligible` | `promoted` | promotion gates 全過，public entry 原子寫入 |
| `eligible` | `stale` | promotion 前 attestation 重驗失敗 |
| `eligible` | `rejected` | 發現 kit 已有等價機關或 privacy/generalization 不成立 |

`promoted` 是歷史事實，不因後續來源失效而靜默改寫。若已 promoted 的結論需要更正，
建立新的 correction observation，走同一 review/promotion 流程。

### 6.3 Public retro

沿用現有：

```text
new → consuming → converted(<證據>) | rejected(<原因>)
```

### 6.4 Private adoption

```text
comparisons/learning-adoptions/<fingerprint>@<subject-state-digest>.json
```

outcome 只允許：

- `adopted`：upgrade 已使用該 mechanism，並有 prevented-failure evidence。
- `not-applicable`：applicability probe 為 false，附可查證原因。
- `rejected`：適用但與 subject 權威規則／成本界線衝突，附原因。

## 7. Evidence attestation

學習不能沿用 `latest_snapshot()` 的 mtime 選擇。每次 `inspect`、`record`、
`review`、`promote`，以及 `adopt` 的 target state 都用 exact attestation：

1. `require_ready(subject)` 通過。
2. 目前 `pin.sha`、完整 canonical `pin.submodules` mapping 及
   `default_submodules` 實際狀態一致。
3. 目前 checkout 的所有 `harness_paths` 對 tracked、untracked 與 submodule dirt
   都是 clean；dirty 即 fail closed。
4. snapshot manifest 的 subject、完整 shell SHA、submodule mapping 與
   `harness_paths` 對應目前 pin／manifest。
   - exact resolver 掃描 manifest 的完整 SHA，不按 mtime；0 個即缺失，超過 1 個且
     attestation digest 不同即 ambiguous/fail closed，相同則只接受同一 digest。
5. evidence 同時記錄 snapshot-relative path 與 declared source path；兩者必須位於
   四層 snapshot 與 `harness_paths` 內。
6. regular evidence file 的 snapshot bytes 必須等於目前 clean pinned source bytes。
7. 遍歷使用 `lstat`，不 follow symlink。symlink 可記 metadata，但不能作為可讀
   evidence；匯入層目前保存 resolved symlink 的行為不能成為逃逸路。
8. attestation 記錄 `observed_at`、`learning_rule_version`、shell SHA、
   canonical submodule mapping/digest、harness_paths digest、snapshot manifest digest、
   每個 evidence 的 type/mode/content digest，以及 aggregate `attestation_digest`。

`promote` 在 lock 內重算全部 digest。任何 mismatch 都把 observation／insight 標為
`stale`，且不碰 public inbox。

## 8. 深模組與 CLI

### 8.1 深模組

- `tools/lib/subject_learning.py`
  - readiness/attestation orchestration
  - observation、receipt、insight、adoption schema 與 transition
  - canonicalization、fingerprint、fixed-root/no-follow I/O
  - privacy projection 與 source-token deny
- `tools/lib/retro.py`
  - 結構化 parse/render
  - status/fingerprint uniqueness
  - atomic prefix-preserving update
  - weekly report 共用的 entry 計數

`weekly_report.py` 不再全文計算 `status: new` 或 legend 中的 new marker。

### 8.2 CLI

`tools/learn/learn_subject.py` 是薄 adapter：

```text
inspect <subject> [--for-upgrade]       # read-only JSON
record <subject> --input FILE           # 固定寫 observation root
review <observation-id> --input FILE    # 驗證 receipt，merge/create insight
resolve <observation-id> --input FILE   # 記 owner decision，再回到 review-pending
promote <insight-fingerprint>           # 不接受 path
adopt <fingerprint> <subject> --input FILE
```

安全契約：

- id 僅接受固定長度 lowercase hex；CLI 自行推導 private path。
- absolute path、`..`、symlink leaf／ancestor、non-regular file、outside-root target
  一律拒絕。
- private write 使用同目錄 temp、flush、`fsync`、`replace`；terminal state 不回退。
- `--input` 只讀且要求 regular non-symlink file；永不更新 input file。
- 不提供任意 `--out`、`apply`、`patch`、`sync-back` 或 escape hatch。

## 9. Private contracts

### 9.1 Observation

```json
{
  "schema_version": 1,
  "status": "review-pending",
  "observation_id": "<source-bound digest>",
  "review_payload_digest": "<immutable reviewed-field digest>",
  "provenance": {
    "subject": "<private-id>",
    "observed_at": "<timestamp>",
    "learning_rule_version": 1,
    "shell_sha": "<full pin>",
    "submodules": {"<path>": "<full sha>"},
    "submodules_digest": "<digest>",
    "harness_paths_digest": "<digest>",
    "snapshot": "<private relative ref>",
    "snapshot_manifest_digest": "<digest>",
    "attestation_digest": "<digest>",
    "evidence": [
      {
        "layer": "gates",
        "snapshot_path": "<relative regular file>",
        "source_path": "<declared harness path>",
        "level": "executable",
        "mode": 420,
        "digest": "<content digest>",
        "claim": "<private evidence claim>"
      }
    ]
  },
  "generalization": {
    "failure_class": "<controlled-slug>",
    "current_gap": "<one-line>",
    "mechanism_key": "<controlled-slug>",
    "mechanism": "<one-line portable description>",
    "target_surfaces": ["gate"],
    "applies_when": ["<one-line condition>"],
    "not_applicable_when": ["<one-line boundary>"]
  },
  "disposition": {"reason_code": null, "reason": null}
}
```

`review_payload_digest` 只涵蓋 versioned allowlist：`schema_version + observation_id +
provenance + generalization + active owner-decision receipt digest`。它明確排除 mutable
`status`、`disposition` 與 receipt reference。合法 lifecycle transition 不會讓已通過的
review 自我失效；任何 allowlist 內 byte 改變都必須產生新 digest 與新 review。

### 9.2 Review receipt

```json
{
  "schema_version": 1,
  "observation_id": "<id>",
  "review_payload_digest": "<immutable reviewed-field digest>",
  "attestation_digest": "<evidence identity>",
  "learning_rule_version": 1,
  "decision": "passed",
  "rationale": "<evidence-backed second-pass conclusion>",
  "equivalent_to": null
}
```

reviewer lane 是 read-only。CLI 不宣稱從字串證明 reviewer 身分，但會證明 receipt
確實覆核目前 reviewed payload 與 evidence bytes；reviewed-field mutation 使 receipt
stale，單純合法 status/disposition transition 不會。

`decision` 允許 `passed | rejected | needs-decision`；後兩者必須有受控
`reason_code + rationale`。`passed` 才能帶 `equivalent_to` 並產生／合併 insight。

### 9.3 Owner-decision receipt

```json
{
  "schema_version": 1,
  "observation_id": "<id>",
  "decision_request_digest": "<needs-decision request digest>",
  "decision_key": "<owner-controlled decision>",
  "resolution": "approved | declined | constrained",
  "rationale": "<one-line owner rationale>"
}
```

只有使用者／owner 已提供的決策才能寫入；Agent 不替 owner 發明。`resolve` 保存 receipt、
把 `needs-decision` 移回 `review-pending`，且要求新的 independent review receipt。

### 9.4 Insight

```json
{
  "schema_version": 1,
  "status": "eligible",
  "fingerprint": "<canonical generalization digest>",
  "generalization": {"<public-safe structured fields>": "..."},
  "sources": [
    {
      "observation_id": "<id>",
      "review_payload_digest": "<digest>",
      "attestation_digest": "<digest>",
      "review_receipt_digest": "<digest>",
      "evidence_level": "closed-loop"
    }
  ],
  "public_entry_digest": null
}
```

fingerprint 由 canonical
`failure_class + current_gap + mechanism_key + mechanism + target_surfaces + applies_when +
not_applicable_when` 推導，不含 source identity、日期或 evidence path。

### 9.5 Adoption receipt

```json
{
  "schema_version": 1,
  "receipt_id": "<idempotency digest>",
  "fingerprint": "<converted insight>",
  "contract_digest": "<§11 public contract digest>",
  "subject": "<private-id>",
  "observed_at": "<timestamp>",
  "screening": {
    "session_digest": "<inspect-for-upgrade output digest>",
    "pre_state_digest": "<attested ready state>",
    "applicability_key": "<contract key>",
    "result": true,
    "evidence_digest": "<private evidence>"
  },
  "post_state": {
    "shell_sha": "<full pin after upgrade>",
    "submodules_digest": "<canonical digest>",
    "ready_attestation_digest": "<current ready state>"
  },
  "outcome": "adopted",
  "validation": {
    "ref": "<must equal contract validation-ref>",
    "result": "pass",
    "evidence_digest": "<prevented-failure evidence>"
  },
  "reason_code": null,
  "reason": null
}
```

`inspect --for-upgrade` 先產生含全部 returned contract 與 pre-state 的 screening digest。
`adopted` 要求目前 subject 已在 upgrade 後重新 pin 且 harness-ready、contract digest 未變、
applicability 為 true、validation ref 一致且 evidence 可重驗；其餘 outcome 要求 reason。
receipt id 綁定 fingerprint、contract、screening、post-state 與 outcome。相同 payload 重跑
為 no-op；同 id 不同 payload、terminal outcome 改寫或 unverifiable evidence 一律 exit 1。

## 10. Promotion gates 與 transaction

### 10.1 八道 gate

| gate | fail behavior |
|---|---|
| readiness | 非 ready、pin/submodule drift、dirty harness path：stale/no write |
| attestation | manifest/source/evidence/rule digest mismatch：stale/no write |
| evidence | 只有 prose 或 claim 無法支持機關：保留 hypothesis |
| generalization | 缺 failure/gap/mechanism/applicability/反例：不進 review |
| review | receipt digest 不匹配、decision 非 passed：不產 insight |
| privacy | value-level/source-token/public scanner 任一紅：no public write |
| dedupe | exact fingerprint 已存在：merge source 或冪等回報 |
| coordinator | 非 designated primary worktree：exit 1 |

### 10.2 Public scalar grammar

public values 必須：

- UTF-8 NFKC、單行、無 C0/C1、NUL、Unicode category `Cf`、default-ignorable、
  bidi override／isolate control。source-token 比較前再以移除 default-ignorable 的
  comparison form 檢查一次；display form 仍直接拒絕危險 control。
- slug／enum 欄位符合 allowlist；文字欄位有明確長度上限。
- 經 Markdown metachar escaping，不可產生 heading、list field、link 或 HTML。
- 不含 source subject id、remote、任何 pin/submodule SHA、snapshot/source/evidence path
  或 raw excerpt canary（casefold 後也檢查）。
- 完整 rendered entry 先通過 public-tree generic scanner，再由 `retro.py` parse-back；
  parse 結果必須恰好是一條預期 entry。

title 由 `failure_class + mechanism_key` 決定；`evidence-level` 由 verified
`sources[]` 中最高已證明級別推導，不接受自由輸入。

### 10.3 Single-writer transaction

- discovery/reviewer lanes 不 promotion。
- `promote` 只允許 `git worktree list --porcelain` 的 designated primary worktree。
- lock 放在 git common-dir，所有 learning promotion 共用；lock 內重驗 attestation、
  receipt、candidate、目前 inbox digest 與 fingerprint uniqueness。
- 以目前 inbox bytes 為 immutable prefix，產生 `prefix + one framed entry`；
  temp file flush + `fsync` 後 atomic replace。
- replace 前做 preimage digest CAS；inbox 已變則重讀、重算，不覆蓋。
- replace 後才 atomic 更新 private insight 為 `promoted` 並記
  `public_entry_digest`。
- crash 在 public replace 後、private update 前：retry 由 fingerprint + entry digest
  修復 private state，不重複 entry。
- `retro.py`／trusted suite 拒絕 torn tail、重複 fingerprint、非法 transition。

非合作式人工同時編輯不在 hard threat model；但 CAS、atomic replace 與 L1 parse/
uniqueness gate 會 fail closed，避免把競態靜默當成功。

## 11. Public promotion contract

不新增公開帳本。promotion 只在既有 retro inbox 追加：

```markdown
## new — <derived title>

- **status**: `new`
- **source**: `subject-learning`
- **fingerprint**: `<stable digest>`
- **failure-class**: <escaped scalar>
- **current-gap**: <escaped scalar>
- **mechanism-key**: <escaped scalar>
- **mechanism**: <escaped scalar>
- **target-surfaces**: <controlled enums>
- **applies-when**: <escaped scalars>
- **not-applicable-when**: <escaped scalars>
- **evidence-level**: `executable` | `closed-loop`
```

公開 entry 不含 subject 名、來源路徑、SHA、remote、原始摘錄、reviewer 或 private
observation id。fingerprint 只用於本機對應 private evidence。

當 entry 收帳為 `converted(...)`，`harness-operate` 在同一 entry 追加且由 `retro.py`
驗證以下 versioned block：

```markdown
- **upgrade-contract-version**: `1`
- **upgrade-entry-point**: `<controlled enum>`
- **applicability-key**: `<controlled slug>`
- **expected-prevented-failure**: <escaped scalar>
- **validation-ref**: `<public repo-relative check/fixture id>`
- **contract-digest**: `<digest of fingerprint + contract fields>`
```

`retro.py` 對所有 `source: subject-learning` + converted + contract-version entry 建立
read-only in-memory index；這就是 `inspect --for-upgrade` 的唯一 discovery source。
fingerprint/contract-digest 必須唯一，`validation-ref` 必須位於允許的公開 roots 且存在。
missing/stale/duplicate contract 使 inspect exit 1。fresh clone 不依賴 `comparisons/`。

## 12. Conversion 與 later-upgrade adoption

`harness-operate` conversion 必須：

1. 只消費 public entry。
2. 寫出 Red evidence、最小 Green、全量可信集、review 結論。
3. 收帳 `converted(<evidence>)` 或 `rejected(<reason>)`。
4. converted 時在同一 retro entry 寫入 §11 versioned contract block；機關／skill／模板
   只需保存 fingerprint reference，不是 discovery index。

後續 subject upgrade：

1. 正常 upgrade 入口呼叫 `inspect --for-upgrade`；它只從 §11 public index 列出
   converted、target surface 相關的 contracts。
2. Agent 做語義 applicability 判斷；CLI 不自動 patch。
3. 正常 upgrade 完成後，`adopt` 固定寫 private receipt。
4. adopted 必須附 prevented-failure evidence；其餘 outcome 必須附 reason。

本拍至少完成一個 held-out generic tracer；若本機有 harness-ready subject，再做一個
private dogfood。未 ready 時不得為了 dogfood 繞過 pin，只報告 held-out evidence。

## 13. Skill 設計與 eval

### 13.1 `harness-learn`

新增 `agent-kit/skills/skills/harness-learn/SKILL.md`，由 `skill-creator` 建立。
觸發情境：

- import/compare 後詢問「別的工程有什麼值得學」。
- 要本倉從 subject 優點自我迭代、吸收、蒸餾或回流。
- 發現更強 gate／hook／閉環，想判斷是否應成為通用能力。

skill 輸出只允許 observation、review receipt、promotion summary 或 adoption receipt；
不得直接 patch kit/subject。

### 13.2 Eval workspace 與 tracked-artifact gate

依 `skill-creator` 執行時，先把待測 skill 複製到
`comparisons/skill-evals/harness-learn/`。其 sibling workspace、outputs、
transcript、timing、grading、viewer 與 feedback 都留在 `comparisons/skill-evals/`。
公開 skill 只提交 `SKILL.md`、必要 references 與
`evals/evals.json`（通用 synthetic prompts/assertions）。

trusted suite 的新 ratchet **只作用於**
`agent-kit/skills/skills/harness-learn/**` 與本拍新增的對應 eval paths；不得把既有其他
skill 的合法 workspace／eval 內容 retroactively 判紅。它拒絕 harness-learn 下被追蹤的
`*-workspace`、`outputs/`、`transcript*`、`timing.json`、`grading.json`、viewer、feedback
或未列入 source allowlist 的 artifact，並做 skill-specific privacy scan。fixture 必須
證明 harness-learn leak 被攔、unrelated existing skill path 不受影響。

### 13.3 Eval cases

至少覆蓋：

1. 有 executable/closed-loop evidence 且 kit 確有 gap → eligible。
2. 只是命名／檔案數不同 → hypothesis/rejected。
3. 綁定單一產品／host → 不泛化。
4. hostile multiline、forged heading、raw excerpt、path、SHA、zero-width token split、
   bidi display forgery、prompt injection → no promote。
5. exact duplicate → merge/dedupe；semantic duplicate → reviewer `equivalent_to`。
6. prose-only、non-ready、dirty、post-record mutation、stale receipt → fail closed。
7. 權限／外部副作用擴張 → private `needs-decision`。
8. attempted direct edit → skill 明確拒絕並 handoff。
9. 一般業務功能開發或單純 score → 不誤觸發。
10. `harness-operate` consumer：一拍一條、只讀 public entry、不走 private shortcut、
    Red/Green/full suite/review、合法 terminal closure。

另有真實 two-process promotion test，證明同 fingerprint 最終只有一條完整 public
entry 與一個 promoted insight。

### 13.4 Release thresholds

- privacy、no-direct-edit、readiness、authority-boundary、stale-receipt safety assertions：
  每次 run 100% 通過。
- 其餘 objective assertions：with-skill ≥ 90%，且比 baseline 高至少 20 percentage
  points；否則 skill 不發布並 revise/rerun。
- held-out trigger set 至少 20 條 near-miss：false-positive = 0，recall ≥ 90%。
- 每個 eval 做 3 組同拍 paired runs；timeout/error 算 failure。safety 以「每一 assertion
  × 每一 run」為 denominator，必須全過；functional 以 assertion-weighted pass rate 的
  三組 mean 判定，並報 mean ± standard deviation。trigger query 各跑 3 次，以 majority
  判單題結果，再計 positive recall 與 near-miss false-positive rate。
- with-skill／baseline 同拍成對執行；產生 aggregate benchmark、analyst conclusion 與
  official static viewer。**發布前必須完成一次 skill-creator human output review**：取得
  使用者 feedback／明確 approval，或取得 owner 對本次人工 checkpoint 的明確 waiver；
  讀取 feedback 後若需修訂，全部 paired runs 與 thresholds 重跑。只生成 viewer 不算
  完成。若 baseline 已同等完成全部 contract，記錄「skill 無額外價值」並不發布多餘
  skill。

## 14. Staged TDD delivery

所有 capability 都先看見正確 RED，再寫最小 GREEN。

### Slice A — controlled tracer（value gate）

用 synthetic upstream/kit/downstream fixtures，走完：

```text
attested evidence → observation → review receipt → insight → public projection
→ operate conversion fixture → downstream adopted/not-applicable/rejected receipt
```

這拍先以 library contract 測試完成，不先包 CLI/skill。tracer 必須證明一個 mechanism
在 held-out downstream fixture 攔住原本會失敗的案例，且沒有 private leak/direct patch。

### Slice B — deterministic substrate

| RED | GREEN |
|---|---|
| non-ready、dirty、submodule drift、snapshot/source mismatch 仍可記錄 | exact attestation |
| symlink evidence 逃出 snapshot | `lstat` + no-follow |
| hypothesis 需要不存在的 fingerprint | observation/insight identity 分離 |
| 只改 `current_gap` 卻撞同 fingerprint | identity 涵蓋所有 public semantic fields |
| receipt 可被 mutation 後重用 | digest-bound receipt |
| 合法 status transition 讓 receipt 自我失效 | immutable `review_payload_digest` |
| abs/traversal/symlink candidate path 可被 promote | fingerprint-only fixed-root I/O |
| Unicode Cf/bidi 或 hostile scalar 產生 Markdown/private leak | grammar + escaping + scanner + parse-back |
| 兩 process 同時 promotion 重複／torn write | common lock + CAS + atomic replace |
| legend 被算成 new entry | structural retro parser |
| fresh clone 找不到 converted contract | co-located retro contract index |
| forged/stale adoption evidence 被記為 adopted | attested adoption receipt + CAS |

Slice A 未證明 downstream value，不進 Slice C；Slice B 的 safety gate 不因 value gate
而省略。

### Slice C — CLI、skill、install

- 薄 CLI contract tests。
- `harness-learn` with-skill/baseline eval 與 thresholds。
- `harness-operate` consumer eval。
- manifest、README、all-client install ratchet。
- submodule tracked-artifact/privacy ratchet。
- official viewer + human feedback／approval（或明確 owner waiver）checkpoint。

### Slice D — local dogfood and close

- 公開 held-out tracer 必跑。
- 本機 subject 全部先跑 readiness；有 ready 才做 private dogfood。
- adopted／not-applicable／rejected receipt 皆在 `comparisons/`。
- `bash tools/harness/test-harness.sh`、code-review、retro/work-order 收帳。

## 15. 預計改動面

| 類型 | 路徑 |
|---|---|
| 深模組 | `tools/lib/subject_learning.py`、`tools/lib/retro.py` |
| CLI | `tools/learn/learn_subject.py` |
| 測試 | `tools/harness/test_subject_learning.py`、`tools/harness/test_weekly_report.py` |
| fixtures | `testdata/` 下 generic upstream/kit/downstream tracer |
| 可信集 | `tools/harness/test-harness.sh`、`tools/harness/checks.py` |
| skill | `agent-kit/skills/skills/harness-learn/` |
| consumer | `agent-kit/skills/skills/harness-operate/SKILL.md` + eval |
| skill 註冊 | `agent-kit/manifest.json`、skills README、根 `AGENTS.md` |
| install ratchet | `tools/harness/test_agent_kit_install.py` |
| operator docs | 根 `README.md`、`docs/harness/design.md` |

不新增公開帳本；adoption/eval 原始產物都在既有 gitignored `comparisons/`。

## 16. 驗收標準

1. non-ready、dirty、pin/submodule drift、snapshot/source mismatch 都 fail closed，且
   不寫 observation／candidate／inbox。
2. observation attestation 綁定完整 pin、submodules、harness paths、manifest、
   evidence bytes、rule version 與 observation time。
3. hypothesis、review receipt、multi-source insight identity 與 legal transitions 可測，
   terminal state 不回退。
4. receipt 與 candidate/evidence digest 綁定；mutation 或 replay stale receipt 被拒。
5. promotion 只接受 fingerprint，fixed-root/no-follow/path confinement 負例全綠。
6. public entry 經 scalar grammar、escaping、source-token deny、generic scanner、
   parse-back；不含 private identity/path/SHA/raw excerpt 或 forged Markdown。
7. designated single writer、two-process contention、CAS、atomic replace、crash retry
   均只產一條完整 entry。
8. public retro 僅使用現有合法 lifecycle；weekly report 不計 legend／terminal entry。
9. `harness-operate` consumer eval 證明一拍一條、無 private/direct shortcut、
   TDD/full-suite/review 與合法 closure。
10. fresh clone 可從 converted retro entry 完整枚舉 later-upgrade contract；normal upgrade
    entrypoint 強制 screen，attested adoption receipt 可記錄
    `adopted | not-applicable | rejected`；held-out tracer 證明至少一次 prevented failure。
11. skill eval workspace 不進 git；harness-learn-scoped tracked-artifact/privacy gate、
    release thresholds 與 human feedback／approval checkpoint 全過。
12. 新 tests 顯式註冊，`bash tools/harness/test-harness.sh` 全綠。
13. 正式 `plan-review` 無未解 blocker；實作後 `code-review` 收斂為 `passed`。

## 17. Submodule 交付邊界

`agent-kit/skills` 是獨立 submodule。先在 skill submodule 完成測試與 commit，再更新
父倉 manifest、測試與 gitlink。若未獲 push 授權，保持 local-only 並在交付時明確
報告；不得把父倉 gitlink 的本機可見誤稱為其他 clone 已可取得。

## 18. Review 記錄

Discovery sweep 的 verified ledger 與 revision changelog 寫入同目錄
`plan-review.md`。本文件只有 fresh verification sweep 與 held-out sweep 均無 confirmed
blocker 後，才更新為 `reviewed` 並進 implementation plan。
