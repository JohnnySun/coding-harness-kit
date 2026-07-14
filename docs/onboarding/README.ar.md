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

> **هذا المتجر يعمل على سيارتك: coding harness.** وهي طبقة حواجز تطوير الذكاء الاصطناعي المحيطة بمستودع منتج. يمتلك مستودع المنتج — أي subject — السيارة؛ وشيفرة الأعمال هي المحرك، ونحن نترك المحرك مغلقًا.
> المسار المختصر: شغّل أمر الاستقبال ذي السطر الواحد ← ثبّت Agent-Kit لـ Cursor أو Claude Code أو Codex ← وصّل subject حقيقيًا اختياريًا، ثم نفّذ sync وpin وتحقق من `harness-ready`. يجب أن تمر القطع الجديدة على منصة القياس. فحص الطلاء ليس خطة اختبار.

| المصطلح | المعنى (تشبيه المتجر) |
|------|---------|
| **coding harness** | سيارتك: طبقة حواجز تطوير الذكاء الاصطناعي حول مستودع منتج (rules وskills وhooks وtrusted suite وledgers) |
| **subject** | مستودع المنتج الذي يملك السيارة (نسخة محلية؛ لا تُحفظ في هذا المستودع) |
| **harness surface** | حجرة القطع: `AGENTS.md` وskills وhooks وملفات الحواجز المشابهة؛ وليست شيفرة الأعمال |
| **Agent-Kit** | رف القطع: ينشر skills المنهجية وقوالب hooks في Cursor وClaude Code وCodex وغيرها |
| **public trusted suite** | منصة القياس: `bash tools/harness/test-harness.sh` (نفس L2 CI) |

## 1. الاستقبال (التهيئة)

أسرع طريق إلى حجرة العمل هو المثبّت ذو السطر الواحد. فهو ينسخ المستودع، ويهيئ submodules، ويثبّت git hooks وAgent-Kit، ثم يشغّل public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

إذا لم تكن shell لديك تدعم process substitution، فاستخدم صيغة pipe المكافئة:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

متغيرا البيئة الاختياريان هما `TARGET_DIR` و`CLIENT`. اضبط `CLIENT` على `cursor` / `claude` / `codex` / `codex-native` / `skip`.

للرجوع إلى التثبيت اليدوي، أو لمتابعة كل خطوة:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

يجب أن تكون الآن داخل `los-santos-customs/` مع تهيئة submodules وتثبيت git hooks. يثبّت مسار السطر الواحد أيضًا Agent-Kit للعميل الذي اخترته ويشغّل public suite. إذا اتبعت المسار اليدوي، فتابع إلى §2. ناقل الحركة اليدوي يحتاج خطوة إضافية؛ ولا علاقة لذلك بالحنين.

## 2. تركيب القطع (Agent-Kit)

يثبّت Agent-Kit مهارات هذا المتجر وhooks الخاصة به في المحرر أو CLI. يوفر التثبيت الأساسي هذه الإعدادات الافتراضية المنتقاة:

- منهجية محلية؛
- مهارات SP منتقاة للتحقق وTDD والمراجعة؛
- مكتبة Matt يستدعيها المستخدم؛
- موجّه إرشادي منخفض التكرار.

لا يثبّت bootstrap الخاص بـ `using-superpowers` / `brainstorming` ولا vendor hooks. أشجار العملاء (`.cursor` / `.claude` / `.codex` / `.agents`) هي مخرجات تثبيت ولا تُحفظ في git. أعد إنشاءها بأمر install؛ فالملفات المولدة لا تحتاج إلى إصلاح هيكل.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| المعامل | القيم |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (اختياري) | `lean`, `guided`, `structured`؛ يضبط كثافة الإرشادات فقط |

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

يبقى `PLUGIN` فقط كمسار توافق صريح مع full-plugin لسير العمل القديم. لم يعد مسار التثبيت الموصى به. لا ينسخ materialization الافتراضي للمكتبة vendor plugins أوhooks أوskills خارج allowlist؛ فوجود قائمة جرد لرف القطع مقصود.

## 3. إدخال سيارتك الخاصة (اختياري)

يمكن لنسخة عامة تشغيل public trusted suite من دون أي مستودعات منتجات خاصة. لا توصل سيارة عميل بحجرة العمل المحلية إلا عندما تحتاج إلى sync أوimport أوcompare لـ subject حقيقي:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

الترتيب مهم:

1. أنشئ `subjects/manifest.yaml` من المثال. وجّه remotes إلى مستودعات يمكنك الوصول إليها.
2. شغّل sync لجلب harness surface لكل subject.
3. استخدم `<id> --pin` لتسجيل المراجعة الدقيقة التي تريد تقييمها.
4. شغّل فحص absorb المحلي. يصبح subject الناجح `harness-ready`؛ وعندها فقط يمكن أن تنتج عمليات import وcompare وscore نتائج موثوقة.

تُعد `subjects/manifest.yaml` و`pin.json` و`checkout/` و`snapshots/` و`comparisons/` سيارات عملاء وأوامر عمل. تبقى محلية، ويستثنيها git، ولا تدخل صالة العرض العامة أبدًا. هذه ليست سرية؛ بل إدارة أساسية للمفاتيح.

---

أصبحت السيارة تتحرك بقوتها الذاتية. وما يلي مرجع لحجرة الصيانة.

## أوامر شائعة

| الغرض | الأمر |
|---------|---------|
| Public trusted suite (إغلاق الحلقة / CI) | `bash tools/harness/test-harness.sh` |
| التحقق من Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| مزامنة harness surface | `bash tools/sync/sync-subjects.sh` |
| إعادة كتابة pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| جاهزية absorb المحلية | `bash tools/harness/check-local-absorb.sh --all` |
| استيراد snapshot | `python3 tools/import/import_subject.py --all` |
| تقرير compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| التقرير الأسبوعي | `python3 tools/harness/weekly_report.py` |

## البنية

| المسار | الدور | ضمن git؟ |
|------|------|---------|
| `agent-kit/skills` | منهجية مفتوحة (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | قوالب hooks/settings للعملاء | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | مخرجات التثبيت | ✗ |
| `subjects/manifest.example.yaml` | مثال عام للسجل | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | سجل / نسخة محلية | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | تجهيزات عامة (CI) | ✓ |
| `snapshots/` / `comparisons/` | مخرجات absorb | ✗ |
| `docs/harness/` | التصميم + السجلات | جزئي |
| `AGENTS.md` | المصدر الوحيد لقيود النظام (`CLAUDE.md` → إليه) | ✓ |

## التوثيق

- [`docs/README.md`](../README.md) — قواعد وضع الوثائق
- [`docs/harness/design.md`](../harness/design.md) — تصميم harness لهذا المستودع
- [`docs/specs/`](../specs/) — أرشيف التصميم
- [`AGENTS.md`](../../AGENTS.md) — تعريف الاكتمال والقائمة المحظورة وخريطة الآليات

## الترخيص

[MIT](../../LICENSE)
