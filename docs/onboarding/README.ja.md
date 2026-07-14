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

> **このショップが整備する車は、あなたの coding harness です。** つまり、プロダクトリポジトリの外側を囲む AI 開発用のガードレール層です。車の持ち主はそのプロダクトリポジトリ、すなわち subject。業務ソースはエンジンなので、ボンネットは開けません。
> 最短ルート：1 行の受付コマンドを実行 → Cursor、Claude Code、または Codex 用の Agent-Kit をインストール → 必要なら実際の subject を接続し、sync、pin、`harness-ready` の確認へ進みます。新しい部品は public trusted suite というダイノに載せます。塗装の点検はテスト計画ではありません。

| 用語 | 意味（ショップでの対応） |
|------|---------|
| **coding harness** | あなたの車：プロダクトリポジトリを囲む AI 開発用ガードレール層（rules、skills、hooks、trusted suite、ledgers） |
| **subject** | 車を所有するプロダクトリポジトリ（ローカル clone。本リポジトリにはコミットしない） |
| **harness surface** | 部品作業区画：`AGENTS.md`、skills、hooks などのガードレールファイル。業務ソースではない |
| **Agent-Kit** | 部品棚：方法論の skills / hook テンプレートを Cursor、Claude Code、Codex などへ展開する |
| **public trusted suite** | ダイノ：`bash tools/harness/test-harness.sh`（L2 CI と同じ） |

## 1. 受付（初期化）

最速で作業区画に入る方法は、1 行のインストーラです。リポジトリを clone し、submodules を初期化し、git hooks と Agent-Kit をインストールしてから、public trusted suite を実行します。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

シェルが process substitution に対応していない場合は、同等の pipe 形式を使います。

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

任意の環境変数は `TARGET_DIR` と `CLIENT` です。`CLIENT` には `cursor` / `claude` / `codex` / `codex-native` / `skip` を指定します。

手動での代替手順、またはレンチの一回転ずつを確認したい場合：

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

これで、submodules が初期化され、git hooks がインストールされた `los-santos-customs/` 内にいるはずです。1 行ルートでは、選択した client 用の Agent-Kit もインストールし、public trusted suite も実行します。手動ルートを選んだ場合は §2 へ進んでください。マニュアル車には手順が 1 つ多くありますが、懐古趣味ではありません。

## 2. 部品を取り付ける（Agent-Kit）

Agent-Kit は、このショップの skills と hooks をエディタまたは CLI にインストールします。引数なしの install には、次の方針付きデフォルトが含まれます。

- ローカルの方法論
- 選定済みの SP verification、TDD、review skills
- ユーザーが呼び出す Matt library
- 低頻度の advisory router

`using-superpowers` / `brainstorming` bootstrap や vendor hooks はインストールしません。client trees（`.cursor` / `.claude` / `.codex` / `.agents`）はインストール出力であり、コミットしません。install で再生成してください。生成ファイルに板金作業は不要です。

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| パラメータ | 値 |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold`（任意） | `lean`, `guided`, `structured`。advisory の密度だけを調整 |

```bash
# Install all four clients (common local bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Inspect or adjust the repo profile (agents write via CLI only)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire fragments, then check
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` は、古い workflow 向けの明示的な full-plugin 互換ルートとしてのみ残っています。推奨インストール方法ではありません。デフォルトの library 展開では、allowlist 外の vendor plugins、hooks、skills はコピーしません。部品棚に在庫表があるのには理由があります。

## 3. （任意）自分の車を持ち込む

public clone は、private なプロダクトリポジトリなしで public trusted suite を実行できます。実際の subject を sync、import、compare する必要がある場合だけ、顧客の車をローカル作業区画へ接続します。

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

順序が重要です。

1. example から `subjects/manifest.yaml` を作成し、アクセスできる repos を remotes に指定します。
2. sync を実行し、各 subject の harness surface を取得します。
3. `<id> --pin` で、評価する正確な revision を記録します。
4. local absorb check を実行します。合格した subject が `harness-ready` です。それから初めて、import、compare、score が信頼できる結果を出せます。

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` は顧客の車と作業指示書です。ローカルに残り、gitignore され、public showroom には入りません。秘密主義ではなく、鍵の基本管理です。

---

これで車は自力で走ります。以下はサービスベイのリファレンスです。

## よく使うコマンド

| 目的 | コマンド |
|------|----------|
| public trusted suite（loop を閉じる / CI） | `bash tools/harness/test-harness.sh` |
| Agent-Kit の検証 | `bash tools/harness/agent-kit.sh validate` |
| harness surface の sync | `bash tools/sync/sync-subjects.sh` |
| pin の書き換え | `bash tools/sync/sync-subjects.sh <id> --pin` |
| local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot の import | `python3 tools/import/import_subject.py --all` |
| compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| score | `python3 tools/score/score_subject.py <id>` |
| weekly report | `python3 tools/harness/weekly_report.py` |

## レイアウト

| パス | 役割 | git? |
|------|------|------|
| `agent-kit/skills` | オープンな方法論（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | install outputs | ✗ |
| `subjects/manifest.example.yaml` | public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | public fixtures（CI） | ✓ |
| `snapshots/` / `comparisons/` | absorb products | ✗ |
| `docs/harness/` | design + ledgers | 一部 |
| `AGENTS.md` | 制約の SSOT（`CLAUDE.md` → it） | ✓ |

## ドキュメント

- [`docs/README.md`](../README.md) — ドキュメント配置ルール
- [`docs/harness/design.md`](../harness/design.md) — このリポジトリの harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — 完了条件、blacklist、mechanism map

## ライセンス

[MIT](../../LICENSE)
