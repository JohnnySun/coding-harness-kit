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
  <strong>Tiếng Việt</strong> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **Gói gọn trong một dòng:** đây là lò độ *lan can bảo vệ* cho repo của bạn. Thứ được đưa lên cầu nâng không phải mã nguồn nghiệp vụ, mà là **coding harness** bao quanh nó—lớp ngăn AI (Cursor, Claude Code, Codex) đốt cháy giai đoạn, giả vờ “xong rồi”, hoặc nhét vào git những thứ không được phép commit.
>
> **Bạn được gì:** dùng ngay methodology skills đã tinh chỉnh và hooks chống thao tác nhầm của chúng tôi, hoặc gắn cùng bộ lan can đó vào repo của riêng bạn. Chúng tôi không đụng đến động cơ (source nghiệp vụ); chỉ hàn khung chống lật bên ngoài cho đến khi AI không thể tiện tay vò nát chiếc xe.
>
> **Ba số để lăn bánh:** cài bằng một dòng → (đề máy) đưa Agent-Kit lên giá → (tùy chọn) lái subject của bạn vào xưởng. Trước khi đóng ca, hãy chạy `bash tools/harness/test-harness.sh`—bảng đồng hồ xanh hết nghĩa là đã qua đăng kiểm, đủ điều kiện xuống đường.

## Bảng thuật ngữ (tiếng lóng trong xưởng)

Bạn sẽ gặp những từ này khắp phần dưới. Học một lần ở đây; phần còn lại của tài liệu sẽ dùng thẳng.

| Tiếng lóng | Nghĩa thông thường |
|------------|--------------------|
| **coding harness** | “Chiếc xe” mà chúng tôi thực sự chỉnh sửa: toàn bộ lớp bảo vệ phát triển bằng AI quanh repo sản phẩm—rules, skills, hooks, trusted suite và ledgers |
| **subject** | Repo sản phẩm được đưa vào khoang để absorb / compare; chỉ clone cục bộ và **không bao giờ** commit tại đây |
| **harness surface** | Các tấm ốp độ trên xe (`AGENTS.md`, skills, hooks)—không phải động cơ (source nghiệp vụ) |
| **Agent-Kit** | Bộ lắp giá phụ tùng—đưa methodology skills / hook templates vào Cursor, Claude Code, Codex, v.v. |
| **public trusted suite** | `bash tools/harness/test-harness.sh`—bài chạy dyno trước khi xưởng xuất bất cứ thứ gì (cùng hệ thống với L2 CI) |

## Làn nhanh nhất: tiếp nhận bằng một dòng

Một lệnh lo toàn bộ: clone xưởng, kéo submodules, cài git hooks, đưa Agent-Kit lên giá, rồi chạy thẳng lên dyno (public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Hơi cầu kỳ? Pipe kiểu cũ vẫn nổ cùng một động cơ:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Muốn chọn nơi cài và client cần đấu nối? Hãy đặt hai environment variables:

- `TARGET_DIR` — directory đích để cài đặt
- `CLIENT` — client cần đấu nối: `cursor` / `claude` / `codex` / `codex-native`, hoặc `skip` để dành Agent-Kit cho lần sau

Lệnh một dòng cũng đưa Agent-Kit lên giá và chạy suite giúp bạn—**đa số có thể tắt máy, hết ca ngay tại đây**. Muốn gắn từng món một, hoặc lệnh một dòng chết máy giữa đường? Hãy đi theo làn manual bên dưới.

## Tiếp nhận manual (tự tay lắp ráp)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Lúc này cửa khoang sửa mới chỉ mở—thùng phụ tùng (Agent-Kit) vẫn nằm dưới sàn. Tiếp tục nào.

## Đưa Agent-Kit lên giá (treo thùng phụ tùng lên tường)

Agent-Kit đưa methodology skills và hooks của repo này vào editor / CLI của bạn. Bản cài cơ bản cung cấp một bộ mặc định đã tinh chỉnh: methodology cục bộ, các SP skills được tuyển chọn cho verification / TDD / review, Matt library để bạn chủ động gọi, cùng advisory router tần suất thấp.

Nó **không** lén đưa vào bootstrap `using-superpowers` / `brainstorming`, cũng không đụng đến vendor hooks—những thứ đó chỉ được cài khi bạn chủ động chọn. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) là **output cài đặt và không bao giờ được commit**: luôn tạo lại bằng install, đừng sửa tay rồi lén đưa ngược vào git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Tham số | Giá trị |
|---------|---------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (tùy chọn) | `lean`, `guided`, `structured`; chỉ thay đổi mật độ advisory prompts—**không bao giờ** đụng đến enforcement |

