# 洛聖都改車王（Los Santos Customs）

<h3 align="center">
  <strong>繁體中文</strong> |
  <a href="docs/onboarding/README.zh-CN.md">简体中文</a> |
  <a href="docs/onboarding/README.en.md">English</a> |
  <a href="docs/onboarding/README.ja.md">日本語</a> |
  <a href="docs/onboarding/README.ko.md">한국어</a> |
  <a href="docs/onboarding/README.es.md">Español</a> |
  <a href="docs/onboarding/README.fr.md">Français</a> |
  <a href="docs/onboarding/README.de.md">Deutsch</a> |
  <a href="docs/onboarding/README.pt-BR.md">Português</a> |
  <a href="docs/onboarding/README.ru.md">Русский</a> |
  <a href="docs/onboarding/README.ar.md">العربية</a> |
  <a href="docs/onboarding/README.hi.md">हिन्दी</a> |
  <a href="docs/onboarding/README.id.md">Bahasa Indonesia</a> |
  <a href="docs/onboarding/README.vi.md">Tiếng Việt</a> |
  <a href="docs/onboarding/README.th.md">ไทย</a> |
  <a href="docs/onboarding/README.it.md">Italiano</a> |
  <a href="docs/onboarding/README.nl.md">Nederlands</a> |
  <a href="docs/onboarding/README.pl.md">Polski</a> |
  <a href="docs/onboarding/README.tr.md">Türkçe</a> |
  <a href="docs/onboarding/README.uk.md">Українська</a>
</h3>

> **這間改裝廠改的是你的車：coding harness。** 它是包在產品倉外面的 AI 開發防護層；產品倉（subject）擁有這台車，業務源碼是引擎，本廠不拆。
> 最短路線：執行一鍵安裝 → 為 Cursor／Claude Code／Codex 裝 Agent-Kit →（可選）接上真實 subject，依序 sync、pin、檢查 `harness-ready`。零件裝完要上測功機，不能只看烤漆。

| 術語 | 含義（改裝廠對照） |
|------|------|
| **coding harness** | 你的「車」：包在業務倉外層的 AI 開發防護體系（規則、skills、hooks、可信集、帳本） |
| **subject** | 擁有這台車的產品／業務倉（本機 clone，不進本倉 git） |
| **harness 表面** | 零件安裝面：`AGENTS.md`、skills、hooks 等；業務源碼不在工單內 |
| **Agent-Kit** | 零件架：把方法論 skills / hooks 模板裝進 Cursor、Claude Code、Codex 等客戶端 |
| **公開可信集** | 測功機：`bash tools/harness/test-harness.sh`（與 L2 CI 同構） |

## 1. 進廠（初始化）

最快的工位是一鍵安裝。它會完成 clone、submodule、git hooks、Agent-Kit，並跑公開可信集：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

若你的 shell 不接受 process substitution，改用等價的 pipe 寫法：

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

可選環境變數是 `TARGET_DIR` 與 `CLIENT`。`CLIENT` 可設為 `cursor` / `claude` / `codex` / `codex-native` / `skip`。

想逐項看技師動手，或一鍵安裝不適用時，手動執行：

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# 若克隆時漏了 --recurse-submodules
git submodule update --init --recursive

# 裝 L1 安檢（拒收私有樹、必要時跑可信集）
bash tools/harness/install-git-hooks.sh
```

完成後，你應該位於 `los-santos-customs/`，submodule 已初始化，git hooks 已安裝。一鍵路線還會替所選客戶端裝好 Agent-Kit 並跑公開可信集；手動路線請繼續 §2。手排車多一個步驟，這次不是情懷。

## 2. 裝零件（Agent-Kit）

Agent-Kit 把本廠的 skills 與 hooks 裝進編輯器／CLI。裸 install 會裝這套有主見的預設：

- 本地方法論；
- 精選 SP 驗證／TDD／review skills；
- 由使用者主動呼叫的 Matt library；
- 低頻 advisory router。

它不安裝 `using-superpowers`／`brainstorming` bootstrap 或 vendor hooks。客戶端目錄（`.cursor` / `.claude` / `.codex` / `.agents`）是安裝產物，不進 git；壞了就重新 install，不必替生成檔做鈑金。

```bash
# 裝到指定客戶端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 校驗零件是否裝齊
bash tools/harness/agent-kit.sh validate

# 預覽（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 參數 | 可選值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `--process-scaffold`（可選） | `lean`、`guided`、`structured`；只調 advisory 密度 |

```bash
# 四個客戶端都裝一遍（常見本機起步）
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# 查看或調整 repo profile（Agent 一律經 CLI 寫入）
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# 輸出可攜 profile 到 subject；依 fragment 接線後檢查
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` 只保留作舊流程的顯式完整插件相容入口，不再是推薦安裝方式。預設 library materialization 不會複製 vendor plugin、hooks 或未列入 allowlist 的 skill；零件架有清單，不靠地上那盒「可能用得到」。

## 3. （可選）把自己的車開進來

公開 clone 不需要任何私有業務倉，也能把公開可信集跑綠。只有要 sync / import / compare 真實 subject 時，才把客戶的車接進本機工位：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 編輯 remotes 為你有權限的倉庫，再：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本機 harness-ready（非公開套件）
```

順序很重要：

1. 從範本建立 `subjects/manifest.yaml`，把 remotes 改成你有權限存取的倉庫。
2. 執行 sync，取得 subject 的 harness 表面。
3. 用 `<id> --pin` 記錄要評估的確切版本。
4. 跑本機 absorb 檢查；通過才是 `harness-ready`，之後才能可靠地 import、compare、score。

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` 都是客戶車輛與工單資料：只留本機，已被 `.gitignore` 擋住，不會停進公開展廳。這不是神祕，是基本的鑰匙管理。

---

新車已會走了。以下是日常保養資料，按需查閱。

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
