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
  <strong>العربية</strong> |
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

> **في سطر واحد:** هذا مرآب تعديل *حواجز الأمان* في مستودعك. ما يصعد على الرافعة ليس شيفرة أعمالك، بل **coding harness** المحيط بها: الطبقة التي تمنع الذكاء الاصطناعي (Cursor وClaude Code وCodex) من اختصار الطريق أو ادعاء أن العمل «اكتمل» أو دسّ ما لا ينبغي حفظه داخل git.
>
> **ما الذي ستكسبه:** يمكنك الانطلاق مباشرة بمهاراتنا المنهجية المضبوطة وhooks المقاومة للأخطاء، أو تركيب حواجز الأمان نفسها في مستودعاتك. لا نلمس المحرك (شيفرة أعمالك)؛ إنما نلحم قفص الحماية الخارجي حتى لا يستطيع الذكاء الاصطناعي سحقه بلا اكتراث.
>
> **ثلاث سرعات للانطلاق:** تثبيت بسطر واحد ← (تشغيل المحرك) ضع Agent-Kit على الرف ← (اختياري) أدخل subject الخاص بك. وقبل إغلاق الورشة، شغّل `bash tools/harness/test-harness.sh`؛ إذا أضاءت لوحة العدادات كلها بالأخضر، فقد اجتازت السيارة الفحص وأصبحت صالحة للطريق.

## مسرد المصطلحات (لغة الورشة)

سترى هذه الكلمات في كل مكان أدناه. تعلّمها مرة هنا، ثم ستستخدمها بقية الوثيقة مباشرة.

| لغة الورشة | المعنى ببساطة |
|------------|---------------|
| **coding harness** | «السيارة» التي نعمل عليها فعلًا: طبقة حواجز تطوير الذكاء الاصطناعي كاملة حول مستودع منتج، وتشمل rules وskills وhooks وtrusted suite وledgers |
| **subject** | مستودع منتج يدخل حجرة الصيانة لإجراء absorb / compare؛ يُنسخ محليًا فقط ولا يُحفظ هنا **أبدًا** |
| **harness surface** | ألواح التعديل في تلك السيارة (`AGENTS.md` وskills وhooks)، لا المحرك (شيفرة الأعمال) |
| **Agent-Kit** | مثبّت رف القطع؛ يضع skills المنهجية / hook templates في Cursor وClaude Code وCodex وغيرها |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — اختبار منصة القياس قبل أن تسلّم الورشة أي شيء (المنصة نفسها المستخدمة في L2 CI) |

## المسار الأسرع: استقبال بسطر واحد

