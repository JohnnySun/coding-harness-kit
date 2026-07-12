# TDD and verification scope repair

Date: 2026-07-12

## Intent

Repair an over-broad TDD policy in two existing upstream subjects, then repair
the shared HarnessKit skill source that propagated it. TDD is a development
workflow for maintained behavior; it is not a prerequisite for every terminal
command, design activity, research task, or read-only investigation.

Verification remains mandatory where the repository completion contract
requires evidence. Removing a Red-first requirement from discovery work does
not remove the requirement to verify conclusions or run the trusted suite
before completing maintained code, policy, harness, or dangerous write-path
changes.

## Decision rule

Use TDD when behavior is intended to be repeatable, maintained, or protected
against future drift:

- reusable code, parsers, validators, generators, installers, and recovery tools;
- bug fixes with a reproducible regression fixture;
- flash, rollback, verified-boot, partition write-set, user-data, and hardware-write logic;
- harness, hooks, policy enforcement, and release artifact production;
- stable contracts whose future drift must be detected automatically.

TDD is not required when the purpose is to discover or record what the current
environment does:

- read-only device exploration and log inspection;
- one-off image, partition, system, package, or service inspection;
- public research, source browsing, environment discovery, and hypothesis tests;
- design and planning work that does not implement maintained behavior;
- compiler- or linker-driven iteration where the build is the direct feedback loop;
- generated evidence, transcripts, and ordinary research notes.

When exploration produces a lasting implementation assumption, safety
decision, parser, validator, or reusable runner, only that promoted maintained
behavior enters the TDD path.

## Repair order

1. Repair the effective root policy files in both existing upstream subjects so
   agents can immediately route non-development work correctly.
2. Repair the already-installed development and review skills that still apply
   a universal failing-test-first gate.
3. Repair the HarnessKit skill source, examples, and tests so reinstalling or
   synchronizing cannot restore the over-broad rule.
4. Attach both existing working trees through the private subject registry by
   symbolic link, without creating duplicate clones.
5. Verify each repository through its own trusted suite, then verify HarnessKit
   through its complete public trusted suite and local subject readiness checks.

## Repository boundaries

Existing unrelated changes in an upstream subject belong to the user. Policy
edits must be narrow, made in the repository or submodule that owns each file,
and must not reset, rewrite, or silently include unrelated work.

Installed client trees remain generated local surfaces. The durable fix belongs
in HarnessKit's source skills; local installed copies may be refreshed only
after their source behavior is corrected and validated.

The private subject registry, pins, symbolic links, real remotes, and checkout
paths remain gitignored. Public files use generic upstream-subject language and
must not contain private identifiers or local absolute paths.

## Acceptance criteria

- Effective policy in both upstream subjects contains the maintained-behavior
  decision rule and explicit discovery, research, design, build-iteration, and
  evidence exemptions.
- Review prompts ask for failing-test-first evidence only when TDD applies.
- Harness operation still requires regression tests for maintained gate, hook,
  policy, parser, installer, release, and dangerous write-path behavior.
- A policy fixture proves that maintained reusable behavior remains on the TDD
  path.
- A policy fixture proves that read-only exploration, research, design, and
  compiler-driven iteration are not rejected for lacking a Red test.
- Both existing working trees are connected through private symbolic-link
  subject checkouts and have reproducible local pins; no new clone is created.
- Each affected repository's trusted suite passes, followed by HarnessKit's
  complete trusted suite.

## Non-goals

- Rewriting historical plans, reviews, evidence, or completed work records.
- Weakening verification, safety approval, rollback, release, or hardware-write
  boundaries.
- Flattening the upstream subjects into HarnessKit's internal layout.
- Committing private subject paths, remotes, pins, snapshots, or comparisons.
