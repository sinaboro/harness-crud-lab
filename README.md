# harness-crud-lab

**하네스 엔지니어링 입문 — AI 에이전트에게 맡겨 만들고, 내가 이해하고, 검증해서 저장하는 메모 CRUD 프로젝트**

코드를 먼저 배운 뒤에 AI 를 쓰는 과정이 아니다.
**AI 에이전트에게 개발을 맡기면서**, 그 과정에서 코드와 개발 원리를 이해하는 과정이다.
대신 "되는 것 같으니 넘어가자"로 끝내지 않는다. AI 의 작업을 **규칙·도구·권한·실행·검증**으로 통제하고, **테스트를 통과한 코드만 Git 에 저장**한다.

| | |
|---|---|
| 대상 | 프로그래밍을 처음 배우는 사람 (코딩 경험이 없어도 된다) |
| 기간 | 3일 × 8시간 = 24시간, 12교시 (1교시 = 2시간) |
| 결과물 | 메모 CRUD 웹 서비스 (FastAPI + PostgreSQL + HTML·JS 화면 + 자동 테스트) |
| 사용 기술 | Docker, OpenRouter, OpenCode(AI 에이전트), Python, FastAPI, PostgreSQL, pytest, Git |
| 교안 PDF | [`docs/하네스_엔지니어링_입문_학습교안.pdf`](docs/하네스_엔지니어링_입문_학습교안.pdf) |

---

## 1. 바이브 코딩과 하네스 엔지니어링

**바이브 코딩**은 AI 에게 말로 시키고, 돌아가는 것 같으면 그대로 받아들이는 방식이다. 빠르지만 세 가지가 남지 않는다.
무엇을 만들기로 했는지(기준), 정말 되는지(증거), 내가 이해했는지(지식).

**하네스 엔지니어링**은 AI 가 일하는 **환경을 설계**하는 일이다. 하네스(harness)는 말에게 씌우는 마구를 뜻한다. 힘센 말이 원하는 방향으로 달리게 하는 장치다.

| | 바이브 코딩 | 하네스 엔지니어링 (이 과정) |
|---|---|---|
| 시키는 방법 | "메모 앱 만들어 줘" | 요구사항 명세 + 작업 지시서 |
| AI 가 따르는 것 | 그때그때의 대화 | 문서로 적어 둔 규칙 (`AGENTS.md`) |
| AI 가 할 수 있는 일 | 무엇이든 | 허용한 것만 (`opencode.jsonc` 의 권한) |
| "다 됐다"의 기준 | 돌아가는 것 같다 | 검증 스크립트 통과 (`scripts/verify.sh`) |
| 저장 | 아무 때나 | 검증을 통과해야만 커밋된다 (`pre-commit`) |
| 오류가 나면 | "안 돼, 고쳐 줘" | 오류 출력 전달 → 원인 설명 → 수정 → 재검증 |
| 끝난 뒤 나에게 남는 것 | 설명할 수 없는 코드 | 읽고 설명할 수 있는 코드 + 작업 기록 |

### 하네스의 다섯 요소

| 요소 | 질문 | 이 저장소에서 |
|---|---|---|
| 규칙 | 어떻게 일해야 하는가? | `AGENTS.md` |
| 도구 | 무엇으로 일하는가? | Docker 컨테이너, `scripts/verify.sh` |
| 권한 | 어디까지 해도 되는가? | `opencode.jsonc` (allow / ask / deny) |
| 실행 | 어디에서 실행되는가? | dev 컨테이너 안, `/workspace` 폴더만 |
| 검증 | 다 됐다는 것을 어떻게 아는가? | `tests/`, `scripts/verify.sh`, `.githooks/pre-commit` |

---

## 2. 수업의 흐름

모든 실습은 아래 다섯 단계를 반복한다. 6교시부터는 교시마다 이 고리를 한 바퀴씩 돈다.

```text
 ① 사람이 요구사항 작성           무엇을 만들고 싶은지 명확히 적는다
        │                        → harness/REQUIREMENTS.md
        ▼
 ② AI 에이전트에게 개발 지시       OpenRouter 를 통해 모델을 쓴다
        │                        → harness/tasks/ 의 작업 지시서
        ▼
 ③ 하네스로 개발 과정 제어         규칙 · 도구 · 권한 · 실행 · 검증
        │                        → AGENTS.md, opencode.jsonc
        ▼
 ④ 코드 실행 및 테스트             FastAPI + PostgreSQL
        │                        → sh scripts/verify.sh
        ▼
 ⑤ 오류 확인 → AI 수정 → 재검증    통과하면 Git 에 저장
                                 → git commit (pre-commit 이 한 번 더 검증)
```

---

## 3. 준비물

