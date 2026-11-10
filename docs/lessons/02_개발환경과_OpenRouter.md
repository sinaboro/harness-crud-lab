# 2교시. 개발환경 및 OpenRouter 연결

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | AI 모델 호출 성공 |
| 필요한 것 | Windows PC, 인터넷, OpenRouter 계정(결제 수단) |

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
                    └─ 이번 교시: AI 를 부를 수 있게 하고, 하네스의 "도구"와 "실행 환경"을 세운다
```

## 학습 목표

1. Docker Desktop, Git, 편집기를 설치하고 저장소를 `C:\harness-crud-lab` 에 내려받는다.
2. 컨테이너, 이미지, 바인드 마운트가 무엇인지 설명하고 직접 확인한다.
3. OpenRouter API 키를 발급받아 `.env` 에 넣고, 키가 Git 에 올라가지 않는 이유를 설명한다.
4. 스크립트(`ask_ai.py`)와 에이전트(OpenCode)로 AI 모델을 한 번씩 불러 본다.

## 명령 앞의 표시

이 과정에서는 명령을 치는 곳이 세 군데다. 명령 블록 위에 어디에서 치는지 표시한다.

| 표시 | 어디 | 프롬프트 모양 |
|---|---|---|
| **[PS]** | 윈도우의 PowerShell | `PS C:\harness-crud-lab>` |
| **[dev]** | dev 컨테이너 안의 셸 | `root@…:/workspace#` |
| **[AI]** | OpenCode 의 입력 칸 | (OpenCode 화면) |

---

## 1. 개념

### 왜 Docker 로 하는가

Python, PostgreSQL, AI 에이전트를 PC 에 직접 설치하면 PC 마다 버전과 경로가 달라서 "제 화면은 달라요"가 끝없이 나온다.
**Docker** 는 프로그램과 그 실행 환경을 통째로 상자에 담아 실행하는 도구다.

| 낱말 | 뜻 | 비유 |
|---|---|---|
| 이미지 | 프로그램과 실행 환경을 담아 둔 틀. 바뀌지 않는다. | 붕어빵 틀 |
| 컨테이너 | 이미지로 만들어 실제로 돌아가는 것. 지우고 다시 만들 수 있다. | 붕어빵 |
| Dockerfile | 이미지를 만드는 순서를 적은 파일 | 틀의 설계도 |
| docker-compose.yml | 컨테이너 여러 개를 한꺼번에 켜는 방법을 적은 파일 | 가게 차림표 |

하네스 관점에서 Docker 는 한 가지 일을 더 한다. **AI 에이전트를 컨테이너 안에 가둔다.**
에이전트는 컨테이너 안에서 실행되므로, 내 PC 의 문서 폴더나 다른 프로젝트를 볼 수도 고칠 수도 없다. 볼 수 있는 것은 우리가 연결해 준 폴더 하나뿐이다.

### 컨테이너 3개

| 이름 | 하는 일 | 접속 |
|---|---|---|
| `db` | PostgreSQL 데이터베이스 | 다른 컨테이너에서 `db:5432` |
| `app` | FastAPI 서버 | 브라우저에서 `http://localhost:8000` |
| `dev` | 작업실. pytest, git, OpenCode 를 여기서 실행한다 | `docker compose exec dev bash` |

`app` 과 `dev` 는 같은 이미지(도구 상자)로 만든다. 하나는 서버를 켜 두는 데 쓰고, 하나는 우리가 들어가서 명령을 치는 데 쓴다.

### 바인드 마운트 — C 드라이브 폴더를 컨테이너에 연결하기

컨테이너는 지우면 안에 있던 파일도 사라진다. 그래서 **남겨야 하는 것은 내 PC 의 폴더에 두고, 그 폴더를 컨테이너에 연결**한다. 이것이 바인드 마운트다. 복사가 아니다. 같은 폴더를 양쪽에서 함께 본다.

`docker-compose.yml` 에서 해당하는 줄:

```yaml
  app:
    volumes:
      - .:/workspace                               # 이 파일이 있는 폴더(C:\harness-crud-lab) ↔ 컨테이너의 /workspace
  db:
    volumes:
      - ./data/postgres:/var/lib/postgresql/data   # C:\harness-crud-lab\data\postgres ↔ DB 데이터 폴더
```

