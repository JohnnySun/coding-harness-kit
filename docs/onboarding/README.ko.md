# coding-harness-kit

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

> **코딩 하네스를 구축·반복**하기 위한 오픈소스 툴킷입니다.  
> 이 저장소에는 비즈니스 소스가 없습니다. 대상은 각 subject의 **harness 표면**입니다.  
> 시작 3단계: submodule 초기화 → Agent-Kit 설치 → (선택) subject 동기화.

| 용어 | 의미 |
|------|------|
| **coding harness** | 제품 저장소 바깥의 AI 개발 가드레일(규칙, skills, hooks, 신뢰 스위트, 장부) |
| **subject** | 이 툴킷이 흡수·비교하는 제품 저장소(로컬 clone, 여기에는 커밋하지 않음) |
| **harness 표면** | subject 안의 harness 관련 경로(`AGENTS.md`, skills, hooks). 비즈니스 소스 아님 |
| **Agent-Kit** | 방법론 skills/hooks 템플릿을 Cursor / Claude Code / Codex 등에 설치하는 설치기 |
| **공개 신뢰 스위트** | `bash tools/harness/test-harness.sh` — 이 저장소의 원커맨드 검증(L2 CI와 동일) |

## 1. 초기화

One-line install (clone + submodules + hooks + Agent-Kit + trusted suite):

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/coding-harness-kit/main/scripts/install.sh)
```

Or:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/coding-harness-kit/main/scripts/install.sh | bash
```

Optional: `TARGET_DIR`, `CLIENT`, `PLUGIN`.

Manual steps:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/coding-harness-kit.git
cd coding-harness-kit
git submodule update --init --recursive
bash tools/harness/install-git-hooks.sh
```

## 2. Agent-Kit 설치 (AI 도구)

클라이언트 트리(`.cursor` / `.claude` / `.codex` / `.agents`)는 **설치 산출물이며 git에 넣지 않습니다**. 항상 install로 재생성하세요.

```bash
CLIENT=<client> bash tools/harness/agent-kit.sh install
bash tools/harness/agent-kit.sh validate
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| 파라미터 | 값 |
|-----------|-----|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `PLUGIN`(선택) | `superpowers`, `mattpocock-skills` |

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
CLIENT=cursor PLUGIN='superpowers mattpocock-skills' bash tools/harness/agent-kit.sh install
```

## 3. (선택) 자체 subject 연결

공개 clone은 **사설 제품 저장소 없이** 신뢰 스위트를 통과할 수 있습니다.

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all
```

---

일상 참고.

## 자주 쓰는 명령

| 목적 | 명령 |
|------|------|
| 공개 신뢰 스위트 | `bash tools/harness/test-harness.sh` |
| Agent-Kit 검증 | `bash tools/harness/agent-kit.sh validate` |
| harness 표면 동기화 | `bash tools/sync/sync-subjects.sh` |
| pin 기록 | `bash tools/sync/sync-subjects.sh <id> --pin` |
| 로컬 absorb 준비 | `bash tools/harness/check-local-absorb.sh --all` |
| snapshot 가져오기 | `python3 tools/import/import_subject.py --all` |
| 비교 리포트 | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| 점수 | `python3 tools/score/score_subject.py <id>` |
| 주간 리포트 | `python3 tools/harness/weekly_report.py` |

## 레이아웃

| 경로 | 역할 | git? |
|------|------|------|
| `agent-kit/skills` | 오픈 방법론(submodule) | ✓ |
| `agent-kit/hooks/clients/` | 클라이언트 hooks/settings 템플릿 | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | 설치 산출물 | ✗ |
| `subjects/manifest.example.yaml` | 공개 registry 예제 | ✓ |
| `subjects/**`(example 제외) | 로컬 registry / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | 공개 fixture(CI) | ✓ |
| `snapshots/` / `comparisons/` | 흡수 산출물 | ✗ |
| `docs/harness/` | 설계와 장부 | 일부 |
| `AGENTS.md` | 제약 SSOT | ✓ |

## 문서

- [`docs/README.md`](../README.md)
- [`docs/harness/design.md`](../harness/design.md)
- [`docs/specs/`](../specs/)
- [`AGENTS.md`](../../AGENTS.md)

## 라이선스

[MIT](../../LICENSE)
