# 8교시. FastAPI 와 DB 연결

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | 메모 저장·조회 (서버를 다시 켜도 메모가 남는다) |
| 시작 상태 | 6교시의 메모 초안이 커밋되어 있고, 7교시의 SQL 을 읽을 수 있다 |

6교시 결과가 없으면 **[dev]** `sh scripts/checkpoint.sh 06` 으로 가져온다.

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
 └────────────── 이번 교시: 두 번째 바퀴. 이번에는 "속만 바꾸는" 작업이다 ──────────────┘
```

## 학습 목표

1. "겉은 그대로, 속만 바꾼다"(저장소 교체)가 무슨 뜻인지 설명한다.
2. **테스트를 한 글자도 바꾸지 않는다**는 조건으로 AI 에게 일을 시키고, 지켜졌는지 확인한다.
3. 파이썬에서 PostgreSQL 에 접속해 SQL 을 실행하는 코드를 읽는다.
4. 자리표시자(`%s`)가 왜 필요한지 설명한다.
5. 테스트 전용 DB 가 왜 필요한지 설명하고, 진짜 데이터가 지워지지 않는 것을 확인한다.

---

## 1. 개념

### 겉과 속

6교시에 만든 API 는 메모를 딕셔너리에 넣는다. 이번 교시에는 PostgreSQL 에 넣게 바꾼다.

```text
 바꾸지 않는 것 (겉)                    바꾸는 것 (속)
 ──────────────────────                ──────────────────────
 주소        POST /memos                저장하는 곳   딕셔너리 → PostgreSQL
 요청 모양   {"title": …}               저장하는 코드  memos[id] = … → INSERT INTO …
 응답 모양   {"id": …, "title": …}
 상태 코드   201, 200, 404, 422
```

API 를 쓰는 쪽(브라우저, `curl`, 테스트)에서 보면 **아무것도 달라지지 않는다.** 달라지는 것은 하나, 서버를 다시 켜도 메모가 남는다는 점이다.

### 테스트는 계약서다

6교시에 만든 테스트는 "이렇게 부르면 이런 답이 온다"만 확인한다. 메모가 딕셔너리에 있는지 DB 에 있는지는 묻지 않는다. 그래서 **속을 바꿔도 테스트는 그대로 통과해야 한다.**

이번 교시의 가장 중요한 조건:

> **`tests/test_memos.py` 는 한 글자도 바꾸지 않는다.**

AI 가 속을 바꾸다가 겉을 건드리면(응답 모양이 달라지거나 404 문구가 바뀌면) 테스트가 실패해서 알려 준다. 반대로 AI 가 테스트를 고쳐 버리면 이 경보기가 꺼진다. 그래서 테스트 파일을 범위 밖으로 묶어 둔다.

### 테스트 전용 DB

테스트는 시작할 때마다 테이블을 비운다. 진짜 메모가 든 DB 에서 테스트를 돌리면 **테스트할 때마다 내 메모가 지워진다.** (1교시의 사례 4 가 이것이다.)

| 데이터베이스 | 누가 쓰는가 | 환경 변수 |
|---|---|---|
| `memo_db` | 서버(app 컨테이너). 진짜 메모 | `DATABASE_URL` |
| `memo_test` | 테스트(dev 컨테이너의 pytest). 매번 비워진다 | `TEST_DATABASE_URL` |

두 주소는 `docker-compose.yml` 이 컨테이너에 넣어 준다.

**[dev]**

```bash
echo $DATABASE_URL
echo $TEST_DATABASE_URL
```

```text
postgresql://memo:memo1234@db:5432/memo_db
postgresql://memo:memo1234@db:5432/memo_test
```

주소 읽는 법: `postgresql://계정:비밀번호@호스트:포트/데이터베이스`. 호스트가 `localhost` 가 아니라 `db` 다. 컨테이너끼리는 서비스 이름으로 부른다. (4교시의 `http://app:8000` 과 같은 원리다.)

