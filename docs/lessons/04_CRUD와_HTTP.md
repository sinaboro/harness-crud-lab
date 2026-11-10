# 4교시. CRUD 와 HTTP 기초

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | GET·POST 테스트 |
| 시작 상태 | 3교시를 마친 상태 (`/hello` 가 동작하고 커밋되어 있다) |

막혔거나 3교시 결과가 없으면 **[dev]** `sh scripts/checkpoint.sh 03` 으로 3교시 완성 예시를 가져온다.

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
 └─ 이번 교시: 요구사항에 쓰이는 "말"(주소·방식·상태 코드·JSON)을 배운다
```

`harness/REQUIREMENTS.md` 는 "`POST /memos` 를 부르면 201 을 돌려준다"처럼 적혀 있다. 이 문장을 읽고 쓸 수 있어야 AI 에게 정확히 시킬 수 있고, AI 의 결과가 맞는지 판단할 수 있다.

## 학습 목표

1. CRUD 네 가지를 HTTP 방식(POST·GET·PUT·DELETE)과 짝지을 수 있다.
2. 요청과 응답이 무엇으로 이루어지는지 말할 수 있다.
3. 상태 코드 200·201·204·404·422 의 뜻을 안다.
4. 메모를 만들고(POST) 보는(GET) API 를 손으로 만들고, `/docs` 와 `curl` 로 시험한다.
5. 메모리에 저장한 데이터가 서버를 다시 켜면 사라지는 것을 확인한다.

---

## 1. 개념

### CRUD

데이터를 다루는 일은 결국 네 가지다.

| | 뜻 | 메모장에서 |
|---|---|---|
| **C**reate | 만들기 | 새 메모 쓰기 |
| **R**ead | 읽기 | 메모 목록 보기, 메모 한 건 보기 |
| **U**pdate | 고치기 | 메모 내용 바꾸기 |
| **D**elete | 지우기 | 메모 지우기 |

### HTTP — 브라우저와 서버가 주고받는 말

브라우저(클라이언트)가 **요청**을 보내고 서버가 **응답**을 돌려준다. 한 번 묻고 한 번 답하면 끝이다.

**요청**은 세 부분이다.

| 부분 | 뜻 | 예 |
|---|---|---|
| 방식(메서드) | 무엇을 하려는가 | `GET`, `POST`, `PUT`, `DELETE` |
| 주소(경로) | 무엇에 대해서인가 | `/memos`, `/memos/1` |
| 본문(body) | 함께 보내는 데이터 (없을 수도 있다) | `{"title": "장보기"}` |

**응답**은 두 부분이다.

| 부분 | 뜻 | 예 |
|---|---|---|
| 상태 코드 | 어떻게 되었는가 (세 자리 숫자) | `200`, `404` |
| 본문 | 돌려주는 데이터 (없을 수도 있다) | `{"id": 1, "title": "장보기"}` |

### CRUD ↔ HTTP ↔ SQL

같은 일을 세 가지 말로 부른다. 이 표는 3일 내내 쓴다.

| 하는 일 | HTTP 방식 + 주소 | 성공 상태 코드 | SQL (7교시) |
|---|---|---|---|
| 만들기 | `POST /memos` | 201 | `INSERT` |
| 목록 보기 | `GET /memos` | 200 | `SELECT` |
| 한 건 보기 | `GET /memos/1` | 200 | `SELECT … WHERE` |
| 고치기 | `PUT /memos/1` | 200 | `UPDATE … WHERE` |
| 지우기 | `DELETE /memos/1` | 204 | `DELETE … WHERE` |

주소가 `/memos` 하나인데 방식에 따라 하는 일이 달라진다는 점에 주목한다. 주소는 **무엇**(메모들)을 가리키고, 방식은 **어떻게**(만든다/본다)를 말한다.

### 상태 코드

| 코드 | 이름 | 뜻 | 메모장에서 |
|---|---|---|---|
| 200 | OK | 성공 | 목록 보기, 고치기 성공 |
| 201 | Created | 성공했고 새로 만들어졌다 | 메모 만들기 성공 |
| 204 | No Content | 성공했고 돌려줄 내용이 없다 | 메모 지우기 성공 |
| 404 | Not Found | 그런 것이 없다 | 없는 번호의 메모를 찾을 때 |
| 422 | Unprocessable Content | 보낸 데이터가 규칙에 맞지 않는다 | 제목 없이 만들려 할 때 |
| 500 | Internal Server Error | 서버 코드가 오류를 냈다 | 버그 |

첫 자리로 큰 뜻을 안다. **2xx 는 성공, 4xx 는 요청한 쪽의 잘못, 5xx 는 서버의 잘못.**

### JSON

요청과 응답의 본문은 **JSON** 이라는 형식으로 쓴다. 파이썬의 딕셔너리·리스트와 거의 똑같이 생겼다.

```json
{"id": 1, "title": "장보기", "content": "우유, 달걀"}
```

- 이름과 글자는 **큰따옴표**로 감싼다. 작은따옴표는 안 된다.
- 메모 여러 건은 `[ {…}, {…} ]` 처럼 대괄호로 감싼다.

---

## 따라 하기

### 1단계. 메모 만들기·보기 API 손으로 쓰기 (25분)

VS Code 에서 `app/main.py` 를 연다. 아래 세 군데를 고친다. 다 고친 모습은 `checkpoints/lesson04/app/main.py` 와 같다.

**(1) 맨 위의 import 에 한 줄을 추가한다.**

```python
from fastapi import FastAPI
from pydantic import BaseModel
```

**(2) `app = FastAPI(...)` 줄 아래에 추가한다.**

```python
# 메모를 담아 둘 리스트. 서버가 켜져 있는 동안에만 유지된다.
memos: list[dict] = []


