# 6교시. AI 에게 CRUD 구현 지시

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | 메모 CRUD 초안 (만들기·목록·한 건 보기, 메모리 저장, 테스트 포함) |
| 시작 상태 | 5교시를 마친 상태 (`AGENTS.md`, 권한 규칙, `pre-commit` 훅이 있다) |

4교시 코드가 없으면 **[dev]** `sh scripts/checkpoint.sh 04` 로 가져온다. 하네스 파일이 없으면 `cp harness/AGENTS.md AGENTS.md`, `cp harness/opencode.jsonc opencode.jsonc`, `git config core.hooksPath .githooks` 를 실행한다.

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
 └────────────── 이번 교시: 다섯 단계를 처음으로 한 바퀴 돈다 ──────────────┘
```

## 학습 목표

1. 요구사항 명세에서 이번에 만들 범위를 골라낸다.
2. 작업 지시서의 여섯 칸(목표·요구사항·범위·하지 말 것·완료 조건·진행 방법)을 읽고 쓸 수 있다.
3. AI 의 계획을 검토하고 승인하거나 고치게 한다.
4. 검증 체크리스트로 AI 의 결과를 검토한다.
5. AI 가 쓴 코드를 읽고 내 말로 설명한 뒤 커밋한다.

## 왜 CRUD 를 한 번에 시키지 않는가

이번 교시의 범위는 **만들기(C)와 보기(R)** 까지다. 고치기·지우기는 9교시, DB 연결은 8교시에 한다.

- 작은 작업은 AI 가 틀릴 여지가 적다.
- 바뀐 코드가 적어야 **내가 읽고 이해할 수 있다.**
- 문제가 생기면 그 작업 하나만 되돌리면 된다.

기준: **AI 가 바꾼 내용을 내가 10분 안에 읽고 설명할 수 있는 크기.**

---

## 따라 하기

### 1단계. ① 요구사항 읽기 (10분)

VS Code 에서 `harness/REQUIREMENTS.md` 를 열고 **R1, R2, R3, R6** 을 읽는다. 4교시 4단계에서 채운 대조표를 다시 꺼낸다. 그때 "맞지 않다"고 적은 항목들이 이번에 AI 가 채워야 할 것들이다.

| 요구사항 | 4교시에 손으로 만든 코드 | 이번 교시의 목표 |
|---|---|---|
| R1. 응답에 `created_at`, `updated_at` | 없다 | 있다 |
| R2. 나중에 만든 메모가 앞에 | 먼저 만든 것이 앞 | 나중 것이 앞 |
| R3. 한 건 보기, 없으면 404 | 없다 | 있다 |
| R6. 빈 제목, 100자 넘는 제목 → 422 | 받아들인다 | 422 |

### 2단계. ② 작업 지시서 읽기 (10분)

`harness/tasks/06_memo_draft.md` 를 연다. 5교시에 실패했던 한 줄 지시("메모 삭제 기능 만들어 줘")와 비교하며 읽는다.

| 칸 | 이 지시서에 적힌 것 | 없으면 생기는 일 |
|---|---|---|
| 1. 목표 | 만들기·목록·한 건 보기. 저장소는 메모리 | 어디까지가 끝인지 모른다 |
| 2. 요구사항 | R1, R2, R3, R6 | 상태 코드·문구를 AI 가 지어낸다 |
| 3. 범위 | 고칠 파일 2개, 새 파일 2개 | 관계없는 파일까지 고친다 |
| 4. 하지 말 것 | 수정·삭제, DB, 화면, 새 패키지 | 시키지 않은 기능이 생긴다 |
| 5. 완료 조건 | 체크 항목 7개 | "다 했습니다"를 확인할 수 없다 |
| 6. 진행 방법 | 계획 먼저, "진행" 뒤에 구현 | 방향이 틀려도 끝난 뒤에야 안다 |

지시서의 틀과 칸마다의 설명은 `harness/TASK_TEMPLATE.md` 에 있다.

### 3단계. ② 지시하고 ③ 계획 검토하기 (20분)

시작 전에 상태가 깨끗한지 확인한다.

**[dev]**

```bash
git status
sh scripts/verify.sh
```

`working tree clean` 이고 "검증 통과"여야 한다. **깨끗한 상태에서 시작해야, 끝난 뒤의 `git diff` 가 온전히 AI 가 한 일이 된다.**

OpenCode 를 열고 지시서를 건넨다.

**[dev]**

```bash
opencode
```

**[AI]**

```text
harness/tasks/06_memo_draft.md 를 읽고 그 지시대로 작업해 줘. AGENTS.md 의 작업 절차를 따라, 먼저 계획만 말하고 내 승인을 기다려.
```

AI 가 파일들을 읽고 **계획**을 말한다. 바로 "진행"이라고 하지 않는다. 아래 항목으로 계획을 검토한다.

**계획 검토 체크리스트**

- [ ] 고치겠다는 파일이 지시서의 "범위" 안에 있는가?
- [ ] 수정(PUT)·삭제(DELETE)·DB·화면을 만들겠다는 말이 **없는가?**
- [ ] 테스트를 만들겠다고 했는가? R1, R2, R3, R6 이 모두 언급되었는가?
- [ ] 없는 번호 → 404, 오류 문구가 요구사항과 같은가?
- [ ] 새 패키지를 설치하겠다는 말이 **없는가?**
- [ ] 이해되지 않는 낱말이 있는가? 있으면 지금 묻는다.

계획에 문제가 있으면 구체적으로 짚어 고치게 한다.

**[AI]** (예시 — 계획에 삭제가 들어 있을 때)

```text
계획 3번에 삭제 API 가 들어 있어. 지시서 4번(하지 말 것)에 따라 삭제는 이번 범위가 아니야. 빼고 계획을 다시 말해 줘.
```

**[AI]** (예시 — 모르는 낱말이 있을 때)

```text
계획에 나온 "fixture" 가 무슨 뜻이야? 초보자에게 설명하듯 두 문장으로 알려 줘. 파일은 아직 고치지 마.
```

계획이 지시서와 맞으면 승인한다.

**[AI]**

```text
진행
```

### 4단계. ③ 하네스가 일하는 것 지켜보기 (15분)

AI 가 파일을 고치고 명령을 실행한다. 지켜보며 아래를 기록한다. 이 기록은 7단계의 `WORKLOG.md` 에 적는다.

| 지켜볼 것 | 기록 |
|---|---|
| 묻지 않고 실행한 명령 (`pytest`, `sh scripts/verify.sh`, `git status` …) | |
| 나에게 물어본 명령 — 무엇이었고, 허락했는가 거절했는가 | |
| 막힌(deny) 일이 있었는가 | |
| 검증이 처음에 실패했는가? AI 가 스스로 고쳤는가? 몇 번? | |

**물어볼 때의 판단 기준.**

- 지시서와 `AGENTS.md` 에 비추어 필요한 일인가? → `once`
- 왜 필요한지 모르겠는가? → 일단 `reject` 하고 이유를 묻는다. "방금 그 명령은 왜 필요했어?"
- `pip install` 처럼 지시서가 금지한 일인가? → `reject`

VS Code 를 옆에 띄워 두면 AI 가 고치는 파일이 **실시간으로 바뀌는 것**이 보인다. 2교시의 바인드 마운트 덕분이다.

AI 가 보고를 마치면 OpenCode 를 닫지 말고 그대로 둔다. 다음 단계에서 질문할 것이다. dev 셸이 하나 더 필요하므로 PowerShell 창을 새로 열어 들어간다.

**[PS]**

```powershell
cd C:\harness-crud-lab
docker compose exec dev bash
```

### 5단계. ④ 검증 — AI 의 말을 믿지 않고 직접 실행하기 (15분)

AI 가 "검증 통과했습니다"라고 보고했더라도 **직접 실행한다.** `harness/VERIFY_CHECKLIST.md` 를 열어 놓고 1단계부터 따라간다.

**(1) 기계가 확인하는 것**

**[dev]** (새로 연 셸)

```bash
sh scripts/verify.sh
```

마지막 줄이 "검증 통과"인지, 통과한 테스트가 몇 개인지 본다. 참고로 이 교시의 완성 예시(`checkpoints/lesson06`)는 다음과 같이 나온다. 테스트 개수는 AI 가 만든 것에 따라 다를 수 있다.

```text
............                                                             [100%]
12 passed in 0.08s
```

**(2) 무엇이 바뀌었는지**

**[dev]**

```bash
git status
git diff --stat
```

- [ ] 바뀌거나 새로 생긴 파일이 `app/main.py`, `app/schemas.py`, `tests/conftest.py`, `tests/test_memos.py` 뿐인가?
- [ ] `tests/test_health.py` 는 바뀌지 않았는가?
- [ ] `AGENTS.md`, `harness/`, `scripts/` 는 바뀌지 않았는가?

**(3) 직접 불러 보기**

**[dev]**

```bash
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": "장보기", "content": "우유, 달걀"}'
```

```text
{"id":1,"title":"장보기","content":"우유, 달걀","created_at":"2026-11-10T05:47:04.556149Z","updated_at":"2026-11-10T05:47:04.556149Z"}
```

`created_at`, `updated_at` 이 생겼다. (시각은 실행한 때에 따라 다르다.)

**[dev]**

```bash
curl -s http://app:8000/memos/1
curl -s http://app:8000/memos/999
```

```text
{"id":1,"title":"장보기","content":"우유, 달걀","created_at":"2026-11-10T05:47:04.556149Z","updated_at":"2026-11-10T05:47:04.556149Z"}
{"detail":"메모를 찾을 수 없습니다."}
```

**[dev]**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://app:8000/memos/999
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": ""}'
```

