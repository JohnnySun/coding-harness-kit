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

> **一句话：** 这是一间专门帮你的代码仓「改装防护」的改车厂。真正上举升机的不是你的业务代码，而是包在它外面那层 **coding harness**——让 AI（Cursor／Claude Code／Codex）帮你写代码时，不会偷工减料、不会谎报完工、不会把不该提交的东西塞进 git。
>
> **跟你什么关系：** 你要么直接用我们调校好的方法论 skills 与防呆 hooks，要么把同一套护栏搬到你自己的仓上。引擎（业务源码）我们一颗螺丝都不碰，只把外圈的钢骨焊到 AI 撞不坏。
>
> **怎么进厂（三档）：** 一键安装 →（引擎点火）上架 Agent-Kit →（选配）把你自己的车开进来。收工前踩一脚 `bash tools/harness/test-harness.sh`，仪表盘全绿＝验车通过、可以上路。

## 术语表（进厂先学黑话）

这几个词后面到处都会用，先在这里认一次，之后不再重复解释。

| 黑话 | 白话 |
|------|------|
| **coding harness** | 厂里真正动手改的那台「车」——包在业务仓外的一整套 AI 开发护栏：规则、skills、hooks、可信集、账本 |
| **subject** | 一辆开进厂里被吸收／比较的业务仓；只在你本机 clone，**不会**跟着本仓进 git |
| **harness 表面** | 车身上跟改装有关的那些面板（`AGENTS.md`、skills、hooks）；不是引擎本体（业务源码） |
| **Agent-Kit** | 零件箱上架器——把方法论 skills／hooks 模板装进 Cursor、Claude Code、Codex 等客户端 |
| **公开可信集** | `bash tools/harness/test-harness.sh`——出厂前的测功机（dyno），跟线上 L2 CI 同一套 |

## 一键进厂（最快路线）

一行指令包全套：克隆本厂、拉齐 submodule、装好 git hooks、上架 Agent-Kit，最后直接推上测功机跑一圈公开可信集。

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

嫌上面那写法花哨？老派管道也一样能开：

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

想指定一下装哪、配谁，补这两个环境变量：

- `TARGET_DIR` — 装进哪个目录
- `CLIENT` — 配哪台客户端：`cursor`／`claude`／`codex`／`codex-native`，或填 `skip` 这趟先不碰 Agent-Kit

一键路线会顺手把 Agent-Kit 也装好、可信集也跑完——**多数人到这里就能熄火收工**。想自己一档一档慢慢挂，或者一键跑到一半断线了，往下走手动路线。

## 手动进厂（自己拆步骤）

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# 克隆时忘了 --recurse-submodules？补这一句把零件补齐
git submodule update --init --recursive

# 焊上 git pre-commit hook：挡住私有树误闯 git，必要时顺手踩一脚可信集
bash tools/harness/install-git-hooks.sh
```

跑到这里只是**厂房铁门拉开了**——零件箱（Agent-Kit）还晾在旁边没上架。接着下一节。

## 上架 Agent-Kit（把零件箱装进工具墙）

Agent-Kit 负责把本仓的方法论 skills 与 hooks 塞进你的编辑器／CLI。裸装一次就给你一套调校好的默认：本地方法论、精挑过的 SP 验证／TDD／review skills、需要时你再亲自调用的 Matt library，外加一个低频的 advisory router。

它**不会**擅自塞 `using-superpowers`／`brainstorming` 那类 bootstrap，也不乱动 vendor hooks——那些得你自己点名才装。客户端目录（`.cursor`／`.claude`／`.codex`／`.agents`）都是**安装产物、不进 git**：永远靠 install 重新生成，别手改完偷偷塞回仓里。

```bash
# 装给某一台客户端
CLIENT=<client> bash tools/harness/agent-kit.sh install

# 验一下装出来的配置齐不齐
bash tools/harness/agent-kit.sh validate

# 只想看看会装哪些、先不落地（dry-run）
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 参数 | 可选值 |
|------|--------|
| `CLIENT` | `cursor`、`cursor-cli`、`claude`、`codex`、`codex-native` |
| `--process-scaffold`（可选） | `lean`、`guided`、`structured`；只调 advisory 提示的密度，**不动** enforcement 强度 |

本机起步最常见的做法——四台客户端一次全上：

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

repo 的 profile 一律走 CLI 读写（别手动去编 YAML，那是自找麻烦）。要把这套设定带去别的仓，先 export、再 check：

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# 把可携 profile 导出到某辆 subject；接好 fragment 后再回头验一次
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` 只是留给旧流程的「整组插件」兼容入口，早就不是推荐装法了。默认 library 落地时不会复制 vendor plugin、hooks，或任何没进 allowlist 的 skill。

## 把自己的车开进来（选配：接一辆 subject）

只是想确认本厂能不能跑出全绿？那你**什么都不用接**——公开 clone 不依赖任何私有业务仓，光凭本体就能把可信集跑成满江绿。

真的要 sync／import／compare 一辆实际的 subject，才需要走这道工序：

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# 把 remotes 改成你有权限的仓库，然后：
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # 本机 harness-ready（注意：这不是公开可信集）
```

顺序背一条口诀就好：**建 `manifest.yaml` → sync → `--pin` 写回版本 → `check-local-absorb.sh` 确认 `harness-ready`**；过了这关，才轮到 import／compare／score 上场。

下面这些都是本机私有、早被 `.gitignore` 挡在 git 门外——别费劲往提交里塞，pre-commit hook 也会当场拦下来：

- `subjects/manifest.yaml`
- 各 subject 的 `pin.json` 与 `checkout/`
- `snapshots/`、`comparisons/`

---

以下是日常参考区，需要时再翻，不用一口气读完。

## 常用命令（工具墙速查）

| 想干嘛 | 敲这行 |
|------|------|
| 跑公开可信集（测功机／CI 同构） | `bash tools/harness/test-harness.sh` |
| 校验 Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| 同步 harness 表面 | `bash tools/sync/sync-subjects.sh` |
| 写回 pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| 检查本机 absorb 就绪 | `bash tools/harness/check-local-absorb.sh --all` |
| 导入 snapshot | `python3 tools/import/import_subject.py --all` |
| 产出比较报告 | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| 评分 | `python3 tools/score/score_subject.py <id>` |
| 周报 | `python3 tools/harness/weekly_report.py` |

## 厂房平面图（哪个零件摆在哪）

| 路径 | 这是啥 | 进 git？ |
|------|------|----------|
| `agent-kit/skills` | 开源方法论（submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | 各客户端的 hooks／settings 模板 | ✓ |
| `.cursor`／`.agents`／`.claude`／`.codex` | install 产物 | ✗ |
| `subjects/manifest.example.yaml` | 公开 registry 范本 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 本机 registry／clone | ✗ |
| `tools/` | sync／import／compare／score／可信集／hooks | ✓ |
| `testdata/` | 公开 fixture（CI 用） | ✓ |
| `snapshots/`、`comparisons/` | 吸收产物 | ✗ |
| `docs/harness/` | 设计与账本 | 部分 |
| `AGENTS.md` | 约束 SSOT（`CLAUDE.md` 指向它） | ✓ |

## 说明书柜（想深挖再翻）

- [`docs/README.md`](../README.md) — 文档该落在哪的约定
- [`docs/harness/design.md`](../harness/design.md) — 本仓 harness 的设计
- [`docs/specs/`](../specs/) — 设计文档归档
- [`AGENTS.md`](../../AGENTS.md) — 完成定义、黑名单、机关落点

## 授权

[MIT](../../LICENSE)——想开走随你，出厂证明附在这。
