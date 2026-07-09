# agent-kit

方法論與施工件來自開源倉庫，以 **git submodule** 掛在 `skills/`：

- remote: https://github.com/JohnnySun/skills.git
- 本機客戶端 `skills/` 由 `bash tools/harness/agent-kit.sh install` 鏈到 `agent-kit/skills/skills/<name>`（客戶端樹不進 git）
- hooks/settings 模板：`agent-kit/hooks/clients/`（install 寫入 `.cursor` / `.claude` / `.codex`）

```bash
git submodule update --init --recursive
CLIENT=cursor bash tools/harness/agent-kit.sh install
# 可選：CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

不要把 subject 業務 skill 拷進或 symlink 進本目錄（見根 `AGENTS.md` 黑名單）。
