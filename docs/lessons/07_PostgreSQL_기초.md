# 7교시. PostgreSQL 기초

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | DB·테이블 생성 (SQL 로 메모를 만들고, 보고, 고치고, 지운다) |
| 시작 상태 | 6교시를 마친 상태. 이 교시는 코드를 고치지 않으므로 6교시가 덜 끝났어도 진행할 수 있다 |

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
 └─ 이번 교시: 8교시에 AI 가 쓸 SQL 을, 내가 먼저 읽고 쓸 수 있게 한다
```

8교시에 AI 가 `INSERT INTO memos (title, content) VALUES (%s, %s) RETURNING *` 같은 코드를 쓴다. 이 줄을 읽지 못하면 검토할 수 없다. 이번 교시는 AI 없이 **손으로** SQL 을 친다. 3교시에 `/hello` 를 손으로 만든 것과 같은 이유다.

## 학습 목표

1. 데이터베이스·테이블·행·열이 무엇인지 설명한다.
2. `psql` 로 PostgreSQL 에 접속해 데이터베이스와 테이블을 만든다.
3. `INSERT`·`SELECT`·`UPDATE`·`DELETE` 로 CRUD 를 한다.
4. `NOT NULL`, `PRIMARY KEY`, `DEFAULT` 가 무엇을 지켜 주는지 직접 확인한다.
5. 컨테이너를 지웠다 다시 만들어도 데이터가 남는 것을 확인하고, 그 이유를 설명한다.

---

## 1. 개념

### 왜 데이터베이스인가

4교시에 서버를 다시 켜니 메모가 사라졌다. 파이썬의 리스트·딕셔너리는 프로그램의 메모리에 있고, 프로그램이 꺼지면 없어진다.
**데이터베이스(DB)** 는 데이터를 디스크에 저장하고, 여러 프로그램이 동시에 안전하게 읽고 쓰게 해 주는 프로그램이다. **PostgreSQL** 은 널리 쓰이는 무료 데이터베이스다.

### 낱말

| 낱말 | 뜻 | 엑셀에 빗대면 |
|---|---|---|
| 데이터베이스 | 테이블들을 담는 큰 묶음 | 파일(통합 문서) |
| 테이블 | 같은 모양의 데이터를 모아 둔 표 | 시트 |
| 열(column) | 항목. 이름과 타입이 정해져 있다 | 열 제목 |
| 행(row) | 데이터 한 건 | 한 줄 |
| SQL | 데이터베이스에게 일을 시키는 말 | — |

엑셀과 다른 점: 열마다 **타입과 규칙**이 정해져 있어서, 맞지 않는 데이터는 들어가지 못한다.

### `memos` 테이블

| 열 | 타입 | 규칙 | 뜻 |
|---|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` | 자동으로 1, 2, 3 … 이 붙는 번호. 겹치지 않는다 |
| `title` | `VARCHAR(100)` | `NOT NULL` | 최대 100자의 글자. 비어 있을 수 없다 |
| `content` | `TEXT` | `NOT NULL DEFAULT ''` | 길이 제한 없는 글자. 안 넣으면 빈 문자열 |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` | 날짜와 시각. 안 넣으면 지금 시각 |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` | 날짜와 시각. 안 넣으면 지금 시각 |

`harness/REQUIREMENTS.md` 2절의 "메모 한 건의 모양" 표와 나란히 놓고 본다. 같은 내용이 요구사항 → 파이썬 클래스(`MemoOut`) → 테이블, 세 군데에 같은 모양으로 있다.

### CRUD ↔ SQL

4교시의 표에 SQL 칸을 채운다.

| 하는 일 | HTTP | SQL |
|---|---|---|
| 만들기 | `POST /memos` | `INSERT INTO memos (title, content) VALUES ('…', '…');` |
| 목록 보기 | `GET /memos` | `SELECT * FROM memos ORDER BY id DESC;` |
| 한 건 보기 | `GET /memos/2` | `SELECT * FROM memos WHERE id = 2;` |
| 고치기 | `PUT /memos/2` | `UPDATE memos SET title = '…' WHERE id = 2;` |
| 지우기 | `DELETE /memos/2` | `DELETE FROM memos WHERE id = 2;` |

