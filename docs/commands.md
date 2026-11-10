# 자주 쓰는 명령 모음

명령을 **어디에서 치는지**가 가장 중요하다. 표시를 먼저 확인한다.

| 표시 | 어디 | 프롬프트 모양 | 들어가는 법 |
|---|---|---|---|
| **[PS]** | 윈도우 PowerShell | `PS C:\harness-crud-lab>` | 시작 메뉴 → PowerShell → `cd C:\harness-crud-lab` |
| **[dev]** | dev 컨테이너의 셸 | `root@…:/workspace#` | **[PS]** `docker compose exec dev bash` |
| **[psql]** | PostgreSQL 접속 상태 | `memo_db=#` | **[PS]** `docker compose exec db psql -U memo -d memo_db` |
| **[AI]** | OpenCode 입력 칸 | (OpenCode 화면) | **[dev]** `opencode` |

---

## 1. 하루의 시작과 끝 — [PS]

| 하려는 일 | 명령 |
|---|---|
| 수업 시작 (컨테이너 켜기) | `docker compose up -d` |
| 상태 보기 | `docker compose ps` |
| 작업실 들어가기 | `docker compose exec dev bash` |
| 수업 끝 (멈추기. 지우지 않는다) | `docker compose stop` |
| 멈춘 것 다시 켜기 | `docker compose start` |

PC 를 다시 켠 뒤에는 Docker Desktop 을 먼저 실행하고 "Engine running" 을 기다린다.

## 2. 컨테이너 다루기 — [PS]

| 하려는 일 | 명령 |
|---|---|
| 처음 만들기, `Dockerfile`·`requirements.txt` 를 고친 뒤 | `docker compose up -d --build` |
| `.env` 를 고친 뒤 | `docker compose up -d` (바뀐 컨테이너를 다시 만든다) |
| 서버만 다시 켜기 | `docker compose restart app` |
| 서버 로그 마지막 30줄 | `docker compose logs app --tail 30` |
| 서버 로그 계속 보기 (Ctrl+C 로 멈춤) | `docker compose logs app -f` |
| DB 로그 | `docker compose logs db --tail 30` |
| 컨테이너 지우기 (소스와 DB 데이터는 C 드라이브에 남는다) | `docker compose down` |
| 바인드 마운트 확인 | `docker inspect harness-crud-lab-dev-1 --format "{{ json .Mounts }}"` |

## 3. 검증 — [dev]

| 하려는 일 | 명령 |
|---|---|
| 전체 검증 (코드 검사 + 테스트) | `sh scripts/verify.sh` |
| 테스트만 | `pytest -q` |
| 테스트 이름까지 보기 | `pytest -v` |
| 테스트 하나만 | `pytest -q tests/test_memos.py::test_create_memo` |
| 이름에 낱말이 든 테스트만 | `pytest -q -k update` |
| 코드 검사만 | `ruff check app tests scripts` |

## 4. API 불러 보기 — [dev]

컨테이너 안에서는 주소가 `http://app:8000` 이다. 브라우저에서는 `http://localhost:8000` 이다.

| 하려는 일 | 명령 |
|---|---|
| 목록 보기 | `curl -s http://app:8000/memos` |
| 한 건 보기 | `curl -s http://app:8000/memos/1` |
| 만들기 | `curl -s -X POST http://app:8000/memos -H "Content-Type: application/json" -d '{"title": "장보기", "content": "우유"}'` |
| 고치기 | `curl -s -X PUT http://app:8000/memos/1 -H "Content-Type: application/json" -d '{"title": "새 제목", "content": "새 내용"}'` |
| 지우기 | `curl -s -X DELETE http://app:8000/memos/1` |
| 상태 코드만 보기 | 위 명령에 `-o /dev/null -w "%{http_code}\n"` 를 붙인다 |

브라우저에서 눌러 보기: http://localhost:8000/docs

## 5. Git — [dev]

| 하려는 일 | 명령 |
|---|---|
| 무엇이 바뀌었나 (파일 목록) | `git status` |
| 무엇이 바뀌었나 (파일별 줄 수) | `git diff --stat` |
| 무엇이 바뀌었나 (내용) | `git diff` (`q` 로 나온다) |
| 특정 폴더만 | `git diff tests/` |
| 테스트에서 지워진 줄만 | `git diff tests/ \| grep "^-" \| grep -v "^---"` |
| 저장할 파일 고르기 | `git add -A` (전부) 또는 `git add 파일이름` |
| 저장 | `git commit -m "9교시: 무엇을 했는지 (요구사항 번호)"` |
| 기록 보기 | `git log --oneline` |
| 커밋 하나에서 바뀐 파일 | `git show --stat 커밋번호` |
| 고친 것 버리기 (마지막 커밋 상태로) | `git restore .` |
| `git add` 한 것 취소 | `git restore --staged 파일이름` |
| 훅 켜기 (저장소마다 한 번) | `git config core.hooksPath .githooks` |

