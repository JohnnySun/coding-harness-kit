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

> **Ця майстерня працює з вашим автомобілем — coding harness.** Це рівень захисних механізмів для розробки з AI навколо репозиторію продукту. Репозиторій продукту — subject — володіє автомобілем; бізнес-код є двигуном, і двигун ми не відкриваємо.
> Короткий маршрут: запустіть установлення однією командою → установіть Agent-Kit для Cursor, Claude Code або Codex → за потреби підключіть реальний subject, а потім виконайте sync, pin і перевірку `harness-ready`. Нові деталі все одно проходять випробування на стенді. Огляд фарби не замінює план тестування.

| Термін | Значення (відповідник у майстерні) |
|------|---------|
| **coding harness** | Ваш автомобіль: рівень захисних механізмів для розробки з AI навколо репозиторію продукту (rules, skills, hooks, trusted suite і ledgers) |
| **subject** | Репозиторій продукту, якому належить автомобіль (локальний clone; тут не комітиться) |
| **harness surface** | Зона деталей: `AGENTS.md`, skills, hooks і подібні файли захисних механізмів; не бізнес-код |
| **Agent-Kit** | Стелаж із деталями: матеріалізує методологічні skills і templates hooks у Cursor, Claude Code, Codex тощо |
| **public trusted suite** | Випробувальний стенд: `bash tools/harness/test-harness.sh` (те саме, що L2 CI) |

## 1. Приймання (ініціалізація)

Найшвидший в'їзд до майстерні — інсталятор, що запускається однією командою. Він клонує репозиторій, ініціалізує submodules, установлює git hooks і Agent-Kit, а потім запускає public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Якщо ваш shell не підтримує process substitution, скористайтеся рівноцінною формою з pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Необов'язкові змінні середовища: `TARGET_DIR` і `CLIENT`. Установіть `CLIENT` у `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Ручний запасний варіант або спосіб простежити за кожним кроком:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Якщо ви забули --recurse-submodules
git submodule update --init --recursive

# Установіть перевірку безпеки L1 (блокує приватні дерева; за потреби запускає suite)
bash tools/harness/install-git-hooks.sh
```

Тепер ви маєте перебувати в `los-santos-customs/` з ініціалізованими submodules та встановленими git hooks. Маршрут однієї команди також установлює Agent-Kit для вибраного клієнта й запускає public suite. Якщо ви обрали ручний шлях, перейдіть до §2. Механічна коробка потребує ще одного кроку; справа тут не в ностальгії.

## 2. Установлення деталей (Agent-Kit)

Agent-Kit установлює skills і hooks цієї майстерні у ваш редактор або CLI. Установлення без додаткових параметрів надає такі продумані стандартні налаштування:

- локальну методологію;
- відібрані skills SP для верифікації, TDD і review;
- бібліотеку Matt, яку викликає користувач;
- рекомендаційний router із низькою частотою спрацювання.

Він не встановлює bootstrap `using-superpowers` / `brainstorming` і hooks постачальників. Дерева клієнтів (`.cursor` / `.claude` / `.codex` / `.agents`) є результатами встановлення й не комітяться. Створюйте їх заново через install; згенерованим файлам кузовний ремонт не потрібен.

```bash
# Установіть для конкретного клієнта
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Перевірте, що деталі встановлені правильно
bash tools/harness/agent-kit.sh validate

# Перегляньте встановлення без змін (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Параметр | Значення |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (необов'язково) | `lean`, `guided`, `structured`; змінює лише щільність рекомендацій |

```bash
# Установіть усі чотири клієнти (звичайний локальний bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Перегляньте або налаштуйте profile репозиторію (agents записують лише через CLI)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Експортуйте переносний profile у subject; підключіть fragments, а потім перевірте
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` залишається лише явним шляхом сумісності з повним plugin для старих workflows. Це більше не рекомендований спосіб установлення. Стандартна матеріалізація бібліотеки не копіює plugins, hooks або skills постачальників поза allowlist; стелаж із деталями недарма має інвентарний список.

## 3. (Необов'язково) Приженіть власний автомобіль

Публічний clone може запускати public trusted suite без приватних репозиторіїв продуктів. Підключайте автомобіль клієнта до локальної майстерні лише тоді, коли потрібно виконати sync, import або compare реального subject:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Укажіть у remotes репозиторії, до яких маєте доступ, а потім:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # локальний harness-ready (не public suite)
```

Порядок важливий:

1. Створіть `subjects/manifest.yaml` із прикладу. Спрямуйте його remotes на репозиторії, до яких маєте доступ.
2. Запустіть sync, щоб отримати harness surface кожного subject.
3. Використайте `<id> --pin`, щоб зафіксувати точну ревізію для оцінювання.
4. Запустіть локальну перевірку absorb. Subject, який її пройшов, має статус `harness-ready`; лише після цього import, compare і score можуть давати надійні результати.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` і `comparisons/` — це автомобілі клієнтів і замовлення на роботи. Вони залишаються локальними, ігноруються git і ніколи не потрапляють до публічного салону. Це не секретність, а базовий контроль ключів.

---

Тепер автомобіль рухається власним ходом. Нижче наведено довідкові матеріали майстерні.

## Часті команди

| Призначення | Команда |
|---------|---------|
| Public trusted suite (замикання циклу / CI) | `bash tools/harness/test-harness.sh` |
| Валідація Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Перезапис pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Локальна готовність absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Звіт compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Щотижневий звіт | `python3 tools/harness/weekly_report.py` |

## Структура

| Шлях | Роль | У git? |
|------|------|---------|
| `agent-kit/skills` | Відкрита методологія (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates hooks/settings клієнтів | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Результати встановлення | ✗ |
| `subjects/manifest.example.yaml` | Приклад публічного registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Локальний registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Публічні fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Результати absorb | ✗ |
| `docs/harness/` | Design + ledgers | частково |
| `AGENTS.md` | SSOT обмежень (`CLAUDE.md` → цей файл) | ✓ |

## Документація

- [`docs/README.md`](../README.md) — правила розміщення документації
- [`docs/harness/design.md`](../harness/design.md) — design harness цього репозиторію
- [`docs/specs/`](../specs/) — архів design
- [`AGENTS.md`](../../AGENTS.md) — визначення завершеності, blacklist і карта механізмів

## Ліцензія

[MIT](../../LICENSE)