### 우리 DB 는 어디에 있는가

```text
 [db 컨테이너]  PostgreSQL 17
     │   계정 memo / 비밀번호 memo1234   (.env 의 POSTGRES_USER, POSTGRES_PASSWORD)
     │
     ├─ 데이터베이스 memo_db     ← 앱이 쓰는 진짜 메모 (8교시부터)
     ├─ 데이터베이스 memo_test   ← 테스트 전용 (8교시에 생긴다)
     └─ 데이터베이스 practice    ← 이번 교시의 연습장 (지금 만든다)

 데이터가 실제로 놓이는 곳:  C:\harness-crud-lab\data\postgres\   (바인드 마운트)
```

---

## 따라 하기

### 1단계. 접속하기 (10분)

`psql` 은 PostgreSQL 에 접속해 SQL 을 치는 프로그램이다. db 컨테이너 안에 들어 있다.

**[PS]**

```powershell
cd C:\harness-crud-lab
docker compose exec db psql -U memo -d memo_db
```

- `-U memo` — 계정 이름
- `-d memo_db` — 접속할 데이터베이스

프롬프트가 `memo_db=#` 로 바뀐다. 이제 치는 것은 SQL 이다. 이 교시에서는 이 상태를 **[psql]** 로 표시한다.

`psql` 에는 SQL 말고 `\` 로 시작하는 자체 명령이 있다.

| 명령 | 하는 일 |
|---|---|
| `\l` | 데이터베이스 목록 |
| `\c 이름` | 다른 데이터베이스로 옮겨 가기 |
| `\dt` | 지금 데이터베이스의 테이블 목록 |
| `\d 테이블` | 테이블의 열과 규칙 보기 |
| `\q` | 나가기 |

**[psql]**

```sql
\l
```

목록에 `memo_db` 가 있다. 2교시에 컨테이너를 처음 켤 때 `.env` 의 `POSTGRES_DB` 값으로 자동으로 만들어진 것이다. (`postgres`, `template0`, `template1` 은 PostgreSQL 이 스스로 쓰는 것이니 건드리지 않는다.) 목록이 길어 `(END)` 가 보이면 `q` 를 누른다.

### 2단계. 데이터베이스와 테이블 만들기 (15분)

연습장으로 쓸 데이터베이스를 만든다. **SQL 문장은 세미콜론(`;`)으로 끝낸다.** 세미콜론을 치기 전에는 Enter 를 눌러도 실행되지 않고 다음 줄을 기다린다.

**[psql]**

```sql
CREATE DATABASE practice;
```

```text
CREATE DATABASE
```

연습장으로 옮겨 간다.

**[psql]**

```sql
\c practice
```

프롬프트가 `practice=#` 로 바뀐다.

테이블을 만든다. 여러 줄이지만 문장 하나다. 한 줄씩 치고 Enter 를 눌러도 되고, 통째로 붙여 넣어도 된다.

**[psql]**

```sql
CREATE TABLE memos (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(100) NOT NULL,
    content     TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```text
CREATE TABLE
```

만들어졌는지 본다.

**[psql]**

```sql
\dt
```

```text
       List of relations
 Schema | Name  | Type  | Owner 
--------+-------+-------+-------
 public | memos | table | memo
(1 row)
```

**[psql]**

```sql
\d memos
```

열 이름, 타입, `not null`, 기본값이 표로 나온다. 1절의 표와 대조한다.

### 3단계. Create — `INSERT` (10분)

**[psql]**

```sql
INSERT INTO memos (title, content) VALUES ('장보기', '우유, 달걀');
```

```text
INSERT 0 1
```

마지막 숫자 `1` 이 "1행이 들어갔다"는 뜻이다. SQL 에서 글자는 **작은따옴표**로 감싼다. (JSON 은 큰따옴표였다.)

내용 없이 하나 더 넣는다.

**[psql]**

```sql
INSERT INTO memos (title) VALUES ('운동');
```

`id`, `content`, `created_at`, `updated_at` 은 넣지 않았다. 어떻게 채워졌는지 다음 단계에서 본다.

### 4단계. Read — `SELECT` (15분)

**[psql]**

```sql
SELECT id, title, content FROM memos;
```

```text
 id | title  |  content   
