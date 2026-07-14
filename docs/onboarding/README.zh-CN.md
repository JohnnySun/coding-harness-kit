# 洛圣都改车王（Los Santos Customs）

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <strong>简体中文</strong> |
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

> **这间改装厂改的是你的车：coding harness。** 它是包在产品仓外面的 AI 开发防护层；产品仓（subject）拥有这台车，业务源码是引擎，本厂不拆。
> 最短路线：执行一键安装 → 为 Cursor／Claude Code／Codex 安装 Agent-Kit →（可选）接入真实 subject，依次 sync、pin、检查 `harness-ready`。零件装完要上测功机，不能只看车漆。

| 术语 | 含义（改装厂对照） |
|------|------|
| **coding harness** | 你的「车」：包在业务仓外层的 AI 开发防护体系（规则、skills、hooks、可信集、账本） |
| **subject** | 拥有这台车的产品／业务仓（本机 clone，不进本仓 git） |
| **harness 表面** | 零件安装面：`AGENTS.md`、skills、hooks 等；业务源码不在工单内 |
| **Agent-Kit** | 零件架：把方法论 skills / hooks 模板装进 Cursor、Claude Code、Codex 等客户端 |
| **公开可信集** | 测功机：`bash tools/harness/test-harness.sh`（与 L2 CI 同构） |

## 1. 进厂（初始化）

最快的工位是一键安装。它会完成 clone、submodule、git hooks、Agent-Kit，并运行公开可信集：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

如果你的 shell 不接受 process substitution，改用等价的 pipe 写法：

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

可选环境变量是 `TARGET_DIR` 和 `CLIENT`。`CLIENT` 可设为 `cursor` / `claude` / `codex` / `codex-native` / `skip`。

想逐项看技师动手，或一键安装不适用时，手动执行：

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# 若克隆时漏了 --recurse-submodules
git submodule update --init --recursive

# 装 L1 安检（拒收私有树、必要时跑可信集）
bash tools/harness/install-git-hooks.sh
```

完成后，你应该位于 `los-santos-customs/`，submodule 已初始化，git hooks 已安装。一键路线还会为所选客户端装好 Agent-Kit 并运行公开可信集；手动路线请继续 §2。手动挡多一个步骤，这次不是情怀。

## 2. 装零件（Agent-Kit）

Agent-Kit 把本厂的 skills 和 hooks 装进编辑器／CLI。裸 install 会安装这套有主见的默认配置：

- 本地方法论；
- 精选 SP 验证／TDD／review skills；
- 由用户主动调用的 Matt library；
- 低频 advisory router。

它不安装 `using-superpowers`／`brainstorming` bootstrap 或 vendor hooks。客户端目录（`.cursor` / `.claude` / `.codex` / `.agents`）是安装产物，不进 git；坏了就重新 install，不必给生成文件做钣金。

```bash
# 装到指定客户端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 校验零件是否装齐
bash tools/harness/agent-kit.sh validate

# 预览（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 参数 | 可选值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `--process-scaffold`（可选） | `lean`、`guided`、`structured`；只调 advisory 密度 |

```bash
# 四个客户端都装一遍（常见本机起步）
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# 查看或调整 repo profile（Agent 一律经 CLI 写入）
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# 输出可携 profile 到 subject；依 fragment 接线后检查
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` 只保留作旧流程的显式完整插件兼容入口，不再是推荐安装方式。默认 library materialization 不会复制 vendor plugin、hooks 或未列入 allowlist 的 skill；零件架有清单，不靠地上那盒“可能用得到”。

## 3. （可选）把自己的车开进来

公开 clone 不需要任何私有业务仓，也能把公开可信集跑绿。只有要 sync / import / compare 真实 subject 时，才把客户的车接进本机工位：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 编辑 remotes 为你有权限的仓库，再：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本机 harness-ready（非公开套件）
```

顺序很重要：

1. 从范本建立 `subjects/manifest.yaml`，把 remotes 改成你有权限访问的仓库。
2. 执行 sync，取得 subject 的 harness 表面。
3. 用 `<id> --pin` 记录要评估的准确版本。
4. 运行本机 absorb 检查；通过才是 `harness-ready`，之后才能可靠地 import、compare、score。

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` 都是客户车辆和工单资料：只留本机，已被 `.gitignore` 挡住，不会停进公开展厅。这不是神秘，是基本的钥匙管理。

---

新车已经能走了。以下是日常保养资料，按需查阅。

## 常用命令

| 目的 | 命令 |
|------|------|
| 公开可信集（收环 / CI 同构） | `bash tools/harness/test-harness.sh` |
| 校验 Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| 同步 harness 表面 | `bash tools/sync/sync-subjects.sh` |
| 写回 pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| 本机 absorb 就绪 | `bash tools/harness/check-local-absorb.sh --all` |
| 导入 snapshot | `python3 tools/import/import_subject.py --all` |
| 比较报告 | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| 评分 | `python3 tools/score/score_subject.py <id>` |
| 周报 | `python3 tools/harness/weekly_report.py` |

## 仓库布局

| 路径 | 角色 | 进 git？ |
|------|------|----------|
| `agent-kit/skills` | 开源方法论（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | 各客户端 hooks/settings 模板 | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | install 产物 | ✗ |
| `subjects/manifest.example.yaml` | 公开 registry 范本 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 本机 registry / clone | ✗ |
| `tools/` | sync / import / compare / score / 可信集 / hooks | ✓ |
| `testdata/` | 公开 fixture（CI 用） | ✓ |
| `snapshots/`、`comparisons/` | 吸收产物 | ✗ |
| `docs/harness/` | 设计与账本 | 部分 |
| `AGENTS.md` | 约束 SSOT（`CLAUDE.md` → 之） | ✓ |

## 文件

- [`docs/README.md`](../README.md) — 文档落点约定
- [`docs/harness/design.md`](../harness/design.md) — 本仓 harness 设计
- [`docs/specs/`](../specs/) — 设计文档归档
- [`AGENTS.md`](../../AGENTS.md) — 完成定义、黑名单、机关落点

## 授权

[MIT](../../LICENSE)
