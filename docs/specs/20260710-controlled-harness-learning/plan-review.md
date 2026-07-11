# Plan review — 受控 Harness 學習與自我迭代

> Review type: plan/design
>
> Budget: 5 sweeps
>
> Active roles: A（architecture）、B（risk）、C（quality）、E（workflow value）、
> F（blind-spot reconstruction）
>
> UI reviewer D: not applicable（沒有 UI、journey 或 frontend data-shape 變更）

## Bounded surface

- Artifact: `docs/specs/20260710-controlled-harness-learning/spec.md` 全文。
- Requirement: 從 harness-ready subject 證據學習可泛化優點；不得直接 auto-patch、
  洩漏 private evidence 或擴張 authority；promoted insight 必須有 TDD/review consumer，
  並能在後續 subject upgrade 留下採用證據。
- In-scope context: 根規則、harness design、import/compare/score/readiness、retro/weekly
  report、trusted suite、install manifest、`harness-builder`、`harness-operate`、
  `skill-creator`。
- Out of scope: private subject 內容、UI、network publishing、implementation code review。

Attribution evidence:

- original surface: commit `9c143bd`，spec SHA-256
  `5f33eb174704aa488984bb3dc6d4838795e5fc1cca2b36690f26810a1200eeee`
- current surface after iteration-1 revision: SHA-256
  `f187a2278767156122da89f7c542659c0cdfa63fc831fd77763f973012adba40`
- latest revision diff: `git diff 9c143bd -- docs/specs/20260710-controlled-harness-learning/spec.md`

## Discovery sweep — verified issue ledger

只有 verifier 無法反駁的 critical/major 才進 ledger。Reviewer E 的「需要 WIP 上限」
被 verifier refute：目前 promotion 是顯式、逐 candidate、六閘後動作，沒有 arrival-rate
或實際 backlog 證據，故只保留為非阻塞觀察。

| key | source | verified blocker | iteration-1 revision |
|---|---|---|---|
| PR-01-evidence-attestation | A/B/F | pin label 未綁定 clean harness paths、完整 submodule pins、manifest/evidence bytes、rule version | 新增 exact attestation、digest、stale transition |
| PR-02-observation-insight-identity | A | hypothesis 與跨來源 insight 共用 fingerprint/singular source | 拆 observation ID 與 insight fingerprint；insight 用 `sources[]` |
| PR-03-single-writer-transaction | A/B | worktree-local lock、直接 append、torn tail recovery 不完整 | primary coordinator + common-dir lock + CAS + atomic replace |
| PR-04-path-confinement | B | `promote <path>` 可逃出 private root | 改為 fingerprint-only；fixed-root/no-follow |
| PR-05-public-value-privacy | B | free-text allowlist 仍可注入 Markdown/private token | scalar grammar、escaping、source-token deny、scanner、parse-back |
| PR-06-review-binding | B/F | review 字串未綁 candidate/evidence bytes | digest-bound receipt；mutation/stale replay fail closed |
| PR-07-lifecycle-consumer | B/C | private/public state 混在一起，public `needs-decision` 無 consumer | 完整 private transition；public 保留既有兩終態；新增 owner resolve receipt |
| PR-08-eval-artifact-boundary | B/C | skill-creator workspace 可能落在公開 submodule 且無 ratchet | workspace 固定在 `comparisons/`；tracked-artifact/privacy gate |
| PR-09-eval-release-threshold | B/C | 只有「跑過 eval」，沒有發布判定 | safety 100%、functional/baseline、held-out FP/recall thresholds |
| PR-10-downstream-adoption | E | converted mechanism 未證明後續 subject upgrade 有用 | later-upgrade contract + private adoption receipt + held-out tracer |
| PR-11-value-gated-scope | E | 在第一個 reuse tracer 前先完成全部包裝 | Slice A tracer gate，再進 substrate/skill/dogfood |
| PR-12-contention-consumer-proof | F | 無 two-process promotion 與 `harness-operate` consumer eval | 新增真實 contention test 與 consumer skill eval |

所有 12 個 blocker 已套用 revision，但在 fresh sweep 前仍標為 `open`；沒有
`needs_decision` 或 `missing_evidence` item。

