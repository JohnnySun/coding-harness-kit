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

> **コーディングハーネスを構築・反復**するためのオープンソースツールキット。  
> 本リポジトリに業務ソースは含まれません。対象は各 subject の **harness 表面**です。  
> 始め方は3ステップ：submodule 初期化 → Agent-Kit インストール →（任意）subject 同期。

| 用語 | 意味 |
|------|------|
| **coding harness** | プロダクトリポジトリ外周の AI 開発ガードレール（rules / skills / hooks / 信頼スイート / 台帳） |
| **subject** | 本ツールが吸収・比較するプロダクトリポジトリ（ローカル clone、本リポジトリにはコミットしない） |
| **harness 表面** | subject 内の harness 関連パス（`AGENTS.md`、skills、hooks など）。業務ソースではない |
| **Agent-Kit** | 方法論 skills / hooks テンプレートを Cursor / Claude Code / Codex 等へ展開するインストーラ |
| **公開信頼スイート** | `bash tools/harness/test-harness.sh` — 本リポジトリの一発検証（L2 CI と同型） |

## 1. 初期化

One-line install (clone + submodules + hooks + Agent-Kit + trusted suite):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Or:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Optional: `TARGET_DIR`, `CLIENT`, `PLUGIN`.

Manual steps:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

git submodule update --init --recursive
bash tools/harness/install-git-hooks.sh
```

## 2. Agent-Kit のインストール（AI ツール）

クライアントツリー（`.cursor` / `.claude` / `.codex` / `.agents`）は**インストール成果物で git に入れません**。必ず install で再生成してください。

```bash
CLIENT=<client> bash tools/harness/agent-kit.sh install
bash tools/harness/agent-kit.sh validate
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| パラメータ | 値 |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `PLUGIN`（任意） | `superpowers`, `mattpocock-skills`（空白区切り） |

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

## 3. （任意）独自 subject の接続

公開 clone は**私有プロダクトリポジトリなし**で信頼スイートを緑にできます。実 subject を扱う場合：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all
```

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` はローカル専用で gitignore 済みです。

---

日常リファレンス。

## よく使うコマンド

| 目的 | コマンド |
|------|----------|
| 公開信頼スイート | `bash tools/harness/test-harness.sh` |
| Agent-Kit 検証 | `bash tools/harness/agent-kit.sh validate` |
| harness 表面の同期 | `bash tools/sync/sync-subjects.sh` |
| pin 書き戻し | `bash tools/sync/sync-subjects.sh <id> --pin` |
| ローカル absorb 準備 | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot 取り込み | `python3 tools/import/import_subject.py --all` |
| 比較レポート | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| スコア | `python3 tools/score/score_subject.py <id>` |
| 週次レポート | `python3 tools/harness/weekly_report.py` |

## レイアウト

| パス | 役割 | git? |
|------|------|------|
| `agent-kit/skills` | オープン方法論（submodule） | ✓ |
| `agent-kit/hooks/clients/` | クライアント hooks/settings テンプレート | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | インストール成果物 | ✗ |
| `subjects/manifest.example.yaml` | 公開 registry 例 | ✓ |
| `subjects/**`（example 以外） | ローカル registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | 公開 fixture（CI） | ✓ |
| `snapshots/` / `comparisons/` | 吸収成果物 | ✗ |
| `docs/harness/` | 設計と台帳 | 一部 |
| `AGENTS.md` | 制約 SSOT | ✓ |

## ドキュメント

- [`docs/README.md`](../README.md)
- [`docs/harness/design.md`](../harness/design.md)
- [`docs/specs/`](../specs/)
- [`AGENTS.md`](../../AGENTS.md)

## ライセンス

[MIT](../../LICENSE)
