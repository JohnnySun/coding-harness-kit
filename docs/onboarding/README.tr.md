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

> **Tek satırda:** Burası reponuzun *koruma bariyerleri* için bir modifiye dükkânı. Lifte çıkan iş kodunuz değil, etrafını saran **coding harness**: AI'ın (Cursor, Claude Code, Codex) köşeleri kesmesini, “bitti” numarası yapmasını veya commit edilmemesi gereken şeyleri git'e tıkmasını önleyen katman.
>
> **Size ne kazandırır:** Ayarlanmış metodoloji skills ve hata kaldırmayan hooks paketimizi olduğu gibi kullanabilir ya da aynı bariyerleri kendi repolarınıza takabilirsiniz. Motora (iş kaynak kodunuza) dokunmuyoruz; yalnızca dış kafesi AI'ın kolayca buruşturamayacağı kadar sağlam kaynaklıyoruz.
>
> **Yola çıkmak için üç vites:** tek satırda kurulum → (kontak) Agent-Kit'i rafa kaldır → (isteğe bağlı) kendi subject'inizi içeri sürün. Dükkânı kapatmadan önce `bash tools/harness/test-harness.sh` komutuna basın; gösterge paneli yemyeşilse muayene tamam, araç trafiğe hazır.

## Sözlük (dükkân jargonu)

Aşağıda bu kelimeleri sık göreceksiniz. Burada bir kez öğrenin; belgenin geri kalanı doğrudan kullanır.

| Jargon | Sade karşılığı |
|--------|----------------|
| **coding harness** | Gerçekte anahtar tuttuğumuz “araba”: ürün reposunun çevresindeki rules, skills, hooks, trusted suite ve ledgers dâhil tüm AI geliştirme koruma katmanı |
| **subject** | Absorb / compare için servis gözüne alınan ürün reposu; yalnızca yerelde clone edilir, burada **asla** commit edilmez |
| **harness surface** | Arabanın modifiye panelleri (`AGENTS.md`, skills, hooks); motor (iş kaynak kodu) değil |
| **Agent-Kit** | Raf kurucusu: methodology skills / hook templates öğelerini Cursor, Claude Code, Codex vb. içine yerleştirir |
| **public trusted suite** | `bash tools/harness/test-harness.sh`: bu dükkândan bir şey çıkmadan önce yapılan dyno testi (L2 CI ile aynı tezgâh) |

## En hızlı şerit: tek satırda kabul

Tek komut tüm işi yapar: dükkânı clone eder, submodules öğelerini çeker, git hooks kurar, Agent-Kit'i rafa yerleştirir ve doğruca dyno'ya (public trusted suite) çıkarır.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Fazla mı süslü? Eski usul pipe aynı motoru çalıştırır:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Nereye kurulacağını ve hangi istemcinin bağlanacağını seçmek için iki ortam değişkenini ayarlayın:

- `TARGET_DIR` — kurulumun yapılacağı directory
- `CLIENT` — bağlanacak client: `cursor` / `claude` / `codex` / `codex-native`; Agent-Kit'i sonraya bırakmak için `skip`

Tek satırlık kurulum Agent-Kit'i de rafa kaldırır ve suite'i çalıştırır; **çoğu kişi motoru burada kapatıp paydos edebilir**. Parçaları tek tek takmak mı istiyorsunuz, yoksa kurulum yarı yolda stop mu etti? Aşağıdaki manuel şeride geçin.

## Manuel kabul (kendiniz monte edin)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Bu noktada yalnızca servis kapısı açıldı; parça sandığı (Agent-Kit) hâlâ yerde duruyor. Devam edin.

## Agent-Kit'i rafa alın (parça sandığını duvara kaldırın)

Agent-Kit, bu reponun methodology skills ve hooks öğelerini editörünüze / CLI aracınıza yerleştirir. Seçeneksiz kurulum ayarlanmış bir varsayılan set sunar: yerel metodoloji, seçilmiş SP verification / TDD / review skills, bilinçli çağıracağınız Matt library ve düşük sıklıklı bir advisory router.

