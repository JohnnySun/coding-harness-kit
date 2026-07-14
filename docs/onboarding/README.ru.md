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
  <strong>Русский</strong> |
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

> **Эта мастерская работает с вашей машиной — coding harness.** Это слой защитных механизмов для разработки с AI вокруг репозитория продукта. Репозиторий продукта — subject — владеет машиной; бизнес-код служит двигателем, и двигатель мы не открываем.
> Короткий маршрут: запустите установку одной командой → установите Agent-Kit для Cursor, Claude Code или Codex → при необходимости подключите реальный subject, затем выполните sync, pin и проверку `harness-ready`. Новые детали всё равно проходят испытание на стенде. Осмотр краски не заменяет план тестирования.

| Термин | Значение (аналогия с мастерской) |
|------|---------|
| **coding harness** | Ваша машина: слой защитных механизмов для разработки с AI вокруг репозитория продукта (rules, skills, hooks, trusted suite и ledgers) |
| **subject** | Репозиторий продукта, которому принадлежит машина (локальный clone; здесь не коммитится) |
| **harness surface** | Зона деталей: `AGENTS.md`, skills, hooks и похожие файлы защитных механизмов; не бизнес-код |
| **Agent-Kit** | Стеллаж с деталями: материализует методологические skills и templates hooks в Cursor, Claude Code, Codex и т. д. |
| **public trusted suite** | Испытательный стенд: `bash tools/harness/test-harness.sh` (то же, что L2 CI) |

## 1. Приёмка (инициализация)

Самый быстрый способ попасть в мастерскую — установщик, запускаемый одной командой. Он клонирует репозиторий, инициализирует submodules, устанавливает git hooks и Agent-Kit, а затем запускает public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Если ваш shell не поддерживает process substitution, используйте эквивалентный вариант с pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Необязательные переменные среды: `TARGET_DIR` и `CLIENT`. Установите `CLIENT` в `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Ручной запасной вариант или способ проследить за каждым шагом:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Если вы забыли --recurse-submodules
git submodule update --init --recursive

# Установите проверку безопасности L1 (блокирует приватные деревья; при необходимости запускает suite)
bash tools/harness/install-git-hooks.sh
```

Теперь вы должны находиться в `los-santos-customs/`, с инициализированными submodules и установленными git hooks. Маршрут одной команды также устанавливает Agent-Kit для выбранного клиента и запускает public suite. Если вы выбрали ручной путь, переходите к §2. Механическая коробка требует ещё одного шага; дело здесь не в ностальгии.

## 2. Установка деталей (Agent-Kit)

Agent-Kit устанавливает skills и hooks этой мастерской в ваш редактор или CLI. Установка без дополнительных параметров предоставляет следующие продуманные значения по умолчанию:

- локальную методологию;
- отобранные skills SP для верификации, TDD и review;
- библиотеку Matt, вызываемую пользователем;
- редко срабатывающий рекомендательный router.

Она не устанавливает bootstrap `using-superpowers` / `brainstorming` и hooks поставщиков. Деревья клиентов (`.cursor` / `.claude` / `.codex` / `.agents`) являются результатами установки и не коммитятся. Создавайте их заново через install; сгенерированным файлам кузовной ремонт не нужен.

```bash
# Установите для конкретного клиента
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Проверьте, что детали установлены правильно
bash tools/harness/agent-kit.sh validate

# Предварительно просмотрите установку (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Параметр | Значения |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (необязательно) | `lean`, `guided`, `structured`; меняет только плотность рекомендаций |

```bash
# Установите все четыре клиента (обычный локальный bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Просмотрите или настройте profile репозитория (agents записывают только через CLI)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Экспортируйте переносимый profile в subject; подключите fragments, затем выполните проверку
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` сохраняется только как явный путь совместимости с полным plugin для старых workflows. Это больше не рекомендуемый способ установки. Стандартная материализация библиотеки не копирует plugins, hooks или skills поставщиков за пределами allowlist; у стеллажа с деталями не зря есть инвентарная опись.

## 3. (Необязательно) Пригоните свою машину

Публичный clone может запускать public trusted suite без приватных репозиториев продуктов. Подключайте машину клиента к локальной мастерской, только когда нужно выполнить sync, import или compare реального subject:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Укажите в remotes репозитории, к которым у вас есть доступ, затем:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # локальный harness-ready (не public suite)
```

Порядок важен:

1. Создайте `subjects/manifest.yaml` из примера. Направьте его remotes на репозитории, к которым у вас есть доступ.
2. Запустите sync, чтобы получить harness surface каждого subject.
3. Используйте `<id> --pin`, чтобы зафиксировать точную ревизию для оценки.
4. Запустите локальную проверку absorb. Прошедший её subject получает статус `harness-ready`; только после этого import, compare и score могут давать достоверные результаты.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` и `comparisons/` — это машины клиентов и заказ-наряды. Они остаются локальными, игнорируются git и никогда не попадают в публичный выставочный зал. Это не секретность, а базовый контроль ключей.

---

Теперь машина движется своим ходом. Ниже приведена справочная информация мастерской.

## Частые команды

| Назначение | Команда |
|---------|---------|
| Public trusted suite (замыкание цикла / CI) | `bash tools/harness/test-harness.sh` |
| Валидация Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Перезапись pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Локальная готовность absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Отчёт compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Еженедельный отчёт | `python3 tools/harness/weekly_report.py` |

## Структура

| Путь | Роль | В git? |
|------|------|---------|
| `agent-kit/skills` | Открытая методология (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates hooks/settings клиентов | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Результаты установки | ✗ |
| `subjects/manifest.example.yaml` | Пример публичного registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Локальный registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Публичные fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Результаты absorb | ✗ |
| `docs/harness/` | Design + ledgers | частично |
| `AGENTS.md` | SSOT ограничений (`CLAUDE.md` → этот файл) | ✓ |

## Документация

- [`docs/README.md`](../README.md) — правила размещения документации
- [`docs/harness/design.md`](../harness/design.md) — design harness этого репозитория
- [`docs/specs/`](../specs/) — архив design
- [`AGENTS.md`](../../AGENTS.md) — определение завершённости, blacklist и карта механизмов

## Лицензия

[MIT](../../LICENSE)