```text
404
{"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
```

오류 문구 `메모를 찾을 수 없습니다.` 가 요구사항 R3 과 **한 글자도 다르지 않은지** 확인한다. 다르다면 AI 에게 요구사항의 해당 줄을 가리켜 고치게 한다.

http://localhost:8000/docs 에서도 `GET /memos/{memo_id}` 가 생겼는지 눌러 본다.

### 6단계. ⑤ 코드 읽기 — 내 것으로 만들기 (30분)

테스트가 통과했다. 여기서 커밋하면 바이브 코딩이다. **읽고 이해한 뒤에 커밋한다.**

AI 가 쓴 코드는 사람마다 다르다. 아래는 완성 예시(`checkpoints/lesson06`)를 기준으로 한 읽기 안내다. 내 코드에서 같은 역할을 하는 부분을 찾아가며 읽는다.

**(1) `app/schemas.py` — 데이터의 모양**

```python
class MemoIn(BaseModel):
    """메모를 만들거나 고칠 때 클라이언트가 보내는 데이터"""

    # 제목: 반드시 있어야 하고 1~100자
    title: str = Field(min_length=1, max_length=100)
    # 내용: 안 보내면 빈 문자열, 최대 1000자
    content: str = Field(default="", max_length=1000)


class MemoOut(BaseModel):
    """서버가 돌려주는 메모 한 건"""

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
```

