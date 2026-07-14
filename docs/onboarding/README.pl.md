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
  <a href="README.nl.md">Nederlands</a> |
  <strong>Polski</strong> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **Ten warsztat zajmuje się Twoim samochodem: coding harness.** To warstwa zabezpieczeń procesu tworzenia oprogramowania z AI otaczająca repozytorium produktu. Repozytorium produktu — subject — jest właścicielem samochodu; kod biznesowy to silnik, którego nie otwieramy.
> Krótka trasa: uruchom instalację jednym poleceniem → zainstaluj Agent-Kit dla Cursor, Claude Code lub Codex → opcjonalnie podłącz rzeczywisty subject, a następnie wykonaj sync, pin i sprawdź `harness-ready`. Nowe części nadal trafiają na hamownię. Oględziny lakieru nie są planem testów.

| Termin | Znaczenie (odpowiednik w warsztacie) |
|------|---------|
| **coding harness** | Twój samochód: warstwa zabezpieczeń procesu tworzenia oprogramowania z AI wokół repozytorium produktu (rules, skills, hooks, trusted suite i ledgers) |
| **subject** | Repozytorium produktu będące właścicielem samochodu (lokalny clone; nie jest tutaj commitowane) |
| **harness surface** | Stanowisko z częściami: `AGENTS.md`, skills, hooks i podobne pliki zabezpieczeń; nie kod biznesowy |
| **Agent-Kit** | Regał z częściami: materializuje metodologiczne skills i templates hooks w Cursor, Claude Code, Codex itd. |
| **public trusted suite** | Hamownia: `bash tools/harness/test-harness.sh` (to samo co L2 CI) |

## 1. Przyjęcie (inicjalizacja)

Najszybszym wjazdem do warsztatu jest instalator uruchamiany jednym poleceniem. Klonuje repozytorium, inicjalizuje submodules, instaluje git hooks i Agent-Kit, a następnie uruchamia public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Jeśli Twój shell nie obsługuje process substitution, użyj równoważnej formy z pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Opcjonalne zmienne środowiskowe to `TARGET_DIR` i `CLIENT`. Ustaw `CLIENT` na `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Ręczna ścieżka awaryjna lub sposób na obserwowanie każdego kroku:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Jeśli pominięto --recurse-submodules
git submodule update --init --recursive

# Zainstaluj kontrolę bezpieczeństwa L1 (blokuje prywatne drzewa; w razie potrzeby uruchamia suite)
bash tools/harness/install-git-hooks.sh
```

Teraz katalogiem roboczym powinien być `los-santos-customs/`, z zainicjalizowanymi submodules i zainstalowanymi git hooks. Ścieżka jednego polecenia instaluje także Agent-Kit dla wybranego klienta i uruchamia public suite. Po instalacji ręcznej przejdź do §2. Ręczna skrzynia biegów wymaga jednego dodatkowego kroku; nie chodzi tu o nostalgię.

## 2. Montaż części (Agent-Kit)

Agent-Kit instaluje skills i hooks tego warsztatu w edytorze lub CLI. Instalacja bez dodatkowych opcji zapewnia następujące świadomie wybrane ustawienia domyślne:

- lokalną metodologię;
- wybrane skills SP do weryfikacji, TDD i review;
- bibliotekę Matt uruchamianą przez użytkownika;
- rzadko aktywowany router doradczy.

Nie instaluje bootstrap `using-superpowers` / `brainstorming` ani hooks dostawców. Drzewa klientów (`.cursor` / `.claude` / `.codex` / `.agents`) są wynikami instalacji i nie są commitowane. Odtwarzaj je za pomocą install; wygenerowane pliki nie potrzebują prac blacharskich.

```bash
# Zainstaluj dla konkretnego klienta
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Sprawdź, czy części są prawidłowo osadzone
bash tools/harness/agent-kit.sh validate

# Wyświetl podgląd instalacji (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametr | Wartości |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcjonalny) | `lean`, `guided`, `structured`; zmienia wyłącznie intensywność porad |

```bash
# Zainstaluj wszystkich czterech klientów (typowy lokalny bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Wyświetl lub zmień profile repozytorium (agents zapisują tylko przez CLI)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Wyeksportuj przenośny profile do subject; podłącz fragments, a następnie sprawdź
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` pozostaje jedynie jawną ścieżką zgodności z pełnym pluginem dla starszych workflows. Nie jest już zalecanym sposobem instalacji. Domyślna materializacja biblioteki nie kopiuje plugins, hooks ani skills dostawców spoza allowlist; regał z częściami nie bez powodu ma spis zawartości.

## 3. (Opcjonalnie) Wprowadź własny samochód

Publiczny clone może uruchomić public trusted suite bez prywatnych repozytoriów produktów. Podłącz samochód klienta do lokalnego stanowiska tylko wtedy, gdy musisz wykonać sync, import lub compare rzeczywistego subject:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Zmień remotes na repozytoria, do których masz dostęp, a następnie:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # lokalne harness-ready (nie public suite)
```

Kolejność ma znaczenie:

1. Utwórz `subjects/manifest.yaml` na podstawie przykładu. Skieruj jego remotes do repozytoriów, do których masz dostęp.
2. Uruchom sync, aby pobrać harness surface każdego subject.
3. Użyj `<id> --pin`, aby zapisać dokładną rewizję przeznaczoną do oceny.
4. Uruchom lokalną kontrolę absorb. Subject, który ją przejdzie, jest `harness-ready`; dopiero wtedy import, compare i score mogą dać wiarygodne wyniki.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` i `comparisons/` to samochody klientów i zlecenia serwisowe. Pozostają lokalne, są ignorowane przez git i nigdy nie trafiają do publicznego salonu. To nie tajemnica, lecz podstawowa kontrola kluczy.

---

Samochód porusza się już o własnych siłach. Pozostała część to dokumentacja warsztatowa.

## Częste polecenia

| Cel | Polecenie |
|---------|---------|
| Public trusted suite (zamknięcie cyklu / CI) | `bash tools/harness/test-harness.sh` |
| Walidacja Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Ponowny zapis pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Lokalna gotowość absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Raport compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Raport tygodniowy | `python3 tools/harness/weekly_report.py` |

## Układ

| Ścieżka | Rola | W git? |
|------|------|---------|
| `agent-kit/skills` | Otwarta metodologia (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates hooks/settings klientów | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Wyniki instalacji | ✗ |
| `subjects/manifest.example.yaml` | Przykład publicznego registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokalne registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Publiczne fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produkty absorb | ✗ |
| `docs/harness/` | Design + ledgers | częściowo |
| `AGENTS.md` | SSOT ograniczeń (`CLAUDE.md` → ten plik) | ✓ |

## Dokumentacja

- [`docs/README.md`](../README.md) — zasady umieszczania dokumentacji
- [`docs/harness/design.md`](../harness/design.md) — design harness tego repozytorium
- [`docs/specs/`](../specs/) — archiwum design
- [`AGENTS.md`](../../AGENTS.md) — definicja ukończenia, blacklist i mapa mechanizmów

## Licencja

[MIT](../../LICENSE)
