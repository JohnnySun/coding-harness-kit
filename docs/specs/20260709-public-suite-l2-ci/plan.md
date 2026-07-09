# Plan: Public trusted suite + subject-gate protocol + L2 CI

> Review surface for plan-review (2026-07-09).  
> Rev.2 — addresses confirmed blockers A1, A2/B1, B4 from plan-review sweep 1.  
> Product rename deferred (inbox).

## Context

- **Problem**: Harness-dev will push to public GitHub. Current trusted suite couples to private `subjects/**` (pin/checkout/snapshot), which leaks privacy risk and breaks clean CI clones.
- **Constraint**: Coding-harness toolkit (not generic harness). Subjects are decoupled; this repo must not treat private subject state as its own invariants.
- **Scope (this beat)**: Rebuild public trusted suite; in-repo fixture demos; registry `trusted_suite` + `fixture_root`; subject-agnostic gate checker; GitHub Actions L2; close `l2-ci`; sync design/AGENTS SSOT; defer product naming.
- **Acceptance**:
  1. `bash tools/harness/test-harness.sh` green on a fresh public clone (no private manifest/checkout), **with `agent-kit/skills` submodule initialized**.
  2. Suite source does not call pin/checkout/snapshot checkers against real `subjects/**` (`public-suite-decoupled` check).
  3. Example registry declares `trusted_suite` + `fixture_root`; green fixture passes checker; red fixture fails.
  4. `.github/workflows/harness-trusted.yml` on `main` push+PR runs the same public suite; checkout uses **`submodules: true`** (or equivalent init) before install.
  5. `design.md` §3 步1 rewritten to public-only check IDs; AGENTS/CLAUDE drop `HARNESS_ALLOW_DRIFT` as a public-suite escape; L2 marked closed.
  6. Local absorb readiness has a **named entrypoint** (not the public suite): `python3 -m tools.lib.subject_ready` / import·compare·score `require_ready` (document in AGENTS).
  7. Checker precedence: when **both** `fixture_root` and `subjects/<id>/checkout` exist, **prefer checkout** unless `--fixture` / public-suite mode forces fixture (prevents copy-example false green).
  8. `l2-ci` closed in `gates.json` only after public suite + workflow green; naming deferred in retro-inbox.
- **Out of scope**: Product/repo rename; cloning private remotes in CI; TTADK; making install rewrite hooks.

## Design

### 1. Public vs private decoupling

| Layer | What | Where it runs |
|---|---|---|
| **Public trusted suite** | agent-kit contracts, symlink-health, hook-wiring, example manifest schema, gitignore F5+, fixture submodule predicate, subject-gate checker against **fixtures** (public mode) | Local + GitHub CI (`test-harness.sh`) |
| **Private absorb readiness** | pin/checkout/default_submodules/snapshot against real `subjects/**` | **Not** in public suite. Entrypoint: `tools/lib/subject_ready.py` (consumed by import/compare/score). Optional local helper doc: `bash tools/harness/check-local-absorb.sh` wrapping ready checks when local manifest exists |
| **Subject gate protocol** | Execute registry-declared `trusted_suite` at resolved root | Local tool; CI only via public fixtures / `--fixture` |

### 2. Registry protocol fields

Per subject in YAML registry:

- `trusted_suite` (optional): shell command, cwd = subject root. Trust boundary: committed example + operator-controlled local manifest only (never remote-fetched registry).
- `fixture_root` (optional, public): repo-relative path under `testdata/…`. Required in **public example** when `trusted_suite` is set.
- **Resolution order (rev.2)**:
  1. `--root` CLI override (must stay inside repo if set)
  2. If `--fixture` **or** public-suite invocation: use `fixture_root` (required)
  3. Else if `subjects/<id>/checkout` exists: use checkout (**prefer over fixture**)
  4. Else if `fixture_root` set: use fixture
  5. Else skip
- No `trusted_suite` → skip (not fail).
- `fixture_root` containment: `Path.is_relative_to(ROOT)` (not string prefix).
- Private `manifest.yaml` guidance: omit `fixture_root` (or rely on checkout-prefer rule).

### 3. In-repo fixtures

- `testdata/subjects/demo-coding-harness-min`: minimal coding harness (AGENTS.md + `scripts/harness/test-harness.sh` exit 0).
- `testdata/subjects/demo-coding-harness-red`: exit 1 + stderr marker (negative test).
- Example manifest points both at fixtures with placeholder remotes (CI does not clone them).
- `--all` on example is expected non-zero (red subject); public suite allowlists green subject + separate red assertion.

### 4. Checker

- `tools/harness/check_subject_gates.py` (+ `test_subject_gates.py`).
- Public suite: green must pass; red must fail; static `public-suite-decoupled` ban on private checkers.
- Does not clone remotes; does not read `pin.json`.

### 5. L2 CI

- Workflow: push + PR to `main` only.
- Same entry: `bash tools/harness/test-harness.sh`.
- **Checkout: `actions/checkout@v4` with `submodules: true`** (init `agent-kit/skills`) before any install/suite step.
- Then `agent-kit.sh install` for cursor/claude/codex/codex-native **without** optional plugins.
- No secrets; no private subject sync.
- Close `l2-ci` only after this workflow is green on a clean public path.

### 6. Doc / SSOT migration (in-scope)

- Rewrite `docs/harness/design.md` §3 步1 table to public check IDs only; point pin/checkout/snapshot to `subject_ready` / product tools.
- Update AGENTS.md / CLAUDE.md: 完成定義仍是 `test-harness.sh`; remove or re-scope `HARNESS_ALLOW_DRIFT` away from public suite; 機關落點 L2 → workflow path ✓; mention `testdata/**` fixtures.
- Inbox: product naming deferred.

### 7. Verify order (TDD into suite)

1. Red: protocol unit tests + `public-suite-decoupled` / fixture assertions.
2. Green: checker + checks.py + fixtures.
3. Wire into `test-harness.sh`.
4. Workflow with submodule init.
5. Doc SSOT + close `l2-ci`.

## Explicit non-goals

- CI executing private checkouts.
- Forcing every subject to use the same script path.
- Renaming the repository this beat.
- Exhaustive CI failure-mode catalogs beyond fail-closed steps + submodule init.

## Plan-review ledger (sweep 1 → rev.2)

| ID | Verdict | Disposition in rev.2 |
|---|---|---|
| A1 submodule init | CONFIRMED | §5 + Acceptance #4 |
| A2/B1 design dual SSOT | CONFIRMED | §1 local entrypoint + §6 doc migration + Acceptance #5–#6 |
| B4 fixture before checkout | CONFIRMED | §2 resolution order rev.2 + Acceptance #7 |
| B2 failure-mode prose | REFUTED | — |
| B3 --root RCE in CI | REFUTED | trust boundary note only |
| C1 completion-def rewrite | REFUTED | AGENTS pin wording via A2 |
| C2 TDD order mandatory | REFUTED as blocker | §7 kept as process |