- 4교시의 `title: str` 이 `Field(min_length=1, max_length=100)` 로 바뀌었다. **요구사항 R6 의 문장이 코드 한 줄이 된 것**이다.
- 들어오는 모양(`MemoIn`)과 나가는 모양(`MemoOut`)이 따로 있다. `id` 와 시각은 서버가 정하므로 들어오는 쪽에는 없다.

**(2) `app/main.py` — 저장소**

```python
# 메모 저장소: {번호: 메모} 모양의 딕셔너리. 번호로 바로 찾을 수 있다.
memos: dict[int, dict] = {}
# 다음에 만들 메모의 번호. 메모를 지워도 번호가 다시 쓰이지 않게 따로 센다.
next_id = 1
```

4교시에는 리스트였고 번호를 `len(memos) + 1` 로 정했다. 4교시 확인 문제 7번의 답이 여기 있다.

**(3) `app/main.py` — 한 건 보기와 404**

```python
@app.get("/memos/{memo_id}", response_model=MemoOut)
def get_memo(memo_id: int) -> dict:
    if memo_id not in memos:  # 그런 번호가 없으면
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    return memos[memo_id]
```

- 주소의 `{memo_id}` 자리에 온 값이 함수의 인자 `memo_id` 로 들어간다. `/memos/7` 이면 `memo_id` 는 `7` 이다.
- `memo_id: int` — 정수가 아니면(`/memos/abc`) FastAPI 가 422 를 돌려준다.
- `raise HTTPException(...)` — 함수를 그 자리에서 끝내고 오류 응답을 보낸다.
- `response_model=MemoOut` — 응답이 `MemoOut` 모양으로 나간다.

**(4) `tests/conftest.py` — 테스트마다 깨끗하게**

