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

> **В одной строке:** это тюнинг-ателье для *защитных механизмов* вашего репозитория. На подъёмник попадает не бизнес-код, а окружающий его **coding harness** — слой, который не даёт AI (Cursor, Claude Code, Codex) срезать углы, изображать «готово» и заталкивать в git то, чему там не место.
>
> **Что вы получаете:** можно сразу ехать с нашей отлаженной методологией skills и защищёнными от дурака hooks, а можно приварить те же ограждения к собственным репозиториям. Двигатель — ваш бизнес-код — мы не трогаем; лишь усиливаем внешний каркас, пока AI уже не сможет случайно смять кузов.
>
> **Три передачи до старта:** установка одной строкой → (зажигание) поставить Agent-Kit на стеллаж → (необязательно) загнать свой subject. Перед закрытием смены запустите `bash tools/harness/test-harness.sh`: все индикаторы зелёные — техосмотр пройден, можно на дорогу.

## Словарь (жаргон мастерской)

Эти слова будут встречаться ниже повсюду. Разберитесь с ними один раз — дальше документ просто ими пользуется.

| Жаргон | Простыми словами |
|--------|------------------|
| **coding harness** | «Автомобиль», который мы на самом деле тюнингуем: весь слой защитных механизмов AI-разработки вокруг продуктового репозитория — rules, skills, hooks, trusted suite и ledgers |
| **subject** | Продуктовый репозиторий, загнанный в бокс для absorb / compare; клонируется только локально и **никогда** здесь не коммитится |
| **harness surface** | Съёмные панели этой машины (`AGENTS.md`, skills, hooks), а не двигатель (бизнес-код) |
| **Agent-Kit** | Установщик стеллажа: размещает methodology skills / hook templates в Cursor, Claude Code, Codex и т. д. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — прогон на стенде перед выпуском чего-либо из мастерской (тот же стенд, что и L2 CI) |

## Самая быстрая полоса: приёмка одной строкой

Одна команда делает всё: клонирует мастерскую, подтягивает submodules, устанавливает git hooks, размещает Agent-Kit и сразу отправляет сборку на стенд — в public trusted suite.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Слишком навороченно? Старый добрый pipe заводит тот же мотор:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Хотите выбрать место установки и клиента? Задайте две переменные среды:

- `TARGET_DIR` — каталог для установки
- `CLIENT` — подключаемый клиент: `cursor` / `claude` / `codex` / `codex-native`; либо `skip`, чтобы отложить Agent-Kit

Однострочник также устанавливает Agent-Kit и запускает suite — **большинство на этом глушит мотор и закрывает смену**. Хотите ставить детали по одной или установка заглохла на полпути? Переходите на ручную полосу.

## Ручная приёмка (установите всё сами)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Пока что открылись лишь ворота бокса — ящик с деталями (Agent-Kit) всё ещё стоит на полу. Продолжаем.

## Разместите Agent-Kit (ящик с деталями — на стену)

Agent-Kit устанавливает methodology skills и hooks этого репозитория в редактор / CLI. Базовая установка выдаёт отлаженный набор по умолчанию: локальную методологию, отобранные SP skills для verification / TDD / review, библиотеку Matt для осознанного вызова и advisory router с низкой частотой срабатывания.

Он **не** протаскивает bootstrap `using-superpowers` / `brainstorming` и не трогает vendor hooks — они включаются только явно. Деревья клиентов (`.cursor` / `.claude` / `.codex` / `.agents`) — **результаты установки, которые никогда не коммитятся**: всегда создавайте их заново через install, а не правьте вручную и не пытайтесь тайком вернуть в git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Параметр | Значения |
|----------|----------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (необязательно) | `lean`, `guided`, `structured`; только плотность advisory prompts — **никогда** не меняет enforcement |

Самый распространённый локальный bootstrap — поставить все четыре клиента разом:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Profile репозитория всегда меняется через CLI (ручная правка YAML — верный способ пригласить неприятности). Чтобы перенести настройку в другой репозиторий, сначала экспортируйте её, затем проверьте:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` остаётся только явным полным plugin-путём совместимости для старых workflows — это больше не рекомендуемый маршрут. Стандартная materialization библиотеки не копирует vendor plugins, hooks или skills вне allowlist.

## Загоните свою машину (необязательно: подключите subject)

Хотите лишь убедиться, что в мастерской всё зелёное? **Ничего не подключайте**: публичный clone не зависит от приватных продуктовых репозиториев и всё равно прогоняет trusted suite до стены зелёных индикаторов.

Только если действительно нужно выполнить sync / import / compare реального subject, запускайте:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Запомните порядок: **создать `manifest.yaml` → sync → записать версию через `--pin` → запускать `check-local-absorb.sh`, пока не будет `harness-ready`**. Сначала пройдите этот gate; только после этого разрешены import / compare / score.

Всё перечисленное остаётся локальным и уже находится в gitignore. Не пытайтесь силой протащить это в commit: pre-commit hook немедленно развернёт вас у ворот.

- `subjects/manifest.yaml`
- `pin.json` и `checkout/` каждого subject
- `snapshots/`, `comparisons/`

---

Ниже — справочная стена мастерской на каждый день. Берите нужный инструмент; читать всё подряд необязательно.

## Частые команды (стена инструментов)

| Что вам нужно | Что запустить |
|---------------|---------------|
| Public trusted suite (стенд / форма CI) | `bash tools/harness/test-harness.sh` |
| Проверить Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Выполнить sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Перезаписать pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Проверить готовность local absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Импортировать snapshot | `python3 tools/import/import_subject.py --all` |
| Создать compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Выполнить score | `python3 tools/score/score_subject.py <id>` |
| Создать еженедельный отчёт | `python3 tools/harness/weekly_report.py` |

## План мастерской (где лежат детали)

| Путь | Что это | В git? |
|------|---------|--------|
| `agent-kit/skills` | Открытая методология (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Шаблоны hooks / settings для каждого клиента | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Результаты установки | ✗ |
| `subjects/manifest.example.yaml` | Публичный пример registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Локальный registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Публичные fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Результаты absorb | ✗ |
| `docs/harness/` | Design + ledgers | частично |
| `AGENTS.md` | SSOT ограничений (`CLAUDE.md` указывает сюда) | ✓ |

## Полка руководств (подробнее)

- [`docs/README.md`](../README.md) — правила размещения документации
- [`docs/harness/design.md`](../harness/design.md) — устройство harness этого репозитория
- [`docs/specs/`](../specs/) — архив design
- [`AGENTS.md`](../../AGENTS.md) — определение завершённости, blacklist и карта механизмов

## Лицензия

[MIT](../../LICENSE) — забирайте машину из салона и ездите как угодно: документы уже на руках.
