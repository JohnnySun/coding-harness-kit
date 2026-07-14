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

> **สรุปในบรรทัดเดียว:** ที่นี่คืออู่แต่ง *ราวกันตก* ให้ repo ของคุณ สิ่งที่ขึ้นลิฟต์ไม่ใช่โค้ดธุรกิจ แต่คือ **coding harness** ที่หุ้มอยู่รอบ ๆ—ชั้นที่กันไม่ให้ AI (Cursor, Claude Code, Codex) ลัดขั้นตอน แกล้งบอกว่า “เสร็จแล้ว” หรือยัดของที่ไม่ควร commit เข้า git
>
> **คุณได้อะไร:** จะขับด้วย methodology skills ที่จูนมาแล้วและ hooks แบบกันพลาดของเราทันที หรือยกราวกันตกชุดเดียวกันไปติด repo ของคุณเองก็ได้ เราไม่แตะเครื่องยนต์ (source ธุรกิจของคุณ) แค่เชื่อมโรลเคจด้านนอกให้แน่นจน AI ขยำรถเล่นไม่ได้ง่าย ๆ
>
> **สามเกียร์ก่อนออกตัว:** ติดตั้งบรรทัดเดียว → (บิดกุญแจ) ขึ้นชั้น Agent-Kit → (เลือกได้) ขับ subject ของคุณเข้ามา ก่อนปิดอู่ให้รัน `bash tools/harness/test-harness.sh`—หน้าปัดเขียวทั้งแผงคือผ่านตรวจ พร้อมลงถนน

## ศัพท์ช่างประจำอู่

คำเหล่านี้จะโผล่ตลอดทั้งเอกสาร ทำความรู้จักครั้งเดียว แล้วอ่านส่วนที่เหลือได้ยาว ๆ

| ศัพท์ช่าง | ความหมายแบบตรงไปตรงมา |
|-----------|-------------------------|
| **coding harness** | “รถ” ที่เราลงมือแต่งจริง ๆ: ชั้นราวกันตกสำหรับการพัฒนาด้วย AI รอบ repo ผลิตภัณฑ์ทั้งหมด—rules, skills, hooks, trusted suite และ ledgers |
| **subject** | Repo ผลิตภัณฑ์ที่ขับเข้าช่องซ่อมเพื่อ absorb / compare; clone ไว้ในเครื่องเท่านั้น และ **ไม่เคย** commit ที่นี่ |
| **harness surface** | แผงแต่งของรถ (`AGENTS.md`, skills, hooks)—ไม่ใช่เครื่องยนต์ (source ธุรกิจ) |
| **Agent-Kit** | ตัวติดตั้งชั้นวางอะไหล่—นำ methodology skills / hook templates ไปวางใน Cursor, Claude Code, Codex ฯลฯ |
| **public trusted suite** | `bash tools/harness/test-harness.sh`—การขึ้น dyno ก่อนอู่นี้ปล่อยงานใด ๆ (เครื่องเดียวกับ L2 CI) |

## เลนเร็วสุด: รับรถด้วยคำสั่งเดียว

คำสั่งเดียวจัดให้ครบ: clone อู่ ดึง submodules ติดตั้ง git hooks ขึ้นชั้น Agent-Kit แล้วส่งตรงขึ้น dyno (public trusted suite)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

ไฮเทคไปหน่อย? pipe แบบดั้งเดิมสตาร์ตเครื่องเดียวกัน:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

อยากเลือกว่าจะลงที่ไหนและต่อสายให้ใคร? ตั้ง environment variables สองตัวนี้:

- `TARGET_DIR` — directory ที่จะติดตั้ง
- `CLIENT` — client ที่จะต่อสาย: `cursor` / `claude` / `codex` / `codex-native` หรือ `skip` เพื่อไว้ติด Agent-Kit ภายหลัง

คำสั่งบรรทัดเดียวยังขึ้นชั้น Agent-Kit และรัน suite ให้ด้วย—**คนส่วนใหญ่ดับเครื่องแล้วกลับบ้านตรงนี้ได้เลย** ถ้าอยากติดทีละชิ้น หรือคำสั่งสะดุดกลางทาง ให้เข้าเลน manual ด้านล่าง

## รับรถแบบ manual (ลงมือประกอบเอง)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

ตอนนี้แค่เปิดประตูช่องซ่อม—ลังอะไหล่ (Agent-Kit) ยังวางอยู่บนพื้น ไปต่อกัน

## ขึ้นชั้น Agent-Kit (ยกลังอะไหล่ขึ้นผนัง)

Agent-Kit นำ methodology skills และ hooks ของ repo นี้ไปติดตั้งใน editor / CLI ของคุณ การติดตั้งเปล่า ๆ ให้ชุดมาตรฐานที่จูนมาแล้ว: methodology ในเครื่อง, SP skills ที่คัดสรรสำหรับ verification / TDD / review, Matt library ที่เรียกใช้เมื่อคุณต้องการ และ advisory router ที่โผล่มาเฉพาะจังหวะสำคัญ