`왼쪽:오른쪽` 에서 왼쪽이 내 PC, 오른쪽이 컨테이너다. 맨 앞의 `.` 은 "`docker-compose.yml` 이 있는 폴더"를 뜻한다. 저장소를 `C:\harness-crud-lab` 에 두었으므로 `.` 은 곧 `C:\harness-crud-lab` 이다.

| 연결 | 덕분에 되는 일 |
|---|---|
| `C:\harness-crud-lab` ↔ `/workspace` | 윈도우 편집기로 고친 파일이 컨테이너에 바로 보인다. AI 가 컨테이너에서 고친 파일이 내 편집기에 바로 보인다. |
| `C:\harness-crud-lab\data\postgres` ↔ DB 데이터 폴더 | 컨테이너를 지우고 다시 만들어도 메모가 남는다. |

### OpenRouter 와 API 키

**OpenRouter** 는 여러 회사의 AI 모델을 주소 하나, 키 하나로 부를 수 있게 해 주는 중개 서비스다. 모델 이름만 바꾸면 다른 회사의 모델을 쓸 수 있다.

**API 키**는 "이 요청은 내 계정에서 보낸 것"임을 증명하는 긴 문자열이다(`sk-or-v1-…`). 키를 가진 사람은 누구나 내 돈으로 모델을 쓸 수 있다. **비밀번호와 똑같이 다룬다.**

- 키는 `.env` 파일에만 적는다.
- `.env` 는 `.gitignore` 에 들어 있어 Git 이 무시한다. GitHub 에 올라가지 않는다.
- 저장소에는 값이 비어 있는 견본 `.env.example` 만 올라간다.
- 키를 채팅방, 화면 공유, 캡처 이미지에 노출하지 않는다. 노출했으면 OpenRouter 에서 그 키를 지우고 새로 만든다.

키가 전달되는 길:

```text
 .env 파일  →  docker-compose.yml 의 ${OPENROUTER_API_KEY}  →  dev 컨테이너의 환경 변수  →  ask_ai.py / OpenCode
```

---

## 따라 하기

### 1단계. 프로그램 세 개 설치 (25분)

이미 설치되어 있으면 건너뛴다.

**(1) Docker Desktop**

1. https://www.docker.com/products/docker-desktop/ 에서 Windows 용 설치 파일을 받아 실행한다.
2. 설치 중 "Use WSL 2 instead of Hyper-V" 가 보이면 체크된 채로 둔다.
3. 설치가 끝나면 PC 를 다시 시작하라고 할 수 있다. 다시 시작한다.
4. 시작 메뉴에서 Docker Desktop 을 실행한다. 약관 동의 화면이 나오면 동의한다. 로그인은 건너뛰어도 된다.
5. 화면 왼쪽 아래의 표시가 "Engine running" 이 될 때까지 기다린다.

**(2) Git for Windows**

https://git-scm.com/download/win 에서 받아 설치한다. 설치 화면의 선택지는 모두 기본값으로 둔다.

**(3) VS Code**

https://code.visualstudio.com/ 에서 받아 설치한다. 다른 편집기를 써도 된다.

**확인.** 시작 메뉴에서 "PowerShell" 을 찾아 실행하고 아래 세 명령을 친다.

**[PS]**

```powershell
docker --version
docker compose version
git --version
```

세 명령 모두 버전 번호가 한 줄씩 나오면 된다. "인식되지 않습니다"라는 말이 나오면 PowerShell 창을 닫고 새로 연 뒤 다시 해 본다. 그래도 안 되면 그 프로그램을 다시 설치한다.

### 2단계. 저장소를 C 드라이브에 내려받기 (5분)

**[PS]**

```powershell
git clone https://github.com/sinaboro/harness-crud-lab.git C:\harness-crud-lab
cd C:\harness-crud-lab
dir
```

**확인.** `dir` 결과에 `README.md`, `Dockerfile`, `docker-compose.yml`, `app`, `harness` 가 보인다.

