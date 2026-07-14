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

> **W jednym zdaniu:** to chop shop dla *zabezpieczeń* Twojego repo. Na podnośnik nie trafia kod biznesowy, lecz otaczający go **coding harness** — warstwa, która nie pozwala AI (Cursor, Claude Code, Codex) iść na skróty, udawać, że „gotowe”, ani wciskać do git rzeczy, których nie wolno commitować.
>
> **Co z tego masz:** możesz od razu jeździć z naszymi podkręconymi skills metodologicznymi i odpornymi na pomyłki hooks albo przykręcić te same zabezpieczenia do własnych repozytoriów. Silnika (kodu biznesowego) nie dotykamy — spawamy tylko zewnętrzną klatkę, aż AI nie złoży jej przy pierwszym zakręcie.
>
> **Trzy biegi do startu:** instalacja jednym poleceniem → (zapłon) Agent-Kit na regał → (opcjonalnie) wprowadź własny subject. Przed zamknięciem warsztatu uruchom `bash tools/harness/test-harness.sh` — komplet zielonych kontrolek oznacza zaliczony przegląd i dopuszczenie do ruchu.

## Słowniczek (żargon warsztatowy)

Poniższe określenia pojawiają się wszędzie. Poznaj je raz; dalej dokumentacja używa ich bez ponownego objaśniania.

| Żargon | Po ludzku |
|--------|-----------|
| **coding harness** | „Samochód”, przy którym naprawdę pracujemy — cała warstwa zabezpieczeń rozwoju z AI wokół repozytorium produktu: rules, skills, hooks, trusted suite, ledgers |
| **subject** | Repozytorium produktu wprowadzane na stanowisko do absorb / compare; clone tylko lokalny, **nigdy** tutaj commitowany |
| **harness surface** | Panele do modyfikacji w tym samochodzie (`AGENTS.md`, skills, hooks), nie silnik (kod biznesowy) |
| **Agent-Kit** | Instalator regału — umieszcza skills metodologiczne / hook templates w Cursor, Claude Code, Codex itd. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — przejazd na hamowni przed wydaniem czegokolwiek z warsztatu (ten sam układ co L2 CI) |

## Najszybszy pas: przyjęcie jednym poleceniem

Jedno polecenie robi wszystko: klonuje warsztat, pobiera submodules, instaluje git hooks, ustawia Agent-Kit na regale i od razu uruchamia hamownię (public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Za nowocześnie? Stary dobry pipe odpala ten sam silnik:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Chcesz wybrać miejsce instalacji i klienta do podłączenia? Ustaw dwie zmienne środowiskowe:

- `TARGET_DIR` — katalog instalacji
- `CLIENT` — podłączany client: `cursor` / `claude` / `codex` / `codex-native`; albo `skip`, by zostawić Agent-Kit na później

One-liner ustawia też Agent-Kit i uruchamia suite — **większość osób może tutaj zgasić silnik i zamknąć warsztat**. Jeśli chcesz montować po jednym biegu albo one-liner zgasł w trasie, wybierz poniżej ścieżkę ręczną.

## Przyjęcie ręczne (samodzielny montaż)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Na tym etapie brama warsztatu jest dopiero otwarta — skrzynia z częściami (Agent-Kit) nadal stoi na podłodze. Jedziemy dalej.

## Ustaw Agent-Kit na regale (skrzynia z częściami na ścianę)

Agent-Kit umieszcza skills metodologiczne i hooks tego repozytorium w edytorze / CLI. Podstawowa instalacja daje dostrojony zestaw domyślny: lokalną metodologię, wybrane skills SP do verification / TDD / review, bibliotekę Matt wywoływaną świadomie oraz rzadko odzywający się advisory router.

Nie przemyca bootstrap `using-superpowers` / `brainstorming` i nie rusza vendor hooks — te są wyłącznie opt-in. Drzewa klientów (`.cursor` / `.claude` / `.codex` / `.agents`) to **wyniki instalacji, których nigdy nie commitujemy**. Zawsze odtwarzaj je przez install, zamiast ręcznie klepać blachę i przemycać ją do git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametr | Wartości |
|----------|----------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcjonalny) | `lean`, `guided`, `structured`; tylko gęstość advisory prompts — **nigdy** nie zmienia enforcement |

Najpopularniejszy lokalny bootstrap montuje czterech klientów naraz:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Profile repozytorium zawsze obsługuj przez CLI (ręczna edycja YAML to proszenie się o kłopoty). Aby przenieść konfigurację do innego repozytorium, najpierw ją wyeksportuj, a potem sprawdź:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` pozostał wyłącznie jako jawny właz zgodności z full-plugin dla starszych workflows — nie jest już zalecaną drogą. Domyślna materializacja library nie kopiuje vendor plugins, hooks ani żadnych skills spoza allowlist.

## Wprowadź własny samochód (opcjonalnie: podłącz subject)

Chcesz tylko sprawdzić, czy cały warsztat świeci na zielono? **Niczego nie podłączaj.** Publiczny clone nie wymaga żadnego prywatnego repozytorium produktu, a mimo to uruchamia trusted suite do pełnej zieleni.

Poniższe polecenia uruchom tylko wtedy, gdy naprawdę chcesz wykonać sync / import / compare rzeczywistego subject:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Zapamiętaj jedną kolejność: **utwórz `manifest.yaml` → sync → zapisz wersję przez `--pin` → uruchamiaj `check-local-absorb.sh`, aż będzie `harness-ready`**. Najpierw przejdź tę bramkę; dopiero potem import / compare / score mogą ruszyć.

Poniższe elementy zostają lokalnie i są już gitignored. Nie próbuj wciskać ich do commita — pre-commit hook zawróci je na miejscu:

- `subjects/manifest.yaml`
- `pin.json` i `checkout/` każdego subject
- `snapshots/`, `comparisons/`

---

Poniżej znajduje się codzienna ściana z narzędziami. Sięgaj po to, czego potrzebujesz; nie musisz czytać wszystkiego naraz.

## Częste polecenia (ściana z narzędziami)

| Co chcesz zrobić | Polecenie |
|------------------|-----------|
| Public trusted suite (hamownia / kształt CI) | `bash tools/harness/test-harness.sh` |
| Walidacja Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Ponowny zapis pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Lokalna gotowość absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Raport compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Raport tygodniowy | `python3 tools/harness/weekly_report.py` |

## Plan warsztatu (gdzie leży każda część)

| Ścieżka | Co to jest | W git? |
|---------|------------|--------|
| `agent-kit/skills` | Otwarta metodologia (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings templates dla poszczególnych klientów | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Wyniki instalacji | ✗ |
| `subjects/manifest.example.yaml` | Przykład publicznego registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Lokalne registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Publiczne fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produkty absorb | ✗ |
| `docs/harness/` | Design + ledgers | częściowo |
| `AGENTS.md` | SSOT ograniczeń (`CLAUDE.md` wskazuje tutaj) | ✓ |

## Instrukcje warsztatowe (więcej szczegółów)

- [`docs/README.md`](../README.md) — zasady umieszczania dokumentacji
- [`docs/harness/design.md`](../harness/design.md) — design harness tego repozytorium
- [`docs/specs/`](../specs/) — archiwum design
- [`AGENTS.md`](../../AGENTS.md) — definicja ukończenia, blacklist i mapa mechanizmów

## Licencja

[MIT](../../LICENSE) — odjedź nim, jak chcesz; dokumenty są w schowku.
