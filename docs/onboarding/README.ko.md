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

> **한 줄 요약:** 이곳은 저장소의 *가드레일*을 손보는 튜닝 숍입니다. 리프트에 올라가는 건 비즈니스 코드가 아니라 그 둘레의 **coding harness**입니다. Cursor, Claude Code, Codex 같은 AI가 대충 지름길을 타거나, 검증도 없이 "완료"를 외치거나, git에 들어가면 안 될 것을 밀어 넣지 못하게 막는 바깥층이죠.
>
> **그래서 뭐가 좋은가요:** 이미 튜닝된 방법론 skills와 실수 방지 hooks를 그대로 쓰거나, 같은 가드레일을 다른 저장소에 이식할 수 있습니다. 엔진(비즈니스 소스)은 건드리지 않습니다. AI가 가볍게 찌그러뜨리지 못하도록 바깥 롤케이지만 단단히 용접합니다.
>
> **출발까지 세 단:** 한 줄 설치 → (시동) Agent-Kit 장착 → (선택) 내 subject 입고. 퇴근 전에는 `bash tools/harness/test-harness.sh`를 밟으세요. 계기판이 모두 초록이면 검사 통과, 도로 주행 합법입니다.

## 용어집(정비소 은어)

아래에서 계속 만날 말들입니다. 여기서 한 번 익히면 나머지 문서는 설명 없이 그대로 씁니다.

| 은어 | 쉬운 뜻 |
|------|---------|
| **coding harness** | 우리가 실제로 손보는 "차" — 제품 저장소를 둘러싼 AI 개발 가드레일 전체: rules, skills, hooks, trusted suite, ledgers |
| **subject** | 흡수하거나 비교하려고 작업대에 올리는 제품 저장소. 로컬에만 clone하며, **절대** 여기에 commit하지 않음 |
| **harness surface** | 그 차의 튜닝 패널(`AGENTS.md`, skills, hooks). 엔진(비즈니스 소스)이 아님 |
| **Agent-Kit** | 랙 설치 도구 — 방법론 skills / hook templates를 Cursor, Claude Code, Codex 등에 배치 |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — 이 정비소가 무엇이든 출고하기 전 돌리는 다이노 테스트(L2 CI와 같은 장비) |

## 가장 빠른 차선: 한 줄 접수

명령 하나가 전부 처리합니다. 정비소를 clone하고, submodules를 받고, git hooks를 설치하고, Agent-Kit을 랙에 올린 뒤 곧장 다이노(public trusted suite)까지 돌립니다.

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

너무 신식인가요? 구식 pipe도 같은 엔진에 시동을 겁니다.

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

설치 위치와 배선할 대상을 고르고 싶다면 환경 변수 두 개를 설정하세요.

- `TARGET_DIR` — 설치할 디렉터리
- `CLIENT` — 연결할 client: `cursor` / `claude` / `codex` / `codex-native`, 또는 Agent-Kit을 나중으로 미루려면 `skip`

한 줄 설치는 Agent-Kit 장착과 suite 실행까지 끝냅니다. **대부분은 여기서 시동을 끄고 퇴근해도 됩니다.** 한 단씩 직접 조립하고 싶거나 한 줄 설치가 중간에 멈췄다면 아래 수동 차선으로 가세요.

## 수동 접수(직접 조립하기)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

지금은 작업장 문만 연 상태입니다. 부품 상자(Agent-Kit)는 아직 바닥에 있으니 계속 진행하세요.

## Agent-Kit 장착(부품 상자를 벽 랙으로)

Agent-Kit은 이 저장소의 방법론 skills와 hooks를 편집기 / CLI에 설치합니다. 기본 install만으로도 로컬 방법론, 엄선한 SP verification / TDD / review skills, 필요할 때 직접 부르는 Matt library, 낮은 빈도의 advisory router로 구성된 튜닝 기본 세트를 받습니다.

