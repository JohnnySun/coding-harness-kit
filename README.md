# coding-harness-kit

<h3 align="center">
  <strong>繁體中文</strong> |
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
  <a href="README.uk.md">Українська</a>
</h3>

> 用來**構建 / 迭代 coding harness** 的開源工具倉。  
> 本倉不含業務源碼；工作對象是各業務倉（subject）的 **harness 表面**。  
> 克隆後三步即可開始：初始化 submodule → 安裝 Agent-Kit →（可選）同步你的 subject。

| 術語 | 含義 |
|------|------|
| **coding harness** | 包在業務倉外層的 AI 開發防護體系：規則、skills、hooks、可信集、帳本 |
| **subject** | 被本工具吸收 / 比較的一個業務倉（本機 clone，不進本倉 git） |
| **harness 表面** | subject 裡與 harness 相關的路徑（如 `AGENTS.md`、skills、hooks），不是業務源碼 |
| **Agent-Kit** | 把方法論 skills / hooks 模板安裝到 Cursor、Claude Code、Codex 等客戶端的安裝器 |
| **公開可信集** | `bash tools/harness/test-harness.sh`——本倉自己的一鍵驗證（與 L2 CI 同構） |

## 1. 初始化

```bash
git clone --recurse-submodules https://github.com/JohnnySun/coding-harness-kit.git
cd coding-harness-kit

# 若克隆時漏了 --recurse-submodules
git submodule update --init --recursive

# 安裝 git pre-commit hook（拒收私有樹、必要時跑可信集）
bash tools/harness/install-git-hooks.sh
```

## 2. 安裝 Agent-Kit（AI 工具）

Agent-Kit 為 Cursor / Claude Code / Codex 提供本工程的 skills 與 hooks。  
客戶端目錄（`.cursor` / `.claude` / `.codex` / `.agents`）是**安裝產物，不進 git**——一律用 install 再生。

```bash
# 安裝到指定客戶端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 校驗設定是否完整
bash tools/harness/agent-kit.sh validate

# 預覽安裝內容（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 參數 | 可選值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `PLUGIN`（可選） | `superpowers`、`mattpocock-skills`（空格分隔可多選） |

```bash
# 四個客戶端都裝一遍（常見本機起步）
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# 可選插件
CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

## 3. （可選）接入你自己的 subject

公開 clone **不需要**任何私有業務倉即可跑綠可信集。  
若要 sync / import / compare 真實 subject：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 編輯 remotes 為你有權限的倉庫，再：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本機 harness-ready（非公開套件）
```

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` 均為本機私有，已被 `.gitignore` 擋住。

---

以下為日常參考，按需查閱。

## 常用命令

| 目的 | 命令 |
|------|------|
| 公開可信集（收環 / CI 同構） | `bash tools/harness/test-harness.sh` |
| 校驗 Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| 同步 harness 表面 | `bash tools/sync/sync-subjects.sh` |
| 寫回 pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| 本機 absorb 就緒 | `bash tools/harness/check-local-absorb.sh --all` |
| 導入 snapshot | `python3 tools/import/import_subject.py --all` |
| 比較報告 | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| 評分 | `python3 tools/score/score_subject.py <id>` |
| 週報 | `python3 tools/harness/weekly_report.py` |

## 倉庫佈局

| 路徑 | 角色 | 進 git？ |
|------|------|----------|
| `agent-kit/skills` | 開源方法論（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | 各客戶端 hooks/settings 模板 | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | install 產物 | ✗ |
| `subjects/manifest.example.yaml` | 公開 registry 範本 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 本機 registry / clone | ✗ |
| `tools/` | sync / import / compare / score / 可信集 / hooks | ✓ |
| `testdata/` | 公開 fixture（CI 用） | ✓ |
| `snapshots/`、`comparisons/` | 吸收產物 | ✗ |
| `docs/harness/` | 設計與帳本 | 部分 |
| `AGENTS.md` | 約束 SSOT（`CLAUDE.md` → 之） | ✓ |

## 文件

- [`docs/README.md`](docs/README.md) — 文檔落點約定
- [`docs/harness/design.md`](docs/harness/design.md) — 本倉 harness 設計
- [`docs/specs/`](docs/specs/) — 設計文檔歸檔
- [`AGENTS.md`](AGENTS.md) — 完成定義、黑名單、機關落點

## 授權

[MIT](LICENSE)
