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

> **一句話：** 這是一間專門幫你的程式碼倉「改裝防護」的改車廠。真正上舉升機的不是你的業務程式碼，而是包在它外面那層 **coding harness**——讓 AI（Cursor／Claude Code／Codex）幫你寫程式時，不會偷工減料、不會謊報完工、不會把不該提交的東西塞進 git。
>
> **跟你什麼關係：** 你要嘛直接用我們調校好的方法論 skills 與防呆 hooks，要嘛把同一套護欄搬到你自己的倉上。引擎（業務源碼）我們一根螺絲都不碰，只把外圈的鋼骨焊到 AI 撞不壞。
>
> **怎麼進廠（三檔）：** 一鍵安裝 →（引擎點火）上架 Agent-Kit →（選配）把你自己的車開進來。收工前踩一腳 `bash tools/harness/test-harness.sh`，儀表板全綠＝驗車通過、可以上路。

## 術語表（進廠先學黑話）

這幾個詞後面到處都會用，先在這裡認一次，之後不再重複解釋。

| 黑話 | 白話 |
|------|------|
| **coding harness** | 廠裡真正動手改的那台「車」——包在業務倉外的一整套 AI 開發護欄：規則、skills、hooks、可信集、帳本 |
| **subject** | 一輛開進廠裡被吸收／比較的業務倉；只在你本機 clone，**不會**跟著本倉進 git |
| **harness 表面** | 車身上跟改裝有關的那些面板（`AGENTS.md`、skills、hooks）；不是引擎本體（業務源碼） |
| **Agent-Kit** | 零件箱上架器——把方法論 skills／hooks 模板裝進 Cursor、Claude Code、Codex 等客戶端 |
| **公開可信集** | `bash tools/harness/test-harness.sh`——出廠前的測功機（dyno），跟線上 L2 CI 同一套 |

## 一鍵進廠（最快路線）

一行指令包全套：克隆本廠、拉齊 submodule、裝好 git hooks、上架 Agent-Kit，最後直接推上測功機跑一圈公開可信集。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

嫌上面那寫法花俏？老派管道也一樣能開：

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

想指定一下裝哪、配誰，補這兩個環境變數：

- `TARGET_DIR` — 裝進哪個目錄
- `CLIENT` — 配哪台客戶端：`cursor`／`claude`／`codex`／`codex-native`，或填 `skip` 這趟先不碰 Agent-Kit

一鍵路線會順手把 Agent-Kit 也裝好、可信集也跑完——**多數人到這裡就能熄火收工**。想自己一檔一檔慢慢掛，或者一鍵跑到一半斷線了，往下走手動路線。

## 手動進廠（自己拆步驟）

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# 克隆時忘了 --recurse-submodules？補這一句把零件補齊
git submodule update --init --recursive

# 焊上 git pre-commit hook：擋住私有樹誤闖 git，必要時順手踩一腳可信集
bash tools/harness/install-git-hooks.sh
```

跑到這裡只是**廠房鐵門拉開了**——零件箱（Agent-Kit）還晾在旁邊沒上架。接著下一節。

## 上架 Agent-Kit（把零件箱裝進工具牆）

Agent-Kit 負責把本倉的方法論 skills 與 hooks 塞進你的編輯器／CLI。裸裝一次就給你一套調校好的預設：本地方法論、精挑過的 SP 驗證／TDD／review skills、需要時你再親自呼叫的 Matt library，外加一個低頻的 advisory router。

它**不會**擅自塞 `using-superpowers`／`brainstorming` 那類 bootstrap，也不亂動 vendor hooks——那些得你自己點名才裝。客戶端目錄（`.cursor`／`.claude`／`.codex`／`.agents`）都是**安裝產物、不進 git**：永遠靠 install 重新生成，別手改完偷偷塞回倉裡。

```bash
# 裝給某一台客戶端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 驗一下裝出來的配置齊不齊
bash tools/harness/agent-kit.sh validate

# 只想看看會裝哪些、先不落地（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 參數 | 可選值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `--process-scaffold`（可選） | `lean`、`guided`、`structured`；只調 advisory 提示的密度，**不動** enforcement 強度 |

本機起步最常見的做法——四台客戶端一次全上：

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

repo 的 profile 一律走 CLI 讀寫（別手動去編 YAML，那是自找麻煩）。要把這套設定帶去別的倉，先 export、再 check：

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# 把可攜 profile 匯出到某輛 subject；接好 fragment 後再回頭驗一次
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` 只是留給舊流程的「整組插件」相容入口，早就不是推薦裝法了。預設 library 落地時不會複製 vendor plugin、hooks，或任何沒進 allowlist 的 skill。

## 把自己的車開進來（選配：接一輛 subject）

只是想確認本廠能不能跑出全綠？那你**什麼都不用接**——公開 clone 不依賴任何私有業務倉，光憑本體就能把可信集跑成滿江綠。

真的要 sync／import／compare 一輛實際的 subject，才需要走這道工序：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 把 remotes 改成你有權限的倉庫，然後：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本機 harness-ready（注意：這不是公開可信集）
```

順序背一條口訣就好：**建 `manifest.yaml` → sync → `--pin` 寫回版本 → `check-local-absorb.sh` 確認 `harness-ready`**；過了這關，才輪到 import／compare／score 上場。

下面這些都是本機私有、早被 `.gitignore` 擋在 git 門外——別費勁往提交裡塞，pre-commit hook 也會當場攔下來：

- `subjects/manifest.yaml`
- 各 subject 的 `pin.json` 與 `checkout/`
- `snapshots/`、`comparisons/`

---

以下是日常參考區，需要時再翻，不用一口氣讀完。

## 常用命令（工具牆速查）

| 想幹嘛 | 敲這行 |
|------|------|
| 跑公開可信集（測功機／CI 同構） | `bash tools/harness/test-harness.sh` |
| 校驗 Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| 同步 harness 表面 | `bash tools/sync/sync-subjects.sh` |
| 寫回 pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| 檢查本機 absorb 就緒 | `bash tools/harness/check-local-absorb.sh --all` |
| 導入 snapshot | `python3 tools/import/import_subject.py --all` |
| 產出比較報告 | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| 評分 | `python3 tools/score/score_subject.py <id>` |
| 週報 | `python3 tools/harness/weekly_report.py` |

## 廠房平面圖（哪個零件擺在哪）

| 路徑 | 這是啥 | 進 git？ |
|------|------|----------|
| `agent-kit/skills` | 開源方法論（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | 各客戶端的 hooks／settings 模板 | ✓ |
| `.cursor`／`.agents`／`.claude`／`.codex` | install 產物 | ✗ |
| `subjects/manifest.example.yaml` | 公開 registry 範本 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 本機 registry／clone | ✗ |
| `tools/` | sync／import／compare／score／可信集／hooks | ✓ |
| `testdata/` | 公開 fixture（CI 用） | ✓ |
| `snapshots/`、`comparisons/` | 吸收產物 | ✗ |
| `docs/harness/` | 設計與帳本 | 部分 |
| `AGENTS.md` | 約束 SSOT（`CLAUDE.md` 指向它） | ✓ |

## 說明書櫃（想深挖再翻）

- [`docs/README.md`](docs/README.md) — 文檔該落在哪的約定
- [`docs/harness/design.md`](docs/harness/design.md) — 本倉 harness 的設計
- [`docs/specs/`](docs/specs/) — 設計文檔歸檔
- [`AGENTS.md`](AGENTS.md) — 完成定義、黑名單、機關落點

## 授權

[MIT](LICENSE)——想開走隨你，出廠證明附在這。