## Revision changelog（iteration 1 → 2）

1. **[PR-01/PR-06]** 新增完整 evidence attestation 與 digest-bound review receipt。
2. **[PR-02/PR-07]** 把 source observation、multi-source insight、public retro、
   private adoption 拆成四個 persisted lifecycle；補 `resolve` 與 owner receipt。
3. **[PR-03/PR-04]** promotion 改為 fingerprint-only single writer，使用 common-dir
   lock、preimage CAS、atomic replace 與 retry repair。
4. **[PR-05]** public projection 改成受控 slug/enum + NFKC 單行 grammar、Markdown
   escape、source-token deny、public scanner 與 parse-back。
5. **[PR-08/PR-09]** eval workspace 移到 private `comparisons/`；補 tracked-artifact
   gate 與客觀 release thresholds。
6. **[PR-10/PR-11]** 增加 later-upgrade contract/adoption receipt，並以 held-out
   upstream→kit→downstream tracer 作第一個 value gate。
7. **[PR-12]** TDD matrix 加入 two-process contention 與
   `harness-operate` one-item/no-shortcut/full-closure eval。

## Iteration 1 result

```json
{
  "schemaVersion": "harness.review-loop.v2",
  "reviewType": "plan",
  "iteration": 1,
  "budget": {"maxSweeps": 5, "sweepsUsed": 1},
  "harnessStatus": "continue",
  "reason": "12 confirmed blockers were revised; a fresh verification sweep is required",
  "reasonCode": "open_blockers",
  "activeReviewers": ["A", "B", "C", "E", "F"],
  "surfaceId": "controlled-harness-learning@9c143bd",
  "scores": {"A": -1, "B": -1, "C": -1, "E": -1, "F": -1},
  "convergence": {
    "openBlockers": 12,
    "confirmedFindings": 12,
    "refutedFindings": 1,
    "unresolvedDecisionItems": 0,
    "unresolvedEvidenceItems": 0,
    "newBlockers": 12,
    "reopenedBlockers": 0,
    "latentMissedStreak": 0,
    "novelIssuesBySource": {
      "revision_introduced": 0,
      "latent_missed": 0,
      "scope_expansion": 0,
      "unsupported": 0
    },
    "maxMaterialRevisionAttempts": 1,
    "heldOutSweepsUsed": 0,
    "plateauDetected": false,
    "reviewProcessDefect": false
  },
  "userCheckpoints": {
    "intakeAsked": false,
    "decisionAsked": false,
    "recordedAssumptions": []
  },
  "attributionEvidence": {
    "originalSurfaceSnapshot": "commit 9c143bd + sha256 5f33eb174704aa488984bb3dc6d4838795e5fc1cca2b36690f26810a1200eeee",
    "currentSurfaceSnapshot": "sha256 f187a2278767156122da89f7c542659c0cdfa63fc831fd77763f973012adba40",
    "latestRevisionDiff": "git diff 9c143bd -- docs/specs/20260710-controlled-harness-learning/spec.md"
  },
  "ledger": [
    {"dedupeKey": "PR-01-evidence-attestation", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-02-observation-insight-identity", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-03-single-writer-transaction", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-04-path-confinement", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-05-public-value-privacy", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-06-review-binding", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-07-lifecycle-consumer", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-08-eval-artifact-boundary", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-09-eval-release-threshold", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-10-downstream-adoption", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-11-value-gated-scope", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-12-contention-consumer-proof", "status": "open", "verification": "confirmed"}
  ],
  "nextAction": {
    "type": "fresh_full_sweep",
    "summary": "verify every resolved blocker and attack the whole revised artifact"
  }
}
```

## Verification sweep — iteration 2

Scores: A `-1`、B `-1`、C `-1`、E `-1`、F `+2`。Reviewer F 對 frozen
F-01..F-10 baseline 的 re-diff 為 10/10 covered；其餘 reviewer 提出的 7 個 residual
major 全經 independent verifier 確認：

