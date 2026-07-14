# Los Santos Customs

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

> 用来**构建 / 迭代 coding harness** 的开源工具仓。  
> 本仓不含业务源码；工作对象是各业务仓（subject）的 **harness 表面**。  
> 克隆后三步即可开始：初始化 submodule → 安装 Agent-Kit →（可选）同步你的 subject。

| 术语 | 含义 |
|------|------|
| **coding harness** | 包在业务仓外层的 AI 开发防护体系：规则、skills、hooks、可信集、账本 |
| **subject** | 被本工具吸收 / 比较的一个业务仓（本机 clone，不进本仓 git） |
| **harness 表面** | subject 里与 harness 相关的路径（如 `AGENTS.md`、skills、hooks），不是业务源码 |
| **Agent-Kit** | 把方法论 skills / hooks 模板安装到 Cursor、Claude Code、Codex 等客户端的安装器 |
| **公开可信集** | `bash tools/harness/test-harness.sh`——本仓自己的一键验证（与 L2 CI 同构） |

## 1. 初始化

一键安装（克隆 + submodule + git hooks + Agent-Kit + 公开可信集）：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/coding-harness-kit/main/scripts/install.sh)
```

等价写法：

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/coding-harness-kit/main/scripts/install.sh | bash
```

可选环境变量：`TARGET_DIR`、`CLIENT`（`cursor` / `claude` / `codex` / `codex-native` / `skip`）、`PLUGIN`。

或手动分步执行：

```bash
git clone --recurse-submodules https://github.com/JohnnySun/coding-harness-kit.git
cd coding-harness-kit

# 若克隆时漏了 --recurse-submodules
git submodule update --init --recursive

# 安装 git pre-commit hook（拒收私有树、必要时跑可信集）
bash tools/harness/install-git-hooks.sh
```

## 2. 安装 Agent-Kit（AI 工具）

Agent-Kit 为 Cursor / Claude Code / Codex 提供本工程的 skills 与 hooks。裸 install 默认包含精选 SP 核心、用户主动调用的 Matt library 与低频 advisory router；不安装全局 bootstrap 或 vendor hooks。
客户端目录（`.cursor` / `.claude` / `.codex` / `.agents`）是**安装产物，不进 git**——一律用 install 再生。

```bash
# 安装到指定客户端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 校验配置是否完整
bash tools/harness/agent-kit.sh validate

# 预览安装内容（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 参数 | 可选值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `--process-scaffold`（可选） | `lean`、`guided`、`structured`；只调整 advisory 密度 |

```bash
# 四个客户端都装一遍（常见本机起步）
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# 查看或调整 profile
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided
```

`PLUGIN` 仅保留为旧流程的显式完整插件兼容入口，不再是推荐安装方式。

## 3. （可选）接入你自己的 subject

公开 clone **不需要**任何私有业务仓即可跑绿可信集。  
若要 sync / import / compare 真实 subject：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 编辑 remotes 为你有权限的仓库，再：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本机 harness-ready（非公开套件）
```

`subjects/manifest.yaml`、`pin.json`、`checkout/`、`snapshots/`、`comparisons/` 均为本机私有，已被 `.gitignore` 挡住。

---

以下为日常参考，按需查阅。

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

## 文档

- [`docs/README.md`](../README.md) — 文档落点约定
- [`docs/harness/design.md`](../harness/design.md) — 本仓 harness 设计
- [`docs/specs/`](../specs/) — 设计文档归档
- [`AGENTS.md`](../../AGENTS.md) — 完成定义、黑名单、机关落点

## 许可

[MIT](../../LICENSE)