`git restore .` 는 **커밋하지 않은 변경을 모두 버린다.** 되돌릴 수 없다. 새로 만들어진 파일은 지워지지 않으므로 `git status` 로 확인해 직접 지운다.

올리기(push)는 **[PS]** 에서 한다: `git push`

## 6. AI 부르기 — [dev]

| 하려는 일 | 명령 |
|---|---|
| 질문 하나 (파일을 고치지 못한다) | `python scripts/ask_ai.py "질문"` |
| 파일을 붙여서 질문 | `python scripts/ask_ai.py --file app/main.py "질문"` |
| 다른 모델로 질문 | `python scripts/ask_ai.py --model 모델이름 "질문"` |
| 에이전트에게 한 번 시키기 | `opencode run "시킬 일"` |
| 에이전트 대화 화면 | `opencode` |
| 키가 전달되었나 (글자 수만) | `echo ${#OPENROUTER_API_KEY}` |

## 7. OpenCode 안에서 — [AI]

| 입력 | 하는 일 |
|---|---|
| `/exit` | 끝낸다 |
| `/new` | 새 대화 (앞의 대화를 잊는다) |
| `/undo` | 마지막 요청과 그 요청으로 바뀐 파일을 되돌린다 |
| `/redo` | `/undo` 를 취소한다 |
| `/models` | 모델 목록 |
| `@파일이름` | 파일을 대화에 첨부한다 |

**자주 쓰는 지시 문장**

| 상황 | 문장 |
|---|---|
| 작업 시작 | `harness/tasks/NN_….md 를 읽고 그 지시대로 작업해 줘. 먼저 계획만 말하고 내 승인을 기다려.` |
| 계획 승인 | `진행` |
| 계획 수정 | `계획 N번은 지시서 4번(하지 말 것)에 어긋나. 빼고 다시 말해 줘.` |
| 설명 요청 | `파일은 고치지 말고 설명만 해 줘. (파일)의 (함수/줄)이 무슨 일을 해?` |
| 검증 실패 | `sh scripts/verify.sh 가 실패했어. 아래가 출력이야. 원인을 먼저 설명하고, tests/ 는 건드리지 말고 고쳐 줘.` + 출력 붙여넣기 |
| 범위 위반 | `git diff --stat 에 (파일)이 나와. 지시서 3번에서 고치면 안 된다고 했어. 되돌려 줘.` |

## 8. 데이터베이스 — [PS] 와 [psql]

| 하려는 일 | 명령 |
|---|---|
| 접속 | **[PS]** `docker compose exec db psql -U memo -d memo_db` |
| 접속하지 않고 SQL 한 줄 | **[PS]** `docker compose exec db psql -U memo -d memo_db -c "SELECT id, title FROM memos ORDER BY id;"` |
| 데이터베이스 목록 | **[psql]** `\l` |
| 다른 데이터베이스로 | **[psql]** `\c practice` |
| 테이블 목록 | **[psql]** `\dt` |
| 테이블 구조 | **[psql]** `\d memos` |
| 나가기 | **[psql]** `\q` |

| SQL | 하는 일 |
|---|---|
| `SELECT * FROM memos ORDER BY id DESC;` | 목록 (최신이 위) |
| `SELECT * FROM memos WHERE id = 1;` | 한 건 |
| `INSERT INTO memos (title, content) VALUES ('제목', '내용');` | 만들기 |
| `UPDATE memos SET title = '새 제목' WHERE id = 1;` | 고치기 — **WHERE 필수** |
| `DELETE FROM memos WHERE id = 1;` | 지우기 — **WHERE 필수** |

## 9. 막혔을 때 — [dev]

| 하려는 일 | 명령 |
|---|---|
| N교시 완성 예시 가져오기 | `sh scripts/checkpoint.sh 08` |
| 저장 안 한 변경이 있어도 가져오기 | `sh scripts/checkpoint.sh 08 --force` |
| 가져올 수 있는 목록 보기 | `sh scripts/checkpoint.sh` |
| 하네스 파일 다시 가져오기 | `cp harness/AGENTS.md AGENTS.md` , `cp harness/opencode.jsonc opencode.jsonc` |

체크포인트는 `app/` 과 `tests/` 를 **통째로 바꿔치기**한다. 내 작업이 사라지므로, 남기고 싶으면 먼저 커밋한다.

| 교시를 시작할 때 필요한 상태 | 가져올 체크포인트 |
|---|---|
| 4교시 | `03` |
| 5·6교시 | `04` |
| 7·8교시 | `06` |
| 9교시 | `08` |
| 10교시 | `09` |
| 11교시 | `10` |
| 12교시 | `11` |
