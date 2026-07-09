# Plan-review report: Public suite + L2 CI

**Date**: 2026-07-09  
**Artifact**: `docs/harness/plan-public-suite-l2-ci-2026-07-09.md` (rev.2 after sweep 1)  
**Budget**: 5 sweeps; used 1 discovery + verify + plan revise (held-out not yet run on rev.2)

## Harness status

```json
{
  "schemaVersion": "harness.review-loop.v2",
  "reviewType": "plan",
  "iteration": 1,
  "budget": {"maxSweeps": 5, "sweepsUsed": 1},
  "harnessStatus": "continue",
  "reason": "Confirmed blockers addressed in plan rev.2; need verification sweep + held-out on revised plan before passed",
  "reasonCode": "open_blockers",
  "activeReviewers": ["A", "B", "C", "F"],
  "scores": {"A": -1, "B": -1, "C": -1, "F": -1},
  "convergence": {
    "openBlockers": 0,
    "confirmedFindings": 3,
    "refutedFindings": 4,
    "heldOutSweepsUsed": 0,
    "plateauDetected": false
  },
  "nextAction": {
    "type": "fresh_full_sweep",
    "summary": "Re-review plan rev.2 (A1/A2/B4 fixes), then held-out; or user may authorize implement-from-rev.2 now"
  }
}
```

## Confirmed blockers → plan fixes

1. **CI must init `agent-kit/skills` submodule** → workflow `submodules: true` + acceptance.
2. **design §3 / AGENTS dual SSOT** → public suite table rewrite; name `subject_ready` as local absorb entrypoint; drop ALLOW_DRIFT-as-suite-escape.
3. **`fixture_root` before checkout false-green** → prefer checkout when present; `--fixture` / public mode for CI.

## Refuted (non-blocking)

- Exhaustive CI failure-mode prose  
- PR RCE via `--root` (public suite never passes `--root`)  
- Completion-definition rewrite as independent requirement  
- TDD-order as hard close gate (kept as §7 process)

## Non-blocking notes

- Prefer `Path.is_relative_to` for fixture escape  
- Document `trusted_suite` trust boundary  
- Example `--all` expected non-zero (red subject)

## Next

- **Recommended**: verification sweep on rev.2 → held-out → `passed`, then finish implementation.  
- **Or**: you authorize implement-from-rev.2 now (plan already encodes the three confirmed fixes).