---

## 따라 하기

### 1단계. ①② 요구사항과 지시서 읽기 (15분)

`harness/REQUIREMENTS.md` 4절에서 **N1, N2, N4** 를 읽는다.

`harness/tasks/08_db_connect.md` 를 읽는다. 6교시 지시서와 달라진 점을 찾는다.

| 칸 | 6교시 지시서 | 8교시 지시서 |
|---|---|---|
| 목표 | 새 기능을 만든다 | **겉은 그대로 두고** 저장소만 바꾼다 |
| 범위 — 고치면 안 되는 것 | `tests/test_health.py` | **`tests/test_memos.py`** 도 추가 |
| 하지 말 것 | 수정·삭제, DB, 화면 | ORM 금지, 주소·비밀번호를 코드에 적지 않기 |
| (새로 생긴 칸) | — | **5. 구현 조건** — 테이블 구조, 테스트 전용 DB |
| 완료 조건 | 테스트가 있다 | **테스트 개수가 작업 전과 같다** |

"ORM 을 쓰지 않는다"에 주목한다. ORM(SQLAlchemy 등)은 SQL 을 파이썬 코드 뒤에 감춰 주는 도구다. 실무에서는 많이 쓰지만, 이 과정에서는 **7교시에 배운 SQL 이 코드에 그대로 보여야** 내가 읽고 검토할 수 있다. 사람이 검토할 수 있는 방법을 고르게 하는 것도 하네스다.

### 2단계. 작업 전 상태 기록하기 (5분)

"겉이 그대로인가"를 판단하려면 작업 전의 상태를 알아야 한다.

**[dev]**

```bash
git status
sh scripts/verify.sh
```

`working tree clean` 과 "검증 통과"를 확인한다. **통과한 테스트 개수를 적어 둔다.** (완성 예시 기준 12개. 내 것은 다를 수 있다.)

### 3단계. ②③ 지시하고 계획 검토하기 (20분)

**[dev]**

```bash
opencode
```

**[AI]**

```text
harness/tasks/08_db_connect.md 를 읽고 그 지시대로 작업해 줘. AGENTS.md 의 작업 절차를 따라, 먼저 계획만 말하고 내 승인을 기다려.
```

**계획 검토 체크리스트**

- [ ] `tests/test_memos.py` 를 고치겠다는 말이 **없는가?** (있으면 반드시 빼게 한다)
- [ ] 새로 만드는 파일이 `app/db.py` 하나인가?
- [ ] 접속 주소를 **환경 변수**에서 읽겠다고 했는가? 코드에 `memo1234` 를 적겠다는 말이 없는가?
- [ ] SQL 에 `%s` 자리표시자를 쓰겠다고 했는가?
- [ ] 테스트가 `memo_test` 에서 돌게 하겠다고 했는가? `memo_db` 를 비우겠다는 말이 없는가?
- [ ] SQLAlchemy 같은 새 패키지를 쓰겠다는 말이 **없는가?**
- [ ] 수정·삭제를 만들겠다는 말이 **없는가?**

문제가 있으면 지시서의 해당 줄을 가리켜 고치게 하고, 맞으면 승인한다.

**[AI]**

```text
진행
```

AI 가 일하는 동안 6교시처럼 기록한다. 이번에는 특히 **AI 가 DB 에 직접 명령을 내리려 하는지** 본다. `psql` 이나 `DROP`, `TRUNCATE` 가 든 명령을 실행해도 되냐고 물으면, 어느 데이터베이스에 대한 것인지 확인하고 `memo_db` 라면 거절한다.

### 4단계. ④ 검증 (20분)

OpenCode 는 열어 두고, 다른 dev 셸에서 직접 확인한다. (**[PS]** `docker compose exec dev bash`)

**(1) 기계가 확인하는 것**

**[dev]**

```bash
sh scripts/verify.sh
```

완성 예시의 결과:

```text
............                                                             [100%]
12 passed in 1.04s
```

