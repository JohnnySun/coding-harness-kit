# agent-kit

方法論與施工件來自開源倉庫，以 **git submodule** 掛在 `skills/`：

- remote: https://github.com/JohnnySun/skills.git
- 本機客戶端 `skills/` 由 `bash tools/harness/agent-kit.sh install` 鏈到 `agent-kit/skills/skills/<name>`（客戶端樹不進 git）
- hooks/settings 模板：`agent-kit/hooks/clients/`（install 寫入 `.cursor` / `.claude` / `.codex`）

```bash
git submodule update --init --recursive
CLIENT=cursor bash tools/harness/agent-kit.sh install
bash tools/harness/agent-kit.sh profile show
```

裸 install 已包含精選 SP 核心、使用者主動呼叫的 Matt library 與 profile-aware advisory router；不會 materialize SP bootstrap 或 vendor hooks。設定 SSOT 是 `.harness/agent-profile.yaml`，Agent 只經 `agent-kit.sh profile set` 寫入。`PLUGIN` 僅保留為顯式完整插件相容入口。

輸出到 subject：

```bash
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
# export 會接管該 client 的 prompt-submit advisory event：以 portable runtime
# 取代既有 advisory router，但保留其他 hook events。合併規則契約後：
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

Subject 不維護平行 prompt router 正文。`.harness/profile-runtime/` 與
`.harness/profile-wiring/` 是 agent-kit export 產物；再次 export 會覆蓋 runtime，
並停用原 prompt-submit event 上的舊 advisory 注入路徑。`profile check` 只接受
該 managed runtime 作為 prompt-submit 入口。

不要把 subject 業務 skill 拷進或 symlink 進本目錄（見根 `AGENTS.md` 黑名單）。
