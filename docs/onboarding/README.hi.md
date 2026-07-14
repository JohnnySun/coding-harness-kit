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

> **एक पंक्ति में:** यह आपके repo के *guardrails* की मॉडिफिकेशन शॉप है। लिफ्ट पर आपका business code नहीं, बल्कि उसके चारों ओर लगा **coding harness** चढ़ता है—वह परत जो AI (Cursor, Claude Code, Codex) को शॉर्टकट लेने, झूठा “done” बोलने या ऐसी चीज़ें git में ठूँसने से रोकती है जिन्हें commit नहीं होना चाहिए।
>
> **आपको क्या मिलता है:** हमारी tuned methodology skills और लगभग बेवकूफ़ी-रोधी hooks को सीधे चलाएँ, या वही guardrails अपने repos पर कसें। हम इंजन (आपका business source) नहीं छूते—बस बाहर का roll cage इतना मज़बूत करते हैं कि AI उसे यूँ ही न मोड़ सके।
>
> **चलने के तीन गियर:** one-line install → (इग्निशन) Agent-Kit को rack पर चढ़ाएँ → (वैकल्पिक) अपना subject अंदर लाएँ। शिफ्ट खत्म करने से पहले `bash tools/harness/test-harness.sh` चलाएँ—dashboard पूरा हरा है तो गाड़ी inspection पास और सड़क के लायक है।

## शब्दावली (दुकान की बोली)

नीचे ये शब्द बार-बार मिलेंगे। इन्हें यहाँ एक बार समझ लें; बाकी दस्तावेज़ सीधे इनका इस्तेमाल करेगा।

| दुकान की बोली | सीधा अर्थ |
|---------------|-----------|
| **coding harness** | वह “कार” जिस पर हम सच में रिंच चलाते हैं—product repo के चारों ओर पूरी AI-dev guardrail layer: rules, skills, hooks, trusted suite, ledgers |
| **subject** | absorb / compare के लिए bay में लाया गया product repo; केवल local clone, यहाँ **कभी** commit नहीं होता |
| **harness surface** | उस कार के mod panels (`AGENTS.md`, skills, hooks)—इंजन (business source) नहीं |
| **Agent-Kit** | rack-it installer—methodology skills / hook templates को Cursor, Claude Code, Codex आदि में डालता है |
| **public trusted suite** | `bash tools/harness/test-harness.sh`—दुकान से कुछ निकलने से पहले dyno run (L2 CI वाला ही rig) |

## सबसे तेज़ लेन: one-line intake

एक command पूरा काम करता है: दुकान clone करता है, submodules खींचता है, git hooks install करता है, Agent-Kit को rack करता है और फिर सीधे dyno (public trusted suite) पर दौड़ाता है।

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

ज़रा ज़्यादा fancy लगा? पुराना pipe भी यही इंजन crank करता है:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

कहाँ उतरना है और किस client की wiring करनी है, यह चुनने के लिए ये दो env vars set करें:

- `TARGET_DIR` — किस directory में install करना है
- `CLIENT` — किस client की wiring करनी है: `cursor` / `claude` / `codex` / `codex-native`; या Agent-Kit बाद में लगाने के लिए `skip`

One-liner Agent-Kit को rack करके suite भी चला देता है—**ज़्यादातर लोग यहीं इंजन बंद करके घर निकल सकते हैं**। एक-एक gear खुद लगाना है, या one-liner बीच रास्ते अटक गया? नीचे manual lane लें।

## Manual intake (खुद bolt लगाएँ)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

अभी बस bay का दरवाज़ा खुला है—parts crate (Agent-Kit) अब भी फर्श पर पड़ा है। आगे बढ़ें।

## Agent-Kit को rack करें (parts crate दीवार पर)

Agent-Kit इस repo की methodology skills और hooks को आपके editor / CLI में डालता है। Bare install एक tuned default set देता है: local methodology, SP verification / TDD / review skills का curated चयन, ज़रूरत पर बुलाने वाली Matt library और low-frequency advisory router।

यह चुपके से `using-superpowers` / `brainstorming` bootstrap नहीं डालता और vendor hooks को हाथ नहीं लगाता—वे केवल opt-in हैं। Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) **install outputs हैं और कभी commit नहीं होते**: उन्हें हाथ से edit करके git में घुसाने के बजाय install से हमेशा दोबारा बनाएँ।

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | मान |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (वैकल्पिक) | `lean`, `guided`, `structured`; केवल advisory prompt density—enforcement को **कभी** नहीं छूता |

सबसे आम local bootstrap—चारों clients को एक साथ rack करें:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Repo profile हमेशा CLI से बदलें (YAML को हाथ से edit करना मुसीबत को निमंत्रण है)। Setup दूसरे repo में ले जाना हो तो पहले export करें, फिर check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` पुराने workflows के लिए केवल explicit full-plugin compatibility hatch के रूप में बचा है—अब यह recommended path नहीं है। Default library materialization vendor plugins, hooks या allowlist से बाहर कोई skill copy नहीं करता।

## अपनी कार अंदर लाएँ (वैकल्पिक: subject की wiring)

सिर्फ यह देखना है कि दुकान पूरी हरी चलती है? **कुछ भी wire न करें**—public clone किसी private product repo पर निर्भर नहीं है और फिर भी trusted suite को पूरा हरा चला सकता है।

जब सच में किसी वास्तविक subject को sync / import / compare करना हो, तभी यह चलाएँ:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

एक क्रम याद रखें: **`manifest.yaml` बनाएँ → sync → version वापस लिखने के लिए `--pin` → `harness-ready` होने तक `check-local-absorb.sh`**। पहले यह gate पार करें; उसके बाद ही import / compare / score चल सकते हैं।

ये चीज़ें local रहती हैं और पहले से gitignored हैं—इन्हें commit में जबरन घुसाने की कोशिश न करें; pre-commit hook वहीं वापस उछाल देगा:

- `subjects/manifest.yaml`
- हर subject का `pin.json` और `checkout/`
- `snapshots/`, `comparisons/`

---

नीचे रोज़मर्रा की reference wall है—ज़रूरत पर tool उठाएँ; सब कुछ एक साथ पढ़ने की ज़रूरत नहीं।

## आम commands (tool wall)

| आप क्या चाहते हैं | चलाने वाली line |
|-------------------|-----------------|
| Public trusted suite (dyno / CI-shaped) | `bash tools/harness/test-harness.sh` |
| Agent-Kit validate करें | `bash tools/harness/agent-kit.sh validate` |
| Harness surface sync करें | `bash tools/sync/sync-subjects.sh` |
| Pin फिर लिखें | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot import करें | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Floor plan (कौन-सा part कहाँ है)

| Path | यह क्या है | Git में? |
|------|------------|---------|
| `agent-kit/skills` | Open methodology (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | हर client के hooks / settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Install outputs | ✗ |
| `subjects/manifest.example.yaml` | Public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb products | ✗ |
| `docs/harness/` | Design + ledgers | partial |
| `AGENTS.md` | Constraint SSOT (`CLAUDE.md` points here) | ✓ |

## Manual shelf (और गहराई में)

- [`docs/README.md`](../README.md) — documentation placement rules
- [`docs/harness/design.md`](../harness/design.md) — इस repo का harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — completion definition, blacklist, mechanism map

## License

[MIT](../../LICENSE) — मनचाहे ढंग से lot से निकालें; title यहीं है।