- [ ] "검증 통과"로 끝난다.
- [ ] **테스트 개수가 2단계에서 적어 둔 숫자와 같다.**

실행 시간이 6교시(0.08초)보다 길어졌다. 테스트가 이제 진짜 DB 에 접속하기 때문이다.

**(2) 테스트가 바뀌지 않았는가 — 이번 교시의 핵심 확인**

**[dev]**

```bash
git diff --stat
```

- [ ] 목록에 `tests/test_memos.py` 가 **없다.**
- [ ] 바뀐 파일은 `app/main.py`, `tests/conftest.py` 이고, `git status` 에 새 파일 `app/db.py` 가 보인다.

`tests/test_memos.py` 가 목록에 있다면 AI 가 조건을 어긴 것이다. 무엇을 바꿨는지 `git diff tests/test_memos.py` 로 보고, 되돌리게 한다.

**[AI]**

```text
git diff --stat 에 tests/test_memos.py 가 나와. 지시서 3번에서 이 파일은 고치면 안 된다고 했어. 왜 고쳤는지 설명하고, 원래대로 되돌린 뒤 app/ 쪽을 고쳐서 통과시켜 줘.
```

**(3) 비밀 값이 코드에 들어가지 않았는가**

**[dev]**

```bash
grep -rn "memo1234" app/ tests/
```

아무것도 출력되지 않아야 한다. 출력되면 비밀번호가 코드에 적힌 것이다. 환경 변수에서 읽도록 고치게 한다.

**(4) 직접 불러 보기**

**[dev]**

```bash
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": "장보기", "content": "우유, 달걀"}'
curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": "운동", "content": "저녁 7시 달리기"}'
curl -s http://app:8000/memos
```

마지막 명령의 결과(시각은 실행한 때에 따라 다르다):

```text
[{"id":2,"title":"운동","content":"저녁 7시 달리기","created_at":"2026-11-10T05:47:07.086373Z","updated_at":"2026-11-10T05:47:07.086373Z"},{"id":1,"title":"장보기","content":"우유, 달걀","created_at":"2026-11-10T05:47:07.051297Z","updated_at":"2026-11-10T05:47:07.051297Z"}]
```

응답의 모양이 6교시와 똑같다. **겉은 그대로다.**

**(5) 서버를 다시 켜도 남는가 — N1**

**[PS]**

```powershell
docker compose restart app
```

**[dev]**

```bash
curl -s http://app:8000/memos
```

두 메모가 그대로 나온다. 4교시 5단계에서는 `[]` 였다.

**(6) DB 에 정말 들어 있는가**

`curl` 은 서버를 거친 결과다. 서버를 거치지 않고 DB 를 직접 들여다본다. 7교시에 배운 그대로다.

**[PS]**

```powershell
docker compose exec db psql -U memo -d memo_db -c "SELECT id, title, content FROM memos ORDER BY id;"
```

```text
 id | title  |     content     
----+--------+-----------------
  1 | 장보기 | 우유, 달걀
  2 | 운동   | 저녁 7시 달리기
(2 rows)
```

**(7) 테스트가 진짜 메모를 지우지 않는가**

**[dev]**

```bash
pytest -q
```

**[PS]**

```powershell
docker compose exec db psql -U memo -d memo_db -c "SELECT count(*) FROM memos;"
docker compose exec db psql -U memo -c "\l"
```

- 첫째 명령: `count` 가 여전히 `2` 다. 테스트를 돌렸는데 진짜 메모는 그대로다.
- 둘째 명령: 목록에 `memo_test` 가 생겼다. 테스트가 만든 것이다.

`count` 가 `0` 이 되었다면 테스트가 `memo_db` 에서 돌고 있는 것이다. **심각한 문제다.** AI 에게 지시서 5번의 테스트 전용 DB 조건을 가리켜 고치게 한다.

### 5단계. ⑤ 코드 읽기 (30분)