내 PC 에 설치하는 것은 **세 가지뿐**이다. Python, PostgreSQL, AI 에이전트는 PC 에 설치하지 않는다. 모두 Docker 컨테이너 안에 들어 있다.

| 준비물 | 용도 | 받는 곳 |
|---|---|---|
| Docker Desktop | 모든 도구를 컨테이너로 실행 | https://www.docker.com/products/docker-desktop/ |
| Git for Windows | 저장소 내려받기, GitHub 에 올리기 | https://git-scm.com/download/win |
| 편집기 (VS Code 권장) | 파일 읽기·고치기 | https://code.visualstudio.com/ |
| OpenRouter 계정과 API 키 | AI 모델 사용 | https://openrouter.ai/ |
| GitHub 계정 | 12교시에 결과물 올리기 | https://github.com/ |

- 운영체제: Windows 10 또는 11 (64비트). Docker Desktop 은 WSL 2 방식으로 설치한다(설치 화면의 기본값).
- OpenRouter 는 쓴 만큼 요금을 내는 서비스다. 요금과 키 발급 방법은 [2교시](docs/lessons/02_개발환경과_OpenRouter.md)에서 다룬다.
- 설치 방법은 [2교시](docs/lessons/02_개발환경과_OpenRouter.md)에 단계별로 적혀 있다. 미리 해 두지 않아도 된다.

---

## 4. 시작하는 법

2교시에 자세히 따라 한다. 여기는 한눈에 보는 요약이다. 명령은 **PowerShell** 에서 실행한다.

```powershell
# 1) 저장소를 C 드라이브에 내려받는다. (폴더 위치가 중요하다. 아래 "왜 C 드라이브인가" 참고)
git clone https://github.com/sinaboro/harness-crud-lab.git C:\harness-crud-lab
cd C:\harness-crud-lab

# 2) 환경 변수 파일을 만들고, 메모장으로 열어 OPENROUTER_API_KEY 를 채운다.
Copy-Item .env.example .env
notepad .env

# 3) 컨테이너 3개(db, app, dev)를 만들고 켠다. 처음에는 몇 분 걸린다.
docker compose up -d --build

# 4) 상태를 본다. db 는 healthy, app 과 dev 는 running(Up) 이어야 한다.
docker compose ps
```

브라우저에서 http://localhost:8000/health 를 열어 `{"status":"ok"}` 가 보이면 준비가 끝난 것이다.

작업실(dev 컨테이너)에 들어가는 명령:

```powershell
docker compose exec dev bash
```

이제 [1교시](docs/lessons/01_AI_개발_방식과_하네스.md)부터 순서대로 따라 한다.

---

## 5. 교시표

| 일차 | 교시 | 학습 내용 | 실습 결과 | 하네스에서 배우는 것 |
|---|---|---|---|---|
| 1일 | [1](docs/lessons/01_AI_개발_방식과_하네스.md) | AI 개발 방식과 하네스 이해 | AI·하네스·도구 구분 | 다섯 요소, 수업의 흐름 |
| | [2](docs/lessons/02_개발환경과_OpenRouter.md) | 개발환경 및 OpenRouter 연결 | AI 모델 호출 성공 | 도구·실행 환경(Docker, 바인드 마운트) |
| | [3](docs/lessons/03_Python_FastAPI_기본.md) | Python·FastAPI 기본 이해 | `/hello` API | AI 를 "설명해 주는 선생님"으로 쓰기 |
| | [4](docs/lessons/04_CRUD와_HTTP.md) | CRUD 와 HTTP 기초 | GET·POST 테스트 | 규칙 없는 AI 의 한계 관찰 |
| 2일 | [5](docs/lessons/05_하네스_규칙_작성.md) | 하네스 규칙 작성 | `AGENTS.md` | 규칙·권한·검증을 직접 세운다 |
| | [6](docs/lessons/06_AI에게_CRUD_지시.md) | AI 에게 CRUD 구현 지시 | 메모 CRUD 초안 | 작업 지시서, 계획 승인, 검토 |
| | [7](docs/lessons/07_PostgreSQL_기초.md) | PostgreSQL 기초 | DB·테이블 생성 | AI 가 쓸 SQL 을 내가 먼저 읽을 수 있게 |
| | [8](docs/lessons/08_FastAPI와_DB_연결.md) | FastAPI 와 DB 연결 | 메모 저장·조회 | 테스트는 그대로, 구현만 교체 |
| 3일 | [9](docs/lessons/09_수정_삭제_구현.md) | 수정·삭제 구현 | CRUD 완성 | 테스트 추가만 허용, 삭제 금지 |
| | [10](docs/lessons/10_HTML_JS_화면_연결.md) | HTML·JS 화면 연결 | 웹에서 CRUD 실행 | 테스트가 못 보는 것을 사람이 확인 |
| | [11](docs/lessons/11_자동_테스트와_오류_수정.md) | 자동 테스트와 오류 수정 | 테스트 통과 | 실패하는 테스트 먼저 → AI 수정 → 재검증 |
| | [12](docs/lessons/12_GitHub_저장과_발표.md) | GitHub 저장 및 발표 | 최종 프로젝트 | 기록으로 과정을 설명한다 |

