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

> **This shop works on your car: the coding harness.** It is the AI-development guardrail layer around a product repo. That product repo—the subject—owns the car; its business source is the engine, and we leave the engine closed.
> The short route: run the one-line intake → install Agent-Kit for Cursor, Claude Code, or Codex → optionally connect a real subject, then sync, pin, and check `harness-ready`. New parts still go on the dyno. Paint inspection is not a test plan.

| Term | Meaning (shop mapping) |
|------|---------|
| **coding harness** | Your car: the AI-dev guardrail layer around a product repo (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | The product repo that owns the car (local clone; not committed here) |
| **harness surface** | The parts bay: `AGENTS.md`, skills, hooks, and similar guardrail files; not business source |
| **Agent-Kit** | Parts rack: materializes methodology skills / hook templates into Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | Dyno: `bash tools/harness/test-harness.sh` (same as L2 CI) |

## 1. Intake (initialize)

The fastest bay is the one-line installer. It clones the repo, initializes submodules, installs git hooks and Agent-Kit, then runs the public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

If your shell does not support process substitution, use the equivalent pipe form:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Optional environment variables are `TARGET_DIR` and `CLIENT`. Set `CLIENT` to `cursor` / `claude` / `codex` / `codex-native` / `skip`.

For a manual fallback, or to watch each wrench turn:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

You should now be inside `los-santos-customs/` with initialized submodules and installed git hooks. The one-line route also installs Agent-Kit for your selected client and runs the public suite. If you took the manual route, continue to §2. Manual transmissions have one extra step; this one is not nostalgic.

## 2. Bolt on parts (Agent-Kit)

Agent-Kit installs this shop's skills and hooks into your editor or CLI. A bare install provides these opinionated defaults:

- local methodology;
- curated SP verification, TDD, and review skills;
- a user-invoked Matt library;
- a low-frequency advisory router.

It does not install the `using-superpowers` / `brainstorming` bootstrap or vendor hooks. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) are install outputs and are not committed. Regenerate them with install; generated files do not need bodywork.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
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

# Inspect or adjust the repo profile (agents write via CLI only)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire fragments, then check
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` remains only as an explicit full-plugin compatibility path for older workflows. It is no longer the recommended installation path. Default library materialization does not copy vendor plugins, hooks, or skills outside the allowlist; the parts rack has an inventory for a reason.

## 3. (Optional) Drive your own car in

A public clone can run the public trusted suite without any private product repos. Connect a customer car to your local bay only when you need to sync, import, or compare a real subject:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

Order matters:

1. Create `subjects/manifest.yaml` from the example. Point its remotes at repos you can access.
2. Run sync to fetch each subject's harness surface.
3. Use `<id> --pin` to record the exact revision you intend to evaluate.
4. Run the local absorb check. A passing subject is `harness-ready`; only then can import, compare, and score produce trustworthy results.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/`, and `comparisons/` are customer cars and work orders. They remain local, are gitignored, and never enter the public showroom. That is not secrecy; it is basic key control.

---

The car now moves under its own power. The rest is service-bay reference.

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