완성 예시(`checkpoints/lesson08`)를 기준으로 읽는다. 내 코드에서 같은 역할을 하는 부분을 찾는다.

**(1) `app/db.py` — DB 와 대화하는 부분**

```python
def get_database_url() -> str:
    """환경 변수에서 접속 주소를 읽는다. (docker-compose.yml 이 넣어 준다)"""
    return os.environ["DATABASE_URL"]


def get_conn() -> psycopg.Connection:
    """DB 연결을 하나 연다. 결과 행은 {"열이름": 값} 딕셔너리로 받는다."""
    return psycopg.connect(get_database_url(), row_factory=dict_row)
```

- `os.environ["DATABASE_URL"]` — 주소가 코드에 없다. 2교시의 API 키와 같은 방식이다(N4).
- `row_factory=dict_row` — 결과 한 행을 `{"id": 1, "title": "장보기", …}` 딕셔너리로 받는다. 3교시에 배운 그 딕셔너리다.

```python
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memos (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    …
);
"""

def init_db() -> None:
    with get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)
```

7교시에 손으로 친 `CREATE TABLE` 이 그대로 들어 있다. `IF NOT EXISTS` 가 붙어서, 테이블이 이미 있으면 아무 일도 하지 않는다. 서버가 켜질 때마다 실행해도 안전하다.

**(2) `app/main.py` — 만들기**

```python
@app.post("/memos", response_model=MemoOut, status_code=201)
def create_memo(memo: MemoIn) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "INSERT INTO memos (title, content) VALUES (%s, %s) RETURNING *",
            (memo.title, memo.content),
        ).fetchone()
    return row
```

6교시의 코드와 나란히 놓는다.

| | 6교시 (메모리) | 8교시 (DB) |
|---|---|---|
| 첫 줄 | `@app.post("/memos", response_model=MemoOut, status_code=201)` | **같다** |
| 번호 정하기 | `next_id` 를 직접 센다 | DB 가 한다 (`SERIAL`) |
| 시각 정하기 | `datetime.now(UTC)` | DB 가 한다 (`DEFAULT now()`) |
| 저장 | `memos[next_id] = new_memo` | `INSERT INTO …` |
| 돌려주기 | `return new_memo` | `RETURNING *` 로 받은 행을 `return` |

- `with get_conn() as conn:` — 연결을 열고, 블록이 끝나면 저장(commit)하고 닫는다. 중간에 오류가 나면 저장하지 않고 되돌린다.
- `.fetchone()` — 결과에서 한 행을 꺼낸다. 없으면 `None`.

**(3) 자리표시자 `%s` — 가장 중요한 줄**

```python
"INSERT INTO memos (title, content) VALUES (%s, %s) RETURNING *",
(memo.title, memo.content),
```

SQL 문장과 값이 **따로** 전달된다. `%s` 자리에 값이 들어가는 일은 드라이버(psycopg)가 안전하게 한다.

하면 안 되는 방식:

```python
# 나쁜 예 — 절대 이렇게 쓰지 않는다
conn.execute(f"INSERT INTO memos (title) VALUES ('{memo.title}')")
```

누군가 제목에 `'); DELETE FROM memos; --` 를 넣으면, 이 글자들이 SQL 문장의 일부가 되어 버린다. 사용자가 보낸 글이 명령으로 실행되는 것이다. 이것이 **SQL 인젝션**이다(7교시 9단계에서 AI 에게 물어본 것).

내 코드를 직접 검사한다.

**[dev]**

```bash
grep -n "execute" app/main.py app/db.py
```

`execute(` 가 나오는 줄을 모두 본다. SQL 문자열 앞에 `f` 가 붙어 있거나, `+` 나 `.format(` 으로 값을 이어 붙인 곳이 있으면 규칙(N2) 위반이다.

**(4) `app/main.py` — 한 건 보기와 404**

```python
row = conn.execute("SELECT * FROM memos WHERE id = %s", (memo_id,)).fetchone()
if row is None:  # 그런 번호가 없으면
    raise not_found()
```

