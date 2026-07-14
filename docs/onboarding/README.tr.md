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
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <strong>Türkçe</strong> |
  <a href="README.uk.md">Українська</a>
</h3>

> **Bu dükkân sizin arabanızla, yani coding harness ile çalışır.** Bu, bir ürün reposunun çevresindeki AI geliştirme koruma katmanıdır. Ürün reposu — subject — arabanın sahibidir; iş kaynak kodu motordur ve motoru kapalı tutarız.
> Kısa rota: tek satırlık kurulumu çalıştırın → Cursor, Claude Code veya Codex için Agent-Kit'i kurun → isteğe bağlı olarak gerçek bir subject bağlayın, ardından sync ve pin yapıp `harness-ready` durumunu denetleyin. Yeni parçalar yine dinamometreye çıkar. Boya kontrolü bir test planı değildir.

| Terim | Anlamı (dükkân eşlemesi) |
|------|---------|
| **coding harness** | Arabanız: ürün reposunun çevresindeki AI geliştirme koruma katmanı (rules, skills, hooks, trusted suite ve ledgers) |
| **subject** | Arabanın sahibi olan ürün reposu (yerel clone; burada commit edilmez) |
| **harness surface** | Parça bölmesi: `AGENTS.md`, skills, hooks ve benzeri koruma dosyaları; iş kaynak kodu değildir |
| **Agent-Kit** | Parça rafı: metodoloji skills ve hook templates öğelerini Cursor, Claude Code, Codex vb. içine yerleştirir |
| **public trusted suite** | Dinamometre: `bash tools/harness/test-harness.sh` (L2 CI ile aynı) |

## 1. Kabul (başlatma)

Dükkâna girmenin en hızlı yolu tek satırlık kurucudur. Repoyu clone eder, submodules bileşenlerini başlatır, git hooks ve Agent-Kit'i kurar, ardından public trusted suite'i çalıştırır:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Shell'iniz process substitution desteklemiyorsa eşdeğer pipe biçimini kullanın:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

İsteğe bağlı ortam değişkenleri `TARGET_DIR` ve `CLIENT`'tır. `CLIENT` değerini `cursor` / `claude` / `codex` / `codex-native` / `skip` olarak ayarlayın.

Elle uygulanan yedek yol veya her adımı izlemek için:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Artık başlatılmış submodules ve kurulmuş git hooks ile `los-santos-customs/` içinde olmalısınız. Tek satırlık rota, seçtiğiniz istemci için Agent-Kit'i de kurar ve public suite'i çalıştırır. Elle kurulum yaptıysanız §2'ye geçin. Manuel şanzımanın bir ek adımı vardır; bunun nedeni nostalji değildir.

## 2. Parçaları takma (Agent-Kit)

Agent-Kit, bu dükkânın skills ve hooks öğelerini editörünüze veya CLI aracınıza kurar. Seçeneksiz kurulum şu bilinçli varsayılanları sağlar:

- yerel metodoloji;
- seçilmiş SP doğrulama, TDD ve review skills;
- kullanıcı tarafından çağrılan bir Matt library;
- düşük sıklıkta çalışan tavsiye router.

`using-superpowers` / `brainstorming` bootstrap bileşenini veya tedarikçi hooks öğelerini kurmaz. İstemci ağaçları (`.cursor` / `.claude` / `.codex` / `.agents`) kurulum çıktılarıdır ve commit edilmez. Bunları install ile yeniden üretin; oluşturulan dosyaların kaporta işlemine ihtiyacı yoktur.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametre | Değerler |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (isteğe bağlı) | `lean`, `guided`, `structured`; yalnızca tavsiye yoğunluğunu ayarlar |

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

`PLUGIN`, eski workflows için yalnızca tam plugin uyumluluğuna yönelik açık bir yol olarak kalır. Artık önerilen kurulum yolu değildir. Varsayılan library materialization, allowlist dışındaki tedarikçi plugins, hooks veya skills öğelerini kopyalamaz; parça rafının bir envanteri olmasının nedeni vardır.

## 3. (İsteğe bağlı) Kendi arabanızı getirin

Herkese açık bir clone, özel ürün repoları olmadan public trusted suite'i çalıştırabilir. Yerel dükkânınıza yalnızca gerçek bir subject üzerinde sync, import veya compare yapmanız gerektiğinde müşteri arabası bağlayın:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

Sıralama önemlidir:

1. Örneği kullanarak `subjects/manifest.yaml` oluşturun. Remotes değerlerini erişebildiğiniz repolara yönlendirin.
2. Her subject'in harness surface alanını almak için sync çalıştırın.
3. Değerlendirmek istediğiniz kesin revision'ı kaydetmek için `<id> --pin` kullanın.
4. Yerel absorb denetimini çalıştırın. Denetimden geçen subject `harness-ready` olur; ancak bundan sonra import, compare ve score güvenilir sonuçlar üretebilir.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` ve `comparisons/` müşteri arabaları ve iş emirleridir. Yerel kalır, git tarafından yok sayılır ve herkese açık teşhir salonuna asla girmezler. Bu gizlilik değil, temel anahtar denetimidir.

---

Araba artık kendi gücüyle hareket ediyor. Geri kalanı servis bölmesi referansıdır.

## Sık kullanılan komutlar

| Amaç | Komut |
|---------|---------|
| Public trusted suite (döngüyü kapatma / CI) | `bash tools/harness/test-harness.sh` |
| Agent-Kit'i doğrulama | `bash tools/harness/agent-kit.sh validate` |
| Harness surface için sync | `bash tools/sync/sync-subjects.sh` |
| Pin'i yeniden yazma | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Yerel absorb hazırlığı | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot import | `python3 tools/import/import_subject.py --all` |
| Compare raporu | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Haftalık rapor | `python3 tools/harness/weekly_report.py` |

## Yerleşim

| Yol | Rol | Git'te mi? |
|------|------|---------|
| `agent-kit/skills` | Açık metodoloji (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | İstemci hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Kurulum çıktıları | ✗ |
| `subjects/manifest.example.yaml` | Herkese açık registry örneği | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Yerel registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Herkese açık fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb ürünleri | ✗ |
| `docs/harness/` | Design + ledgers | kısmen |
| `AGENTS.md` | Kısıtlar için SSOT (`CLAUDE.md` → bu dosya) | ✓ |

## Belgeler

- [`docs/README.md`](../README.md) — belge yerleştirme kuralları
- [`docs/harness/design.md`](../harness/design.md) — bu reponun harness design belgesi
- [`docs/specs/`](../specs/) — design arşivi
- [`AGENTS.md`](../../AGENTS.md) — tamamlanma tanımı, blacklist ve mekanizma haritası

## Lisans

[MIT](../../LICENSE)
