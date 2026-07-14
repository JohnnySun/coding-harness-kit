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

> **อู่นี้ดูแลรถของคุณ: coding harness** ซึ่งเป็นชั้น guardrail สำหรับการพัฒนาด้วย AI ที่ล้อมรอบ repo ผลิตภัณฑ์ repo ผลิตภัณฑ์นั้น—หรือ subject—เป็นเจ้าของรถ ส่วน source ธุรกิจคือเครื่องยนต์ และเราจะไม่เปิดเครื่องยนต์
> เส้นทางสั้น: รันคำสั่งรับรถบรรทัดเดียว → ติดตั้ง Agent-Kit สำหรับ Cursor, Claude Code หรือ Codex → เชื่อมต่อ subject จริงหากต้องการ แล้วจึง sync, pin และตรวจสอบ `harness-ready` Part ใหม่ยังต้องขึ้น dyno การตรวจสีรถไม่ใช่แผนการทดสอบ

| คำศัพท์ | ความหมาย (เทียบกับอู่) |
|------|---------|
| **coding harness** | รถของคุณ: ชั้น guardrail สำหรับ AI-dev รอบ repo ผลิตภัณฑ์ (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Repo ผลิตภัณฑ์ที่เป็นเจ้าของรถ (clone ในเครื่อง; ไม่ commit ที่นี่) |
| **harness surface** | ช่องเก็บ part: `AGENTS.md`, skills, hooks และไฟล์ guardrail ที่คล้ายกัน; ไม่ใช่ source ธุรกิจ |
| **Agent-Kit** | ชั้นวาง part: materialize methodology skills / hook templates ลงใน Cursor, Claude Code, Codex และอื่น ๆ |
| **public trusted suite** | Dyno: `bash tools/harness/test-harness.sh` (เหมือนกับ L2 CI) |

## 1. รับรถ (เริ่มต้น)

ทางเข้าอู่ที่เร็วที่สุดคือ installer บรรทัดเดียว โดยจะ clone repo, เริ่มต้น submodules, ติดตั้ง git hooks และ Agent-Kit แล้วรัน public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

หาก shell ของคุณไม่รองรับ process substitution ให้ใช้รูปแบบ pipe ที่เทียบเท่ากัน:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Environment variable ที่เลือกใช้ได้คือ `TARGET_DIR` และ `CLIENT` กำหนด `CLIENT` เป็น `cursor` / `claude` / `codex` / `codex-native` / `skip`

หากต้องการใช้วิธีติดตั้งด้วยตนเอง หรือดูทุกขั้นตอน:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

ตอนนี้คุณควรอยู่ใน `los-santos-customs/` โดยมี submodules ที่เริ่มต้นแล้วและ git hooks ที่ติดตั้งแล้ว เส้นทางบรรทัดเดียวยังติดตั้ง Agent-Kit สำหรับ client ที่คุณเลือกและรัน public suite ด้วย หากเลือกวิธีด้วยตนเอง ให้ไปต่อที่ §2 เกียร์ธรรมดามีขั้นตอนเพิ่มอีกหนึ่งขั้น ซึ่งไม่ใช่เรื่องความคิดถึง

## 2. ติดตั้ง part (Agent-Kit)

Agent-Kit ติดตั้ง skills และ hooks ของอู่นี้ลงใน editor หรือ CLI ของคุณ การติดตั้งพื้นฐานมีค่าเริ่มต้นที่คัดสรรดังนี้:

- methodology ในเครื่อง;
- SP skills ที่คัดสรรสำหรับ verification, TDD และ review;
- Matt library ที่ผู้ใช้เรียกใช้;
- advisory router ความถี่ต่ำ

ระบบไม่ติดตั้ง bootstrap `using-superpowers` / `brainstorming` หรือ vendor hooks Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) เป็น output จากการติดตั้งและจะไม่ถูก commit ให้สร้างใหม่ด้วย install; ไฟล์ที่ generate แล้วไม่ต้องทำตัวถังใหม่

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | ค่า |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (เลือกได้) | `lean`, `guided`, `structured`; ปรับเฉพาะความหนาแน่นของ advisory |

