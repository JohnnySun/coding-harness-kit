# Spec: Documentation conventions for Harness-dev

**Status**: Accepted (implementation this beat)  
**Date**: 2026-07-09

## Intent

Stop scattering design docs under `docs/harness/` and ad-hoc paths. Adopt a
centralized shape (single landing zone + sentinels + L1 gate), adapted for a
coding-harness toolkit (no product TD/Lark chain).

## Rules

1. Design artifacts → `docs/specs/YYYYMMDD-slug/`.
2. `docs/harness/` = ledgers + long-lived `design.md` only.
3. Sentinels block legacy paths: root `specs`, `docs/superpowers`, `docs/technical-design`.
4. L1 pre-commit rejects **new** markdown directly under `docs/` outside allowlist.
5. Public trusted suite asserts README + sentinels + no loose design files in `docs/harness/`.

## Allowlist (docs/*.md new files)

`specs|harness|onboarding|arch|rfcs`

## Migration (this beat)

| From | To |
|------|-----|
| `docs/harness/plan-public-suite-l2-ci-2026-07-09.md` | `docs/specs/20260709-public-suite-l2-ci/plan.md` |
| `docs/harness/plan-review-public-suite-l2-ci-2026-07-09.md` | `docs/specs/20260709-public-suite-l2-ci/plan-review.md` |
| `docs/harness/plan-review-2026-07-09.md` | `docs/specs/20260709-harness-design-review/plan-review.md` |

## Non-goals

- Full redlines.json / make redlines-check port
- Forcing `_meta.yaml` on every folder
- Product rename