각 교시 안내서의 구성: **학습 목표 → 개념 → 따라 하기(명령·기대 결과·확인 방법) → 하네스 관점 → 자주 만나는 오류 → 확인 문제**

보조 문서

- [`docs/commands.md`](docs/commands.md) — 자주 쓰는 명령 모음 (어디에서 치는 명령인지 구분)
- [`docs/glossary.md`](docs/glossary.md) — 용어 풀이
- [`docs/troubleshooting.md`](docs/troubleshooting.md) — 오류 해결 모음
- [`harness/README.md`](harness/README.md) — 하네스 문서 안내

---

## 6. 실행 환경 한눈에 보기

```text
 내 PC (Windows)
 │
 ├─ C:\harness-crud-lab\               ← 편집기로 여는 폴더. 여기 파일을 고친다.
 │    ├─ app\  tests\  harness\ ...
 │    └─ data\postgres\                ← 메모 데이터가 실제로 쌓이는 곳
 │
 └─ Docker Desktop
      │
      ├─ [app 컨테이너]  FastAPI 서버          → 브라우저에서 http://localhost:8000
      │     /workspace  ⇄  C:\harness-crud-lab          (바인드 마운트)
      │
      ├─ [dev 컨테이너]  작업실: pytest, git, OpenCode(AI 에이전트)
      │     /workspace  ⇄  C:\harness-crud-lab          (바인드 마운트)
      │
      └─ [db 컨테이너]   PostgreSQL 17
            /var/lib/postgresql/data  ⇄  C:\harness-crud-lab\data\postgres   (바인드 마운트)
```

### 왜 C 드라이브인가 — 바인드 마운트

**바인드 마운트**는 내 PC 의 폴더를 컨테이너 안의 폴더에 **그대로 연결**하는 것이다. 복사가 아니라 같은 폴더를 양쪽에서 보는 것이다.

- VS Code 로 `C:\harness-crud-lab\app\main.py` 를 고치면 → 컨테이너의 `/workspace/app/main.py` 가 바로 바뀐다 → 서버가 저절로 다시 켜진다.
- AI 에이전트가 컨테이너 안에서 파일을 고치면 → 내 PC 의 편집기에 바로 보인다. **AI 가 무엇을 고쳤는지 내 눈으로 볼 수 있다.**
- 컨테이너를 지워도(`docker compose down`) 소스와 DB 데이터는 C 드라이브에 그대로 남는다.
- 모든 수강생이 같은 경로(`C:\harness-crud-lab`)를 쓰면 교안의 명령과 화면이 똑같아진다.

확인 방법은 [2교시](docs/lessons/02_개발환경과_OpenRouter.md)에서 직접 해 본다.

---

## 7. 저장소 구조

```text
harness-crud-lab/
├─ README.md                  이 문서
├─ Dockerfile                 도구 상자 이미지(Python + pytest + OpenCode)의 설계도
├─ docker-compose.yml         컨테이너 3개(db, app, dev)와 바인드 마운트 설정
├─ docker-compose.volume.yml  DB 데이터 저장 방식의 예비 설정 (문제가 생길 때만)
├─ requirements.txt           파이썬 패키지 목록 (버전 고정)
├─ .env.example               환경 변수 견본 (.env 는 Git 에 올리지 않는다)
├─ opencode.jsonc             AI 에이전트 설정 (출발점: 모델만. 5교시에 권한 규칙 추가)
├─ pytest.ini, ruff.toml      테스트·코드 검사 설정
│
├─ app/                       ★ 내가(AI 와 함께) 만들어 갈 서버 코드. 출발점은 /health 하나
├─ tests/                     ★ 자동 테스트. 출발점은 테스트 하나
│
├─ harness/                   하네스 문서
│   ├─ REQUIREMENTS.md          요구사항 명세 (R1~R7)
│   ├─ AGENTS.md                에이전트 규칙 완성본 (5교시에 맨 위 폴더로 가져간다)
│   ├─ AGENTS.template.md       규칙을 직접 써 보는 틀
│   ├─ opencode.jsonc           권한 규칙 완성본
│   ├─ TASK_TEMPLATE.md         작업 지시서 틀
│   ├─ tasks/                   교시별 작업 지시서 (6·8·9·10·11교시)
│   ├─ VERIFY_CHECKLIST.md      커밋 전 검증 체크리스트
│   └─ WORKLOG.md               작업 기록 (내가 이해한 것을 적는다)
│
├─ scripts/
│   ├─ verify.sh                검증 스크립트 (ruff + pytest)
│   ├─ ask_ai.py                OpenRouter 로 모델에게 질문하기 (2교시)
│   └─ checkpoint.sh            교시별 완성 예시 가져오기
├─ .githooks/pre-commit       커밋 직전에 검증을 실행하는 스크립트
│
├─ tools/build_guide.py       교안 PDF 를 만드는 스크립트 (md 문서들을 한 권으로 묶는다)
│
├─ checkpoints/               교시별 완성 예시 (막혔을 때 비교·복구용)
│   └─ lesson03 · 04 · 06 · 08 · 09 · 10 · 11(완성본)
│
└─ docs/
    ├─ lessons/                 12교시 안내서
    ├─ commands.md, glossary.md, troubleshooting.md
    └─ 하네스_엔지니어링_입문_학습교안.pdf
```