มัน **ไม่** แอบติด bootstrap `using-superpowers` / `brainstorming` และไม่ยุ่งกับ vendor hooks—ของเหล่านั้นต้องเลือกเอง Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) คือ **output จากการติดตั้งและห้าม commit**: สร้างใหม่ด้วย install เสมอ อย่าแก้ด้วยมือแล้วลักลอบยัดกลับเข้า git

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | ค่า |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (เลือกได้) | `lean`, `guided`, `structured`; เปลี่ยนเฉพาะความหนาแน่นของ advisory prompts—**ไม่เคย** แตะ enforcement |

Bootstrap ในเครื่องที่ใช้กันบ่อยที่สุด—ติดตั้งทั้งสี่ client ในคราวเดียว:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Repo profile ต้องจัดการผ่าน CLI เสมอ (แก้ YAML ด้วยมือคือชวนปัญหาเข้าช่องซ่อม) หากจะยกการตั้งค่าไป repo อื่น ให้ export ก่อนแล้วค่อย check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` เหลือไว้เป็นช่อง compatibility แบบ full-plugin ที่ต้องเลือกชัดเจนสำหรับ workflows เก่าเท่านั้น—ไม่ใช่เส้นทางแนะนำแล้ว Default library materialization จะไม่คัดลอก vendor plugins, hooks หรือ skills ใด ๆ นอก allowlist

## ขับรถของคุณเข้ามา (เลือกได้: ต่อ subject)

แค่อยากเช็กว่าอู่ขึ้นไฟเขียวครบไหม? **ไม่ต้องต่ออะไรเลย**—public clone ไม่พึ่ง repo ผลิตภัณฑ์ส่วนตัวแม้แต่น้อย และยังรัน trusted suite จนเขียวทั้งแผงได้

รันชุดนี้เฉพาะเมื่อคุณต้องการ sync / import / compare subject จริง:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

จำลำดับเดียวนี้ไว้: **สร้าง `manifest.yaml` → sync → ใช้ `--pin` เขียน version กลับ → รัน `check-local-absorb.sh` จนเป็น `harness-ready`** ผ่าน gate นี้ก่อน แล้ว import / compare / score จึงจะทำงานได้

รายการเหล่านี้อยู่ในเครื่องและถูก gitignore ไว้แล้ว อย่าฝืนยัดเข้า commit เพราะ pre-commit hook จะเด้งกลับหน้าประตูทันที:

- `subjects/manifest.yaml`
- `pin.json` และ `checkout/` ของแต่ละ subject
- `snapshots/`, `comparisons/`

---

ด้านล่างคือผนังเครื่องมืออ้างอิงประจำวัน หยิบเฉพาะชิ้นที่ต้องใช้ ไม่ต้องอ่านรวดเดียวทั้งหมด

## คำสั่งที่ใช้บ่อย (ผนังเครื่องมือ)

| สิ่งที่ต้องการ | คำสั่งที่ต้องรัน |
|----------------|------------------|
| Public trusted suite (dyno / รูปแบบเดียวกับ CI) | `bash tools/harness/test-harness.sh` |
| ตรวจสอบ Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| เขียน pin ใหม่ | `bash tools/sync/sync-subjects.sh <id> --pin` |
| ตรวจความพร้อมของ local absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| สร้าง compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| ทำ score | `python3 tools/score/score_subject.py <id>` |
| สร้างรายงานประจำสัปดาห์ | `python3 tools/harness/weekly_report.py` |

## แผนผังอู่ (อะไหล่อยู่ตรงไหน)

| Path | คืออะไร | อยู่ใน git? |
|------|---------|------------|
| `agent-kit/skills` | Methodology แบบเปิด (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings templates แยกตาม client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output จากการติดตั้ง | ✗ |
| `subjects/manifest.example.yaml` | ตัวอย่าง registry สาธารณะ | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone ในเครื่อง | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures สาธารณะ (CI) | ✓ |
| `snapshots/` / `comparisons/` | ผลผลิตจาก absorb | ✗ |
| `docs/harness/` | Design + ledgers | บางส่วน |
| `AGENTS.md` | SSOT ของ constraints (`CLAUDE.md` ชี้มาที่นี่) | ✓ |

## ชั้นคู่มือ (อ่านต่อ)

- [`docs/README.md`](../README.md) — กฎการวางเอกสาร
- [`docs/harness/design.md`](../harness/design.md) — design ของ harness ใน repo นี้
- [`docs/specs/`](../specs/) — archive ของ design
- [`AGENTS.md`](../../AGENTS.md) — นิยามความเสร็จ, blacklist และแผนผังกลไก

## สัญญาอนุญาต

[MIT](../../LICENSE) — ขับออกจากอู่ไปใช้แบบไหนก็ได้ เอกสารรถพร้อมอยู่ตรงนี้แล้ว
