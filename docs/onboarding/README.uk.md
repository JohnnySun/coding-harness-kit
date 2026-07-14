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
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <strong>Українська</strong>
</h3>

> **Одним рядком:** це тюнінг-ательє для *захисних огорож* вашого репозиторію. На підіймач потрапляє не бізнес-код, а **coding harness** навколо нього — шар, що не дає AI (Cursor, Claude Code, Codex) зрізати кути, удавати, ніби «все готово», або пхати в git те, чого там бути не повинно.
>
> **Що ви отримуєте:** можете одразу їхати з нашими налаштованими methodology skills і захищеними від дурня hooks або прикрутити такі самі огорожі до власних репозиторіїв. Двигун — ваш бізнес-код — ми не чіпаємо; лише зварюємо зовнішній каркас так міцно, щоб AI не міг ненароком зім'яти кузов.
>
> **Три передачі до старту:** встановлення одним рядком → (запалювання) поставити Agent-Kit на стелаж → (необов'язково) загнати власний subject. Перед закриттям зміни запустіть `bash tools/harness/test-harness.sh`: усі індикатори зелені — техогляд пройдено, можна на дорогу.

## Словник (жаргон майстерні)

Ці слова траплятимуться нижче всюди. Розберіться з ними тут один раз — далі документ просто ними користується.

| Жаргон | Простими словами |
|--------|------------------|
| **coding harness** | «Автомобіль», над яким ми насправді працюємо: увесь шар захисних механізмів AI-розробки навколо продуктового репозиторію — rules, skills, hooks, trusted suite і ledgers |
| **subject** | Продуктовий репозиторій, загнаний у бокс для absorb / compare; клонується лише локально й **ніколи** тут не комітиться |
| **harness surface** | Знімні панелі цієї машини (`AGENTS.md`, skills, hooks), а не двигун (бізнес-код) |
| **Agent-Kit** | Установник стелажа: розміщує methodology skills / hook templates у Cursor, Claude Code, Codex тощо |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — прогін на стенді перед тим, як майстерня щось випустить (той самий стенд, що й L2 CI) |

## Найшвидша смуга: приймання одним рядком

Одна команда робить усе: клонує майстерню, підтягує submodules, установлює git hooks, ставить Agent-Kit на стелаж і відразу відправляє збірку на стенд — у public trusted suite.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Занадто вигадливо? Старий добрий pipe заводить той самий двигун:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Хочете вибрати місце встановлення й клієнта? Задайте дві змінні середовища:

- `TARGET_DIR` — directory для встановлення
- `CLIENT` — client для підключення: `cursor` / `claude` / `codex` / `codex-native`; або `skip`, щоб відкласти Agent-Kit на потім

Однорядкова команда також ставить Agent-Kit на стелаж і запускає suite — **більшість людей тут глушить двигун і закриває зміну**. Хочете встановлювати по одній деталі чи команда заглухла посеред заїзду? Переходьте на ручну смугу.

## Ручне приймання (установіть самі)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Наразі лише відчинилися ворота боксу — ящик із деталями (Agent-Kit) досі стоїть на підлозі. Рушаймо далі.

## Поставте Agent-Kit на стелаж (ящик із деталями — на стіну)

Agent-Kit установлює methodology skills і hooks цього репозиторію у ваш редактор / CLI. Базове встановлення дає налаштований стандартний комплект: локальну методологію, відібрані SP skills для verification / TDD / review, бібліотеку Matt для свідомого виклику й advisory router із низькою частотою спрацювання.

Він **не** протягує нишком bootstrap `using-superpowers` / `brainstorming` і не чіпає vendor hooks — вони лише за явним вибором. Дерева клієнтів (`.cursor` / `.claude` / `.codex` / `.agents`) — це **результати встановлення, які ніколи не комітяться**: завжди створюйте їх заново через install, а не редагуйте вручну й не намагайтеся потай повернути в git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Параметр | Значення |
|----------|----------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (необов'язково) | `lean`, `guided`, `structured`; лише щільність advisory prompts — **ніколи** не змінює enforcement |

Найпоширеніший локальний bootstrap — поставити всі чотири клієнти одночасно:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Profile репозиторію завжди налаштовується через CLI (редагувати YAML вручну — запрошувати халепу). Щоб перенести налаштування в інший репозиторій, спочатку export, потім check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` залишається лише явним повним plugin-шляхом сумісності для старих workflows — це більше не рекомендований маршрут. Стандартна materialization бібліотеки не копіює vendor plugins, hooks або skills поза allowlist.

## Заганяйте власну машину (необов'язково: підключіть subject)

Хочете лише переконатися, що в майстерні все зелене? **Нічого не підключайте**: public clone не залежить від приватних продуктових репозиторіїв і все одно проганяє trusted suite до суцільної зелені.

Лише коли справді потрібно виконати sync / import / compare реального subject, запускайте:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Запам'ятайте один порядок: **створити `manifest.yaml` → sync → записати версію через `--pin` → запускати `check-local-absorb.sh`, доки не буде `harness-ready`**. Спочатку пройдіть цей gate; лише після цього дозволено import / compare / score.

Усе перелічене залишається локальним і вже додане до gitignore. Не намагайтеся силоміць протягти це в commit: pre-commit hook одразу розверне вас біля воріт.

- `subjects/manifest.yaml`
- `pin.json` і `checkout/` кожного subject
- `snapshots/`, `comparisons/`

---

Нижче — щоденна довідкова стіна майстерні. Беріть потрібний інструмент; читати все за раз не потрібно.

## Часті команди (стіна інструментів)

| Що вам потрібно | Що запустити |
|-----------------|--------------|
| Public trusted suite (стенд / форма CI) | `bash tools/harness/test-harness.sh` |
| Перевірити Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Виконати sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Перезаписати pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Перевірити готовність local absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Імпортувати snapshot | `python3 tools/import/import_subject.py --all` |
| Створити compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Виконати score | `python3 tools/score/score_subject.py <id>` |
| Створити щотижневий звіт | `python3 tools/harness/weekly_report.py` |

## План майстерні (де лежать деталі)

| Шлях | Що це | У git? |
|------|--------|--------|
| `agent-kit/skills` | Відкрита методологія (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Шаблони hooks / settings для кожного клієнта | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Результати встановлення | ✗ |
| `subjects/manifest.example.yaml` | Публічний приклад registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Локальний registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Публічні fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Результати absorb | ✗ |
| `docs/harness/` | Design + ledgers | частково |
| `AGENTS.md` | SSOT обмежень (`CLAUDE.md` вказує сюди) | ✓ |

## Полиця посібників (докладніше)

- [`docs/README.md`](../README.md) — правила розміщення документації
- [`docs/harness/design.md`](../harness/design.md) — design harness цього репозиторію
- [`docs/specs/`](../specs/) — архів design
- [`AGENTS.md`](../../AGENTS.md) — визначення завершеності, blacklist і карта механізмів

## Ліцензія

[MIT](../../LICENSE) — забирайте авто із салону й кермуйте як заманеться: документи вже тут.