| key | attribution | residual |
|---|---|---|
| PR-10a-contract-discovery | carryover | converted contract 沒有 fresh-clone 可枚舉 public SSOT |
| PR-02-current-gap-identity | carryover | fingerprint 漏掉 public semantic field `current_gap` |
| PR-06-review-payload | carryover | receipt 綁 whole mutable observation，合法 transition 會自我失效 |
| PR-05-unicode-format-controls | carryover | NFKC/C0/C1 未攔 Unicode `Cf`、default-ignorable、bidi |
| PR-10b-adoption-attestation | carryover | adoption receipt 缺 target state／contract／evidence attestation |
| PR-08-harness-learn-scope | revision-introduced | tracked-artifact gate 誤寫成整個 skills submodule |
| PR-09-human-feedback | revision-introduced | viewer generation 未要求 skill-creator human feedback loop |

非阻塞 minor：eval threshold 的 denominator、run count、timeout 與 variance 口徑不明。

### Revision changelog（iteration 2 → 3）

1. **[PR-10a]** converted contract co-locate 到原 retro entry；`retro.py` 建 fresh-clone
   in-memory index；normal upgrade 入口強制 `inspect --for-upgrade`。
2. **[PR-02]** `current_gap` 納入 canonical fingerprint，補衝突 RED。
3. **[PR-06]** 新增 immutable `review_payload_digest` allowlist，排除 mutable
   status/disposition/receipt refs。
4. **[PR-05]** public scalar 拒絕 `Cf`、default-ignorable、bidi controls，補 token-split
   與 display-forgery 負例。
5. **[PR-10b]** 新增 versioned adoption schema：contract digest、screening/pre/post ready
   state、validation ref/result/evidence digest、CAS/idempotency。
6. **[PR-08]** tracked-artifact ratchet 限定 `harness-learn/**` 與本拍新增 eval paths，
   保留 unrelated existing skill content。
7. **[PR-09]** 發布前要求 official viewer 的 human feedback／approval 或明確 owner waiver；
   修訂後全量 paired eval 重跑。
8. **[minor]** 固定每 eval 3 組 paired runs、assertion-weighted denominator、
   timeout/error=failure、mean±stddev 與 trigger majority 計法。

```json
{
  "schemaVersion": "harness.review-loop.v2",
  "reviewType": "plan",
  "iteration": 2,
  "budget": {"maxSweeps": 5, "sweepsUsed": 2},
  "harnessStatus": "continue",
  "reason": "7 verified residual blockers were revised; a second verification sweep is required",
  "reasonCode": "open_blockers",
  "activeReviewers": ["A", "B", "C", "E", "F"],
  "surfaceId": "controlled-harness-learning@iteration-2",
  "scores": {"A": -1, "B": -1, "C": -1, "E": -1, "F": 2},
  "convergence": {
    "openBlockers": 7,
    "confirmedFindings": 7,
    "refutedFindings": 0,
    "unresolvedDecisionItems": 0,
    "unresolvedEvidenceItems": 0,
    "newBlockers": 2,
    "reopenedBlockers": 0,
    "latentMissedStreak": 0,
    "novelIssuesBySource": {
      "revision_introduced": 2,
      "latent_missed": 0,
      "scope_expansion": 0,
      "unsupported": 0
    },
    "maxMaterialRevisionAttempts": 2,
    "heldOutSweepsUsed": 0,
    "plateauDetected": false,
    "reviewProcessDefect": false
  },
  "userCheckpoints": {
    "intakeAsked": false,
    "decisionAsked": false,
    "recordedAssumptions": []
  },
  "attributionEvidence": {
    "originalSurfaceSnapshot": "commit 9c143bd + sha256 5f33eb174704aa488984bb3dc6d4838795e5fc1cca2b36690f26810a1200eeee",
    "currentSurfaceSnapshot": "sha256 6bb4c38ce6c286355e48509da80cf86c913fe679e01b5ac7df14af0a069aa4cc",
    "latestRevisionDiff": "git diff 9c143bd -- docs/specs/20260710-controlled-harness-learning/spec.md"
  },
  "ledger": [
    {"dedupeKey": "PR-10a-contract-discovery", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-02-current-gap-identity", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-06-review-payload", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-05-unicode-format-controls", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-10b-adoption-attestation", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-08-harness-learn-scope", "status": "open", "verification": "confirmed"},
    {"dedupeKey": "PR-09-human-feedback", "status": "open", "verification": "confirmed"}
  ],
  "nextAction": {
    "type": "fresh_full_sweep",
    "summary": "verify second material revision; any same carryover blocker now forces blocked"
  }
}
```