```bash
# Install all four clients (common local bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Inspect or adjust the repo profile (agents write via CLI only)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire fragments, then check
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` ยังคงอยู่เพื่อเป็นเส้นทางความเข้ากันได้แบบ full-plugin ที่ระบุชัดเจนสำหรับ workflow รุ่นเก่าเท่านั้น และไม่ใช่เส้นทางการติดตั้งที่แนะนำอีกต่อไป Default library materialization จะไม่คัดลอก vendor plugins, hooks หรือ skills นอก allowlist; ชั้นวาง part มีรายการสินค้าด้วยเหตุผลนี้

## 3. (เลือกได้) นำรถของคุณเข้าอู่

Public clone สามารถรัน public trusted suite ได้โดยไม่ต้องมี repo ผลิตภัณฑ์ส่วนตัว เชื่อมต่อรถของลูกค้ากับช่องซ่อมในเครื่องเฉพาะเมื่อต้อง sync, import หรือ compare subject จริง:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

ลำดับมีความสำคัญ:

1. สร้าง `subjects/manifest.yaml` จากตัวอย่าง แล้วชี้ remotes ไปยัง repo ที่คุณเข้าถึงได้
2. รัน sync เพื่อ fetch harness surface ของแต่ละ subject
3. ใช้ `<id> --pin` เพื่อบันทึก revision ที่แน่นอนซึ่งคุณต้องการประเมิน
4. รัน local absorb check Subject ที่ผ่านจะเป็น `harness-ready`; หลังจากนั้นเท่านั้น import, compare และ score จึงจะสร้างผลลัพธ์ที่เชื่อถือได้

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` และ `comparisons/` คือรถของลูกค้าและ work order ทั้งหมดจะอยู่ในเครื่อง ถูก gitignore และไม่เข้าสู่ showroom สาธารณะ นี่ไม่ใช่การปกปิด แต่เป็นการควบคุมกุญแจขั้นพื้นฐาน

---

ตอนนี้รถวิ่งได้ด้วยกำลังของตัวเองแล้ว ส่วนที่เหลือคือเอกสารอ้างอิงของช่องบริการ

## คำสั่งที่ใช้บ่อย

| วัตถุประสงค์ | คำสั่ง |
|---------|---------|
| Public trusted suite (ปิด loop / CI) | `bash tools/harness/test-harness.sh` |
| Validate Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| เขียน pin ใหม่ | `bash tools/sync/sync-subjects.sh <id> --pin` |
| ความพร้อมของ local absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| รายงาน compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| รายงานประจำสัปดาห์ | `python3 tools/harness/weekly_report.py` |

## โครงสร้าง

| Path | บทบาท | อยู่ใน git? |
|------|------|---------|
| `agent-kit/skills` | Methodology แบบเปิด (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Template hooks/settings ของ client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output จากการติดตั้ง | ✗ |
| `subjects/manifest.example.yaml` | ตัวอย่าง registry สาธารณะ | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone ในเครื่อง | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture สาธารณะ (CI) | ✓ |
| `snapshots/` / `comparisons/` | ผลิตภัณฑ์จาก absorb | ✗ |
| `docs/harness/` | Design + ledgers | บางส่วน |
| `AGENTS.md` | SSOT ของ constraint (`CLAUDE.md` → ไฟล์นี้) | ✓ |

## เอกสาร

- [`docs/README.md`](../README.md) — กฎการจัดวางเอกสาร
- [`docs/harness/design.md`](../harness/design.md) — design harness ของ repo นี้
- [`docs/specs/`](../specs/) — archive ของ design
- [`AGENTS.md`](../../AGENTS.md) — นิยามความเสร็จสมบูรณ์ blacklist และแผนผังกลไก

## สัญญาอนุญาต

[MIT](../../LICENSE)
