# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <strong>English</strong> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.pt-BR.md">Português</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.hi.md">हिन्दी</a> |
  <a href="README.id.md">Bahasa Indonesia</a> |
  <a href="README.vi.md">Tiếng Việt</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **In one line:** This is a chop shop for your repo's *guardrails*. What goes up on the lift isn't your business code — it's the **coding harness** wrapped around it: the layer that keeps an AI (Cursor, Claude Code, Codex) from cutting corners, faking "done," or shoving things that shouldn't be committed into git.
>
> **What's in it for you:** Either drive with our tuned methodology skills and idiot-proof hooks as-is, or bolt the same guardrails onto your own repos. We don't touch the engine (your business source) — we just weld the outer roll cage until an AI can't casually crumple it.
>
> **Three gears to get rolling:** one-line install → (ignition) rack Agent-Kit → (optional) drive your own subject in. Before you clock out, hit `bash tools/harness/test-harness.sh` — dashboard all green means it passed inspection and it's street-legal.

## Glossary (shop slang)

You'll see these words everywhere below. Learn them once here; the rest of the doc just uses them.

| Slang | Plain English |
|-------|---------------|
| **coding harness** | The "car" we actually wrench on — the whole AI-dev guardrail layer around a product repo: rules, skills, hooks, trusted suite, ledgers |
| **subject** | A product repo driven onto the bay to be absorbed / compared; cloned locally only, **never** committed here |
| **harness surface** | The mod panels on that car (`AGENTS.md`, skills, hooks) — not the engine (business source) |
| **Agent-Kit** | The rack-it installer — drops methodology skills / hook templates into Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — the dyno run before this shop ships anything (same rig as L2 CI) |

## Fastest lane: one-line intake

One command does the whole job: clone the shop, pull submodules, install git hooks, rack Agent-Kit, then run it straight onto the dyno (the public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Too fancy? The old-school pipe cranks the same engine:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Want to pick where it lands and who it wires up? Set these two env vars:

- `TARGET_DIR` — which directory to install into
- `CLIENT` — which client to wire: `cursor` / `claude` / `codex` / `codex-native`, or `skip` to leave Agent-Kit for later

The one-liner also racks Agent-Kit and runs the suite for you — **most people cut the engine and clock out right here**. Want to bolt on one gear at a time, or did the one-liner stall mid-run? Take the manual lane below.

## Manual intake (bolt it on yourself)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

At this point the bay door is just open — the parts crate (Agent-Kit) is still sitting on the floor. Keep going.

## Rack Agent-Kit (parts crate onto the wall)

Agent-Kit drops this repo's methodology skills and hooks into your editor / CLI. A bare install hands you a tuned default set: local methodology, a curated pick of SP verification / TDD / review skills, a Matt library you call on purpose, plus a low-frequency advisory router.

It does **not** sneak in `using-superpowers` / `brainstorming` bootstrap, and it leaves vendor hooks alone — those are opt-in only. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) are **install outputs and never committed**: always regenerate via install rather than hand-editing them and smuggling them back into git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Values |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optional) | `lean`, `guided`, `structured`; advisory prompt density only — **never** touches enforcement |

The most common local bootstrap — rack all four clients at once:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

The repo profile always goes through the CLI (don't hand-edit the YAML — that's asking for trouble). To carry the setup into another repo, export first, then check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` only survives as an explicit full-plugin compatibility hatch for older workflows — it's no longer the recommended path. Default library materialization won't copy vendor plugins, hooks, or any skill outside the allowlist.

## Drive your own car in (optional: wire up a subject)

Just want to confirm the shop runs all green? **Wire up nothing** — a public clone leans on zero private product repos and still runs the trusted suite to a wall of green.

Only when you actually want to sync / import / compare a real subject do you run this line:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Memorize one order: **create `manifest.yaml` → sync → `--pin` to write the version back → `check-local-absorb.sh` until `harness-ready`**. Clear that gate first; only then do import / compare / score get to run.

These stay local and are already gitignored — don't fight to force them into a commit; the pre-commit hook will bounce them on the spot anyway:

- `subjects/manifest.yaml`
- each subject's `pin.json` and `checkout/`
- `snapshots/`, `comparisons/`

---

Below is the daily reference wall — pull a tool when you need it, no need to read it all at once.

## Common commands (tool wall)

| What you want | The line to run |
|---------------|-----------------|
| Public trusted suite (dyno / CI-shaped) | `bash tools/harness/test-harness.sh` |
| Validate Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Rewrite pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Floor plan (where each part lives)

| Path | What it is | In git? |
|------|------------|---------|
| `agent-kit/skills` | Open methodology (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Per-client hooks / settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Install outputs | ✗ |
| `subjects/manifest.example.yaml` | Public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb products | ✗ |
| `docs/harness/` | Design + ledgers | partial |
| `AGENTS.md` | Constraint SSOT (`CLAUDE.md` points here) | ✓ |

## Manual shelf (dig deeper)

- [`docs/README.md`](../README.md) — documentation placement rules
- [`docs/harness/design.md`](../harness/design.md) — this repo's harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — completion definition, blacklist, mechanism map

## License

[MIT](../../LICENSE) — drive it off the lot however you like; the title's right here.