Bootstrap cục bộ phổ biến nhất—đưa cả bốn client lên giá cùng lúc:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Repo profile luôn phải đi qua CLI (sửa YAML bằng tay là tự mời rắc rối vào xưởng). Để mang thiết lập sang repo khác, hãy export trước rồi check:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` chỉ còn là lối tương thích full-plugin tường minh cho các workflows cũ—không còn là đường cài đặt được khuyến nghị. Default library materialization sẽ không sao chép vendor plugins, hooks hay bất kỳ skill nào ngoài allowlist.

## Lái xe của bạn vào xưởng (tùy chọn: đấu nối subject)

Chỉ muốn kiểm tra xưởng có xanh toàn bộ không? **Đừng đấu nối gì cả**—public clone không phụ thuộc vào repo sản phẩm riêng tư nào mà vẫn chạy trusted suite đến khi cả bảng xanh rì.

Chỉ khi thực sự muốn sync / import / compare một subject thật, bạn mới cần chạy:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Chỉ cần nhớ đúng một thứ tự: **tạo `manifest.yaml` → sync → dùng `--pin` ghi version trở lại → chạy `check-local-absorb.sh` cho đến khi đạt `harness-ready`**. Vượt gate này trước; chỉ sau đó import / compare / score mới được phép chạy.

Các mục sau luôn ở cục bộ và đã được gitignore. Đừng cố nhồi chúng vào commit; pre-commit hook sẽ chặn ngay tại cửa:

- `subjects/manifest.yaml`
- `pin.json` và `checkout/` của từng subject
- `snapshots/`, `comparisons/`

---

Bên dưới là bức tường tra cứu dùng hằng ngày. Cần dụng cụ nào thì lấy dụng cụ đó; không cần đọc hết trong một lượt.

## Lệnh thường dùng (tường dụng cụ)

| Việc bạn muốn làm | Dòng lệnh cần chạy |
|-------------------|--------------------|
| Public trusted suite (dyno / theo cấu trúc CI) | `bash tools/harness/test-harness.sh` |
| Xác thực Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Ghi lại pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Kiểm tra mức sẵn sàng local absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Tạo compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Chạy score | `python3 tools/score/score_subject.py <id>` |
| Tạo báo cáo hằng tuần | `python3 tools/harness/weekly_report.py` |

## Sơ đồ xưởng (từng bộ phận nằm ở đâu)

| Path | Đây là gì | Trong git? |
|------|-----------|------------|
| `agent-kit/skills` | Methodology mở (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings templates theo từng client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output cài đặt | ✗ |
| `subjects/manifest.example.yaml` | Ví dụ registry công khai | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone cục bộ | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures công khai (CI) | ✓ |
| `snapshots/` / `comparisons/` | Sản phẩm absorb | ✗ |
| `docs/harness/` | Design + ledgers | một phần |
| `AGENTS.md` | SSOT của constraints (`CLAUDE.md` trỏ về đây) | ✓ |

## Giá hướng dẫn (đọc sâu hơn)

- [`docs/README.md`](../README.md) — quy tắc đặt tài liệu
- [`docs/harness/design.md`](../harness/design.md) — design harness của repo này
- [`docs/specs/`](../specs/) — kho lưu trữ design
- [`AGENTS.md`](../../AGENTS.md) — định nghĩa hoàn tất, blacklist và bản đồ cơ chế

## Giấy phép

[MIT](../../LICENSE) — cứ lái xe khỏi xưởng theo cách bạn muốn; giấy tờ ở ngay đây.
