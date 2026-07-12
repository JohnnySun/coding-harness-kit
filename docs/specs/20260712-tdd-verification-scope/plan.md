# Scoped TDD and Verification Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the current over-broad TDD contracts in two upstream subjects, repair the shared HarnessKit source that propagated them, and attach the existing working trees to the private subject registry without cloning.

**Architecture:** Treat TDD applicability and completion verification as separate decisions. Repair each owning repository first, then repair shared source prompts and install surfaces, and finally wire the already-existing working trees through private symbolic-link checkouts and reproducible pins.

**Tech Stack:** Markdown policy contracts, shell and Python harness checks, Node test fixtures, Git submodules, YAML private registry, symbolic links.

---

### Task 1: Capture pre-change evidence and ownership boundaries

**Files:**
- Read: root policy, harness policy, review skills, and trusted-suite entrypoints in each affected repository
- Read: `agent-kit/skills/skills/harness-operate/SKILL.md`
- Read: `agent-kit/skills/skills/harness-builder/SKILL.md`
- Read: `agent-kit/skills/skills/plan-review/references/reviewer-prompts.md`
- Read: `agent-kit/skills/skills/code-review/SKILL.md`

- [ ] **Step 1: Record repository state without modifying it**

Run `git status --short --branch` and `git submodule status` in each repository. Record which policy files are owned by submodules and preserve all unrelated dirt.

- [ ] **Step 2: Classify every proposed edit**

For each edit, record one of: policy prose, maintained policy validator, installed generated surface, or private subject wiring. Policy prose and private wiring do not require Red-first evidence; maintained validators and propagation checks do.

### Task 2: Repair the first upstream subject's effective policy

**Files:**
- Modify: effective root agent policy
- Modify: TDD workflow documentation
- Modify: harness documentation and pull-request template
- Test: existing engineering-policy contract tests

- [ ] **Step 1: Add failing policy-contract assertions**

Assert that the effective policy contains both clauses:

```text
TDD applies to maintained repeatable behavior.
TDD is not required for discovery, design, research, direct build feedback, or generated evidence.
```

Also assert that reusable code, regression fixes, safety-relevant writes, harness policy, and release artifacts remain covered.

- [ ] **Step 2: Run the focused policy test and confirm the old contract fails**

Run the repository's focused engineering-policy test. Expected result: failure because the exemption language and conditional review rule are absent.

- [ ] **Step 3: Replace universal Red-first wording with the scoped decision rule**

Keep full trusted-suite requirements for maintained code, policy, harness, release, and dangerous write-boundary changes. Do not require Red-first evidence for read-only inspection, research, design, compiler-driven iteration, or ordinary evidence updates.

- [ ] **Step 4: Run focused and full verification**

Run the focused engineering-policy test, then the repository's complete local trusted suite. Expected result: all pass.

### Task 3: Repair the second upstream subject's effective policy and routed skills

**Files:**
- Modify: effective root instruction file and the effective child instruction files that duplicate its TDD contract
- Modify: the development-routing skill that currently stacks TDD for every deployable change
- Modify: plan-review and code-review prompts in the owning skill submodule
- Test: existing skill-hook and policy fixtures, adding focused classification fixtures where required

- [ ] **Step 1: Add failing classification fixtures**

Positive fixtures must keep TDD for reusable code, reproducible fixes, validators, hooks, stable public contracts, release outputs, and dangerous writes. Negative fixtures must show that design, research, environment inspection, compiler-driven iteration, and generated evidence do not receive a mandatory Red-first gate.

- [ ] **Step 2: Run focused fixtures and confirm the old router or contract fails**

Expected result: at least the negative classification fixtures fail under the current universal wording.

- [ ] **Step 3: Repair policy and skill routing in their owning repositories**

Use the same maintained-behavior decision rule everywhere. Preserve stricter stable-contract rules for privacy, public APIs, harness control planes, and safety-relevant execution.