`app/` 과 `tests/` 는 **거의 비어 있는 상태에서 시작**한다. 교시를 따라가며 AI 에이전트와 함께 채운다.
완성된 모습을 먼저 보고 싶으면 `checkpoints/lesson11/` 을 본다. 실습이 막히면 `sh scripts/checkpoint.sh 08` 처럼 그 교시의 완성 예시를 가져올 수 있다.

---

## 8. 사용 도구와 선택 이유

| 도구 | 역할 | 이 도구를 고른 이유 |
|---|---|---|
| **Docker Desktop** | 모든 도구를 컨테이너로 실행 | PC 마다 다른 설치 문제를 없앤다. AI 에이전트를 PC 가 아닌 컨테이너 안에 가둬 둘 수 있다. |
| **OpenRouter** | 여러 회사의 AI 모델을 하나의 주소·하나의 키로 부르는 서비스 | 키 하나로 모델을 바꿔 가며 쓸 수 있다. 키마다 사용 한도를 걸 수 있어 수업에 안전하다. |
| **OpenCode** | AI 에이전트 (파일을 읽고 고치고 명령을 실행하는 프로그램) | ① OpenRouter 를 기본 지원한다(환경 변수 `OPENROUTER_API_KEY`). ② 프로젝트의 `AGENTS.md` 를 자동으로 읽는다. ③ 설정 파일의 `permissions` 로 allow / ask / deny 를 정할 수 있다 — 하네스의 "규칙"과 "권한"을 파일로 보여 주기에 알맞다. ④ 터미널 프로그램이라 컨테이너 안에서 실행된다. |
| **FastAPI** | 웹 API 프레임워크 | 코드가 짧고, `/docs` 화면에서 바로 API 를 눌러 볼 수 있다. |
| **PostgreSQL + psycopg** | 데이터베이스와 파이썬 드라이버 | ORM 없이 SQL 을 직접 쓴다. 7교시에 배운 SQL 이 코드에 그대로 보여서 AI 가 쓴 코드를 읽을 수 있다. |
| **pytest + ruff** | 자동 테스트와 코드 검사 | "다 됐다"를 말이 아니라 명령 한 줄의 결과로 판단한다. |
| **Git + GitHub** | 변경 기록과 저장 | AI 가 바꾼 내용을 `git diff` 로 읽고, 검증을 통과한 것만 저장한다. |

버전은 `Dockerfile`(OpenCode 2.2.6, Python 3.12), `docker-compose.yml`(PostgreSQL 17), `requirements.txt` 에 고정해 두었다.
기본 모델은 OpenRouter 의 `anthropic/claude-haiku-5.5` 다. 바꾸는 방법은 2교시에 있다.

---

## 9. 이 교안의 명령과 결과에 대하여

- API 응답(JSON), `pytest`·`ruff` 결과, SQL 실행 결과는 **실제로 실행해서 나온 것**을 실었다.
  교시별 완성 예시(`checkpoints/`)의 코드를 실제 PostgreSQL 에 연결해 실행한 결과다.
- 시각(`created_at` 등)과 실행 시간(`in 0.08s`)은 실행할 때마다 달라진다.
- **AI 의 답변과 AI 가 만든 코드는 실을 수 없다.** 같은 지시에도 매번 다르게 나오기 때문이다.
  그래서 이 교안은 "AI 가 이렇게 답한다" 대신 **"결과가 이 조건을 만족하는지 이렇게 확인한다"** 를 적는다. 이것이 하네스 엔지니어링의 사고방식이기도 하다.
- Docker 명령의 화면 출력과 OpenCode 의 화면 모양은 버전에 따라 조금씩 다를 수 있어, 화면을 그대로 싣는 대신 **무엇을 확인해야 하는지**를 글로 적었다.

---

## 10. 만든 사람

강사 김대철 · 수업용 실습 저장소. 수업·학습 목적으로 자유롭게 사용할 수 있다.
