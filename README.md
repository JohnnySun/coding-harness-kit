# coding-harness-kit

A harness for building and iterating **coding harnesses** across subjects  
（導入 / 同步 / 比較 / 評價）。業務源碼不是一等公民；工作對象是 harness 表面。

本倉設計為**可公開提交**：工具與開源方法論進 git；subject 本體、吸收產物、以及各 AI 客戶端安裝樹留本機。

## 佈局

| 路徑 | 角色 | 進 git |
|------|------|--------|
| `agent-kit/skills` | 開源方法論（git submodule → JohnnySun/skills） | ✓ |
| `agent-kit/hooks/clients/` | 各客戶端 hooks/settings 模板（install SSOT） | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | **install 產物**（skills + hooks） | ✗ |
| `subjects/manifest.example.yaml` | 公開 registry 範本 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 本機 registry / clone | ✗ |
| `tools/` | sync / import / compare / score / 可信集 / hooks | ✓ |
| `snapshots/`、`comparisons/` | import / 評分產物（吸收 subject） | ✗ |
| `docs/harness/` | 設計、結構帳本；runtime jsonl/reports 本機 | 部分 |
| `AGENTS.md` | 約束 SSOT（`CLAUDE.md` → 之） | ✓ |

## 首次本機

```bash
git submodule update --init --recursive

# 安裝 AI 客戶端表面（skills + hooks）；可選 PLUGIN=…
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
# 可選插件：CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install

cp subjects/manifest.example.yaml subjects/manifest.yaml
# 編輯 remotes 為你有權限的 subject，再：
bash tools/sync/sync-subjects.sh
bash tools/harness/test-harness.sh
bash tools/harness/install-git-hooks.sh   # L1
```

## 常用命令

```bash
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/test-harness.sh
bash tools/harness/agent-kit.sh validate
CLIENT=cursor bash tools/harness/agent-kit.sh install
python3 tools/import/import_subject.py --all          # → 本機 snapshots/
python3 tools/compare/compare_subjects.py -o comparisons/report.md
python3 tools/score/score_subject.py <id>
python3 tools/harness/weekly_report.py
```

## 狀態

- 設計：[`docs/harness/design.md`](docs/harness/design.md)
- 脫敏邊界：見 `AGENTS.md`「公開 / 本機邊界」
- L2 CI：`.github/workflows/harness-trusted.yml`
