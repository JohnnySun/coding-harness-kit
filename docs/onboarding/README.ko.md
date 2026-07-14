# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <strong>한국어</strong> |
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
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **이 정비소가 손보는 차는 여러분의 coding harness입니다.** 제품 저장소를 둘러싼 AI 개발 가드레일 계층입니다. 그 제품 저장소, 즉 subject가 차의 주인입니다. 비즈니스 소스는 엔진이므로 보닛은 열지 않습니다.
> 가장 짧은 경로: 한 줄 접수 명령 실행 → Cursor, Claude Code 또는 Codex용 Agent-Kit 설치 → 필요하면 실제 subject를 연결한 뒤 sync, pin, `harness-ready` 확인. 새 부품은 public trusted suite라는 다이노에 올립니다. 도장 상태 확인은 테스트 계획이 아닙니다.

| 용어 | 의미(정비소 비유) |
|------|---------|
| **coding harness** | 여러분의 차: 제품 저장소를 둘러싼 AI 개발 가드레일 계층(rules, skills, hooks, trusted suite, ledgers) |
| **subject** | 차를 소유한 제품 저장소(로컬 clone이며 여기에는 커밋하지 않음) |
| **harness surface** | 부품 작업대: `AGENTS.md`, skills, hooks 같은 가드레일 파일. 비즈니스 소스가 아님 |
| **Agent-Kit** | 부품 선반: 방법론 skills / hook templates를 Cursor, Claude Code, Codex 등에 설치 |
| **public trusted suite** | 다이노: `bash tools/harness/test-harness.sh`(L2 CI와 동일) |

## 1. 접수(초기화)

가장 빠르게 작업대에 들어오는 방법은 한 줄 설치 프로그램입니다. 저장소를 clone하고 submodules를 초기화하며 git hooks와 Agent-Kit을 설치한 다음 public trusted suite를 실행합니다.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

셸이 process substitution을 지원하지 않으면 같은 효과의 pipe 형식을 사용합니다.

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

선택 환경 변수는 `TARGET_DIR`과 `CLIENT`입니다. `CLIENT`는 `cursor` / `claude` / `codex` / `codex-native` / `skip` 중 하나로 설정합니다.

수동 대체 경로를 쓰거나 렌치가 도는 과정을 하나씩 보고 싶다면:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

이제 submodules가 초기화되고 git hooks가 설치된 `los-santos-customs/` 안에 있어야 합니다. 한 줄 경로는 선택한 client용 Agent-Kit도 설치하고 public trusted suite도 실행합니다. 수동 경로를 택했다면 §2로 가세요. 수동 변속에는 단계가 하나 더 있지만, 추억을 위한 것은 아닙니다.

## 2. 부품 장착(Agent-Kit)

Agent-Kit은 이 정비소의 skills와 hooks를 편집기나 CLI에 설치합니다. 별도 옵션 없는 install은 다음과 같은 선별된 기본값을 제공합니다.

- 로컬 방법론
- 엄선된 SP verification, TDD, review skills
- 사용자가 직접 호출하는 Matt library
- 낮은 빈도의 advisory router

`using-superpowers` / `brainstorming` bootstrap이나 vendor hooks는 설치하지 않습니다. client trees(`.cursor` / `.claude` / `.codex` / `.agents`)는 설치 출력이며 커밋하지 않습니다. install로 다시 생성하세요. 생성 파일에는 판금 작업이 필요 없습니다.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 파라미터 | 값 |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold`(선택) | `lean`, `guided`, `structured`; advisory 밀도만 조정 |

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

`PLUGIN`은 이전 workflow를 위한 명시적 full-plugin 호환 경로로만 남아 있습니다. 더 이상 권장 설치 경로가 아닙니다. 기본 library materialization은 allowlist 밖의 vendor plugins, hooks 또는 skills를 복사하지 않습니다. 부품 선반에 재고표가 있는 데는 이유가 있습니다.

## 3. (선택) 내 차 입고하기

public clone은 private 제품 저장소 없이 public trusted suite를 실행할 수 있습니다. 실제 subject를 sync, import 또는 compare해야 할 때만 고객의 차를 로컬 작업대에 연결합니다.

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

순서가 중요합니다.

1. example에서 `subjects/manifest.yaml`을 만들고 remotes가 접근 가능한 repos를 가리키게 합니다.
2. sync를 실행하여 각 subject의 harness surface를 가져옵니다.
3. `<id> --pin`으로 평가할 정확한 revision을 기록합니다.
4. local absorb check를 실행합니다. 통과한 subject가 `harness-ready`입니다. 그 후에만 import, compare, score가 신뢰할 수 있는 결과를 낼 수 있습니다.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/`, `comparisons/`는 고객의 차와 작업 지시서입니다. 로컬에 남고 gitignore되며 public showroom에는 들어가지 않습니다. 비밀주의가 아니라 기본적인 키 관리입니다.

---

이제 차가 스스로 움직입니다. 아래는 서비스 베이 참고 자료입니다.

## 자주 쓰는 명령

| 목적 | 명령 |
|------|------|
| public trusted suite(loop 닫기 / CI) | `bash tools/harness/test-harness.sh` |
| Agent-Kit 검증 | `bash tools/harness/agent-kit.sh validate` |
| harness surface sync | `bash tools/sync/sync-subjects.sh` |
| pin 다시 쓰기 | `bash tools/sync/sync-subjects.sh <id> --pin` |
| local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot import | `python3 tools/import/import_subject.py --all` |
| compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| score | `python3 tools/score/score_subject.py <id>` |
| weekly report | `python3 tools/harness/weekly_report.py` |

## 레이아웃

| 경로 | 역할 | git? |
|------|------|------|
| `agent-kit/skills` | 공개 방법론(submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | install outputs | ✗ |
| `subjects/manifest.example.yaml` | public registry example | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | local registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | public fixtures(CI) | ✓ |
| `snapshots/` / `comparisons/` | absorb products | ✗ |
| `docs/harness/` | design + ledgers | 일부 |
| `AGENTS.md` | 제약 SSOT(`CLAUDE.md` → it) | ✓ |

## 문서

- [`docs/README.md`](../README.md) — 문서 배치 규칙
- [`docs/harness/design.md`](../harness/design.md) — 이 저장소의 harness design
- [`docs/specs/`](../specs/) — design archive
- [`AGENTS.md`](../../AGENTS.md) — 완료 정의, blacklist, mechanism map

## 라이선스

[MIT](../../LICENSE)
