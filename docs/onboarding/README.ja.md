# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <strong>日本語</strong> |
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
  <a href="README.uk.md">Українська</a>
</h3>

> **ひと言で言うと：** ここは repo の *guardrails* を改造するショップです。リフトに載せるのは業務ソースではなく、その外側を包む **coding harness**。AI（Cursor、Claude Code、Codex）が近道をしたり、根拠なしに「完了」と言ったり、commit してはいけないものを git に押し込んだりするのを防ぐ層です。
>
> **何がうれしいのか：** 調整済みの methodology skills とうっかりに強い hooks をそのまま使うことも、同じ guardrails を自分の repos に取り付けることもできます。エンジン（業務ソース）には触れません。AI が気軽に潰せないところまで、外側のロールケージを溶接するだけです。
>
> **走り出すまでの 3 速：** 1 行で install →（点火）Agent-Kit をラックへ →（任意）自分の subject を入庫。店じまいの前に `bash tools/harness/test-harness.sh` を実行してください。メーターが全部緑なら検査合格、公道走行 OK です。

## 用語集（ショップの隠語）

以下の言葉は何度も登場します。ここで一度だけ覚えれば、残りはそのまま読めます。

| 隠語 | 普通の言い方 |
|------|--------------|
| **coding harness** | 実際に整備する「車」—product repo の外側にある AI-dev guardrail layer 全体：rules、skills、hooks、trusted suite、ledgers |
| **subject** | absorb / compare のため作業ベイに入れる product repo。clone はローカルだけで、ここには **決して** commit しない |
| **harness surface** | 車の改造パネル（`AGENTS.md`、skills、hooks）。エンジン（業務ソース）ではない |
| **Agent-Kit** | ラック用 installer。methodology skills / hook templates を Cursor、Claude Code、Codex などへ配置する |
| **public trusted suite** | `bash tools/harness/test-harness.sh`—何かを出荷する前のダイノ走行（L2 CI と同じ設備） |

## 最速レーン：1 行で受付

1 つの command ですべて行います。ショップを clone し、submodules を取得し、git hooks を install し、Agent-Kit をラックに載せ、そのままダイノ（public trusted suite）へ送ります。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

少し派手すぎますか？ 昔ながらの pipe でも同じエンジンがかかります。

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

配置先と配線する client を選ぶなら、次の 2 つの env vars を設定します。

- `TARGET_DIR` — install 先の directory
- `CLIENT` — 配線する client：`cursor` / `claude` / `codex` / `codex-native`。Agent-Kit を後回しにするなら `skip`

One-liner は Agent-Kit の配置と suite の実行まで済ませます。**ほとんどの人はここでエンジンを切って退勤できます**。1 速ずつ自分で組みたい、または one-liner が途中で止まった場合は、以下の manual lane へどうぞ。

## Manual intake（自分で取り付ける）

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

ここではまだ作業ベイの扉を開けただけです。部品箱（Agent-Kit）は床に置かれたまま。先へ進みましょう。

## Agent-Kit をラックへ（部品箱を壁に上げる）

Agent-Kit は、この repo の methodology skills と hooks を editor / CLI に配置します。素の install で入るのは、調整済みの default set です。local methodology、選定済みの SP verification / TDD / review skills、必要なときに呼ぶ Matt library、それに低頻度の advisory router が含まれます。

`using-superpowers` / `brainstorming` bootstrap を勝手に入れることはなく、vendor hooks にも触れません。これらは opt-in 専用です。client trees（`.cursor` / `.claude` / `.codex` / `.agents`）は **install outputs であり、決して commit しません**。手で直して git に紛れ込ませず、必ず install から再生成してください。

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | 値 |
|-----------|----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold`（任意） | `lean`, `guided`, `structured`。advisory prompt の密度だけを変え、enforcement には **決して** 触れない |

最も一般的な local bootstrap—4 つの clients をまとめてラックへ載せます。

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Repo profile は必ず CLI 経由で変更します（YAML の手編集はトラブルの予約席です）。別の repo へ setup を運ぶときは、先に export してから check します。

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` は古い workflows 向けの明示的な full-plugin compatibility hatch としてだけ残っています。現在の recommended path ではありません。Default library materialization は vendor plugins、hooks、allowlist 外の skills をコピーしません。

## 自分の車を入庫（任意：subject を接続）

ショップが全部緑で動くことだけ確認したいですか？ **何も接続しなくて構いません**。public clone は private な product repos に一切依存せず、それでも trusted suite をすべて緑で実行できます。

実際の subject を sync / import / compare したいときだけ、次を実行します。

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

覚える順序は 1 つだけです。**`manifest.yaml` を作成 → sync → `--pin` で version を書き戻す → `harness-ready` になるまで `check-local-absorb.sh`**。まずこの gate を通過してください。import / compare / score を実行できるのはその後です。

以下はローカルに残り、すでに gitignore されています。commit に無理やり入れようとしても、pre-commit hook がその場で跳ね返します。

- `subjects/manifest.yaml`
- 各 subject の `pin.json` と `checkout/`
- `snapshots/`、`comparisons/`

---

以下は日常用のリファレンスウォールです。必要な tool だけ手に取ればよく、一度に全部読む必要はありません。

## よく使う commands（工具の壁）

| やりたいこと | 実行する行 |
|--------------|------------|
| Public trusted suite（ダイノ / CI 形状） | `bash tools/harness/test-harness.sh` |
| Agent-Kit の validate | `bash tools/harness/agent-kit.sh validate` |
| Harness surface の sync | `bash tools/sync/sync-subjects.sh` |
| Pin の書き換え | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot の import | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## フロアマップ（各部品の置き場）

| Path | 内容 | Git に入る？ |
|------|------|--------------|
| `agent-kit/skills` | Open methodology（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | client ごとの hooks / settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Install outputs | ✗ |
| `subjects/manifest.example.yaml` | Public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures（CI） | ✓ |
| `snapshots/` / `comparisons/` | Absorb products | ✗ |
| `docs/harness/` | Design + ledgers | 一部 |
| `AGENTS.md` | Constraint SSOT（`CLAUDE.md` はここを参照） | ✓ |

## マニュアル棚（さらに深く）

- [`docs/README.md`](../README.md) — ドキュメントの配置ルール
- [`docs/harness/design.md`](../harness/design.md) — この repo の harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — completion definition、blacklist、mechanism map

## ライセンス

[MIT](../../LICENSE) — 好きなように乗って帰れます。車検証はこちら。