경로는 반드시 `C:\harness-crud-lab` 으로 한다. 바탕 화면이나 문서 폴더에 두면 경로에 한글·공백이 들어가거나 OneDrive 동기화와 겹쳐서 문제가 생길 수 있다.

VS Code 로 폴더를 연다.

**[PS]**

```powershell
code C:\harness-crud-lab
```

### 3단계. OpenRouter 키 발급 (15분)

1. https://openrouter.ai/ 에 접속해 가입(Sign up)한다.
2. 오른쪽 위 계정 메뉴에서 **Credits** 로 들어가 크레딧을 충전한다. 최소 금액이면 이 과정에 충분하다.
3. 계정 메뉴에서 **Keys** 로 들어가 **Create Key** 를 누른다.
   - 이름: `harness-crud-lab`
   - Credit limit(이 키로 쓸 수 있는 최대 금액)을 작게 정해 둔다. 키가 새어 나가도 피해가 그 금액으로 제한된다.
4. 만들어진 키(`sk-or-v1-` 로 시작)를 복사한다. **이 화면을 닫으면 다시 볼 수 없다.**

> **요금.** OpenRouter 는 쓴 만큼 낸다. 요금은 "토큰"(AI 가 글을 세는 단위) 수로 계산한다.
> 이 과정의 기본 모델 `anthropic/claude-haiku-5.5` 는 2026년 11월 기준 입력 100만 토큰에 0.10달러, 출력 100만 토큰에 0.50달러다. 최신 가격은 https://openrouter.ai/models 에서 확인한다.
> 이름이 `:free` 로 끝나는 무료 모델도 있다. 다만 하루 요청 횟수 제한이 있어(크레딧을 충전하지 않은 계정은 하루 50회) 요청을 여러 번 주고받는 에이전트 실습에는 모자란다.

### 4단계. `.env` 만들기 (5분)

**[PS]**

```powershell
Copy-Item .env.example .env
notepad .env
```

메모장에서 `OPENROUTER_API_KEY=` 뒤에 복사한 키를 붙여 넣고 저장한다. 등호 앞뒤에 공백을 넣지 않는다. 따옴표도 넣지 않는다.

```text
OPENROUTER_API_KEY=sk-or-v1-여기에_내_키
```

**확인.** Git 이 `.env` 를 무시하는지 본다.

**[PS]**

```powershell
git status
```

`nothing to commit, working tree clean` 이 나와야 한다. 방금 `.env` 라는 새 파일을 만들었는데도 Git 은 "바뀐 것이 없다"고 한다. `.gitignore` 에 `.env` 가 적혀 있기 때문이다.

**[PS]**

```powershell
git check-ignore -v .env
```

`.gitignore` 의 몇 번째 줄 때문에 무시되는지 알려 준다.

### 5단계. 컨테이너 만들고 켜기 (15분)

**[PS]**

```powershell
docker compose up -d --build
```

- `up`: 컨테이너를 만들고 켠다.
- `-d`: 뒤에서 돌게 한다(명령 창을 돌려받는다).
- `--build`: `Dockerfile` 로 이미지를 만든다.

처음에는 Python 이미지와 PostgreSQL 이미지를 내려받고 패키지를 설치하느라 몇 분 걸린다. 두 번째부터는 금방 끝난다.

**확인 1.** 컨테이너 상태를 본다.

**[PS]**

```powershell
docker compose ps
```

세 줄(`db`, `app`, `dev`)이 나온다. `STATUS` 칸이 `db` 는 `Up … (healthy)`, `app` 과 `dev` 는 `Up …` 이면 된다.
`db` 가 `healthy` 가 아니면 아래 "자주 만나는 오류"의 첫 항목을 본다.

**확인 2.** 브라우저에서 http://localhost:8000/health 를 연다.

```json
{"status":"ok"}
```

FastAPI 서버가 컨테이너 안에서 돌고 있고, 내 PC 의 브라우저에서 거기에 접속한 것이다.

### 6단계. 바인드 마운트 직접 확인하기 (15분)

**(1) 윈도우 → 컨테이너.** 윈도우에서 파일을 만들고 컨테이너에서 읽는다.

