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

> **Deze werkplaats werkt aan jouw auto: de coding harness.** Dit is de beschermlaag voor AI-ontwikkeling rond een productrepository. Die productrepository — de subject — bezit de auto; de businesscode is de motor, en die motor laten we dicht.
> De korte route: voer de installatie van één regel uit → installeer Agent-Kit voor Cursor, Claude Code of Codex → koppel desgewenst een echte subject en voer daarna sync, pin en de controle op `harness-ready` uit. Nieuwe onderdelen gaan nog steeds op de testbank. Lakinspectie is geen testplan.

| Term | Betekenis (werkplaatsvergelijking) |
|------|---------|
| **coding harness** | Jouw auto: de beschermlaag voor AI-ontwikkeling rond een productrepository (rules, skills, hooks, trusted suite en ledgers) |
| **subject** | De productrepository die de auto bezit (lokale clone; wordt hier niet gecommit) |
| **harness surface** | De onderdelenruimte: `AGENTS.md`, skills, hooks en vergelijkbare beschermingsbestanden; geen businesscode |
| **Agent-Kit** | Het onderdelenrek: materialiseert methodologische skills en hook-templates in Cursor, Claude Code, Codex enzovoort |
| **public trusted suite** | De testbank: `bash tools/harness/test-harness.sh` (hetzelfde als L2 CI) |

## 1. Binnenkomst (initialiseren)

De snelste werkplaatsingang is de installer van één regel. Deze clonet de repository, initialiseert submodules, installeert git hooks en Agent-Kit, en voert daarna de public trusted suite uit:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Gebruik de gelijkwaardige pipe-vorm als je shell geen process substitution ondersteunt:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

De optionele omgevingsvariabelen zijn `TARGET_DIR` en `CLIENT`. Stel `CLIENT` in op `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Als handmatig alternatief, of om elke stap te volgen:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Als je --recurse-submodules bent vergeten
git submodule update --init --recursive

# Installeer de L1-veiligheidscontrole (blokkeert private trees; voert de suite uit wanneer nodig)
bash tools/harness/install-git-hooks.sh
```

Je hoort nu in `los-santos-customs/` te staan, met geïnitialiseerde submodules en geïnstalleerde git hooks. De route van één regel installeert ook Agent-Kit voor de gekozen client en voert de public suite uit. Ging je handmatig te werk, ga dan verder met §2. Een handgeschakelde versnellingsbak vraagt één extra stap; uit nostalgie is dat niet.

## 2. Onderdelen monteren (Agent-Kit)

Agent-Kit installeert de skills en hooks van deze werkplaats in je editor of CLI. Een kale installatie levert deze bewust gekozen standaardinstellingen:

- lokale methodologie;
- geselecteerde SP-skills voor verificatie, TDD en review;
- een door de gebruiker aangeroepen Matt-library;
- een laagfrequente adviserende router.

De bootstrap `using-superpowers` / `brainstorming` en hooks van leveranciers worden niet geïnstalleerd. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) zijn installatie-uitvoer en worden niet gecommit. Genereer ze opnieuw met install; gegenereerde bestanden hebben geen plaatwerk nodig.

```bash
# Installeer voor een specifieke client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Controleer of de onderdelen goed vastzitten
bash tools/harness/agent-kit.sh validate

# Bekijk een voorbeeldinstallatie (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Waarden |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (optioneel) | `lean`, `guided`, `structured`; past alleen de adviesdichtheid aan |

```bash
# Installeer alle vier clients (gebruikelijke lokale bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Bekijk of wijzig het repository-profile (agents schrijven uitsluitend via de CLI)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Exporteer een overdraagbaar profile naar een subject; koppel fragments en controleer daarna
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` blijft alleen bestaan als expliciet compatibiliteitspad naar de volledige plugin voor oudere workflows. Het is niet langer het aanbevolen installatiepad. De standaardmaterialisatie van de library kopieert geen plugins, hooks of skills van leveranciers buiten de allowlist; het onderdelenrek heeft niet voor niets een inventaris.

## 3. (Optioneel) Rijd je eigen auto binnen

Een publieke clone kan de public trusted suite zonder private productrepositories uitvoeren. Koppel alleen een klantauto aan je lokale werkplaats wanneer je een echte subject wilt synchroniseren, importeren of vergelijken:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Bewerk de remotes zodat ze verwijzen naar repositories waar je toegang toe hebt, en voer daarna uit:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # lokale harness-ready (niet de public suite)
```

De volgorde is belangrijk:

1. Maak `subjects/manifest.yaml` op basis van het voorbeeld. Laat de remotes verwijzen naar repositories waar je toegang toe hebt.
2. Voer sync uit om de harness surface van elke subject op te halen.
3. Gebruik `<id> --pin` om precies de revisie vast te leggen die je wilt evalueren.
4. Voer de lokale absorb-controle uit. Een geslaagde subject is `harness-ready`; pas daarna kunnen import, compare en score betrouwbare resultaten opleveren.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` en `comparisons/` zijn klantauto's en werkorders. Ze blijven lokaal, worden door git genegeerd en komen nooit in de publieke showroom. Dat is geen geheimhouding, maar eenvoudig sleutelbeheer.

---

De auto rijdt nu op eigen kracht. De rest is werkplaatsreferentie.

## Veelgebruikte commando's

| Doel | Commando |
|---------|---------|
| Public trusted suite (sluit de cyclus / CI) | `bash tools/harness/test-harness.sh` |
| Agent-Kit valideren | `bash tools/harness/agent-kit.sh validate` |
| Harness surface synchroniseren | `bash tools/sync/sync-subjects.sh` |
| Pin herschrijven | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Lokale absorb-gereedheid | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot importeren | `python3 tools/import/import_subject.py --all` |
| Compare-rapport maken | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score uitvoeren | `python3 tools/score/score_subject.py <id>` |
| Wekelijks rapport maken | `python3 tools/harness/weekly_report.py` |

## Indeling

| Pad | Rol | In git? |
|------|------|---------|
| `agent-kit/skills` | Open methodologie (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates voor client hooks/settings | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Installatie-uitvoer | ✗ |
| `subjects/manifest.example.yaml` | Voorbeeld van publieke registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokale registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Publieke fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb-producten | ✗ |
| `docs/harness/` | Design + ledgers | gedeeltelijk |
| `AGENTS.md` | SSOT voor beperkingen (`CLAUDE.md` → dit bestand) | ✓ |

## Documentatie

- [`docs/README.md`](../README.md) — regels voor documentatieplaatsing
- [`docs/harness/design.md`](../harness/design.md) — harness-design van deze repository
- [`docs/specs/`](../specs/) — designarchief
- [`AGENTS.md`](../../AGENTS.md) — voltooiingsdefinitie, blacklist en mechanismeoverzicht

## Licentie

[MIT](../../LICENSE)