7교시 4단계를 떠올린다. DB 는 없는 번호를 찾아도 오류를 내지 않고 0행을 돌려준다. `fetchone()` 은 그때 `None` 을 준다. 그래서 **코드가 직접** `None` 인지 보고 404 를 만든다.

`(memo_id,)` 의 쉼표에 주목한다. 값이 하나뿐이어도 "묶음"으로 전달해야 해서 쉼표를 붙인다. 쉼표를 빼면 오류가 난다. 초보자가 가장 자주 하는 실수다.

**(5) `app/main.py` — 서버가 켜질 때**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버가 켜질 때 한 번 실행된다: 테이블이 없으면 만든다."""
    init_db()
    yield  # 여기서부터 서버가 요청을 받는다


app = FastAPI(title="메모 CRUD", lifespan=lifespan)
```

`yield` 앞은 서버가 켜질 때, 뒤는 꺼질 때 실행된다. 문법이 낯설면 "서버가 켜질 때 `init_db()` 를 한 번 부른다"만 이해하고 넘어간다.

**(6) `tests/conftest.py` — 테스트 전용 DB**

```python
MAIN_URL = os.environ["DATABASE_URL"]  # 평소에 쓰는 DB (memo_db)
TEST_URL = os.environ["TEST_DATABASE_URL"]  # 테스트 전용 DB (memo_test)

# 앱이 테스트 전용 DB 를 보게 주소를 바꿔 끼운다. (app 을 불러오기 전에 해야 한다)
os.environ["DATABASE_URL"] = TEST_URL
```

테스트를 시작할 때 접속 주소를 `memo_test` 로 바꿔치기한다. 앱 코드는 여전히 `DATABASE_URL` 을 읽을 뿐인데, 그 값이 테스트 DB 를 가리키게 된 것이다. **앱 코드에는 "테스트 중이면…" 같은 분기가 없다.**

```python
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        with get_conn() as conn:
            # 메모를 모두 지우고 번호도 1번부터 다시 시작하게 한다.
            conn.execute("TRUNCATE TABLE memos RESTART IDENTITY")
        yield test_client
```

6교시의 `reset_store()` 가 `TRUNCATE` 로 바뀌었다. 하는 일은 같다. 테스트마다 깨끗하게.
`TRUNCATE` 는 테이블을 통째로 비우는 명령이다. **이 명령이 `memo_test` 에서만 실행된다는 것**을 4단계 (7)에서 확인했다.

**(7) AI 에게 묻기**

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. tests/conftest.py 에서 os.environ["DATABASE_URL"] = TEST_URL 줄을 from app.main import app 아래로 옮기면 어떤 일이 생길 수 있어?
```

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. app/main.py 의 with get_conn() as conn: 블록 안에서 오류가 나면 INSERT 한 내용은 어떻게 돼?
```

### 6단계. ⑤ 기록하고 저장하기 (10분)

`harness/WORKLOG.md` 에 8교시 기록을 쓴다. 이번에는 "3. 하네스가 막거나 물어본 것"에 **AI 가 테스트 파일을 건드렸는지**를 꼭 적는다.

**[dev]**

```bash
git add -A
git status
git commit -m "8교시: 저장소를 PostgreSQL 로 교체 (N1, N2, N4)"
```

OpenCode 를 `/exit` 로 닫는다.

---

## 하네스 관점 — 이번 교시에서 본 것

- **테스트는 계약서다.** 속을 통째로 바꿨는데 테스트 12개가 그대로 통과했다. 겉이 바뀌지 않았다는 증거다. 테스트가 없었다면 응답을 하나하나 눈으로 대조해야 했을 것이다.
- **범위 제한이 경보기를 지킨다.** "테스트 파일을 고치지 않는다"는 조건이 없으면, AI 는 실패하는 테스트를 고쳐서 통과시킬 수 있다. 그 조건을 `git diff --stat` 한 줄로 확인했다.
- **확인은 한 단계 더 깊이.** `curl` 은 서버가 하는 말이다. `psql` 로 DB 를 직접 들여다보고, 서버를 다시 켜 보고, 테스트를 돌린 뒤 진짜 데이터를 세어 봤다. AI 의 보고 → 내 `verify.sh` → `curl` → `psql`. 한 단계씩 더 직접적인 증거로 내려간다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `psycopg.OperationalError: connection failed … Name or service not known` | 접속 주소의 호스트가 틀렸다(`localhost` 로 적었을 수 있다). 컨테이너에서는 `db` 다. `echo $DATABASE_URL` 로 확인한다. |
| `KeyError: 'DATABASE_URL'` 또는 `'TEST_DATABASE_URL'` | 환경 변수가 없다. dev 컨테이너 안에서 실행했는지 확인한다. **[PS]** `docker compose up -d` 뒤 다시 들어간다. |
| `relation "memos" does not exist` | 테이블을 만드는 코드(`init_db`)가 서버 시작 때 실행되지 않는다. `lifespan` 이 `FastAPI(...)` 에 연결되어 있는지 본다. 테스트에서는 `with TestClient(app)` 를 써야 `lifespan` 이 실행된다. |
| `TypeError: … not all arguments converted` 또는 `the query has 1 placeholders but 5 parameters were passed` | `(memo_id,)` 의 쉼표를 빠뜨렸다. 값이 하나여도 쉼표가 필요하다. |
| 서버가 500 을 돌려준다 | **[PS]** `docker compose logs app --tail 30` 에서 `Traceback` 의 마지막 줄을 읽는다. 그 출력을 AI 에게 붙여 준다. |
| 테스트를 돌리면 진짜 메모가 사라진다 | 테스트가 `memo_db` 에서 돈다. `conftest.py` 가 `TEST_DATABASE_URL` 로 주소를 바꿔 끼우는지 확인하게 한다. |
| `database "memo_test" does not exist` | `conftest.py` 가 테스트 DB 를 만들지 않는다. 지시서 5번 조건을 가리켜 고치게 하거나, 급하면 **[PS]** `docker compose exec db psql -U memo -d memo_db -c "CREATE DATABASE memo_test;"` |
| 시각이 9시간 어긋나 보인다 | 응답의 끝이 `Z` 면 세계 표준시(UTC)다. 한국 시각은 9시간을 더한 값이다. 10교시에 화면에서 한국 시각으로 바꿔 보여 준다. |

## 확인 문제

1. 이번 교시에 "바꾼 것"과 "바꾸지 않은 것"을 각각 세 가지씩 쓰시오.
2. 저장소를 통째로 바꿨는데 `tests/test_memos.py` 를 고칠 필요가 없었던 이유는 무엇인가?
3. `git diff --stat` 에 `tests/test_memos.py` 가 나타났다. 이것이 왜 문제인가? 어떻게 대응하는가?
4. `conn.execute("SELECT * FROM memos WHERE id = %s", (memo_id,))` 에서 `%s` 와 `(memo_id,)` 는 각각 무엇인가? 쉼표는 왜 있는가?
5. f-문자열로 SQL 을 만들면 왜 위험한가? 한 문장으로 쓰시오.
6. `fetchone()` 이 `None` 을 돌려주는 경우는 언제인가? 그때 코드는 무엇을 해야 하는가?
7. 테스트 전용 DB 가 없으면 어떤 사고가 생기는가? 이번 교시에 그 사고가 나지 않았음을 어떻게 확인했는가?
8. 접속 주소 `postgresql://memo:memo1234@db:5432/memo_db` 의 각 부분이 무엇인지 쓰시오. 이 주소는 코드의 어디에 적혀 있는가?

## 다음 교시

[9교시. 수정·삭제 구현](09_수정_삭제_구현.md) — 고치기와 지우기를 더해 CRUD 를 완성한다.