class MemoIn(BaseModel):
    """메모를 만들 때 클라이언트가 보내는 데이터의 모양"""

    title: str  # 제목: 글자여야 하고, 반드시 보내야 한다
    content: str = ""  # 내용: 안 보내면 빈 문자열
```

`class MemoIn(BaseModel)` 은 "요청 본문은 이런 모양이어야 한다"는 틀이다. `title` 에는 기본값이 없으므로 **반드시 보내야 하고**, `content` 는 기본값이 `""` 이므로 안 보내도 된다.

**(3) 파일 맨 아래에 추가한다.**

```python
@app.post("/memos", status_code=201)
def create_memo(memo: MemoIn) -> dict:
    """메모 만들기. 성공하면 201(Created)과 함께 만든 메모를 돌려준다."""
    new_memo = {
        "id": len(memos) + 1,  # 번호는 1, 2, 3 ... 순서대로
        "title": memo.title,
        "content": memo.content,
    }
    memos.append(new_memo)  # 리스트에 넣는다
    return new_memo


@app.get("/memos")
def list_memos() -> list[dict]:
    """메모 목록 보기"""
    return memos
```

- `@app.post` — 이번에는 `get` 이 아니라 `post` 다. 같은 주소 `/memos` 에 방식만 다른 함수 두 개를 연결했다.
- `status_code=201` — 성공하면 200 대신 201 을 돌려주라는 뜻이다.
- `memo: MemoIn` — 요청 본문을 `MemoIn` 모양으로 받는다. 모양이 맞지 않으면 이 함수는 실행되지도 않는다.

저장하고, 서버가 다시 켜졌는지 확인한다.

**[PS]**

```powershell
docker compose logs app --tail 5
```

`Application startup complete.` 가 마지막 근처에 있으면 된다. 오류가 보이면 줄 번호를 보고 오타를 고친다.

### 2단계. `/docs` 에서 시험하기 (15분)

http://localhost:8000/docs 를 새로 고친다. `POST /memos` 와 `GET /memos` 가 생겼다.

**(1) 목록 보기.** `GET /memos` → Try it out → Execute.

- Code: `200`
- Response body: `[]` (아직 메모가 없다)

**(2) 만들기.** `POST /memos` → Try it out. Request body 칸을 아래로 바꾸고 Execute.

```json
{"title": "장보기", "content": "우유, 달걀"}
```

- Code: `201`
- Response body: `{"id":1,"title":"장보기","content":"우유, 달걀"}`

**(3) 하나 더.** 이번에는 내용 없이 보낸다.

```json
{"title": "운동"}
```

- Response body: `{"id":2,"title":"운동","content":""}` — `content` 가 빈 문자열로 채워졌다.

**(4) 다시 목록 보기.** `GET /memos` → Execute. 두 메모가 대괄호 안에 들어 있다.

### 3단계. `curl` 로 시험하기 (20분)

`/docs` 는 편하지만 마우스로 눌러야 한다. 같은 일을 명령 한 줄로 하는 도구가 `curl` 이다. AI 에이전트도 서버를 확인할 때 `curl` 을 쓴다.

dev 컨테이너에서 실행한다. 주소가 `localhost` 가 아니라 **`app`** 이라는 점에 주의한다. 컨테이너끼리는 서비스 이름으로 서로를 부른다.

**[dev]**

```bash
curl -s http://app:8000/memos
```

```text
[{"id":1,"title":"장보기","content":"우유, 달걀"},{"id":2,"title":"운동","content":""}]
```

`curl` 은 응답 끝에 줄바꿈을 붙이지 않는다. 결과 바로 뒤에 프롬프트가 붙어 나와도 정상이다.

**POST 로 만들기.** 옵션이 세 가지 붙는다.

**[dev]**

```bash
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": "책 읽기", "content": "30쪽"}'
```

```text
{"id":3,"title":"책 읽기","content":"30쪽"}
```

| 옵션 | 뜻 |
|---|---|
| `-s` | 진행 표시를 숨긴다 |
| `-X POST` | 방식을 POST 로 한다 (안 쓰면 GET) |
| `-H "Content-Type: application/json"` | "본문은 JSON 입니다"라고 알린다 |
| `-d '…'` | 본문. 바깥은 작은따옴표, 안의 JSON 은 큰따옴표 |

**상태 코드만 보기.**

**[dev]**

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://app:8000/memos
```

