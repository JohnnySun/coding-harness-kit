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
  <strong>हिन्दी</strong> |
  <a href="README.id.md">Bahasa Indonesia</a> |
  <a href="README.vi.md">Tiếng Việt</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **यह दुकान आपकी कार पर काम करती है: coding harness।** यह किसी product repo के चारों ओर AI-development guardrail layer है। वह product repo—यानी subject—कार का मालिक है; उसका business source इंजन है, और हम इंजन को बंद ही रखते हैं।
> छोटा रास्ता: one-line intake चलाएँ → Cursor, Claude Code या Codex के लिए Agent-Kit install करें → चाहें तो वास्तविक subject जोड़ें, फिर sync, pin और `harness-ready` जाँचें। नए parts को फिर भी dyno पर जाना होता है। Paint inspection कोई test plan नहीं है।

| शब्द | अर्थ (दुकान का रूपक) |
|------|---------|
| **coding harness** | आपकी कार: product repo के चारों ओर AI-dev guardrail layer (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | कार का मालिक product repo (local clone; यहाँ commit नहीं होता) |
| **harness surface** | parts bay: `AGENTS.md`, skills, hooks और ऐसी ही guardrail files; business source नहीं |
| **Agent-Kit** | parts rack: methodology skills / hook templates को Cursor, Claude Code, Codex आदि में materialize करता है |
| **public trusted suite** | Dyno: `bash tools/harness/test-harness.sh` (L2 CI के समान) |

## 1. इनटेक (initialize)

सबसे तेज़ रास्ता one-line installer है। यह repo clone करता है, submodules initialize करता है, git hooks और Agent-Kit install करता है, फिर public trusted suite चलाता है:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

यदि आपकी shell process substitution को support नहीं करती, तो इसके बराबर pipe form का उपयोग करें:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

वैकल्पिक environment variables `TARGET_DIR` और `CLIENT` हैं। `CLIENT` को `cursor` / `claude` / `codex` / `codex-native` / `skip` पर set करें।

Manual fallback के लिए, या हर step देखने के लिए:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

अब आपको initialized submodules और installed git hooks के साथ `los-santos-customs/` के अंदर होना चाहिए। One-line route आपके चुने हुए client के लिए Agent-Kit भी install करता है और public suite चलाता है। यदि आपने manual route लिया है, तो §2 पर जाएँ। Manual transmission में एक अतिरिक्त step होता है; यह nostalgia नहीं है।

## 2. Parts लगाएँ (Agent-Kit)

Agent-Kit इस दुकान की skills और hooks को आपके editor या CLI में install करता है। Bare install ये चुने हुए defaults देता है:

- local methodology;
- verification, TDD और review के लिए curated SP skills;
- user द्वारा invoke की जाने वाली Matt library;
- low-frequency advisory router।

यह `using-superpowers` / `brainstorming` bootstrap या vendor hooks install नहीं करता। Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) install outputs हैं और commit नहीं किए जाते। इन्हें install से दोबारा बनाएँ; generated files को bodywork की ज़रूरत नहीं है।

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Values |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (वैकल्पिक) | `lean`, `guided`, `structured`; केवल advisory density बदलता है |

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

`PLUGIN` पुराने workflows के लिए केवल एक explicit full-plugin compatibility path है। यह अब recommended installation path नहीं है। Default library materialization allowlist के बाहर vendor plugins, hooks या skills copy नहीं करता; parts rack की inventory एक कारण से है।

## 3. (वैकल्पिक) अपनी कार लाएँ

Public clone बिना किसी private product repo के public trusted suite चला सकता है। Customer car को local bay से तभी जोड़ें, जब वास्तविक subject को sync, import या compare करना हो:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

क्रम महत्वपूर्ण है:

1. उदाहरण से `subjects/manifest.yaml` बनाएँ। इसके remotes को उन repos पर point करें जिन्हें आप access कर सकते हैं।
2. हर subject का harness surface fetch करने के लिए sync चलाएँ।
3. जिस exact revision का evaluation करना है, उसे record करने के लिए `<id> --pin` उपयोग करें।
4. Local absorb check चलाएँ। Pass होने वाला subject `harness-ready` है; उसके बाद ही import, compare और score भरोसेमंद results दे सकते हैं।

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` और `comparisons/` customer cars और work orders हैं। ये local रहते हैं, gitignored हैं और public showroom में कभी नहीं जाते। यह secrecy नहीं, basic key control है।

---

अब कार अपनी शक्ति से चलती है। बाकी service-bay reference है।

## सामान्य कमांड

| उद्देश्य | Command |
|---------|---------|
| Public trusted suite (loop बंद करना / CI) | `bash tools/harness/test-harness.sh` |
| Agent-Kit validate करना | `bash tools/harness/agent-kit.sh validate` |
| Harness surface sync करना | `bash tools/sync/sync-subjects.sh` |
| Pin दोबारा लिखना | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot import करना | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| साप्ताहिक report | `python3 tools/harness/weekly_report.py` |

## संरचना

| Path | भूमिका | Git में? |
|------|------|---------|
| `agent-kit/skills` | Open methodology (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Install outputs | ✗ |
| `subjects/manifest.example.yaml` | Public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb products | ✗ |
| `docs/harness/` | Design + ledgers | आंशिक |
| `AGENTS.md` | Constraint SSOT (`CLAUDE.md` → इसकी ओर) | ✓ |

## दस्तावेज़

- [`docs/README.md`](../README.md) — documentation placement rules
- [`docs/harness/design.md`](../harness/design.md) — इस repo का harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — completion definition, blacklist और mechanism map

## लाइसेंस

[MIT](../../LICENSE)
