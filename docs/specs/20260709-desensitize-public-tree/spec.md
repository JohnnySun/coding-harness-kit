# Public-tree content desensitization

> **Date:** 2026-07-09  
> **Status:** implemented (rev.2 — employer/org brand names are AI constraints, not string scanners)  
> **Trigger:** prompt-skill-router port left private subject names / provenance in public docs & comments (`via <subject>` marker). Path-based F5+ already blocks private *trees*; this beat blocks private *text* inside public files for **generic** leak shapes.

## TL;DR

1. **Executable gate** (`public_tree_desensitize.py`): home absolute paths, absolute `subjects/<id>/checkout`, and (when local) private-manifest subject ids / remotes.
2. **AI gate** (`AGENTS.md` / `CLAUDE.md` + SessionStart advisory): do not write employer/org brand names, internal forge hostnames, or private subject provenance into the public tree — use generic wording. **Do not** implement this as a ban-list string match in code (that reintroduces the token into the repo).
3. Wire the executable scan into the public trusted suite (`checks.py`) and L1 (`pre-commit.sh --staged`).

## Always-on patterns (CI-safe)

| Pattern | Why |
| --- | --- |
| `/Users/<name>/…`, `/home/<name>/…` | Machine-local absolute paths |
| Absolute `…/subjects/<id>/checkout` | Private absorb body path |

## Local-manifest patterns (when `subjects/manifest.yaml` exists)

| Pattern | Why |
| --- | --- |
| Subject ids from private registry | Real work-object names must not leak into public docs/tools |
| `remote:` values from private registry | Real remotes must not appear in public tree |

No private manifest (fresh public clone / CI) → only always-on patterns run.

## AI constraint (not a string scanner)

Public docs / comments / specs must not name a specific employer or internal org brand. Prefer「上游 subject」「內部 forge」「本機私有 registry」等通用指代. Enforcement is agent behavior (read AGENTS on session start), not a regex over the ban token.

## Non-goals

- Scanning gitignored private trees (`subjects/**` bodies, snapshots, comparisons).
- Rewriting upstream `agent-kit/skills` submodule content (owned elsewhere).
- Blocking the public example registry (`subjects/manifest.example.yaml`).
- Embedding employer/org brand ban-lists in harness source or tests.

## Files

- `tools/harness/public_tree_desensitize.py`
- `tools/harness/test_public_tree_desensitize.py`
- `tools/harness/checks.py` — `public-tree-desensitize` check
- `tools/harness/pre-commit.sh` — staged content scan
- `tools/harness/hook-router.mjs` — SessionStart desensitize advisory
- `tools/harness/test-harness.sh` — unittest discover
- `AGENTS.md` / `CLAUDE.md` — AI blacklist wording
- `docs/specs/20260709-desensitize-public-tree/spec.md` (this file)

## Verification

```bash
bash tools/harness/test-harness.sh
python3 tools/harness/public_tree_desensitize.py
```