`using-superpowers` / `brainstorming` bootstrap을 몰래 끼워 넣지 않고 vendor hooks도 건드리지 않습니다. client trees(`.cursor` / `.claude` / `.codex` / `.agents`)는 **설치 결과물이며 절대 commit하지 않습니다**. 손으로 고쳐 git에 밀어 넣지 말고 언제나 install로 다시 생성하세요.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 파라미터 | 값 |
|----------|----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold`(선택) | `lean`, `guided`, `structured`; advisory prompt 밀도만 조절하며 **enforcement는 절대 건드리지 않음** |

가장 흔한 로컬 bootstrap은 네 client를 한 번에 장착하는 방식입니다.

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

저장소 profile은 언제나 CLI를 거칩니다(YAML을 손으로 고치면 정비 견적이 커집니다). 설정을 다른 저장소로 가져가려면 먼저 export한 뒤 check하세요.

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN`은 이전 workflow를 위한 명시적 full-plugin 호환 출구로만 남아 있으며, 더는 권장 경로가 아닙니다. 기본 library materialization은 vendor plugins, hooks 또는 allowlist 밖의 skills를 복사하지 않습니다.

## 내 차 입고하기(선택: subject 연결)

정비소가 모두 초록으로 도는지만 확인하고 싶나요? **아무것도 연결하지 마세요.** public clone은 private 제품 저장소가 하나도 없어도 trusted suite를 초록불 가득하게 돌릴 수 있습니다.

실제 subject를 sync / import / compare하려는 경우에만 다음을 실행하세요.

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

순서는 하나만 기억하세요. **`manifest.yaml` 생성 → sync → `--pin`으로 버전 기록 → `harness-ready`가 될 때까지 `check-local-absorb.sh`**. 이 gate를 먼저 통과해야 import / compare / score가 출발할 수 있습니다.

다음 항목은 로컬에 남고 이미 gitignore되어 있습니다. 억지로 commit하려 하지 마세요. pre-commit hook이 현장에서 바로 돌려보냅니다.

- `subjects/manifest.yaml`
- 각 subject의 `pin.json`과 `checkout/`
- `snapshots/`, `comparisons/`

---

아래는 매일 쓰는 참고 도구 벽입니다. 필요할 때 하나씩 꺼내 쓰면 되며, 한 번에 다 읽을 필요는 없습니다.

## 자주 쓰는 명령(공구 벽)

| 원하는 작업 | 실행할 명령 |
|-------------|-------------|
| Public trusted suite(다이노 / CI 형태) | `bash tools/harness/test-harness.sh` |
| Agent-Kit 검증 | `bash tools/harness/agent-kit.sh validate` |
| Harness surface sync | `bash tools/sync/sync-subjects.sh` |
| Pin 다시 쓰기 | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Snapshot import | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## 작업장 배치도(각 부품의 위치)

| 경로 | 용도 | git에 포함? |
|------|------|-------------|
| `agent-kit/skills` | 공개 방법론(submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | client별 hooks / settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | 설치 결과물 | ✗ |
| `subjects/manifest.example.yaml` | 공개 registry 예시 | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | 로컬 registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | 공개 fixtures(CI) | ✓ |
| `snapshots/` / `comparisons/` | absorb 결과물 | ✗ |
| `docs/harness/` | 설계 + ledgers | 일부 |
| `AGENTS.md` | 제약 SSOT(`CLAUDE.md`가 여기로 연결) | ✓ |

## 정비 매뉴얼(더 깊이 보기)

- [`docs/README.md`](../README.md) — 문서 배치 규칙
- [`docs/harness/design.md`](../harness/design.md) — 이 저장소의 harness 설계
- [`docs/specs/`](../specs/) — 설계 아카이브
- [`AGENTS.md`](../../AGENTS.md) — 완료 정의, blacklist, mechanism map

## 라이선스

[MIT](../../LICENSE) — 마음껏 몰고 나가세요. 차량 등록증도 여기 있습니다.