`using-superpowers` / `brainstorming` bootstrap bileşenini gizlice kurmaz ve vendor hooks öğelerine dokunmaz; bunlar yalnızca açıkça seçilir. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) **kurulum çıktısıdır ve asla commit edilmez**: elle değiştirip git'e kaçırmak yerine her zaman install ile yeniden üretin.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametre | Değerler |
|-----------|----------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (isteğe bağlı) | `lean`, `guided`, `structured`; yalnızca advisory prompt yoğunluğu—enforcement'a **asla** dokunmaz |

En yaygın yerel bootstrap, dört istemciyi birden rafa kaldırır:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Repo profile her zaman CLI üzerinden yönetilir (YAML'ı elle değiştirmek sorun davetiyesidir). Kurulumu başka bir repoya taşımak için önce export edin, sonra check edin:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN`, eski workflows için yalnızca açık bir full-plugin uyumluluk çıkışı olarak kalır; artık önerilen yol değildir. Varsayılan library materialization, vendor plugins, hooks veya allowlist dışındaki hiçbir skill öğesini kopyalamaz.

## Kendi arabanızı içeri sürün (isteğe bağlı: subject bağlayın)

Dükkânın tamamen yeşil çalıştığını görmek mi istiyorsunuz? **Hiçbir şey bağlamayın**: public clone, sıfır özel ürün reposuyla trusted suite'i yine baştan sona yeşil çalıştırır.

Yalnızca gerçek bir subject için sync / import / compare yapmak istediğinizde şu satırları çalıştırın:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Tek bir sırayı ezberleyin: **`manifest.yaml` oluştur → sync → sürümü geri yazmak için `--pin` → `harness-ready` olana kadar `check-local-absorb.sh`**. Önce bu gate'i geçin; import / compare / score ancak ondan sonra çalışabilir.

Aşağıdakiler yerelde kalır ve zaten gitignore kapsamındadır. Commit'e zorla sokmaya uğraşmayın; pre-commit hook daha kapıda geri çevirir:

- `subjects/manifest.yaml`
- her subject'in `pin.json` ve `checkout/` öğeleri
- `snapshots/`, `comparisons/`

---

Aşağısı günlük referans duvarıdır. Gerektiğinde bir alet alın; hepsini tek oturuşta okumanız gerekmez.

## Sık kullanılan komutlar (alet duvarı)

| İstediğiniz işlem | Çalıştırılacak satır |
|-------------------|----------------------|
| Public trusted suite (dyno / CI biçimli) | `bash tools/harness/test-harness.sh` |
| Agent-Kit'i doğrulama | `bash tools/harness/agent-kit.sh validate` |
| Harness surface için sync | `bash tools/sync/sync-subjects.sh` |
| Pin'i yeniden yazma | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb hazırlığı | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot import | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Haftalık rapor | `python3 tools/harness/weekly_report.py` |

## Dükkân planı (her parça nerede)

| Yol | Nedir | Git'te mi? |
|-----|-------|------------|
| `agent-kit/skills` | Açık metodoloji (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | İstemci başına hooks / settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Kurulum çıktıları | ✗ |
| `subjects/manifest.example.yaml` | Public registry örneği | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Yerel registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Public fixtures (CI) | ✓ |
| `snapshots/` / `comparisons/` | Absorb ürünleri | ✗ |
| `docs/harness/` | Design + ledgers | kısmen |
| `AGENTS.md` | Kısıtların SSOT'u (`CLAUDE.md` burayı gösterir) | ✓ |

## El kitabı rafı (daha derine inin)

- [`docs/README.md`](../README.md) — belge yerleşim kuralları
- [`docs/harness/design.md`](../harness/design.md) — bu reponun harness design belgesi
- [`docs/specs/`](../specs/) — design arşivi
- [`AGENTS.md`](../../AGENTS.md) — tamamlanma tanımı, blacklist ve mekanizma haritası

## Lisans

[MIT](../../LICENSE) — ruhsat burada; aracı dükkândan istediğiniz gibi çıkarın.