----+--------+------------
  1 | 장보기 | 우유, 달걀
  2 | 운동   | 
(2 rows)
```

- `id` 가 1, 2 로 **자동으로** 붙었다. (`SERIAL`)
- 2번의 `content` 는 빈 문자열이다. (`DEFAULT ''`)

모든 열을 보려면 `*` 를 쓴다.

**[psql]**

```sql
SELECT * FROM memos;
```

`created_at`, `updated_at` 에 넣은 적 없는 시각이 들어 있다. (`DEFAULT now()`)

**조건으로 고르기 — `WHERE`**

**[psql]**

```sql
SELECT id, title FROM memos WHERE id = 2;
```

```text
 id | title 
----+-------
  2 | 운동
(1 row)
```

`GET /memos/2` 가 하는 일이 이것이다.

**순서 정하기 — `ORDER BY`**

**[psql]**

```sql
SELECT id, title FROM memos ORDER BY id DESC;
```

```text
 id | title  
----+--------
  2 | 운동
  1 | 장보기
(2 rows)
```

`DESC` 는 큰 것부터(내림차순)다. 요구사항 R2 "나중에 만든 메모가 앞에"가 이 한 줄이다.

없는 번호를 찾으면 어떻게 되는지도 본다.

**[psql]**

```sql
SELECT id, title FROM memos WHERE id = 999;
```

오류가 아니라 `(0 rows)` 가 나온다. **DB 는 "없다"를 오류로 알려 주지 않는다.** 그래서 서버 코드가 "결과가 0건이면 404"를 직접 만들어야 한다. 8교시에 AI 가 쓴 코드에서 이 부분을 찾아볼 것이다.

### 5단계. Update — `UPDATE` (10분)

**[psql]**

```sql
UPDATE memos SET content = '저녁 7시 달리기', updated_at = now() WHERE id = 2;
```

```text
UPDATE 1
```

**[psql]**

```sql
SELECT id, title, content FROM memos ORDER BY id;
```

```text
 id | title  |     content     
----+--------+-----------------
  1 | 장보기 | 우유, 달걀
  2 | 운동   | 저녁 7시 달리기
(2 rows)
```

> **`WHERE` 를 빠뜨리면 모든 행이 바뀐다.**
> `UPDATE memos SET content = '…';` 는 메모 전체의 내용을 같은 글로 덮어쓴다. 되돌릴 수 없다.
> `AGENTS.md` 5절에 "`UPDATE` 와 `DELETE` 에는 반드시 `WHERE` 를 쓴다"가 있는 이유다. 9교시에 AI 가 쓴 코드에서 이 규칙이 지켜졌는지 내가 확인한다.

### 6단계. 규칙이 지켜 주는 것 (10분)

제목 없이 넣어 본다.

**[psql]**

```sql
INSERT INTO memos (content) VALUES ('제목이 없는 메모');
```

```text
ERROR:  null value in column "title" of relation "memos" violates not-null constraint
```

"`title` 열에 빈 값(null)을 넣으려 해서 not-null 규칙을 어겼다." 들어가지 않았다.

4교시에는 FastAPI 가 제목 없는 요청을 422 로 막았다. 이제 DB 도 막는다. **같은 규칙을 두 겹으로 지킨다.** 서버 코드에 버그가 있어도 DB 가 잘못된 데이터를 받지 않는다.

### 7단계. Delete — `DELETE` (10분)

**[psql]**

```sql
DELETE FROM memos WHERE id = 1;
```

```text
DELETE 1
```

**[psql]**

```sql
SELECT id, title, content FROM memos;
```

```text
 id | title |     content     
----+-------+-----------------
  2 | 운동  | 저녁 7시 달리기
(1 row)
```

없는 번호를 지워 본다.

**[psql]**

```sql
DELETE FROM memos WHERE id = 999;
```

```text
DELETE 0
```

오류가 아니다. `0` 이 "0행을 지웠다"는 뜻이다. 요구사항 R5 는 이때 404 를 돌려주라고 한다. 서버 코드가 이 숫자(또는 그에 해당하는 결과)를 보고 404 를 만들어야 한다.

새 메모를 넣으면 번호는 어떻게 될까?

**[psql]**

```sql
INSERT INTO memos (title) VALUES ('새 메모') RETURNING id, title;
```

```text
 id |  title  
