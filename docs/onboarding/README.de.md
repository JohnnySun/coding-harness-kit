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

> **In einem Satz:** Das hier ist eine Tuningwerkstatt für die *Leitplanken* deines Repos. Auf die Hebebühne kommt nicht dein Business-Code, sondern der **coding harness** drumherum: die Schicht, die eine AI (Cursor, Claude Code, Codex) daran hindert, Abkürzungen zu nehmen, „fertig“ zu schwindeln oder Dinge in git zu schieben, die dort nichts verloren haben.
>
> **Was du davon hast:** Du kannst unsere abgestimmten Methodik-skills und narrensicheren hooks direkt fahren oder dieselben Leitplanken an deine eigenen Repos schrauben. Den Motor (deinen Business-Quellcode) fassen wir nicht an — wir schweißen nur den äußeren Überrollkäfig so lange nach, bis eine AI ihn nicht mehr beiläufig zerknüllen kann.
>
> **Drei Gänge bis zur Abfahrt:** Einzeiler installieren → (Zündung) Agent-Kit ins Regal hängen → (optional) dein eigenes subject vorfahren. Bevor du Feierabend machst, tritt auf `bash tools/harness/test-harness.sh` — leuchtet das Armaturenbrett komplett grün, hat der Wagen die Abnahme bestanden und darf auf die Straße.

## Glossar (Werkstattjargon)

Diese Begriffe tauchen unten ständig auf. Einmal hier lernen, danach benutzt die Anleitung sie einfach.

| Werkstattjargon | Klartext |
|-----------------|----------|
| **coding harness** | Das „Auto“, an dem wir tatsächlich schrauben — die gesamte AI-Entwicklungs-Schutzschicht um ein Produkt-Repo: rules, skills, hooks, trusted suite, ledgers |
| **subject** | Ein Produkt-Repo, das zum Absorbieren / Vergleichen in die Werkstatt gefahren wird; nur lokal geklont und **niemals** hier committet |
| **harness surface** | Die Tuningteile an diesem Auto (`AGENTS.md`, skills, hooks) — nicht der Motor (Business-Quellcode) |
| **Agent-Kit** | Der Regal-Installer — legt Methodik-skills / hook templates in Cursor, Claude Code, Codex usw. ab |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — der Prüfstandlauf, bevor diese Werkstatt etwas ausliefert (dieselbe Anlage wie L2 CI) |

## Schnellste Spur: Annahme per Einzeiler

Ein Befehl erledigt alles: Werkstatt klonen, submodules holen, git hooks installieren, Agent-Kit einräumen und den Wagen direkt auf den Prüfstand schicken (die public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Zu schick? Die klassische Pipe kurbelt denselben Motor an:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Du willst bestimmen, wo alles landet und welcher client verkabelt wird? Setze diese beiden Umgebungsvariablen:

- `TARGET_DIR` — das Installationsverzeichnis
- `CLIENT` — der zu verkabelnde client: `cursor` / `claude` / `codex` / `codex-native`, oder `skip`, um Agent-Kit später einzubauen

Der Einzeiler räumt außerdem Agent-Kit ein und führt die suite für dich aus — **die meisten können hier den Motor abstellen und Feierabend machen**. Du willst einen Gang nach dem anderen montieren, oder der Einzeiler ist unterwegs abgesoffen? Dann nimm unten die manuelle Spur.

## Manuelle Annahme (selbst anschrauben)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Bis hierher ist nur das Werkstatttor offen — die Teilekiste (Agent-Kit) steht noch auf dem Boden. Weiter geht’s.

## Agent-Kit einräumen (Teilekiste an die Wand)

Agent-Kit bringt die Methodik-skills und hooks dieses Repos in deinen Editor / deine CLI. Eine nackte Installation liefert ein abgestimmtes Standardset: lokale Methodik, eine kuratierte Auswahl an SP verification- / TDD- / review-skills, eine Matt library für den bewussten Aufruf sowie einen selten eingeblendeten advisory router.

`using-superpowers` / `brainstorming` bootstrap schmuggelt es **nicht** hinein, und vendor hooks lässt es in Ruhe — beides gibt es nur per Opt-in. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sind **Installationsausgaben und werden nie committet**: Erzeuge sie immer per install neu, statt sie von Hand zu bearbeiten und zurück in git zu mogeln.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Werte |
|-----------|-------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optional) | `lean`, `guided`, `structured`; nur die Dichte der advisory prompts — **ändert niemals die enforcement** |