```python
@pytest.fixture
def client():
    reset_store()  # 앞 테스트가 남긴 메모를 지운다
    with TestClient(app) as test_client:
        yield test_client
```

`@pytest.fixture` 가 붙은 함수는 "테스트가 쓸 준비물을 만드는 함수"다. 테스트 함수가 인자로 `client` 를 받으면 pytest 가 이 함수를 먼저 실행한다. 테스트마다 저장소를 비우므로 테스트끼리 서로 영향을 주지 않는다.

**(5) `tests/test_memos.py` — 요구사항이 테스트가 되었는가**

```python
def test_get_memo_not_found(client):
    response = client.get("/memos/999")  # 없는 번호
    assert response.status_code == 404
    assert response.json() == {"detail": "메모를 찾을 수 없습니다."}
```

요구사항 R3 의 둘째 줄과 나란히 놓고 본다.

> 그 번호의 메모가 없으면 상태 코드 **404** 와 `{"detail": "메모를 찾을 수 없습니다."}` 를 돌려준다.

**문장이 그대로 코드가 되었다.** `harness/VERIFY_CHECKLIST.md` 3단계의 대응표를 펴고, R1·R2·R3·R6 마다 테스트가 있는지 내 `tests/test_memos.py` 에서 찾아 체크한다. 빠진 것이 있으면 AI 에게 추가하게 한다.

**(6) AI 에게 묻기**

읽다가 막힌 줄은 열어 둔 OpenCode 에 묻는다. 좋은 질문은 **파일과 줄을 짚는다.**

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. app/main.py 에서 global next_id 는 왜 필요해? 그 줄을 지우면 어떤 오류가 나?
```

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. POST /memos 요청이 들어와서 201 응답이 나갈 때까지, 어떤 파일의 어떤 함수가 어떤 순서로 실행되는지 번호를 붙여 알려 줘.
```

**[AI]**

```text
tests/test_memos.py 에 R2("나중에 만든 메모가 앞에")를 확인하는 테스트가 있어? 있으면 이름을, 없으면 없다고 말해 줘.
```

AI 의 설명은 3교시에 배운 대로 **실행해서 확인한다.** 예를 들어 `global next_id` 줄을 지우고 저장한 뒤 `sh scripts/verify.sh` 를 실행해 본다. AI 가 말한 오류가 나는가? 확인했으면 되돌린다(`git restore app/main.py` 는 쓰지 않는다. 아직 커밋 전이라 AI 의 작업까지 사라진다. VS Code 에서 Ctrl+Z 로 되돌린다).

### 7단계. ⑤ 기록하고 저장하기 (10분)

**(1) 작업 기록.** VS Code 에서 `harness/WORKLOG.md` 를 열고, 맨 아래에 틀을 복사해 6교시 기록을 쓴다. "4. 바뀐 코드를 내 말로 설명하기"의 세 문장을 쓰지 못하면 6단계로 돌아간다.

**(2) 마지막 검토.** `VERIFY_CHECKLIST.md` 의 4단계(코드를 사람이 읽는다) 항목을 체크한다.

**[dev]**

```bash
git diff app/
```

**(3) 커밋.**

**[dev]**

```bash
git add -A
git status
git commit -m "6교시: 메모 만들기·보기 초안 (R1, R2, R3, R6)"
```

`git status` 에서 커밋될 파일 목록에 `.env` 가 없는지 본다. 커밋하면 `pre-commit` 이 검증을 한 번 더 실행한다.

**[dev]**

```bash
git log --oneline -3
```

OpenCode 는 `/exit` 로 닫는다.

---

## 검증이 실패했을 때 — ⑤ 의 다른 길

AI 가 끝냈다고 했는데 내가 실행한 `sh scripts/verify.sh` 가 실패하면, **오류 전체를 붙여서** 전달한다.

**[AI]**

```text
sh scripts/verify.sh 가 실패했어. 아래가 출력이야.
원인을 먼저 설명하고, 내가 "진행"이라고 하면 고쳐 줘. 테스트를 느슨하게 고쳐서 통과시키지는 마.

(여기에 오류 출력을 붙여 넣는다)
```

고친 뒤에는 5단계부터 다시 한다. 세 번 고쳐도 통과하지 못하면 멈춘다.

**[dev]**

```bash
git restore .
git status
```

