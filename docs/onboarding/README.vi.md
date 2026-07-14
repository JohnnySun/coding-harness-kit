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

> **Xưởng này làm việc trên chiếc xe của bạn: coding harness.** Đây là lớp rào chắn phát triển AI bao quanh một repo sản phẩm. Repo sản phẩm đó—subject—sở hữu chiếc xe; source nghiệp vụ là động cơ, và chúng tôi để động cơ đóng kín.
> Lộ trình ngắn: chạy lệnh tiếp nhận một dòng → cài Agent-Kit cho Cursor, Claude Code hoặc Codex → tùy chọn kết nối một subject thật, rồi sync, pin và kiểm tra `harness-ready`. Part mới vẫn phải lên dyno. Kiểm tra nước sơn không phải là kế hoạch kiểm thử.

| Thuật ngữ | Ý nghĩa (theo cách gọi của xưởng) |
|------|---------|
| **coding harness** | Chiếc xe của bạn: lớp rào chắn AI-dev quanh repo sản phẩm (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Repo sản phẩm sở hữu chiếc xe (clone cục bộ; không commit tại đây) |
| **harness surface** | Khoang part: `AGENTS.md`, skills, hooks và các file rào chắn tương tự; không phải source nghiệp vụ |
| **Agent-Kit** | Giá part: materialize methodology skills / hook templates vào Cursor, Claude Code, Codex, v.v. |
| **public trusted suite** | Dyno: `bash tools/harness/test-harness.sh` (giống L2 CI) |

## 1. Tiếp nhận (khởi tạo)

Lối nhanh nhất vào khoang sửa chữa là installer một dòng. Lệnh này clone repo, khởi tạo submodules, cài git hooks và Agent-Kit, rồi chạy public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Nếu shell của bạn không hỗ trợ process substitution, hãy dùng dạng pipe tương đương:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Các environment variable tùy chọn là `TARGET_DIR` và `CLIENT`. Đặt `CLIENT` thành `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Để dùng phương án thủ công, hoặc theo dõi từng bước thao tác:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Bây giờ bạn phải đang ở trong `los-santos-customs/`, với submodules đã được khởi tạo và git hooks đã được cài. Lộ trình một dòng cũng cài Agent-Kit cho client bạn chọn và chạy public suite. Nếu chọn lộ trình thủ công, hãy tiếp tục đến §2. Hộp số sàn có thêm một bước; đây không phải chuyện hoài cổ.

## 2. Lắp part (Agent-Kit)

Agent-Kit cài skills và hooks của xưởng này vào editor hoặc CLI của bạn. Một bản cài cơ bản cung cấp các mặc định được tuyển chọn sau:

- methodology cục bộ;
- các SP skills được tuyển chọn cho verification, TDD và review;
- Matt library do người dùng gọi;
- advisory router tần suất thấp.

Agent-Kit không cài bootstrap `using-superpowers` / `brainstorming` hay vendor hooks. Client trees (`.cursor` / `.claude` / `.codex` / `.agents`) là output cài đặt và không được commit. Hãy tạo lại bằng install; file được generate không cần làm lại thân vỏ.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Tham số | Giá trị |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (tùy chọn) | `lean`, `guided`, `structured`; chỉ điều chỉnh mật độ advisory |

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

`PLUGIN` chỉ còn là đường dẫn tương thích full-plugin tường minh cho các workflow cũ. Đây không còn là đường dẫn cài đặt được khuyến nghị. Quá trình materialization library mặc định không sao chép vendor plugins, hooks hay skills ngoài allowlist; giá part có danh mục là có lý do.

## 3. (Tùy chọn) Đưa xe của bạn vào xưởng

Một public clone có thể chạy public trusted suite mà không cần repo sản phẩm riêng tư nào. Chỉ kết nối xe của khách hàng với khoang sửa chữa cục bộ khi bạn cần sync, import hoặc compare một subject thật:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

Thứ tự rất quan trọng:

1. Tạo `subjects/manifest.yaml` từ file mẫu. Trỏ remotes đến các repo mà bạn có quyền truy cập.
2. Chạy sync để fetch harness surface của từng subject.
3. Dùng `<id> --pin` để ghi lại chính xác revision bạn định đánh giá.
4. Chạy local absorb check. Subject vượt qua sẽ là `harness-ready`; chỉ khi đó import, compare và score mới có thể tạo kết quả đáng tin cậy.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` và `comparisons/` là xe của khách hàng và work order. Chúng luôn ở cục bộ, bị gitignore và không bao giờ vào showroom công khai. Đây không phải là che giấu; đây là kiểm soát khóa cơ bản.

---

Giờ chiếc xe đã tự chạy bằng động lực của mình. Phần còn lại là tài liệu tham khảo cho khoang dịch vụ.

## Lệnh thường dùng

| Mục đích | Lệnh |
|---------|---------|
| Public trusted suite (khép vòng lặp / CI) | `bash tools/harness/test-harness.sh` |
| Xác thực Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync harness surface | `bash tools/sync/sync-subjects.sh` |
| Ghi lại pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Mức sẵn sàng absorb cục bộ | `bash tools/harness/check-local-absorb.sh --all` |
| Import snapshot | `python3 tools/import/import_subject.py --all` |
| Báo cáo compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Báo cáo hằng tuần | `python3 tools/harness/weekly_report.py` |

## Bố cục

| Path | Vai trò | Trong git? |
|------|------|---------|
| `agent-kit/skills` | Methodology mở (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Template hooks/settings cho client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output cài đặt | ✗ |
| `subjects/manifest.example.yaml` | Ví dụ registry công khai | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone cục bộ | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture công khai (CI) | ✓ |
| `snapshots/` / `comparisons/` | Sản phẩm absorb | ✗ |
| `docs/harness/` | Design + ledgers | một phần |
| `AGENTS.md` | SSOT của constraint (`CLAUDE.md` → file này) | ✓ |

## Tài liệu

- [`docs/README.md`](../README.md) — quy tắc đặt tài liệu
- [`docs/harness/design.md`](../harness/design.md) — design harness của repo này
- [`docs/specs/`](../specs/) — kho lưu trữ design
- [`AGENTS.md`](../../AGENTS.md) — định nghĩa hoàn tất, blacklist và bản đồ cơ chế

## Giấy phép

[MIT](../../LICENSE)