- [ ] **Step 4: Verify each touched submodule before changing any parent gitlink**

Run each submodule's own focused tests and trusted suite. Do not stage unrelated submodule dirt. Parent gitlinks remain opt-in and narrowly scoped.

### Task 4: Repair HarnessKit source skills and propagation

**Files:**
- Modify: `agent-kit/skills/skills/harness-operate/SKILL.md`
- Modify: `agent-kit/skills/skills/harness-builder/SKILL.md`
- Modify: `agent-kit/skills/skills/harness-builder/references/axioms.md`
- Modify: `agent-kit/skills/skills/harness-builder/references/three-loops.md`
- Modify: `agent-kit/skills/skills/harness-builder/references/worked-example.md`
- Modify: `agent-kit/skills/skills/plan-review/references/reviewer-prompts.md`
- Modify: `agent-kit/skills/skills/code-review/SKILL.md`
- Modify: `agent-kit/skills/README.md`
- Test: `tools/harness/test_agent_kit_install.py` and a focused source-policy contract test added beside it

- [ ] **Step 1: Add failing source-contract tests**

Test that source skills retain TDD for maintained harness behavior while plan and code review ask for Red-first evidence only when the task is TDD-applicable. Test that install output is sourced from the repaired files.

- [ ] **Step 2: Run focused tests and confirm failure against the old source wording**

Expected result: conditional-scope assertions fail while install mechanics remain green.

- [ ] **Step 3: Apply the minimum source edits**

Change unconditional headings such as `TDD (cannot skip)` into a classification step followed by conditional TDD. Keep real regression fixtures and positive controls mandatory for maintained gate and hook behavior.

- [ ] **Step 4: Refresh generated client surfaces through the installer**

Use the repository installer for all supported clients. Do not hand-maintain generated client trees as durable source.

- [ ] **Step 5: Run the full HarnessKit trusted suite**

Run `bash tools/harness/test-harness.sh`. Expected result: complete pass, not only focused tests.

### Task 5: Attach the existing working trees as private subjects

**Files:**
- Create locally: `subjects/manifest.yaml` (gitignored)
- Create locally: two `subjects/<id>/checkout` symbolic links (gitignored)
- Create locally: two `subjects/<id>/pin.json` files (gitignored)

- [ ] **Step 1: Build the private manifest from the public schema**

Use each existing repository's actual origin, branch, harness paths, trusted-suite command, and default harness submodules. Do not write these private values into public files.

- [ ] **Step 2: Create symbolic-link checkout attachments**

Point each private `subjects/<id>/checkout` at the corresponding existing working tree. Confirm with `test -L` and `readlink`; do not invoke clone.

- [ ] **Step 3: Generate pins from observed repository state**

Record the current root HEAD and every declared default submodule HEAD. Do not reset or fetch the attached repositories as part of pinning.

- [ ] **Step 4: Verify local readiness**

Run `python3 tools/lib/subject_ready.py <id>` for each attached subject, followed by `bash tools/harness/check-local-absorb.sh --all`. Expected result: both subjects are harness-ready or a precise drift/submodule diagnosis is reported without claiming success.

### Task 6: Independent review and completion evidence

**Files:**
- Review: all diffs created by Tasks 2-4
- Verify: private wiring from Task 5 without staging it

- [ ] **Step 1: Run adversarial code review**

Review specifically for accidental weakening of safety verification, universal TDD wording left in active prompts, modification of historical records, public-tree leakage, and unrelated submodule changes.

- [ ] **Step 2: Re-run every repository's full trusted suite after review fixes**

Focused tests are iteration evidence only. Completion requires each affected repository's own trusted suite and `bash tools/harness/test-harness.sh` to pass on the final tree.

- [ ] **Step 3: Report exact state**

Report changed files by owning repository, test commands and results, subject readiness, preserved local dirt, commits created, and any gitlink or installation action deliberately left local.