ينجز أمر واحد المهمة كلها: ينسخ الورشة، ويجلب submodules، ويثبّت git hooks، ويرتّب Agent-Kit على الرف، ثم يدفع السيارة مباشرة إلى منصة القياس (أي public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

أكثر أناقة مما يلزم؟ صيغة pipe التقليدية تشغّل المحرك نفسه:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

هل تريد اختيار مكان التثبيت والعميل الذي سيُوصّل؟ اضبط متغيرَي البيئة التاليين:

- `TARGET_DIR` — المجلد الذي سيتم التثبيت فيه
- `CLIENT` — العميل المطلوب توصيله: `cursor` / `claude` / `codex` / `codex-native`، أو `skip` لتأجيل Agent-Kit

يرتّب أمر السطر الواحد Agent-Kit ويشغّل suite نيابةً عنك أيضًا؛ **يمكن لمعظم الناس إطفاء المحرك وإغلاق الورشة هنا**. أتريد تركيب كل سرعة على حدة، أم تعطل أمر السطر الواحد في منتصف الطريق؟ اتبع المسار اليدوي أدناه.

## الاستقبال اليدوي (ركّبه بنفسك)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

حتى هذه اللحظة لم تفعل سوى فتح باب حجرة الصيانة؛ فما يزال صندوق القطع (Agent-Kit) على الأرض. واصل العمل.

## ترتيب Agent-Kit (صندوق القطع على الحائط)

يضع Agent-Kit مهارات هذا المستودع المنهجية وhooks في محررك / CLI. يمنحك التثبيت الأساسي مجموعة افتراضية مضبوطة: منهجية محلية، وتشكيلة منتقاة من مهارات SP الخاصة بـ verification / TDD / review، ومكتبة Matt تستدعيها عن قصد، إلى جانب advisory router منخفض التكرار.

وهو **لا** يدسّ bootstrap الخاص بـ `using-superpowers` / `brainstorming`، ولا يعبث بـ vendor hooks؛ فكلاهما اختياري فقط. أما أشجار العملاء (`.cursor` / `.claude` / `.codex` / `.agents`) فهي **مخرجات تثبيت لا تُحفظ أبدًا**: أعد إنشاءها دائمًا عبر install بدل تعديلها يدويًا ومحاولة تهريبها إلى git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| المعامل | القيم |
|---------|-------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (اختياري) | `lean`, `guided`, `structured`؛ يغيّر كثافة advisory prompts فقط، ولا يمسّ enforcement **أبدًا** |

أكثر طرق bootstrap المحلية شيوعًا: رتّب العملاء الأربعة دفعة واحدة.

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

تُدار إعدادات المستودع دائمًا عبر CLI (لا تعدّل YAML يدويًا؛ فتلك دعوة صريحة للمتاعب). لنقل الإعداد إلى مستودع آخر، صدّره أولًا ثم تحقّق منه:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

لم يعد `PLUGIN` سوى مخرج توافق صريح بنمط full-plugin من أجل workflows القديمة؛ ولم يعد المسار الموصى به. لا تنسخ library materialization الافتراضية أي vendor plugins أو hooks أو skills خارج allowlist.

## أدخل سيارتك الخاصة (اختياري: وصّل subject)

أتريد فقط التأكد من أن كل مؤشرات الورشة خضراء؟ **لا توصل شيئًا**؛ فالنسخة العامة لا تعتمد على أي مستودعات منتجات خاصة، ومع ذلك تشغّل trusted suite حتى تمتلئ اللوحة باللون الأخضر.

لا تشغّل الأسطر التالية إلا عندما تريد فعلًا إجراء sync / import / compare لـ subject حقيقي:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

احفظ ترتيبًا واحدًا: **أنشئ `manifest.yaml` ← نفّذ sync ← استخدم `--pin` لكتابة الإصدار ← شغّل `check-local-absorb.sh` حتى تصل إلى `harness-ready`**. اجتز هذه البوابة أولًا؛ عندها فقط يُسمح لعمليات import / compare / score بالعمل.

تبقى العناصر التالية محلية، وهي مضمنة مسبقًا في gitignore. لا تحاول إجبارها على دخول commit؛ فسيردّها pre-commit hook فورًا:

- `subjects/manifest.yaml`
- ملف `pin.json` ومجلد `checkout/` لكل subject
- `snapshots/` و`comparisons/`

---

ما يلي هو جدار المراجع للعمل اليومي؛ تناول الأداة التي تحتاج إليها، ولا حاجة إلى قراءة كل شيء دفعة واحدة.

## الأوامر الشائعة (جدار الأدوات)

| ما تريد فعله | السطر المطلوب تشغيله |
|--------------|----------------------|
| Public trusted suite (منصة القياس / بشكل يماثل CI) | `bash tools/harness/test-harness.sh` |
| التحقق من Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| مزامنة harness surface | `bash tools/sync/sync-subjects.sh` |
| إعادة كتابة pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| جاهزية absorb المحلية | `bash tools/harness/check-local-absorb.sh --all` |
| استيراد snapshot | `python3 tools/import/import_subject.py --all` |
| تقرير compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| التقرير الأسبوعي | `python3 tools/harness/weekly_report.py` |

## مخطط الورشة (مكان كل قطعة)

| المسار | ماهيته | ضمن git؟ |
|--------|--------|----------|
| `agent-kit/skills` | منهجية مفتوحة (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | قوالب hooks / settings لكل عميل | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | مخرجات التثبيت | ✗ |
| `subjects/manifest.example.yaml` | مثال عام للسجل | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | سجل / clone محلي | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | تجهيزات عامة (CI) | ✓ |
| `snapshots/` / `comparisons/` | نواتج absorb | ✗ |
| `docs/harness/` | التصميم + ledgers | جزئي |
| `AGENTS.md` | SSOT للقيود (`CLAUDE.md` يشير إليه) | ✓ |

## رف الأدلة (للتعمق)

- [`docs/README.md`](../README.md) — قواعد وضع الوثائق
- [`docs/harness/design.md`](../harness/design.md) — تصميم harness لهذا المستودع
- [`docs/specs/`](../specs/) — أرشيف التصميم
- [`AGENTS.md`](../../AGENTS.md) — تعريف الاكتمال والقائمة المحظورة وخريطة الآليات

## الترخيص

[MIT](../../LICENSE) — قدها خارج الورشة كما تشاء؛ أوراق الملكية جاهزة.