Der häufigste lokale bootstrap — alle vier clients auf einmal einräumen:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Das Repo-Profil wird immer über die CLI verwaltet (YAML nicht von Hand bearbeiten — das schreit nach Ärger). Um das Setup in ein anderes Repo mitzunehmen, erst exportieren, dann prüfen:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` bleibt nur als ausdrückliche full-plugin-Kompatibilitätsluke für ältere workflows erhalten — empfohlen wird dieser Weg nicht mehr. Die standardmäßige library materialization kopiert weder vendor plugins noch hooks oder skills außerhalb der allowlist.

## Das eigene Auto vorfahren (optional: ein subject verkabeln)

Du willst nur sehen, ob in der Werkstatt alles grün läuft? **Dann verkable gar nichts** — ein public clone kommt ohne private Produkt-Repos aus und fährt die trusted suite trotzdem bis zur grünen Wand.

Nur wenn du ein echtes subject wirklich syncen / importieren / vergleichen willst, führst du diese Zeilen aus:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Präge dir eine Reihenfolge ein: **`manifest.yaml` erstellen → sync → mit `--pin` die Version zurückschreiben → `check-local-absorb.sh`, bis `harness-ready` erreicht ist**. Erst dieses Tor passieren; nur dann dürfen import / compare / score loslegen.

Diese Dinge bleiben lokal und sind bereits gitignored — versuche nicht, sie gewaltsam in einen commit zu drücken; der pre-commit hook schickt sie ohnehin sofort zurück:

- `subjects/manifest.yaml`
- `pin.json` und `checkout/` jedes subjects
- `snapshots/`, `comparisons/`

---

Ab hier hängt die Referenzwand für den Werkstattalltag — nimm dir bei Bedarf ein Werkzeug, du musst nicht alles auf einmal lesen.

## Häufige Befehle (Werkzeugwand)

| Was du vorhast | Auszuführender Befehl |
|----------------|-----------------------|
| Public trusted suite (Prüfstand / CI-förmig) | `bash tools/harness/test-harness.sh` |
| Agent-Kit validieren | `bash tools/harness/agent-kit.sh validate` |
| harness surface syncen | `bash tools/sync/sync-subjects.sh` |
| pin neu schreiben | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Lokale absorb-Bereitschaft | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot importieren | `python3 tools/import/import_subject.py --all` |
| compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| score | `python3 tools/score/score_subject.py <id>` |
| weekly report | `python3 tools/harness/weekly_report.py` |

## Werkstattplan (wo welches Teil liegt)

| Pfad | Bedeutung | In git? |
|------|-----------|---------|
| `agent-kit/skills` | Offene Methodik (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | hooks- / settings-templates pro client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Installationsausgaben | ✗ |
| `subjects/manifest.example.yaml` | Öffentliches Registry-Beispiel | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokale Registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Öffentliche fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | absorb-Produkte | ✗ |
| `docs/harness/` | Design + ledgers | teilweise |
| `AGENTS.md` | SSOT der Einschränkungen (`CLAUDE.md` verweist hierher) | ✓ |

## Handbuchregal (tiefer einsteigen)

- [`docs/README.md`](../README.md) — Regeln für die Dokumentablage
- [`docs/harness/design.md`](../harness/design.md) — harness design dieses Repos
- [`docs/specs/`](../specs/) — Designarchiv
- [`AGENTS.md`](../../AGENTS.md) — Definition von „fertig“, blacklist, Mechanismenübersicht

## Lizenz

[MIT](../../LICENSE) — fahr damit vom Hof, wie du willst; der Fahrzeugbrief liegt bereit.