----+---------
  4 | 새 메모
(1 row)

INSERT 0 1
```

두 가지를 본다.

- **`RETURNING`** — 넣은 행을 바로 돌려받는다. `INSERT` 뒤에 `SELECT` 를 또 하지 않아도 된다. 8교시의 코드에 나온다.
- **번호가 4 다.** 1번을 지웠지만 다시 쓰지 않는다. 3번은 6단계에서 실패한 `INSERT` 가 가져갔다가 버렸다. `SERIAL` 은 겹치지 않는 것만 보장하고, 빈틈이 없는 것은 보장하지 않는다.

**[psql]**

```sql
SELECT count(*) FROM memos;
```

```text
 count 
-------
     2
(1 row)
```

### 8단계. 컨테이너를 지워도 데이터가 남는가 (20분)

`psql` 에서 나온다.

**[psql]**

```sql
\q
```

**(1) 데이터가 놓인 곳을 본다.**

**[PS]**

```powershell
dir C:\harness-crud-lab\data\postgres
```

`base`, `global`, `pg_wal`, `PG_VERSION` … PostgreSQL 이 쓰는 파일들이다. 방금 넣은 메모가 이 안 어딘가에 들어 있다.

**(2) 컨테이너를 모두 지운다.** `stop` 이 아니라 `down` 이다. 컨테이너가 삭제된다.

**[PS]**

```powershell
docker compose down
docker compose ps
```

`docker compose ps` 에 아무것도 나오지 않는다. db 컨테이너는 이제 없다.

**(3) C 드라이브의 폴더는?**

**[PS]**

```powershell
dir C:\harness-crud-lab\data\postgres
```

그대로 있다.

**(4) 컨테이너를 새로 만든다.**

**[PS]**

```powershell
docker compose up -d
docker compose ps
```

`db` 가 `healthy` 가 될 때까지 기다린다.

**(5) 메모가 있는지 본다.** `-c` 뒤에 SQL 을 주면 접속하지 않고 한 번에 실행한다.

**[PS]**

```powershell
docker compose exec db psql -U memo -d practice -c "SELECT id, title FROM memos ORDER BY id;"
```

`운동` 과 `새 메모` 두 행이 나온다. **컨테이너는 새것인데 데이터는 그대로다.**

```text
 지워진 것:  db 컨테이너 (PostgreSQL 프로그램이 돌던 상자)
 남은 것:    C:\harness-crud-lab\data\postgres\ (데이터)
 새 컨테이너가 같은 폴더를 다시 연결해서 이어 쓴다  ← 바인드 마운트
