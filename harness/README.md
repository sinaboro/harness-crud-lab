# harness 폴더 — AI 의 작업을 통제하는 장치들

**하네스(harness)** 는 원래 말에게 씌우는 마구(고삐·안장)를 뜻한다. 말은 힘이 세지만, 마구가 없으면 그 힘을 원하는 방향으로 쓸 수 없다.
AI 에이전트도 같다. 코드를 빠르게 많이 쓰지만, **무엇을·어디까지·어떤 기준으로** 할지 정해 주는 장치가 없으면 결과를 믿을 수 없다.

이 폴더에는 그 장치들이 들어 있다.

## 하네스의 다섯 요소와 파일

| 요소 | 질문 | 이 프로젝트에서 담당하는 파일 |
|---|---|---|
| **규칙** | 어떻게 일해야 하는가? | [`AGENTS.md`](AGENTS.md) — 작업 절차, 코드 규칙, 보고 형식 |
| **도구** | 무엇으로 일하는가? | `Dockerfile`·`docker-compose.yml`(도구 상자), `scripts/verify.sh`, `AGENTS.md` 2절 |
| **권한** | 어디까지 해도 되는가? | [`opencode.jsonc`](opencode.jsonc) — allow / ask / deny 규칙 |
| **실행** | 어디에서, 무엇을 가지고 실행되는가? | dev 컨테이너(`/workspace` 만 보인다), [`tasks/`](tasks/) 의 작업 지시서 |
| **검증** | 다 됐다는 것을 어떻게 아는가? | `scripts/verify.sh`, `tests/`, `.githooks/pre-commit`, [`VERIFY_CHECKLIST.md`](VERIFY_CHECKLIST.md) |

규칙(`AGENTS.md`)은 AI 에게 하는 **부탁**이고, 권한(`opencode.jsonc`)과 검증(`pre-commit`)은 부탁이 지켜지지 않아도 작동하는 **잠금장치**다. 둘 다 있어야 한다.

## 파일 목록

| 파일 | 누가 쓰는가 | 언제 쓰는가 |
|---|---|---|
| [`REQUIREMENTS.md`](REQUIREMENTS.md) | 사람이 쓴다 | 요구사항 명세. 무엇을 만들지의 기준. 모든 교시에서 참고 |
| [`AGENTS.md`](AGENTS.md) | 사람이 쓴다, AI 가 읽는다 | 규칙 완성본. 5교시에 프로젝트 맨 위 폴더로 가져간다 |
| [`AGENTS.template.md`](AGENTS.template.md) | 학습자가 채운다 | 5교시에 규칙을 직접 써 보는 틀 |
| [`opencode.jsonc`](opencode.jsonc) | 사람이 쓴다 | 권한 규칙 완성본. 5교시에 프로젝트 맨 위 폴더로 가져간다 |
| [`TASK_TEMPLATE.md`](TASK_TEMPLATE.md) | 학습자가 채운다 | AI 에게 일을 시킬 때마다 쓰는 작업 지시서 틀 |
| [`tasks/`](tasks/) | 사람이 쓴다, AI 가 읽는다 | 6·8·9·10·11교시의 작업 지시서 |
| [`VERIFY_CHECKLIST.md`](VERIFY_CHECKLIST.md) | 학습자가 체크한다 | AI 가 "다 했다"고 한 뒤, 커밋하기 전 |
| [`WORKLOG.md`](WORKLOG.md) | 학습자가 쓴다 | 교시마다 한 일과 이해한 내용을 기록 |

## 왜 `AGENTS.md` 가 여기(harness 폴더)에 있는가

OpenCode 는 프로젝트 **맨 위 폴더**의 `AGENTS.md` 를 자동으로 읽는다.
처음에는 맨 위 폴더에 `AGENTS.md` 가 없다. 그래서 2~4교시에는 AI 가 아무 규칙 없이 일한다.
5교시에 규칙을 직접 써서 맨 위 폴더에 놓고, **규칙이 있을 때와 없을 때 AI 의 행동이 어떻게 달라지는지** 비교한다.

## 한 번의 작업이 흘러가는 길

```text
 ① 요구사항        REQUIREMENTS.md 에서 이번에 만들 번호(R1 ...)를 고른다
      │
 ② 작업 지시       tasks/NN_….md 를 AI 에게 건넨다  (틀: TASK_TEMPLATE.md)
      │
 ③ 하네스가 통제   AGENTS.md(규칙) + opencode.jsonc(권한) 안에서만 AI 가 움직인다
      │               · 계획을 먼저 말하고 사람의 "진행"을 기다린다
      │               · 금지된 명령·파일은 실행 자체가 막힌다
      │
 ④ 실행·테스트     sh scripts/verify.sh  (ruff + pytest)
      │
 ⑤ 확인·수정·재검증
      ├─ 실패 → 오류를 AI 에게 보여 주고 수정 → ④ 로 돌아간다
      └─ 통과 → 사람이 VERIFY_CHECKLIST.md 로 검토 → git commit
                 (pre-commit 이 한 번 더 검증한다. 실패하면 커밋이 취소된다)
```
