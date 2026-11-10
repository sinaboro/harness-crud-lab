# 3교시. Python·FastAPI 기본 이해

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | `/hello` API |
| 시작 상태 | 2교시를 마친 상태 (컨테이너 3개가 켜져 있고, `ask_ai.py` 가 동작한다) |

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
                                                      └─ 이번 교시: 실행하고, 테스트하고, 저장하는 일을 손으로 한 번 해 본다
```

AI 에게 맡기기 전에, 맡길 일이 무엇인지 **한 번은 손으로** 해 본다. 한 번 해 본 일이라야 AI 가 한 결과를 읽을 수 있다.

## 학습 목표

1. 파이썬의 값·변수·딕셔너리·함수를 읽을 수 있다.
2. FastAPI 코드에서 "주소 → 함수 → 응답"의 연결을 찾을 수 있다.
3. `/hello` 주소를 직접 추가하고 브라우저와 `/docs` 에서 확인한다.
4. AI 에게 코드 설명을 요청하고, 그 설명이 맞는지 실행해서 확인한다.
5. 테스트를 실행하고, 통과한 코드를 Git 에 저장(commit)한다.

---

## 1. 파이썬 15분 맛보기

dev 컨테이너에 들어가 파이썬을 대화식으로 실행한다.

**[PS]**

```powershell
cd C:\harness-crud-lab
docker compose exec dev bash
```

**[dev]**

```bash
python
```

`>>>` 가 나오면 파이썬이 명령을 기다리는 중이다. 한 줄씩 치고 Enter 를 누른다. `>>>` 뒤만 친다.

### 값과 변수

```python
>>> title = "장보기"
>>> count = 3
>>> title
'장보기'
>>> count + 1
4
```

- 따옴표로 감싼 것은 **글자(문자열, str)**, 감싸지 않은 숫자는 **정수(int)** 다.
- `=` 는 "같다"가 아니라 "오른쪽 값을 왼쪽 이름에 담는다"는 뜻이다.

### f-문자열 — 글자 안에 값 끼워 넣기

```python
>>> name = "철수"
>>> f"안녕하세요, {name}!"
'안녕하세요, 철수!'
```

따옴표 앞에 `f` 를 붙이면 `{ }` 안의 변수가 값으로 바뀐다.

### 딕셔너리 — 이름표가 붙은 값 묶음

```python
>>> memo = {"id": 1, "title": "장보기", "content": "우유, 달걀"}
>>> memo["title"]
'장보기'
>>> memo["content"] = "우유"
>>> memo
{'id': 1, 'title': '장보기', 'content': '우유'}
```

`{"이름": 값}` 모양이다. 메모 한 건을 이렇게 표현한다. 이 모양을 기억해 둔다. 서버가 주고받는 **JSON** 이 거의 똑같이 생겼다.

### 리스트 — 순서가 있는 값 묶음

```python
>>> memos = []
>>> memos.append(memo)
>>> len(memos)
1
```

`[ ]` 는 리스트다. 메모 여러 건은 "딕셔너리가 든 리스트"로 표현한다.

### 함수 — 이름을 붙인 일 묶음

```python
>>> def hello(name="하네스"):
...     return f"안녕하세요, {name}!"
...
>>> hello()
'안녕하세요, 하네스!'
>>> hello("철수")
'안녕하세요, 철수!'
```

- `def 이름(인자):` 로 만든다. 둘째 줄부터는 **띄어쓰기 4칸**으로 들여 쓴다. 파이썬에서 들여쓰기는 "여기까지가 함수 안"이라는 표시다.
- `...` 에서 Enter 를 한 번 더 치면 함수 만들기가 끝난다.
- `name="하네스"` 는 "값을 안 주면 하네스를 쓴다"는 뜻이다(기본값).
- `return` 은 함수가 돌려주는 값이다.

파이썬에서 나온다.

```python
>>> exit()
```

여기까지가 이 교시에 필요한 파이썬의 전부다. 나머지는 코드를 읽다가 나올 때마다 AI 에게 묻는다.

## 2. FastAPI 코드 읽기

VS Code 에서 `app/main.py` 를 연다. 주석을 빼면 일곱 줄이다.

```python
from fastapi import FastAPI

app = FastAPI(title="메모 CRUD")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

| 줄 | 뜻 |
|---|---|
| `from fastapi import FastAPI` | fastapi 라는 패키지에서 FastAPI 라는 도구를 가져온다. |
| `app = FastAPI(...)` | 서버(앱)를 하나 만들어 `app` 이라는 이름에 담는다. |
| `@app.get("/health")` | **바로 아래 함수**를 `/health` 주소에 연결한다. "누가 `/health` 를 GET 방식으로 부르면 이 함수를 실행해라." |
| `def health() -> dict:` | 함수 이름은 `health`, 돌려주는 것은 딕셔너리(`dict`)라는 표시다. |
| `return {"status": "ok"}` | 이 딕셔너리가 JSON 으로 바뀌어 브라우저로 간다. |

