# Prompt Skill Router — model-tier-prompting + refine

> **Date:** 2026-07-09  
> **Status:** implemented  
> **Source:** upstream subject skill-hook intent rules → subject workspace `prompt-skill-router` (2026-07-09) → Harness-dev  
> **Skills SSOT:** `agent-kit/skills/skills/{model-tier-prompting,refine}` (already in harness-dev profile)

## TL;DR

Harness-dev already shipped the methodology skills via agent-kit install. What was missing was **advisory intent routing** on prompt submit:

1. On Claude/Codex `UserPromptSubmit` and Cursor `beforeSubmitPrompt`, run `tools/harness/prompt-skill-router.mjs`.
2. Suggest `model-tier-prompting` or `refine` via context injection (no deny).
3. Keep intent rules isomorphic with the upstream port (`prompt(?![_a-z])` guard, refine B/C heuristics).

There is **no separate auto-optimize engine** — detect intent → inject skill → skill protocol does the work.

## Why

Without the router, agents only discover `model-tier-prompting` / `refine` via description matching. Explicit asks like「優化提示詞」「派工 prompt」「/refine」and thin big-task prompts were not force-suggested.

## Mechanism map

| Piece | Upstream subject workspace | Harness-dev |
| --- | --- | --- |
| Skills | `agent-kit/skills/{…}` (copied) | `agent-kit/skills/skills/{…}` (SSOT submodule; already installed) |
| Intent routing | `scripts/harness/prompt-skill-router.mjs` | `tools/harness/prompt-skill-router.mjs` |
| Tests | `prompt-skill-router.test.mjs` in subject suite | same + `test-harness.sh` |
| Claude/Codex wire | `agent-kit/hooks/hooks.json` UserPromptSubmit | `agent-kit/hooks/clients/{claude.settings,codex.hooks}.json` |
| Cursor wire | not wired (upstream) | `beforeSubmitPrompt` → same router (best-effort `continue` + `agent_message`) |
| Skill path in inject text | `agent-kit/skills/…` | `agent-kit/skills/skills/…` |

## Intent rules (advisory only)

### `model-tier-prompting`

Fires on prompt-engineering / optimize-rewrite-migrate / dispatch-prompt / model-tier language.

**Negative guard:** `prompt(?:s)?(?![_a-z])` so snake_case identifiers (`prompt_cache_key`) do not misfire.

### `refine`

- **B — explicit:** `/refine`, 「需求寫清楚」, 「展開成任務書/spec」.
- **C — thin big-task heuristic (prompt-submit only):** length 4–120, build verb, no acceptance/boundary words, not prompt-domain. Follow-ups excluded.

Never deny — session-deduped (2h TTL, `/tmp/harness-dev-prompt-skill-*.json`).

## Files touched

- `tools/harness/prompt-skill-router.mjs` + `.test.mjs`
- `tools/harness/test-harness.sh` — include router unit tests
- `tools/harness/checks.py` — hook-wiring asserts prompt-skill-router
- `tools/harness/test_agent_kit_install.py` — install contract for three clients
- `agent-kit/hooks/clients/cursor.hooks.json` — `beforeSubmitPrompt`
- `agent-kit/hooks/clients/claude.settings.json` — `UserPromptSubmit`
- `agent-kit/hooks/clients/codex.hooks.json` — `UserPromptSubmit`
- `docs/specs/20260709-prompt-skill-router/spec.md` (this file)

## Verification

```bash
bash tools/harness/test-harness.sh
# after template change, refresh local client trees:
for c in cursor claude codex; do CLIENT=$c bash tools/harness/agent-kit.sh install; done
```

## Out of scope

- Porting the full upstream skill-hook (domain/UI/deny gates).
- Symlinking subject business skills into this repo's client trees (blacklist).
- Declaring routes inside empty `agent-kit/hooks/hooks.json` (Harness-dev uses per-client templates under `hooks/clients/`, not the upstream monolithic hooks.json profile map).

## Intentional differences vs upstream subject workspace

1. **Skill path prefix** is `agent-kit/skills/skills/` (Harness-dev submodule layout).
2. **Cursor** is wired (`beforeSubmitPrompt`); upstream left Cursor unwired for this router.
3. **No** subject-local workflow-guide skill / declarative `routes` map — Harness-dev has no equivalent; AGENTS.md already lists the methodology skills as priority.
4. Session flag prefix is `harness-dev-prompt-skill-` (not subject-prefixed).