**[PS]**

```powershell
Set-Content C:\harness-crud-lab\from_windows.txt "made on windows"
docker compose exec dev cat /workspace/from_windows.txt
```

`made on windows` 가 출력된다. 컨테이너로 복사한 적이 없는데 컨테이너 안에 있다.

**(2) 컨테이너 → 윈도우.** 컨테이너에서 파일을 만들고 윈도우에서 읽는다.

**[PS]**

```powershell
docker compose exec dev sh -c "echo made in container > /workspace/from_container.txt"
Get-Content C:\harness-crud-lab\from_container.txt
```

`made in container` 가 출력된다. VS Code 의 파일 목록에도 두 파일이 나타나 있다.

**(3) 연결 정보 보기.**

**[PS]**

```powershell
docker inspect harness-crud-lab-dev-1 --format "{{ json .Mounts }}"
```

출력에서 `"Type":"bind"` 와 `"Destination":"/workspace"` 를 찾는다. `"Source"` 에는 내 PC 쪽 경로가 적혀 있다(`harness-crud-lab` 으로 끝난다).

**(4) DB 데이터 폴더 보기.**

**[PS]**

```powershell
dir C:\harness-crud-lab\data\postgres
```

`PG_VERSION`, `base`, `global` 같은 파일과 폴더가 보인다. PostgreSQL 이 컨테이너 안에서 쓴 데이터가 C 드라이브에 놓여 있는 것이다. 이 폴더의 파일은 직접 열거나 고치지 않는다.

**(5) 뒷정리.**

**[PS]**

```powershell
Remove-Item C:\harness-crud-lab\from_windows.txt, C:\harness-crud-lab\from_container.txt
git status
```

`working tree clean` 이 나오면 원래대로 돌아온 것이다.

### 7단계. 작업실에 들어가기 (5분)

**[PS]**

```powershell
docker compose exec dev bash
```

프롬프트가 `root@(영문·숫자):/workspace#` 로 바뀐다. 이제 컨테이너 안이다. 여기서 치는 명령은 **[dev]** 로 표시한다.

**[dev]**

```bash
pwd
ls
python --version
pytest --version
opencode --version
```

- `pwd` → `/workspace`
- `ls` → 윈도우의 `C:\harness-crud-lab` 과 같은 파일 목록
- 나머지 세 줄 → 각 도구의 버전. 이 도구들은 내 PC 가 아니라 컨테이너 안에만 있다.

나갈 때는 `exit` 를 친다. 다시 들어올 때는 **[PS]** 에서 `docker compose exec dev bash` 를 친다.
지금은 나가지 말고 이어서 한다.

### 8단계. AI 모델 불러 보기 — 스크립트 (15분)

키가 컨테이너에 전달되었는지 먼저 본다. 키 전체를 화면에 찍지 않도록 글자 수만 센다.

**[dev]**

```bash
echo ${#OPENROUTER_API_KEY}
```

`0` 이 아닌 숫자가 나오면 전달된 것이다. `0` 이면 "자주 만나는 오류"를 본다.

모델에게 질문한다.

**[dev]**

```bash
python scripts/ask_ai.py "FastAPI 가 뭐야? 두 문장으로 알려 줘"
```

**기대 결과.** 세 부분이 출력된다.

```text
[모델] (실제로 답한 모델 이름)
[답변]
(AI 의 답. 실행할 때마다 다르다)
[사용량] 보낸 토큰 (숫자) / 받은 토큰 (숫자)
```

같은 명령을 한 번 더 실행해 본다. 답이 조금 다르게 나온다. **AI 의 출력은 매번 다르다.** 이것이 "돌아가는 것 같다"를 기준으로 삼을 수 없는 이유이고, 4교시부터 "검증"을 따로 두는 이유다.

`scripts/ask_ai.py` 를 VS Code 로 열어 본다. 주석을 따라 읽으면서 아래 세 가지를 찾는다.

1. 요청을 보내는 주소(`API_URL`)
2. 키를 어디에서 읽는가 (`os.environ`)
3. 답은 응답의 어느 부분에 들어 있는가 (`choices` …)