`@` 로 시작하는 줄을 **데코레이터**라고 한다. 지금은 "아래 함수에 붙이는 이름표"라고만 알면 된다.

```text
 브라우저: http://localhost:8000/health
        │  GET /health
        ▼
 app 컨테이너의 FastAPI  ──▶  @app.get("/health") 가 붙은 함수 health() 실행
        │
        ▼  {"status": "ok"}  (딕셔너리 → JSON)
 브라우저 화면에 표시
```

---

## 따라 하기

### 1단계. `/hello` 추가하기 (15분)

VS Code 에서 `app/main.py` 의 **맨 아래**에 다음을 추가하고 저장(Ctrl+S)한다. 위의 `health` 함수와 두 줄 띄운다.

```python
@app.get("/hello")
def hello(name: str = "하네스") -> dict:
    """/hello?name=철수 처럼 부르면 이름을 넣어 인사한다."""
    # name: str = "하네스" → 글자(str)를 받고, 안 주면 "하네스"를 쓴다는 뜻
    return {"message": f"안녕하세요, {name}!"}
```

1절에서 만든 `hello` 함수와 거의 같다. 달라진 것은 두 가지다.

- 위에 `@app.get("/hello")` 가 붙었다. → 주소에 연결되었다.
- 글자가 아니라 딕셔너리를 돌려준다. → JSON 으로 나간다.

서버를 다시 켤 필요는 없다. `app` 컨테이너는 `app` 폴더의 파일이 바뀌면 저절로 다시 켜진다. 정말 그런지 로그로 본다.

**[PS]** (PowerShell 창을 하나 더 연다)

```powershell
cd C:\harness-crud-lab
docker compose logs app --tail 5
```

`Reloading...` 과 `Application startup complete.` 가 보이면 다시 켜진 것이다.

> 내가 윈도우에서 파일을 고쳤는데 컨테이너 안의 서버가 알아챘다. 2교시의 바인드 마운트(`C:\harness-crud-lab` ↔ `/workspace`) 덕분이다.

### 2단계. 브라우저로 확인하기 (10분)

브라우저에서 차례로 연다.

| 주소 | 화면에 보이는 것 |
|---|---|
| http://localhost:8000/hello | `{"message":"안녕하세요, 하네스!"}` |
| http://localhost:8000/hello?name=철수 | `{"message":"안녕하세요, 철수!"}` |
| http://localhost:8000/nothing | `{"detail":"Not Found"}` |

- 주소 뒤의 `?name=철수` 를 **쿼리 파라미터**라고 한다. 이 값이 함수의 인자 `name` 으로 들어간다.
- 세 번째처럼 연결된 함수가 없는 주소를 부르면 FastAPI 가 "그런 주소 없음"이라고 답한다.

### 3단계. `/docs` — 자동으로 만들어지는 설명서 (10분)

브라우저에서 http://localhost:8000/docs 를 연다.

1. `GET /health` 와 `GET /hello` 두 줄이 보인다. 우리가 문서를 쓴 적이 없는데 FastAPI 가 코드를 읽고 만든 것이다.
2. `GET /hello` 를 눌러 펼친다. 함수 아래에 적은 설명(`"""…"""`)이 그대로 보인다.
3. **Try it out** 을 누르고, `name` 칸에 자기 이름을 넣고, **Execute** 를 누른다.
4. 아래 **Response body** 에 결과가, **Code** 에 `200` 이 나온다.

`200` 은 "성공"을 뜻하는 상태 코드다. 4교시에 자세히 배운다. 앞으로 API 를 만들면 항상 이 화면에서 먼저 눌러 본다.

### 4단계. AI 에게 설명시키고, 맞는지 확인하기 (20분)

AI 를 "코드를 쓰는 사람"이 아니라 "설명해 주는 선생님"으로 써 본다.

**[dev]**

```bash
python scripts/ask_ai.py --file app/main.py "이 파일을 처음 보는 초보자에게 한 줄씩 설명해 줘. 데코레이터가 무엇인지도 비유로 알려 줘."
```

답을 읽는다. 그리고 **그대로 믿지 않는다.** AI 는 그럴듯하게 틀릴 수 있다. 설명이 맞는지 실행으로 확인하는 습관을 지금 들인다.

**확인 실험 1.** AI 에게 묻는다.

**[dev]**

