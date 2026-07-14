# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
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
  <strong>Nederlands</strong> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **In één zin:** dit is een chopshop voor de *vangrails* van je repo. Op de brug staat niet je businesscode, maar de **coding harness** eromheen: de laag die voorkomt dat een AI (Cursor, Claude Code, Codex) bochten afsnijdt, ten onrechte „klaar” roept of rommel in git duwt die daar niet thuishoort.
>
> **Wat heb jij eraan:** rijd meteen weg met onze afgestelde methodologie-skills en foolproof hooks, of schroef dezelfde vangrails op je eigen repo's. We komen niet aan de motor (je businessbroncode); we lassen alleen de rolkooi eromheen totdat een AI hem niet meer achteloos in de kreukels rijdt.
>
> **Drie versnellingen om weg te komen:** installatie in één regel → (contact aan) Agent-Kit in het rek → (optioneel) je eigen subject binnenrijden. Trap vóór sluitingstijd `bash tools/harness/test-harness.sh` in: alle lampjes groen betekent goedgekeurd en straatlegaal.

## Woordenlijst (werkplaatstaal)

Deze woorden kom je hieronder overal tegen. Leer ze hier één keer; daarna gebruikt de handleiding ze zonder omhaal.

| Werkplaatstaal | Gewoon Nederlands |
|----------------|-------------------|
| **coding harness** | De „auto” waaraan we echt sleutelen: de volledige AI-ontwikkelvangrail rond een productrepo — rules, skills, hooks, trusted suite en ledgers |
| **subject** | Een productrepo die de werkplaats in rijdt om te worden geabsorbeerd / vergeleken; alleen lokaal gecloned en **nooit** hier gecommit |
| **harness surface** | De te tunen panelen van die auto (`AGENTS.md`, skills, hooks), niet de motor (businessbroncode) |
| **Agent-Kit** | De rek-installer: zet methodologie-skills / hook-templates klaar voor Cursor, Claude Code, Codex enzovoort |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — de rollenbank voordat deze garage iets aflevert (dezelfde installatie als L2 CI) |

## Snelste rijstrook: intake in één regel

Eén commando doet alles: de garage clonen, submodules ophalen, git hooks installeren, Agent-Kit in het rek hangen en meteen door naar de rollenbank (de public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Te modern? De ouderwetse pipe start dezelfde motor:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Wil je bepalen waar hij landt en voor wie de bedrading wordt gelegd? Stel deze twee omgevingsvariabelen in:

- `TARGET_DIR` — de installatiemap
- `CLIENT` — de aan te sluiten client: `cursor` / `claude` / `codex` / `codex-native`, of `skip` om Agent-Kit voor later te bewaren

De one-liner hangt Agent-Kit ook op en draait de suite voor je — **de meeste mensen kunnen hier de motor uitzetten en naar huis**. Wil je versnelling voor versnelling monteren, of sloeg de one-liner onderweg af? Neem dan hieronder de handmatige rijstrook.

## Handmatige intake (zelf monteren)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

De garagedeur staat nu alleen nog maar open; de onderdelenkist (Agent-Kit) staat nog op de vloer. Ga dus door.

## Agent-Kit ophangen (onderdelenkist tegen de muur)

Agent-Kit zet de methodologie-skills en hooks van deze repo in je editor / CLI. Een kale installatie levert een afgestelde standaardset: lokale methodologie, een selectie SP-skills voor verification / TDD / review, een Matt-library die je bewust aanroept en een laagfrequente advisory router.

Hij smokkelt geen `using-superpowers` / `brainstorming`-bootstrap binnen en laat vendor hooks met rust; die zijn alleen opt-in. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) zijn **installatie-uitvoer en worden nooit gecommit**. Genereer ze altijd opnieuw via install in plaats van ze met de hand te verbouwen en git in te smokkelen.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Waarden |
|-----------|---------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optioneel) | `lean`, `guided`, `structured`; alleen de dichtheid van advisory prompts — raakt enforcement **nooit** |

De gebruikelijkste lokale bootstrap hangt alle vier clients tegelijk op:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Het repo-profile loopt altijd via de CLI (de YAML met de hand bewerken is vragen om problemen). Wil je de configuratie meenemen naar een andere repo, exporteer hem dan eerst en controleer hem daarna:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` bestaat alleen nog als expliciet full-plugin-compatibiliteitsluik voor oudere workflows; het is niet meer de aanbevolen route. De standaardmaterialisatie van de library kopieert geen vendor plugins, hooks of skills buiten de allowlist.

## Rijd je eigen auto binnen (optioneel: subject aansluiten)

Wil je alleen zien of alle lampjes van de garage groen worden? **Sluit niets aan.** Een public clone gebruikt nul private productrepo's en draait de trusted suite toch volledig groen.

Voer deze regels alleen uit als je echt een subject wilt syncen / importeren / vergelijken:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Onthoud één volgorde: **`manifest.yaml` maken → sync → met `--pin` de versie terugschrijven → `check-local-absorb.sh` tot alles `harness-ready` is**. Eerst door die poort; pas daarna mogen import / compare / score rijden.

Dit blijft lokaal en is al gitignored. Probeer het niet een commit in te wringen; de pre-commit hook stuurt het direct terug:

- `subjects/manifest.yaml`
- `pin.json` en `checkout/` van ieder subject
- `snapshots/`, `comparisons/`

---

Hieronder hangt de dagelijkse gereedschapswand. Pak wat je nodig hebt; je hoeft hem niet in één keer uit je hoofd te leren.

## Veelgebruikte commando's (gereedschapswand)

| Wat je wilt | Uit te voeren regel |
|-------------|---------------------|
| Public trusted suite (rollenbank / CI-vorm) | `bash tools/harness/test-harness.sh` |
| Agent-Kit valideren | `bash tools/harness/agent-kit.sh validate` |
| Harness surface syncen | `bash tools/sync/sync-subjects.sh` |
| Pin herschrijven | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Lokale absorb-gereedheid | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot importeren | `python3 tools/import/import_subject.py --all` |
| Compare-rapport maken | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score uitvoeren | `python3 tools/score/score_subject.py <id>` |
| Wekelijks rapport maken | `python3 tools/harness/weekly_report.py` |

## Plattegrond (waar ieder onderdeel ligt)

| Pad | Wat het is | In git? |
|-----|------------|---------|
| `agent-kit/skills` | Open methodologie (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings-templates per client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Installatie-uitvoer | ✗ |
| `subjects/manifest.example.yaml` | Openbaar registry-voorbeeld | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokale registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Openbare fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb-producten | ✗ |
| `docs/harness/` | Design + ledgers | gedeeltelijk |
| `AGENTS.md` | SSOT voor beperkingen (`CLAUDE.md` verwijst hiernaar) | ✓ |

## Werkplaatshandboek (meer diepgang)

- [`docs/README.md`](../README.md) — regels voor documentatieplaatsing
- [`docs/harness/design.md`](../harness/design.md) — harness-design van deze repo
- [`docs/specs/`](../specs/) — designarchief
- [`AGENTS.md`](../../AGENTS.md) — voltooiingsdefinitie, blacklist en mechanismeoverzicht

## Licentie

[MIT](../../LICENSE) — rijd ermee weg zoals je wilt; het kentekenbewijs ligt klaar.