파일을 함께 보내서 질문할 수도 있다.

**[dev]**

```bash
python scripts/ask_ai.py --file app/main.py "이 코드가 하는 일을 초보자에게 세 문장으로 설명해 줘"
```

키가 틀렸을 때 무슨 일이 생기는지도 일부러 본다.

**[dev]**

```bash
OPENROUTER_API_KEY=sk-or-v1-invalid python scripts/ask_ai.py "안녕"
```

```text
[실패] 상태 코드 401: API 키가 틀렸습니다. .env 의 OPENROUTER_API_KEY 값을 확인하세요.
{"error":{"message":"User not found.","code":401}}
```

`401` 은 "누구인지 확인할 수 없음"이라는 뜻의 상태 코드다. 상태 코드는 4교시에 배운다.

### 9단계. AI 모델 불러 보기 — 에이전트 (15분)

이번에는 에이전트 OpenCode 로 같은 모델을 부른다. 어떤 모델을 쓸지는 `opencode.jsonc` 에 적혀 있다.

**[dev]**

```bash
cat opencode.jsonc
```

`"model": "openrouter/anthropic/claude-haiku-5.5"` 한 줄을 찾는다. `openrouter/` 뒤가 OpenRouter 의 모델 이름이다.

질문 하나를 던지고 답만 받아 본다.

**[dev]**

```bash
opencode run "이 폴더에 어떤 파일들이 있는지 살펴보고, 무엇을 하는 프로젝트인지 세 줄로 요약해 줘"
```

**관찰.** 8단계의 스크립트와 무엇이 다른가?

- 스크립트는 우리가 `--file` 로 준 파일 하나만 알았다.
- 에이전트는 **스스로 폴더를 살펴보고 파일을 골라 읽은 뒤** 답했다. 파일 이름을 알려 주지 않았는데도.

이것이 모델과 에이전트의 차이다. 에이전트에게는 "손과 눈"(파일 읽기, 명령 실행)이 있다.

대화 화면으로도 열어 본다.

**[dev]**

```bash
opencode
```

화면 아래 입력 칸에 다음을 치고 Enter 를 누른다.

**[AI]**

```text
안녕. 너는 지금 어떤 폴더에서 실행되고 있어? 파일을 고치지는 말고 대답만 해 줘.
```

답을 확인한 뒤 `/exit` 를 쳐서 나온다.

| OpenCode 에서 쓰는 명령 | 하는 일 |
|---|---|
| `/exit` | OpenCode 를 끝낸다 |
| `/new` | 새 대화를 시작한다 (앞의 대화를 잊는다) |
| `/undo` | 마지막 요청과, 그 요청으로 바뀐 파일을 되돌린다 |
| `/models` | 쓸 수 있는 모델 목록을 본다 |
| `@파일이름` | 그 파일을 대화에 첨부한다 |

> 지금 OpenCode 에는 **규칙도 권한 제한도 없다.** 파일을 고치라고 하면 묻지 않고 고친다.
> 그래서 4교시까지는 OpenCode 에게 "설명해 줘"만 시키고, 고치는 일은 5교시에 하네스를 세운 뒤에 시킨다.

### 10단계. Git 에 내 이름 알려 주기 (5분)

커밋에는 "누가 저장했는지"가 기록된다. 이 저장소에서 쓸 이름과 메일을 정한다.

**[dev]**

```bash
git config user.name "홍길동"
git config user.email "gildong@example.com"
git config user.name
```

자기 이름과 메일로 바꿔 친다. 마지막 명령이 방금 넣은 이름을 출력하면 된다.
이 설정은 `C:\harness-crud-lab\.git\config` 에 저장되므로 컨테이너를 다시 만들어도 남는다.

---

## 하루를 마칠 때와 다시 시작할 때

**[PS]**

```powershell
docker compose stop      # 컨테이너를 멈춘다 (지우지 않는다)
docker compose start     # 멈춘 컨테이너를 다시 켠다
```

PC 를 껐다 켠 뒤에는 Docker Desktop 을 먼저 실행하고, `C:\harness-crud-lab` 에서 `docker compose up -d` 를 친다.
자주 쓰는 명령은 [`docs/commands.md`](../commands.md) 에 모아 두었다.

