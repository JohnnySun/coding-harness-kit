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
  <strong>Bahasa Indonesia</strong> |
  <a href="README.vi.md">Tiếng Việt</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **Bengkel ini menangani mobil Anda: coding harness.** Ini adalah lapisan pagar pengaman pengembangan AI yang mengelilingi sebuah repo produk. Repo produk tersebut—subject—memiliki mobilnya; source bisnis adalah mesinnya, dan mesin itu kami biarkan tertutup.
> Rute singkat: jalankan intake satu baris → instal Agent-Kit untuk Cursor, Claude Code, atau Codex → bila perlu, hubungkan subject nyata, lalu lakukan sync, pin, dan periksa `harness-ready`. Part baru tetap harus diuji di dyno. Inspeksi cat bukanlah rencana pengujian.

| Istilah | Arti (pemetaan bengkel) |
|------|---------|
| **coding harness** | Mobil Anda: lapisan pagar pengaman AI-dev di sekitar repo produk (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Repo produk pemilik mobil (clone lokal; tidak di-commit di sini) |
| **harness surface** | Ruang part: `AGENTS.md`, skills, hooks, dan file pagar pengaman serupa; bukan source bisnis |
| **Agent-Kit** | Rak part: mewujudkan methodology skills / hook templates ke Cursor, Claude Code, Codex, dan lainnya |
| **public trusted suite** | Dyno: `bash tools/harness/test-harness.sh` (sama dengan L2 CI) |

## 1. Intake (inisialisasi)

Jalur tercepat ke ruang servis adalah installer satu baris. Installer ini meng-clone repo, menginisialisasi submodules, menginstal git hooks dan Agent-Kit, lalu menjalankan public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Jika shell Anda tidak mendukung process substitution, gunakan bentuk pipe yang setara:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Environment variable opsional adalah `TARGET_DIR` dan `CLIENT`. Atur `CLIENT` ke `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Untuk fallback manual, atau untuk melihat setiap langkah pengerjaan:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Sekarang Anda seharusnya berada di dalam `los-santos-customs/`, dengan submodules yang sudah diinisialisasi dan git hooks yang sudah terinstal. Rute satu baris juga menginstal Agent-Kit untuk client pilihan Anda dan menjalankan public suite. Jika Anda mengambil rute manual, lanjutkan ke §2. Transmisi manual memang memiliki satu langkah tambahan; ini bukan soal nostalgia.

## 2. Pasang part (Agent-Kit)

Agent-Kit menginstal skills dan hooks bengkel ini ke editor atau CLI Anda. Instalasi dasar menyediakan default pilihan berikut:

- methodology lokal;
- SP skills terkurasi untuk verification, TDD, dan review;
- Matt library yang dipanggil oleh pengguna;
- advisory router berfrekuensi rendah.

Agent-Kit tidak menginstal bootstrap `using-superpowers` / `brainstorming` maupun vendor hooks. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) adalah output instalasi dan tidak di-commit. Buat ulang dengan install; file hasil generate tidak memerlukan bodywork.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Nilai |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opsional) | `lean`, `guided`, `structured`; hanya menyesuaikan kepadatan advisory |

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

`PLUGIN` dipertahankan hanya sebagai jalur kompatibilitas full-plugin yang eksplisit untuk workflow lama. Ini bukan lagi jalur instalasi yang direkomendasikan. Materialization library default tidak menyalin vendor plugins, hooks, atau skills di luar allowlist; rak part memiliki inventaris karena suatu alasan.

## 3. (Opsional) Bawa masuk mobil Anda

Clone publik dapat menjalankan public trusted suite tanpa repo produk privat. Hubungkan mobil pelanggan ke ruang servis lokal hanya ketika Anda perlu melakukan sync, import, atau compare pada subject nyata:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

Urutan itu penting:

1. Buat `subjects/manifest.yaml` dari contoh. Arahkan remotes-nya ke repo yang dapat Anda akses.
2. Jalankan sync untuk mengambil harness surface setiap subject.
3. Gunakan `<id> --pin` untuk mencatat revision tepat yang ingin Anda evaluasi.
4. Jalankan local absorb check. Subject yang lolos berstatus `harness-ready`; baru setelah itu import, compare, dan score dapat menghasilkan hasil yang tepercaya.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/`, dan `comparisons/` adalah mobil pelanggan dan work order. Semuanya tetap lokal, masuk gitignore, dan tidak pernah masuk showroom publik. Ini bukan kerahasiaan; ini kendali kunci dasar.

---

Mobil sekarang bergerak dengan tenaganya sendiri. Bagian selanjutnya adalah referensi ruang servis.

## Perintah umum

| Tujuan | Perintah |
|---------|---------|
| Public trusted suite (menutup loop / CI) | `bash tools/harness/test-harness.sh` |
| Validasi Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Tulis ulang pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Kesiapan absorb lokal | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Laporan compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Laporan mingguan | `python3 tools/harness/weekly_report.py` |

## Struktur

| Path | Peran | Di git? |
|------|------|---------|
| `agent-kit/skills` | Methodology terbuka (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Template hooks/settings client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output instalasi | ✗ |
| `subjects/manifest.example.yaml` | Contoh registry publik | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone lokal | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture publik (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produk absorb | ✗ |
| `docs/harness/` | Design + ledgers | sebagian |
| `AGENTS.md` | SSOT constraint (`CLAUDE.md` → file ini) | ✓ |

## Dokumentasi

- [`docs/README.md`](../README.md) — aturan penempatan dokumentasi
- [`docs/harness/design.md`](../harness/design.md) — design harness repo ini
- [`docs/specs/`](../specs/) — arsip design
- [`AGENTS.md`](../../AGENTS.md) — definisi selesai, blacklist, dan peta mekanisme

## Lisensi

[MIT](../../LICENSE)