```text
200
```

**규칙에 맞지 않는 요청 보내기.** 제목 없이 내용만 보낸다.

**[dev]**

```bash
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"content": "제목이 없어요"}'
```

```text
{"detail":[{"type":"missing","loc":["body","title"],"msg":"Field required","input":{"content":"제목이 없어요"}}]}
```

읽는 법: `"type":"missing"` — 빠졌다. `"loc":["body","title"]` — 본문의 title 이. `"msg":"Field required"` — 꼭 있어야 하는 칸이다.

상태 코드도 확인한다.

**[dev]**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"content": "제목이 없어요"}'
```

```text
422
```

우리는 "제목이 없으면 422 를 돌려줘라"는 코드를 쓴 적이 없다. `MemoIn` 에 `title: str` 이라고 **모양만 적어 두었더니** FastAPI 가 검사해 준 것이다.

### 4단계. 요구사항과 비교하기 (15분)

`harness/REQUIREMENTS.md` 의 R1, R2 를 읽고, 지금 만든 API 가 요구사항을 지키는지 한 줄씩 대조한다.

| 요구사항 | 지금 코드 | 맞는가 |
|---|---|---|
| R1. `POST /memos` → 201 | 201 이 온다 | |
| R1. 응답에 id, title, content, **created_at, updated_at** | ? | |
| R1. content 를 빼면 `""` | ? | |
| R2. `GET /memos` → 200, 배열 | ? | |
| R2. **나중에 만든 메모가 앞에** | ? | |
| R2. 없으면 `[]` | ? | |
| R6. title 이 없으면 422 | 422 가 온다 | |
| R6. title 이 **빈 문자열**(`""`)이면 422 | ? | |

마지막 줄은 직접 보내서 확인한다.

**[dev]**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": ""}'
```

결과를 표에 적는다. **요구사항을 지키지 못한 항목이 몇 개인가?**

이것이 "돌아가는 것 같다"와 "요구사항을 만족한다"의 차이다. 화면에서 눌러 보면 잘 되는 것처럼 보이지만, 명세와 한 줄씩 대조하면 빠진 것이 드러난다. 6교시에 이 빈칸들을 AI 에이전트에게 채우게 한다.

### 5단계. 서버를 다시 켜면? (10분)

지금 메모가 몇 개인지 본다.

**[dev]**

```bash
curl -s http://app:8000/memos
```

서버를 다시 켠다.

**[PS]**

```powershell
docker compose restart app
```

몇 초 뒤 다시 본다.

**[dev]**