```

> 반대로, `C:\harness-crud-lab\data\postgres` 폴더를 지우면 데이터가 모두 사라진다. DB 를 완전히 처음부터 다시 시작하고 싶을 때만, 컨테이너를 내린 뒤(`docker compose down`) 이 폴더를 지운다.

dev 컨테이너도 새로 만들어졌다. 계속하려면 다시 들어간다.

**[PS]**

```powershell
docker compose exec dev bash
```

### 9단계. AI 에게 물어 확인하기 (10분)

이번 교시에 배운 것을 AI 의 설명과 맞춰 본다. 고치는 일이 아니라 묻는 일이다.

**[dev]**

```bash
python scripts/ask_ai.py "PostgreSQL 에서 UPDATE 문에 WHERE 를 빠뜨리면 어떻게 되는지, 그리고 그 실수를 막는 습관 두 가지를 초보자에게 알려 줘."
```

**[dev]**

```bash
python scripts/ask_ai.py "SQL 인젝션이 뭐야? 파이썬에서 SQL 문자열에 값을 직접 이어 붙이면 왜 위험한지, 짧은 예 하나로 설명해 줘."
```

둘째 질문의 답을 잘 읽어 둔다. `AGENTS.md` 의 "SQL 에 값을 넣을 때는 반드시 `%s` 자리표시자를 쓴다"가 왜 있는지에 대한 답이다. 8교시에 AI 가 쓴 코드에서 이 규칙을 내가 확인한다.

이 교시에는 코드를 고치지 않았으므로 커밋할 것이 없다. `harness/WORKLOG.md` 에 "5. 새로 알게 된 것"만 적어 둔다.

---

## 하네스 관점 — 이번 교시에서 본 것

- **검토하려면 읽을 수 있어야 한다.** 이번 교시는 AI 를 쓰지 않았지만, AI 의 다음 작업을 검토할 준비를 했다. SQL 다섯 문장을 읽을 수 있으면 8·9교시의 `git diff` 를 읽을 수 있다.
- **규칙에는 이유가 있다.** `AGENTS.md` 의 DB 규칙 두 줄(`%s` 자리표시자, `WHERE` 필수)은 5교시에 옮겨 적기만 했다. 이번 교시에 왜 필요한지 직접 봤다.
- **데이터는 실행 환경 밖에 둔다.** 컨테이너(실행)는 언제든 지우고 다시 만들 수 있고, 데이터는 C 드라이브에 남는다. AI 가 컨테이너 안에서 무엇을 하든 컨테이너를 새로 만들면 깨끗한 실행 환경으로 돌아온다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| Enter 를 쳐도 아무 일이 없고 프롬프트가 `practice-#` 로 바뀐다 | 세미콜론(`;`)을 빠뜨렸다. `;` 를 치고 Enter 를 누른다. |
| 프롬프트가 `practice'#` 로 바뀌고 빠져나오지 못한다 | 작은따옴표를 닫지 않았다. `'` 를 치고 `;` 를 친다. 그래도 안 되면 Ctrl+C. |
| `ERROR: relation "memos" does not exist` | `practice` 가 아닌 다른 데이터베이스에 있다. 프롬프트를 보고 `\c practice` 로 옮긴다. |
| `ERROR: database "practice" already exists` | 이미 만들었다. `\c practice` 로 들어간다. |
| `ERROR: syntax error at or near …` | 오타다. 가리키는 낱말의 **바로 앞**을 본다. 쉼표나 괄호가 빠진 경우가 많다. |
| `ERROR: column "장보기" does not exist` | 글자를 큰따옴표로 감쌌다. SQL 의 글자는 작은따옴표다. |
| 한글이 깨져 보인다 | 오래된 명령 창(cmd)에서 그럴 수 있다. Windows Terminal 이나 PowerShell 을 쓴다. |
| 결과가 길어 `(END)` 나 `:` 에서 멈춘다 | `q` 를 누른다. |
| 8단계에서 메모가 사라졌다 | `data\postgres` 폴더를 지웠거나, 예비 설정(`docker-compose.volume.yml`) 없이 켰다가 있이 켰다. [`docs/troubleshooting.md`](../troubleshooting.md) 를 본다. |

## 확인 문제

1. 데이터베이스, 테이블, 행, 열을 엑셀이 아닌 다른 것(예: 도서관)에 빗대어 설명하시오.
2. `INSERT INTO memos (title) VALUES ('운동');` 을 실행하면 `id`, `content`, `created_at` 에는 각각 무엇이 들어가는가? 각각 어떤 규칙 때문인가?
3. `SELECT * FROM memos WHERE id = 999;` 와 `DELETE FROM memos WHERE id = 999;` 는 오류를 내는가? 이 사실이 서버 코드에 어떤 일을 요구하는가?
4. `UPDATE memos SET title = '회의';` 를 실행하면 어떤 일이 생기는가?
5. 요구사항 R2("나중에 만든 메모가 앞에")를 SQL 한 문장으로 쓰시오.
6. `RETURNING` 은 무엇을 해 주는가? 없다면 같은 일을 하려고 무엇을 더 해야 하는가?
7. `docker compose down` 뒤에도 데이터가 남은 이유를 `docker-compose.yml` 의 해당 줄을 인용해 설명하시오.
8. 제목 없는 메모를 FastAPI(422)와 DB(NOT NULL)가 둘 다 막는다. 한쪽만 있으면 안 되는 이유를 쓰시오.

## 다음 교시

[8교시. FastAPI 와 DB 연결](08_FastAPI와_DB_연결.md) — AI 에이전트에게 저장소를 PostgreSQL 로 바꾸게 한다. 테스트는 한 글자도 바꾸지 않는다.