```bash
python scripts/ask_ai.py --file app/main.py "hello 함수에서 name 의 기본값 '하네스' 를 지우고 name: str 만 남기면, /hello 를 name 없이 불렀을 때 어떻게 돼? 상태 코드까지 예측해 줘."
```

AI 의 예측을 적어 둔다. 그다음 **직접 해 본다.** `app/main.py` 에서 `name: str = "하네스"` 를 `name: str` 로 고쳐 저장하고, 브라우저에서 http://localhost:8000/hello 를 연다.

- AI 의 예측과 실제 결과가 같은가?
- `/docs` 에서 `name` 칸 옆에 무엇이 새로 붙었는가?

확인했으면 `name: str = "하네스"` 로 **되돌려 놓고** 저장한다.

**확인 실험 2.** 에이전트에게 설명시킨다. 스크립트와 달리 파일 이름만 알려 주면 스스로 읽는다.

**[dev]**

```bash
opencode run "app/main.py 를 읽고, 브라우저가 /hello?name=철수 를 불렀을 때 응답이 나가기까지 일어나는 일을 순서대로 설명해 줘. 파일은 고치지 마."
```

> "파일은 고치지 마"를 꼭 붙인다. 지금은 규칙도 권한도 없어서, 말로 부탁하는 것 말고는 막을 방법이 없다. 이 불편함을 기억해 둔다. 5교시에 해결한다.

### 5단계. 테스트 실행하기 (15분)

지금까지는 브라우저를 눈으로 보고 "된다"고 판단했다. 이 확인을 **코드로 적어 둔 것**이 테스트다.

`tests/test_health.py` 를 VS Code 로 연다.

```python
def test_health(client):
    response = client.get("/health")  # GET /health 를 부른다
    assert response.status_code == 200  # 성공(200)이어야 한다
    assert response.json() == {"status": "ok"}  # 답의 내용도 정확히 같아야 한다
```

- `client` 는 가짜 브라우저다. `tests/conftest.py` 에서 만든다.
- `assert 식` 은 "이 식이 참이어야 한다"는 뜻이다. 거짓이면 테스트가 실패한다.

실행한다.

**[dev]**

```bash
pytest -q
```

```text
.                                                                        [100%]
1 passed in 0.02s
```

점(`.`) 하나가 통과한 테스트 하나다.

이제 `/hello` 의 테스트를 추가한다. `tests/test_health.py` 의 **맨 아래**에 붙여 넣고 저장한다.

```python


def test_hello_default(client):
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요, 하네스!"}


def test_hello_with_name(client):
    # params 는 주소 뒤에 ?name=철수 를 붙여 준다.
    response = client.get("/hello", params={"name": "철수"})
    assert response.json() == {"message": "안녕하세요, 철수!"}
```

**[dev]**

```bash
pytest -q
```

```text
...                                                                      [100%]
3 passed in 0.03s
```

**일부러 실패시켜 본다.** `app/main.py` 에서 `안녕하세요` 를 `반갑습니다` 로 바꿔 저장하고 `pytest -q` 를 다시 실행한다.

출력에서 아래 세 가지를 찾는다.

- `FAILED tests/test_health.py::test_hello_default` — 어떤 테스트가 실패했는가
- `assert` 줄 아래의 비교 — 무엇을 기대했고 실제로 무엇이 왔는가
- 마지막 줄 `2 failed, 1 passed` — 몇 개가 실패했는가

코드를 바꿨더니 테스트가 알려 줬다. **테스트는 "누군가(나 또는 AI)가 약속을 깨뜨렸을 때 울리는 경보기"다.**

`반갑습니다` 를 `안녕하세요` 로 **되돌리고** `pytest -q` 로 `3 passed` 를 확인한다.

코드 검사도 실행해 본다. 검사와 테스트를 한꺼번에 돌리는 스크립트가 `scripts/verify.sh` 다.

**[dev]**

```bash
sh scripts/verify.sh
```

```text
[1/2] 코드 검사 (ruff) ----------------------------
All checks passed!
[2/2] 자동 테스트 (pytest) ------------------------
...                                                                      [100%]
3 passed in 0.03s
----------------------------------------------------
검증 통과: 이제 저장(commit)해도 됩니다.
```

### 6단계. Git 에 저장하기 (15분)

**커밋(commit)** 은 "지금 이 상태"를 기록으로 남기는 일이다. 게임의 저장 지점과 같다. 나중에 망가져도 이 지점으로 돌아올 수 있다.

**(1) 무엇이 바뀌었는지 본다.**

**[dev]**

```bash
git status
```

`modified:` 뒤에 `app/main.py` 와 `tests/test_health.py` 두 파일이 나온다.

**[dev]**

```bash
git diff
```