```bash
curl -s http://app:8000/memos
```

```text
[]
```

**메모가 모두 사라졌다.** `memos` 는 파이썬 리스트이고, 리스트는 프로그램의 메모리에 있다. 프로그램이 꺼지면 함께 없어진다.

파일을 고쳐서 서버가 저절로 다시 켜질 때도 마찬가지로 사라진다. 요구사항 N1("서버를 다시 켜도 메모가 남아 있다")을 지킬 수 없다. 그래서 7~8교시에 데이터베이스가 필요해진다.

### 6단계. 저장하기 (5분)

**[dev]**

```bash
sh scripts/verify.sh
git status
git diff
git add app/main.py
git commit -m "4교시: 메모 만들기·목록 보기(메모리 저장) 추가"
```

`git diff` 로 바뀐 내용을 읽은 뒤에 커밋한다. 이 순서를 습관으로 만든다.

---

## 하네스 관점 — 이번 교시에서 본 것

- 요구사항은 **HTTP 의 말**로 쓴다. "`POST /memos` → 201". 이 말을 알아야 요구사항을 쓸 수 있고, AI 의 결과를 판단할 수 있다.
- 4단계에서 한 "명세와 한 줄씩 대조하기"는 사람이 하면 느리고 빠뜨리기 쉽다. 이 대조를 코드로 적어 두면 **테스트**가 된다. 6교시에 AI 가 요구사항 번호마다 테스트를 만들게 한다.
- `curl` 과 상태 코드는 AI 에이전트가 자기 작업을 확인할 때 쓰는 도구이기도 하다. 사람이 읽을 수 있어야 AI 의 확인이 제대로 된 것인지 알 수 있다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `curl: (6) Could not resolve host: app` | 윈도우 PowerShell 에서 쳤다. `app` 이라는 이름은 컨테이너 안에서만 통한다. dev 컨테이너에서 친다. |
| `curl: (7) Failed to connect to app port 8000` | 서버가 꺼져 있다. 코드에 오류가 있을 가능성이 높다. **[PS]** `docker compose logs app --tail 20` 을 읽는다. |
| `{"detail":"Method Not Allowed"}` (405) | 주소는 있는데 그 방식에 연결된 함수가 없다. `-X POST` 를 빠뜨렸거나 `@app.post` 를 `@app.get` 으로 썼다. |
| `{"detail":[{"type":"json_invalid", …` | 본문이 올바른 JSON 이 아니다. 작은따옴표를 썼거나, 쉼표·중괄호가 빠졌다. |
| `NameError: name 'BaseModel' is not defined` | 맨 위의 `from pydantic import BaseModel` 을 빠뜨렸다. |
| PowerShell 에서 `curl … -d '{"title": …}'` 이 422 | PowerShell 은 따옴표를 다르게 처리한다. 본문이 있는 `curl` 은 dev 컨테이너에서 친다. |
| 방금 만든 메모가 없어졌다 | 파일을 저장해서 서버가 다시 켜졌다. 5단계에서 본 현상이다. 정상이다. |

## 확인 문제

1. CRUD 네 가지를 HTTP 방식·주소와 짝지어 표로 쓰시오.
2. `GET /memos` 와 `POST /memos` 는 주소가 같다. 서버는 둘을 어떻게 구분하는가?
3. 상태 코드 201 과 204 는 둘 다 성공이다. 무엇이 다른가?
4. 없는 번호의 메모를 조회하면 어떤 상태 코드가 와야 하는가? 왜 200 과 빈 내용을 돌려주면 안 되는가?
5. `{'title': '장보기'}` 는 올바른 JSON 인가? 아니라면 어디가 틀렸는가?
6. `title: str` 과 `content: str = ""` 의 차이를 "반드시"라는 낱말을 써서 설명하시오.
7. 지금 코드에서 메모 번호를 `len(memos) + 1` 로 정한다. 9교시에 "지우기"가 생기면 이 방식에 어떤 문제가 생기는가?
8. 서버를 다시 켰을 때 메모가 사라진 이유를 설명하시오.

## 다음 교시

[5교시. 하네스 규칙 작성](05_하네스_규칙_작성.md) — AI 에이전트에게 일을 맡기기 전에, 규칙·권한·검증을 세운다.
