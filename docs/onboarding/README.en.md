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

> An open-source toolkit for **building and iterating coding harnesses**.  
> This repo contains no business source code — it works on the **harness surface** of each subject repo.  
> Three steps to get started: init submodules → install Agent-Kit → (optional) sync your subjects.

| Term | Meaning |
|------|---------|
| **coding harness** | The AI-dev guardrail layer around a product repo: rules, skills, hooks, trusted suite, ledgers |
| **subject** | A product repo absorbed / compared by this toolkit (local clone; not committed here) |
| **harness surface** | Harness-related paths in a subject (`AGENTS.md`, skills, hooks) — not business source |
| **Agent-Kit** | Installer that materializes methodology skills / hook templates into Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — one-command verification for this repo (same as L2 CI) |

## 1. Initialize

One-line install (clone + submodules + git hooks + Agent-Kit + public trusted suite):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Equivalent:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Optional env vars: `TARGET_DIR`, `CLIENT` (`cursor` / `claude` / `codex` / `codex-native` / `skip`), `PLUGIN`.

Or manually step by step:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install git pre-commit hook (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

## 2. Install Agent-Kit (AI tools)

Agent-Kit provides skills and hooks for Cursor / Claude Code / Codex. A bare install includes the curated SP core, a user-invoked Matt library, and a low-frequency advisory router; it does not install global bootstrap skills or vendor hooks.
Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) are **install outputs and are not committed** — always regenerate via install.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate configuration
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Values |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optional) | `lean`, `guided`, `structured`; adjusts advisory density only |

```bash
# Install all four clients (common local bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Inspect or adjust the profile
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided
```

`PLUGIN` remains only as an explicit full-plugin compatibility path for older workflows; it is no longer the recommended installation path.

## 3. (Optional) Wire your own subjects

A public clone can run the trusted suite **green without any private product repos**.  
To sync / import / compare real subjects:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/`, and `comparisons/` stay local and are gitignored.

---

Daily reference — consult as needed.

## Common commands

| Purpose | Command |
|---------|---------|
| Public trusted suite (close the loop / CI) | `bash tools/harness/test-harness.sh` |
| Validate Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Rewrite pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Layout

| Path | Role | In git? |
|------|------|---------|
| `agent-kit/skills` | Open methodology (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Install outputs | ✗ |
| `subjects/manifest.example.yaml` | Public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb products | ✗ |
| `docs/harness/` | Design + ledgers | partial |
| `AGENTS.md` | Constraint SSOT (`CLAUDE.md` → it) | ✓ |

## Docs

- [`docs/README.md`](../README.md) — documentation placement rules
- [`docs/harness/design.md`](../harness/design.md) — this repo's harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — completion definition, blacklist, mechanism map

## License

[MIT](../../LICENSE)
