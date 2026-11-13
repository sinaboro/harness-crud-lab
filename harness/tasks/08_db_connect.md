# 작업 지시서: 저장소를 PostgreSQL 로 바꾸기 (8교시)

## 1. 목표
메모를 메모리 대신 PostgreSQL 에 저장한다.
API 의 겉모습(주소, 요청, 응답, 상태 코드)은 **하나도 바꾸지 않는다.** 바뀌는 것은 저장하는 곳뿐이다.

## 2. 요구사항
`harness/REQUIREMENTS.md` 의 **R1, R2, R3, R6** 을 그대로 유지하면서 **N1, N2, N4** 를 만족한다.

## 3. 범위
- 새로 만드는 파일: `app/db.py`
- 고쳐도 되는 파일: `app/main.py`, `tests/conftest.py`
- 고치면 안 되는 것: **`tests/test_memos.py`, `tests/test_health.py`** (테스트는 한 글자도 바꾸지 않는다)

## 4. 하지 말 것
- 수정(PUT)과 삭제(DELETE)는 만들지 않는다. (9교시에 한다)
- ORM(SQLAlchemy 등)을 쓰지 않는다. `psycopg` 로 저장 명령을 직접 실행한다. (저장 코드가 사람 눈에 그대로 보이게 하기 위해서다)
- 접속 주소나 비밀번호를 코드에 적지 않는다.
- 새 패키지를 추가하지 않는다. (`psycopg` 는 이미 설치되어 있다)

## 5. 구현 조건
- 접속 주소는 환경 변수 `DATABASE_URL` 에서 읽는다.
- 테이블 이름은 `memos`. 열은 `id`(SERIAL PRIMARY KEY), `title`(VARCHAR(100) NOT NULL), `content`(TEXT NOT NULL DEFAULT ''), `created_at`·`updated_at`(TIMESTAMPTZ NOT NULL DEFAULT now()).
- 서버가 켜질 때 테이블이 없으면 만든다. (`CREATE TABLE IF NOT EXISTS`)
- SQL 에 값을 넣을 때는 `%s` 자리표시자를 쓴다.
- 테스트는 환경 변수 `TEST_DATABASE_URL` 이 가리키는 **테스트 전용 DB**(`memo_test`)에서만 돈다.
  - 테스트 전용 DB 가 없으면 `tests/conftest.py` 가 만든다.
  - 테스트 하나가 시작될 때마다 `memos` 테이블을 비우고 번호를 1부터 다시 시작한다.

## 6. 완료 조건
- [ ] `sh scripts/verify.sh` 가 "검증 통과"로 끝난다. **테스트 개수는 작업 전과 같다.**
- [ ] `git diff --stat` 에 `tests/test_memos.py` 가 나타나지 않는다.
- [ ] 메모를 만든 뒤 서버를 다시 켜도 메모가 남아 있다. (사람이 확인한다)
- [ ] 테스트를 실행해도 `memo_db` 의 메모는 지워지지 않는다. (사람이 확인한다)
- [ ] `app/main.py` 에 메모리 저장소(딕셔너리, `next_id`, `reset_store`)가 남아 있지 않다.

## 7. 진행 방법
`AGENTS.md` 의 작업 절차를 따른다. 먼저 계획을 말하고, 내가 "진행"이라고 하면 구현한다.
끝나면 `AGENTS.md` 의 보고 형식으로 보고한다.
