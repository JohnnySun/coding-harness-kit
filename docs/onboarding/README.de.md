# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <strong>Deutsch</strong> |
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

> **Diese Werkstatt arbeitet an deinem Auto: dem coding harness.** Das ist die Schutzschicht für AI-Entwicklung rund um ein Produkt-Repository. Dieses Produkt-Repository – das subject – besitzt das Auto. Der Business-Quellcode ist der Motor, und die Motorhaube bleibt zu.
> Die kurze Route: Einzeiler für die Annahme ausführen → Agent-Kit für Cursor, Claude Code oder Codex installieren → optional ein echtes subject anbinden, dann syncen, pinnen und `harness-ready` prüfen. Neue Teile kommen weiterhin auf den Prüfstand, die public trusted suite. Eine Lackkontrolle ist kein Testplan.

| Begriff | Bedeutung (Werkstattzuordnung) |
|------|---------|
| **coding harness** | Dein Auto: die Schutzschicht für AI-Entwicklung rund um ein Produkt-Repository (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Das Produkt-Repository, dem das Auto gehört (lokaler clone; wird hier nicht committet) |
| **harness surface** | Die Teilebucht: `AGENTS.md`, skills, hooks und ähnliche Schutzdateien; kein Business-Quellcode |
| **Agent-Kit** | Das Teilelager: bringt Methodik-skills / hook templates in Cursor, Claude Code, Codex usw. |
| **public trusted suite** | Der Prüfstand: `bash tools/harness/test-harness.sh` (identisch mit L2 CI) |

## 1. Fahrzeugannahme (initialisieren)

Am schnellsten geht es mit dem Einzeiler. Er clont das Repository, initialisiert submodules, installiert git hooks und Agent-Kit und führt anschließend die public trusted suite aus:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Falls deine Shell keine process substitution unterstützt, verwende die gleichwertige Pipe-Variante:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Optionale Umgebungsvariablen sind `TARGET_DIR` und `CLIENT`. Setze `CLIENT` auf `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Als manuelle Ausweichroute – oder wenn du jede Drehung des Schraubenschlüssels sehen willst:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Du solltest dich nun in `los-santos-customs/` befinden; die submodules sind initialisiert und die git hooks installiert. Der Einzeiler installiert außerdem Agent-Kit für den gewählten client und führt die public suite aus. Nach der manuellen Route geht es mit §2 weiter. Ein Schaltgetriebe hat einen zusätzlichen Schritt; Nostalgie ist nicht der Grund.

## 2. Teile anschrauben (Agent-Kit)

Agent-Kit installiert die skills und hooks dieser Werkstatt in deinem Editor oder CLI. Eine Installation ohne weitere Optionen liefert diese bewusst gewählten Standards:

- lokale Methodik;
- kuratierte SP verification-, TDD- und review-skills;
- eine vom Benutzer aufgerufene Matt library;
- einen selten eingeblendeten advisory router.

Der `using-superpowers` / `brainstorming` bootstrap und vendor hooks werden nicht installiert. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sind Installationsausgaben und werden nicht committet. Erzeuge sie per install neu; generierte Dateien brauchen keine Karosseriearbeit.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Werte |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optional) | `lean`, `guided`, `structured`; ändert nur die Dichte der Hinweise |

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

`PLUGIN` bleibt nur als ausdrücklich gewählter full-plugin-Kompatibilitätspfad für ältere workflows bestehen. Es ist nicht mehr der empfohlene Installationsweg. Die standardmäßige library materialization kopiert keine vendor plugins, hooks oder skills außerhalb der allowlist. Das Teilelager führt nicht ohne Grund Inventar.

## 3. (Optional) Das eigene Auto vorfahren

Ein public clone kann die public trusted suite ohne private Produkt-Repositories ausführen. Binde ein Kundenauto nur dann an die lokale Werkstatt, wenn du ein echtes subject syncen, importieren oder vergleichen musst:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

Die Reihenfolge ist wichtig:

1. Erstelle `subjects/manifest.yaml` aus dem Beispiel. Richte die remotes auf Repositories, auf die du zugreifen kannst.
2. Führe sync aus, um die harness surface jedes subjects abzurufen.
3. Zeichne mit `<id> --pin` die genaue revision auf, die du bewerten willst.
4. Führe den local absorb check aus. Ein erfolgreich geprüftes subject ist `harness-ready`; erst dann liefern import, compare und score vertrauenswürdige Ergebnisse.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` und `comparisons/` sind Kundenautos und Arbeitsaufträge. Sie bleiben lokal, werden von git ignoriert und gelangen nie in den public showroom. Das ist keine Geheimniskrämerei, sondern grundlegende Schlüsselverwaltung.

---

Das Auto fährt jetzt aus eigener Kraft. Der Rest ist die Referenz für die Servicebucht.

## Häufige Befehle

| Zweck | Befehl |
|---------|---------|
| Public trusted suite (Loop schließen / CI) | `bash tools/harness/test-harness.sh` |
| Agent-Kit validieren | `bash tools/harness/agent-kit.sh validate` |
| harness surface syncen | `bash tools/sync/sync-subjects.sh` |
| pin neu schreiben | `bash tools/sync/sync-subjects.sh <id> --pin` |
| local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot importieren | `python3 tools/import/import_subject.py --all` |
| compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| score | `python3 tools/score/score_subject.py <id>` |
| weekly report | `python3 tools/harness/weekly_report.py` |

## Layout

| Pfad | Rolle | In git? |
|------|------|---------|
| `agent-kit/skills` | Offene Methodik (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Installationsausgaben | ✗ |
| `subjects/manifest.example.yaml` | Öffentliches Registry-Beispiel | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokale Registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Öffentliche fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | absorb-Produkte | ✗ |
| `docs/harness/` | Design + ledgers | teilweise |
| `AGENTS.md` | SSOT der Einschränkungen (`CLAUDE.md` → it) | ✓ |

## Dokumentation

- [`docs/README.md`](../README.md) — Regeln für die Dokumentablage
- [`docs/harness/design.md`](../harness/design.md) — harness design dieses Repositories
- [`docs/specs/`](../specs/) — Designarchiv
- [`AGENTS.md`](../../AGENTS.md) — Definition von „fertig“, blacklist, Mechanismenübersicht

## Lizenz

[MIT](../../LICENSE)
