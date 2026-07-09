# Documentation conventions (SSOT)

This repo is a **coding-harness toolkit**. Design artifacts and harness ledgers
are separated on purpose.

## Design documents → `docs/specs/`

**All design documents** (spec, plan, technical design, brainstorm, grill
convergence, plan-review reports, superpowers design/plan output) go to:

```
docs/specs/YYYYMMDD-slug/
```

| Rule | Detail |
|------|--------|
| **Location** | `docs/specs/` — the single landing zone for design |
| **Naming** | `YYYYMMDD-slug/` (e.g. `20260709-public-suite-l2-ci/`) |
| **Content** | Any format inside: `spec.md`, `plan.md`, `plan-review.md`, `technical-design.md`, `design.md`, free-form |
| **plan-review / grill** | Write convergence **into the same folder** (do not create a new root under `docs/`) |
| **Do NOT write to** | `docs/superpowers`, `docs/technical-design`, root `specs/`, or loose `docs/*.md` |

## Other documentation

| Directory | Purpose |
|-----------|---------|
| `docs/harness/` | **Ledgers & long-lived harness SSOT only**: `design.md`, `gates.json`, `retro-inbox.md`, `work-orders.md`, `deviation-log.md`, `gate-events.jsonl`, `reports/` |
| `docs/onboarding/` | Getting-started / CI / install cheatsheets; **localized READMEs** (`README.<locale>.md`) |
| `docs/README.md` | This file — placement SSOT |

### Root README vs locales

| Path | Role |
|------|------|
| `/README.md` | **Default language only** (Traditional Chinese). Keep the root clean — do not dump every locale here. |
| `docs/onboarding/README.<locale>.md` | Translations (zh-CN, en, ja, …). Linked from the language switcher in `/README.md`. |

`docs/harness/` is **not** a dumping ground for plans. If it is a design beat,
it belongs under `docs/specs/`.

## What NOT to commit

- Private subject remotes, pins, checkouts, snapshots, comparisons
- Private subject **names / remotes / home absolute paths** inside otherwise-public file bodies (docs, tools, comments)
- Employer / org brand names or internal forge hostnames in public-tree prose (AI constraint in `AGENTS.md` — not a ban-list string scanner)
- One-off debugging notes / experiment dumps
- Plugin vendor docs under `.cursor/plugins/**` or `.codex/plugins/**` (install outputs)

## Enforcement

| Layer | Mechanism |
|-------|-----------|
| Constraint | This README + `AGENTS.md` / `CLAUDE.md` |
| L1 | `tools/harness/pre-commit.sh` blocks **new** `docs/*.md` outside allowed subdirs; also runs `public_tree_desensitize.py --staged` |
| Trusted suite | `docs-placement` + `public-tree-desensitize` in `tools/harness/checks.py` |

See also: `docs/specs/20260709-docs-conventions/spec.md`.