## 하네스 관점 — 이번 교시에서 세운 것

| 요소 | 이번 교시에 한 일 |
|---|---|
| 도구 | Python·pytest·ruff·git·OpenCode 가 든 도구 상자(이미지)를 만들었다. 버전이 고정되어 있어 모두가 같은 도구를 쓴다. |
| 실행 | 에이전트는 dev 컨테이너 안에서 돈다. 내 PC 에서 에이전트에게 보이는 것은 `C:\harness-crud-lab` 하나뿐이다. |
| 권한 (일부) | API 키는 `.env` 에만 있고 Git 에 올라가지 않는다. 키에 사용 한도를 걸었다. |
| 규칙·검증 | **아직 없다.** 5교시에 세운다. |

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `docker compose ps` 에서 `db` 가 계속 `starting` 이거나 `unhealthy`, 또는 사라짐 | **[PS]** `docker compose logs db` 로 마지막 20줄을 읽는다. `Operation not permitted`, `wrong ownership`, `could not change permissions` 가 보이면 윈도우 폴더의 권한 문제다. [`docs/troubleshooting.md`](../troubleshooting.md) 의 "DB 가 켜지지 않는다"를 따라 예비 설정으로 바꾼다. |
| `error during connect … docker_engine` | Docker Desktop 이 실행 중이 아니다. 시작 메뉴에서 실행하고 "Engine running" 을 기다린다. |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | 8000 번 포트를 다른 프로그램이 쓰고 있다. 그 프로그램을 끄거나, `docker-compose.yml` 의 `"8000:8000"` 을 `"8001:8000"` 으로 바꾸고 `http://localhost:8001` 로 접속한다. |
| `echo ${#OPENROUTER_API_KEY}` 가 `0` | `.env` 를 고친 뒤 컨테이너를 다시 만들지 않았다. **[PS]** `docker compose up -d` 를 실행하고(바뀐 설정이 있으면 컨테이너를 다시 만든다) dev 에 다시 들어간다. 파일 이름이 `.env.txt` 로 저장되지 않았는지도 확인한다. |
| `ask_ai.py` 가 `401` | 키를 잘못 붙여 넣었다. 앞뒤 공백, 따옴표, 빠진 글자를 확인한다. |
| `ask_ai.py` 가 `402` | 크레딧이 없거나 키의 한도를 다 썼다. OpenRouter 의 Credits·Keys 화면을 확인한다. |
| `docker compose up` 중 OpenCode 설치 단계에서 실패 | 인터넷 연결이나 보안 프로그램이 내려받기를 막은 경우다. 다시 실행해 본다. 계속 실패하면 강사에게 알린다. |
| `http://localhost:8000` 이 열리지 않는다 | **[PS]** `docker compose logs app` 을 읽는다. 마지막 줄에 `Uvicorn running on http://0.0.0.0:8000` 이 있어야 한다. |

## 확인 문제

1. 이미지와 컨테이너의 관계를 붕어빵 말고 다른 비유로 설명하시오.
2. `docker-compose.yml` 의 `- .:/workspace` 에서 `.` 은 내 PC 의 어느 폴더인가? 그렇게 판단한 근거는?
3. 컨테이너를 지웠다가 다시 만들어도 메모 데이터가 남는 이유를 "바인드 마운트"라는 낱말을 써서 설명하시오.
4. `.env` 와 `.env.example` 은 각각 Git 에 올라가는가? 왜 두 파일로 나누었는가?
5. API 키가 `.env` 에서 `ask_ai.py` 까지 전달되는 길을 순서대로 쓰시오.
6. 8단계(스크립트)와 9단계(에이전트)에서 AI 가 파일 내용을 알게 된 방법은 어떻게 달랐는가?
7. 에이전트를 내 PC 에 직접 설치하지 않고 컨테이너 안에서 실행하면 무엇이 안전해지는가?

## 다음 교시

[3교시. Python·FastAPI 기본 이해](03_Python_FastAPI_기본.md) — 서버 코드를 읽고, `/hello` 주소를 직접 만든다.