## Verification sweep — iteration 3（terminal）

- Reviewer B: `+2 APPROVE`
- Reviewer C: `+1 APPROVE`（只有 review metadata／waiver wording minor）
- Reviewer A: `-1 REVISE`
- Independent verifier:
  - **P1 CONFIRMED**：PR-10b 在第二次 material revision 後仍未定義
    `not-applicable`／`rejected` 的 outcome-discriminated screening、post-state、validation
    required/forbidden matrix。
  - **P2 CONFIRMED**：PR-10c 為 revision-introduced；mandatory upgrade screening 沒有
    具名的 authoritative upgrade entrypoint／bypass gate。

P1 命中 stop condition：「同一 confirmed blocker 經 2 次 material revision 仍 open」。
因此本 loop 以 `plateau` 結束；不跑 held-out、不寫 implementation plan、不進 TDD。
A 的 finding 已經足以觸發 terminal condition，iteration 3 在 A/B/C + verifier 後早停，
沒有再花 sweep 預算重跑 E/F。

```json
{
  "schemaVersion": "harness.review-loop.v2",
  "reviewType": "plan",
  "iteration": 3,
  "budget": {"maxSweeps": 5, "sweepsUsed": 3},
  "harnessStatus": "blocked",
  "reason": "PR-10b remained confirmed after two material revisions; PR-10c is also open",
  "reasonCode": "plateau",
  "activeReviewers": ["A", "B", "C"],
  "surfaceId": "controlled-harness-learning@iteration-3",
  "scores": {"A": -1, "B": 2, "C": 1},
  "convergence": {
    "openBlockers": 2,
    "confirmedFindings": 2,
    "refutedFindings": 0,
    "unresolvedDecisionItems": 0,
    "unresolvedEvidenceItems": 0,
    "newBlockers": 1,
    "reopenedBlockers": 0,
    "latentMissedStreak": 0,
    "novelIssuesBySource": {
      "revision_introduced": 1,
      "latent_missed": 0,
      "scope_expansion": 0,
      "unsupported": 0
    },
    "maxMaterialRevisionAttempts": 2,
    "heldOutSweepsUsed": 0,
    "plateauDetected": true,
    "reviewProcessDefect": false
  },
  "userCheckpoints": {
    "intakeAsked": false,
    "decisionAsked": false,
    "recordedAssumptions": []
  },
  "attributionEvidence": {
    "originalSurfaceSnapshot": "commit 9c143bd + sha256 5f33eb174704aa488984bb3dc6d4838795e5fc1cca2b36690f26810a1200eeee",
    "currentSurfaceSnapshot": "sha256 6bb4c38ce6c286355e48509da80cf86c913fe679e01b5ac7df14af0a069aa4cc",
    "latestRevisionDiff": "git diff 9c143bd -- docs/specs/20260710-controlled-harness-learning/spec.md"
  },
  "ledger": [
    {
      "dedupeKey": "PR-10b-adoption-attestation",
      "severity": "major",
      "status": "open",
      "verification": "confirmed",
      "materialRevisionAttempts": 2,
      "novelIssueSource": "none",
      "disposition": "same carryover remained after second material revision"
    },
    {
      "dedupeKey": "PR-10c-upgrade-entrypoint-enforcement",
      "severity": "major",
      "status": "open",
      "verification": "confirmed",
      "materialRevisionAttempts": 0,
      "novelIssueSource": "revision_introduced",
      "disposition": "mandatory screening has no named enforcement surface"
    }
  ],
  "nextAction": {
    "type": "stop",
    "summary": "owner must choose a redesigned adoption boundary and authoritative upgrade entrypoint before starting a fresh review surface"
  }
}
```
