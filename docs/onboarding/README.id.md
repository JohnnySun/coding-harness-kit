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

> **Singkatnya:** Ini bengkel modifikasi untuk *guardrails* repo Anda. Yang naik lift bukan source bisnis, melainkan **coding harness** yang membungkusnya: lapisan yang mencegah AI (Cursor, Claude Code, Codex) mengambil jalan pintas, mengaku “selesai” tanpa bukti, atau menyelundupkan hal yang tak boleh di-commit ke git.
>
> **Untungnya buat Anda:** Pakai langsung methodology skills yang sudah disetel dan hooks yang tahan salah pencet, atau pasang guardrails yang sama ke repo Anda sendiri. Kami tidak menyentuh mesin (source bisnis Anda)—kami hanya mengelas roll cage luarnya sampai AI tak bisa meremukkannya dengan santai.
>
> **Tiga gigi untuk mulai jalan:** instalasi satu baris → (kontak menyala) pasang Agent-Kit di rak → (opsional) masukkan subject Anda. Sebelum tutup bengkel, jalankan `bash tools/harness/test-harness.sh`—dashboard serbahijau berarti lolos inspeksi dan laik jalan.

## Glosarium (bahasa bengkel)

Istilah berikut akan sering muncul. Pelajari sekali di sini; bagian lain langsung memakainya.

| Bahasa bengkel | Arti biasa |
|----------------|------------|
| **coding harness** | “Mobil” yang benar-benar kami oprek—seluruh lapisan guardrail AI-dev di sekitar repo produk: rules, skills, hooks, trusted suite, ledgers |
| **subject** | Repo produk yang dibawa ke ruang servis untuk di-absorb / compare; hanya di-clone lokal, **tidak pernah** di-commit di sini |
| **harness surface** | Panel modifikasi mobil itu (`AGENTS.md`, skills, hooks)—bukan mesin (source bisnis) |
| **Agent-Kit** | Installer rak part—memasang methodology skills / hook templates ke Cursor, Claude Code, Codex, dan lainnya |
| **public trusted suite** | `bash tools/harness/test-harness.sh`—uji dyno sebelum apa pun keluar dari bengkel (rig yang sama dengan L2 CI) |

## Jalur tercepat: intake satu baris

Satu command mengerjakan semuanya: meng-clone bengkel, menarik submodules, menginstal git hooks, memasang Agent-Kit, lalu langsung membawanya ke dyno (public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Terlalu canggih? Pipe gaya lama memutar mesin yang sama:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Mau menentukan lokasi pendaratan dan client yang dipasangi kabel? Atur dua env vars ini:

- `TARGET_DIR` — directory tujuan instalasi
- `CLIENT` — client yang dipasangi kabel: `cursor` / `claude` / `codex` / `codex-native`, atau `skip` untuk memasang Agent-Kit nanti

One-liner juga memasang Agent-Kit dan menjalankan suite—**kebanyakan orang bisa mematikan mesin dan pulang dari sini**. Ingin memasang satu gigi demi satu, atau one-liner mogok di tengah jalan? Masuk jalur manual berikut.

## Intake manual (pasang sendiri)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Sampai sini pintu ruang servis baru terbuka—peti part (Agent-Kit) masih tergeletak di lantai. Lanjutkan.

## Pasang Agent-Kit di rak (peti part ke dinding)

Agent-Kit memasukkan methodology skills dan hooks repo ini ke editor / CLI Anda. Instalasi polos memberi set default yang sudah disetel: methodology lokal, pilihan terkurasi SP verification / TDD / review skills, Matt library yang Anda panggil saat perlu, plus advisory router berfrekuensi rendah.

Agent-Kit **tidak** diam-diam memasang bootstrap `using-superpowers` / `brainstorming`, dan vendor hooks dibiarkan apa adanya—semuanya hanya opt-in. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) adalah **output instalasi dan tidak pernah di-commit**: selalu buat ulang lewat install, jangan diedit manual lalu diselundupkan ke git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parameter | Nilai |
|-----------|-------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opsional) | `lean`, `guided`, `structured`; hanya kepadatan advisory prompt—**tidak pernah** mengubah enforcement |

Bootstrap lokal paling umum—pasang keempat client sekaligus:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Profile repo selalu diubah lewat CLI (jangan edit YAML manual—itu mengundang masalah). Untuk membawa setup ke repo lain, export dulu, lalu check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` hanya bertahan sebagai pintu kompatibilitas full-plugin yang eksplisit untuk workflow lama—bukan lagi jalur yang disarankan. Materialization library default tidak menyalin vendor plugins, hooks, atau skill apa pun di luar allowlist.

## Masukkan mobil Anda (opsional: hubungkan subject)

Hanya ingin memastikan bengkel serbahijau? **Jangan hubungkan apa pun**—clone publik tidak bergantung pada repo produk privat dan tetap dapat menjalankan trusted suite sampai semuanya hijau.

Jalankan baris berikut hanya saat Anda benar-benar ingin melakukan sync / import / compare pada subject nyata:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Ingat satu urutan: **buat `manifest.yaml` → sync → `--pin` untuk menulis balik versinya → jalankan `check-local-absorb.sh` sampai `harness-ready`**. Loloskan gate ini dulu; baru import / compare / score boleh berjalan.

Semua ini tetap lokal dan sudah masuk gitignore—jangan paksa masuk commit; pre-commit hook akan langsung memantulkannya:

- `subjects/manifest.yaml`
- `pin.json` dan `checkout/` milik setiap subject
- `snapshots/`, `comparisons/`

---

Berikut dinding referensi harian—ambil tool saat perlu; tak perlu membaca semuanya sekaligus.

## Perintah umum (dinding tool)

| Yang ingin Anda lakukan | Baris yang dijalankan |
|-------------------------|----------------------|
| Public trusted suite (dyno / berbentuk CI) | `bash tools/harness/test-harness.sh` |
| Validasi Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Tulis ulang pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Kesiapan absorb lokal | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Laporan mingguan | `python3 tools/harness/weekly_report.py` |

## Denah bengkel (lokasi setiap part)

| Path | Isinya | Di git? |
|------|--------|---------|
| `agent-kit/skills` | Methodology terbuka (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Template hooks / settings per client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output instalasi | ✗ |
| `subjects/manifest.example.yaml` | Contoh registry publik | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone lokal | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture publik (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produk absorb | ✗ |
| `docs/harness/` | Design + ledgers | sebagian |
| `AGENTS.md` | SSOT constraint (`CLAUDE.md` mengarah ke sini) | ✓ |

## Rak manual (gali lebih dalam)

- [`docs/README.md`](../README.md) — aturan penempatan dokumentasi
- [`docs/harness/design.md`](../harness/design.md) — design harness repo ini
- [`docs/specs/`](../specs/) — arsip design
- [`AGENTS.md`](../../AGENTS.md) — definisi selesai, blacklist, dan peta mekanisme

## Lisensi

[MIT](../../LICENSE) — bawa keluar dari dealer sesuka hati; suratnya ada di sini.
