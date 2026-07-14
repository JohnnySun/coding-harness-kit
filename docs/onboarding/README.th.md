# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
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
  <strong>ไทย</strong> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> ชุดเครื่องมือโอเพนซอร์สสำหรับ **สร้างและทำซ้ำ coding harness** ไม่มีซอร์สธุรกิจ ทำงานบน **พื้นผิว harness** ของแต่ละ subject สามขั้นตอน: submodules → Agent-Kit → (ทางเลือก) sync

| Term | Meaning |
|------|---------|
| **coding harness** | AI-dev guardrail layer around a product repo |
| **subject** | Product repo absorbed/compared locally (not committed here) |
| **harness surface** | Harness-related paths in a subject — not business source |
| **Agent-Kit** | Installer for skills/hooks into Cursor / Claude Code / Codex |
| **public trusted suite** | `bash tools/harness/test-harness.sh` |

## 1. เริ่มต้น

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

## 2. ติดตั้ง Agent-Kit (เครื่องมือ AI)

```bash
CLIENT=<client> bash tools/harness/agent-kit.sh install
bash tools/harness/agent-kit.sh validate
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Values |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `PLUGIN` | `superpowers`, `mattpocock-skills` |

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

## 3. เชื่อม subject ของคุณ (ทางเลือก)

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all
```

---

อ้างอิงประจำวัน

## คำสั่งที่ใช้บ่อย

| Purpose | Command |
|---------|---------|
| Public trusted suite | `bash tools/harness/test-harness.sh` |
| Validate Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Rewrite pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Layout

See [English README](README.en.md#layout) for the full path table. Client trees are install outputs and stay out of git.

## เอกสาร

- [`docs/README.md`](../README.md)
- [`docs/harness/design.md`](../harness/design.md)
- [`docs/specs/`](../specs/)
- [`AGENTS.md`](../../AGENTS.md)

## สัญญาอนุญาต

[MIT](../../LICENSE)