새로 생긴 파일(`Untracked files`)도 지워 처음 상태로 돌린 뒤, `/new` 로 새 대화를 열어 다시 시킨다. 그래도 막히면 `sh scripts/checkpoint.sh 06 --force` 로 완성 예시를 가져와 6단계(코드 읽기)를 한다.

## 하네스 관점 — 이번 교시에서 본 것

| 단계 | 통제한 장치 | 사람이 한 판단 |
|---|---|---|
| ① 요구사항 | `REQUIREMENTS.md` | 이번에 만들 번호를 골랐다 |
| ② 지시 | `tasks/06_memo_draft.md` | 범위와 "하지 말 것"을 정했다 |
| ③ 제어 | `AGENTS.md`(계획 먼저), `opencode.jsonc`(ask/deny) | 계획을 검토하고 승인했다. 명령을 허락하거나 거절했다 |
| ④ 실행·테스트 | `verify.sh` | AI 의 보고를 믿지 않고 직접 실행했다 |
| ⑤ 수정·저장 | `VERIFY_CHECKLIST.md`, `pre-commit`, `WORKLOG.md` | 테스트와 코드를 읽고, 설명할 수 있을 때 커밋했다 |

코드는 AI 가 썼다. **무엇을 만들지, 계획이 맞는지, 결과를 받아들일지는 모두 사람이 정했다.**

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| AI 가 계획 없이 바로 고치기 시작한다 | 지시 문장에 "먼저 계획만 말하고 내 승인을 기다려"를 넣었는지, `AGENTS.md` 가 맨 위 폴더에 있는지 확인한다. 이미 고쳤다면 `/undo` 로 되돌리고 다시 시킨다. |
| AI 가 `harness/tasks/…` 파일을 못 찾는다 | 파일 이름을 잘못 쳤다. 입력 칸에서 `@` 를 치면 파일을 골라 넣을 수 있다. |
| 권한 프롬프트가 너무 자주 뜬다 | 정상이다. 무엇을 묻는지 읽고 `once` 로 답한다. 같은 명령이 반복되면 그 명령이 `AGENTS.md` 2절 표에 있어야 하는 것인지 생각해 본다. |
| `verify.sh` 는 통과하는데 `curl` 결과가 요구사항과 다르다 | 테스트가 그 요구사항을 확인하지 않고 있다. 어느 요구사항인지 짚어 테스트를 추가하게 한다. |
| 테스트를 따로 돌리면 통과하는데 함께 돌리면 실패한다 | 테스트끼리 저장소를 공유하고 있다. `conftest.py` 가 테스트마다 저장소를 비우는지 확인하게 한다. |
| `curl` 로 만든 메모가 자꾸 사라진다 | AI 가 파일을 고칠 때마다 서버가 다시 켜지고, 메모리 저장소가 비워진다. 4교시 5단계에서 본 현상이다. |
| AI 의 답이 중간에 끊기거나 `429`, `402` 오류가 난다 | OpenRouter 의 사용 한도나 크레딧 문제다. 잠시 뒤 다시 시도하거나 Credits 화면을 확인한다. |

## 확인 문제

1. 작업 지시서의 "4. 하지 말 것"이 없으면 어떤 일이 생기는가? 5교시 1단계의 관찰을 예로 들어 설명하시오.
2. AI 의 계획을 승인하기 전에 확인해야 할 것을 세 가지 쓰시오.
3. `Field(min_length=1, max_length=100)` 은 요구사항의 어느 문장을 코드로 옮긴 것인가?
4. `MemoIn` 에는 `id` 가 없고 `MemoOut` 에는 있다. 왜 그런가?
5. `raise HTTPException(status_code=404, ...)` 다음 줄의 `return memos[memo_id]` 는 실행되는가?
6. `conftest.py` 에서 `reset_store()` 를 지우면 어떤 테스트가 왜 실패하게 되는가?
7. AI 가 "12개 테스트 모두 통과"라고 보고했다. 커밋하기 전에 사람이 더 확인해야 할 것을 세 가지 쓰시오.
8. 이번 교시에 사람이 내린 **판단**을 모두 나열하시오.

## 다음 교시

[7교시. PostgreSQL 기초](07_PostgreSQL_기초.md) — 서버를 껐다 켜도 남는 저장소, 데이터베이스를 배운다.