`+` 로 시작하는 초록색 줄이 추가된 줄, `-` 로 시작하는 빨간색 줄이 지워진 줄이다. 화면이 길면 방향키로 움직이고 `q` 로 나온다.

**이 화면을 읽는 것이 이 과정에서 가장 중요한 기술이다.** 6교시부터는 AI 가 바꾼 내용을 이 화면으로 읽고 검토한다.

**(2) 저장할 파일을 고른다.**

**[dev]**

```bash
git add app/main.py tests/test_health.py
git status
```

두 파일이 `Changes to be committed:` 아래로 옮겨졌다. "이번 커밋에 넣겠다"고 표시한 것이다.

**(3) 저장한다.**

**[dev]**

```bash
git commit -m "3교시: /hello 주소와 테스트 추가"
```

`-m` 뒤의 글이 커밋 메시지다. **무엇을 했는지** 한 줄로 적는다.

**(4) 기록을 본다.**

**[dev]**

```bash
git log --oneline -3
```

맨 위에 방금 만든 커밋이 있다. 앞의 일곱 글자는 커밋의 고유 번호다.

**확인.** `git status` 가 `nothing to commit, working tree clean` 을 출력한다.

---

## 하네스 관점 — 이번 교시에서 본 것

이번 교시에는 수업의 흐름 ④·⑤를 **사람이 손으로** 했다.

| 한 일 | 손으로 한 방법 | 5교시부터는 |
|---|---|---|
| 실행·확인 | 브라우저와 `/docs` 를 눈으로 봤다 | 테스트가 대신 확인한다 |
| 검증 | `sh scripts/verify.sh` 를 내가 기억해서 실행했다 | 커밋할 때 자동으로 실행된다 |
| AI 통제 | "파일은 고치지 마"라고 매번 말로 부탁했다 | 규칙과 권한이 대신한다 |
| 저장 | 검증을 건너뛰고도 커밋할 수 있었다 | 검증에 실패하면 커밋이 취소된다 |

오른쪽 칸이 하네스다. 사람이 기억하고 지켜야 하던 일을 장치가 대신하게 만드는 것이다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| 브라우저에 `{"detail":"Not Found"}` | 주소를 잘못 쳤거나, 파일을 저장하지 않았다. VS Code 탭에 흰 점이 있으면 저장되지 않은 것이다. |
| 브라우저가 "사이트에 연결할 수 없음" | 코드에 문법 오류가 있어 서버가 켜지지 못했다. **[PS]** `docker compose logs app --tail 20` 에서 `SyntaxError` 나 `IndentationError` 와 줄 번호를 찾는다. |
| `IndentationError` | 들여쓰기가 맞지 않는다. 함수 안의 줄은 띄어쓰기 4칸이다. 탭과 띄어쓰기를 섞지 않는다. |
| `/docs` 에 `/hello` 가 안 보인다 | `@app.get("/hello")` 줄이 빠졌거나 함수 위에 빈 줄 없이 붙어 있지 않다. 데코레이터는 함수 바로 윗줄에 있어야 한다. |
| `pytest` 가 `command not found` | 윈도우 PowerShell 에서 쳤다. pytest 는 컨테이너 안에만 있다. `docker compose exec dev bash` 로 들어가서 친다. |
| `git commit` 이 `Please tell me who you are` | 2교시 10단계(이름·메일 설정)를 하지 않았다. |
| 한글이 `\uc548\ub155` 처럼 보인다 | 오래된 브라우저 확장이나 다른 도구로 볼 때 그렇다. `/docs` 의 Response body 로 확인한다. |

## 확인 문제

1. `memo = {"id": 1, "title": "장보기"}` 에서 제목을 꺼내는 코드를 쓰시오.
2. `@app.get("/hello")` 한 줄을 지우면 `hello` 함수는 어떻게 되는가? 브라우저에서 `/hello` 를 부르면 무엇이 나오는가?
3. `/hello?name=영희` 에서 `영희` 는 어떤 길을 거쳐 응답의 글자가 되는가? 순서대로 쓰시오.
4. 파일을 고쳤는데 서버를 다시 켜지 않아도 반영된 이유 두 가지를 쓰시오. (힌트: 2교시의 낱말 하나, `docker-compose.yml` 의 옵션 하나)
5. `assert response.status_code == 200` 은 무엇을 확인하는가? 이 줄이 실패하면 화면에 무엇이 나오는가?
6. AI 가 코드를 설명해 줬을 때 그 설명이 맞는지 확인하는 방법을 두 가지 쓰시오.
7. `git add` 와 `git commit` 은 각각 무슨 일을 하는가?

## 다음 교시

[4교시. CRUD 와 HTTP 기초](04_CRUD와_HTTP.md) — GET 과 POST 로 메모를 만들고 보는 API 를 손으로 만든다.
