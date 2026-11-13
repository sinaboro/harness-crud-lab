# 오류 해결 모음

교시별 안내서의 "자주 만나는 오류"를 한곳에 모으고, 길게 설명해야 하는 것을 더했다.

## 먼저 할 일 — 오류를 읽는 순서

1. **어디에서 난 오류인가?** 명령을 친 곳이 [PS] 인가 [dev] 인가. 틀린 곳에서 치면 `command not found` 가 난다.
2. **오류 메시지의 마지막 줄을 읽는다.** 원인은 대부분 맨 아래에 있다.
3. **로그를 본다.** 서버 문제는 `docker compose logs app --tail 30`, DB 문제는 `docker compose logs db --tail 30`.
4. **바꾼 것을 되돌려 본다.** `git status` 로 무엇을 바꿨는지 보고, 방금 바꾼 것이 원인인지 확인한다.
5. 그래도 모르면 **오류 전체를 붙여서** AI 나 강사에게 묻는다. "안 돼요"가 아니라 "이 명령을 쳤더니 이 출력이 나왔다".

---

## 1. DB 가 켜지지 않는다 (가장 중요)

**증상.** `docker compose ps` 에서 `db` 가 `healthy` 가 되지 않거나 목록에서 사라진다. `app`, `dev` 도 켜지지 않는다(DB 를 기다리기 때문이다).

**확인.**

**[PS]**

```powershell
docker compose logs db --tail 30
```

### 경우 A — 윈도우 폴더의 권한 문제

로그에 아래와 비슷한 문구가 보인다.

```text
chmod: changing permissions of '/var/lib/postgresql/data': Operation not permitted
FATAL:  data directory "/var/lib/postgresql/data" has wrong ownership
initdb: error: could not change permissions of directory
```

**원인.** 이 과정은 DB 데이터를 C 드라이브 폴더(`data\postgres`)에 바인드 마운트한다. PostgreSQL 은 데이터 폴더의 소유자와 권한을 엄격하게 검사하는데, PC 의 Docker 설정에 따라 윈도우 폴더에서는 그 검사를 통과하지 못할 수 있다.

**해결.** 예비 설정으로 바꾼다. DB 데이터를 Docker 가 관리하는 저장 공간(이름 있는 볼륨)에 둔다.

> ※ 아래 명령의 `Remove-Item` 은 데이터 폴더를 지운다. 그 안의 메모도 함께 사라진다. 8교시 전이라면 괜찮다. 메모를 지키고 싶다면 이 방법을 쓰기 전에 강사에게 먼저 묻는다.

**[PS]**

```powershell
docker compose down
Remove-Item -Recurse -Force .\data\postgres
docker compose -f docker-compose.yml -f docker-compose.volume.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.volume.yml ps
```

`-f` 를 매번 치지 않으려면 `.env` 맨 아래에 한 줄을 추가한다. 그러면 `docker compose up -d` 만 쳐도 두 파일이 함께 쓰인다.

```text
COMPOSE_FILE=docker-compose.yml;docker-compose.volume.yml
```

(윈도우에서는 두 파일 이름을 세미콜론 `;` 으로 나눈다.)

**달라지는 점.**

| | 기본 설정 (바인드 마운트) | 예비 설정 (이름 있는 볼륨) |
|---|---|---|
| 데이터가 놓이는 곳 | `C:\harness-crud-lab\data\postgres` | Docker 내부의 볼륨 `harness-crud-lab_pgdata` |
| 탐색기에서 보이는가 | 보인다 | 보이지 않는다 |
| `docker compose down` 뒤에 남는가 | 남는다 | 남는다 |
| 완전히 지우려면 | 폴더를 지운다 | `docker compose down -v` |

소스 폴더(`C:\harness-crud-lab` ↔ `/workspace`)의 바인드 마운트는 그대로다. 7교시의 "컨테이너를 지워도 데이터가 남는다" 확인도 그대로 할 수 있다. 데이터 폴더의 파일을 세는 부분만 건너뛴다.

볼륨이 있는지 보는 명령:

**[PS]**

```powershell
docker volume ls
```

### 경우 B — 데이터 폴더가 반쯤 만들어진 채 남았다

로그에 `directory "/var/lib/postgresql/data" exists but is not empty` 가 보인다. 처음 켜다가 중간에 끊긴 경우다.

**[PS]**

```powershell
docker compose down
Remove-Item -Recurse -Force .\data\postgres
docker compose up -d
```

### 경우 C — `.env` 의 계정을 중간에 바꿨다

로그에 `password authentication failed` 또는 `role "…" does not exist` 가 보인다. DB 계정은 **데이터 폴더를 처음 만들 때 한 번만** 정해진다. 그 뒤에 `.env` 의 `POSTGRES_USER`·`POSTGRES_PASSWORD` 를 바꿔도 반영되지 않는다.

`.env` 의 값을 처음 값(`memo` / `memo1234`)으로 되돌린다. 계정을 꼭 바꿔야 하면 경우 B 처럼 데이터 폴더를 지우고 새로 만든다(메모가 모두 사라진다).

---

## 2. Docker

| 증상 | 원인과 해결 |
|---|---|
| `docker : 용어가 … 인식되지 않습니다` | Docker Desktop 이 설치되지 않았거나, 설치 뒤 PowerShell 을 새로 열지 않았다. |
| `error during connect … docker_engine … cannot find the file` | Docker Desktop 이 실행 중이 아니다. 시작 메뉴에서 실행하고 "Engine running" 을 기다린다. |
| Docker Desktop 이 `WSL update` 를 요구한다 | 관리자 PowerShell 에서 `wsl --update` 를 실행하고 PC 를 다시 시작한다. |
| `port is already allocated` (8000) | 다른 프로그램이 8000 번을 쓴다. 그 프로그램을 끄거나 `docker-compose.yml` 의 `"8000:8000"` 을 `"8001:8000"` 으로 바꾼다(브라우저 주소도 8001). |
| `no configuration file provided: not found` | `docker-compose.yml` 이 없는 폴더에서 쳤다. `cd C:\harness-crud-lab` 을 먼저 한다. |
| 빌드 중 OpenCode 설치 단계에서 실패 | 인터넷이나 보안 프로그램이 내려받기를 막았다. `docker compose build --no-cache` 로 다시 해 본다. |
| 빌드가 매우 느리다 | 처음 한 번은 이미지를 내려받느라 몇 분 걸린다. 두 번째부터는 빠르다. |
| `service "dev" is not running` | 컨테이너가 꺼져 있다. `docker compose up -d` 뒤 `docker compose ps`. |
| 디스크가 부족하다 | 쓰지 않는 이미지를 지운다: `docker image prune`. |

## 3. 파일이 반영되지 않는다 (바인드 마운트)

| 증상 | 원인과 해결 |
|---|---|
| 윈도우에서 고친 파일이 컨테이너에서 그대로다 | 저장하지 않았다(VS Code 탭의 흰 점). 또는 `C:\harness-crud-lab` 이 아닌 다른 사본을 고치고 있다. VS Code 창의 제목에서 폴더 경로를 확인한다. |
| 파일을 고쳤는데 서버가 다시 켜지지 않는다 | `app` 폴더 밖의 파일은 서버가 살펴보지 않는다. `app` 안의 파일인데도 그렇다면 `docker compose restart app`. |
| `/workspace` 가 비어 있다 | `docker compose` 를 다른 폴더에서 실행했다. `docker inspect harness-crud-lab-dev-1 --format "{{ json .Mounts }}"` 의 `Source` 를 확인한다. |
| `.sh` 스크립트가 `not found` 또는 `\r` 오류를 낸다 | 줄바꿈이 윈도우 방식(CRLF)으로 바뀌었다. `.gitattributes` 가 있는지 확인하고, VS Code 오른쪽 아래의 `CRLF` 를 눌러 `LF` 로 바꾼 뒤 저장한다. |
| 저장소를 OneDrive·바탕 화면 아래에 두었다 | 동기화 프로그램과 겹쳐 파일이 잠기거나 느려진다. `C:\harness-crud-lab` 으로 옮긴다. |

## 4. OpenRouter 와 OpenCode

| 증상 | 원인과 해결 |
|---|---|
| `echo ${#OPENROUTER_API_KEY}` 가 `0` | `.env` 를 고친 뒤 컨테이너를 다시 만들지 않았다. **[PS]** `docker compose up -d` 뒤 dev 에 다시 들어간다. 파일 이름이 `.env.txt` 가 아닌지, 등호 앞뒤에 공백이 없는지 본다. |
| `401` | 키가 틀렸다. 앞뒤 공백, 따옴표, 빠진 글자를 본다. 키를 지웠다면 새로 만든다. |
| `402` | 크레딧이 없거나 키의 한도를 다 썼다. OpenRouter 의 Credits·Keys 화면을 본다. |
| `404` (모델) | 모델 이름이 틀렸거나 없어졌다. https://openrouter.ai/models 에서 이름을 확인한다. |
| `429` | 요청이 너무 잦다. 잠시 뒤 다시 한다. `:free` 모델은 하루 한도가 작다. |
| OpenCode 가 모델을 찾지 못한다 | `opencode.jsonc` 의 `"model"` 이 `openrouter/` 로 시작하는지 본다. OpenCode 안에서 `/models` 로 목록을 본다. |
| OpenCode 가 설정 오류를 낸다 | `opencode.jsonc` 의 쉼표·중괄호가 깨졌다. `cp harness/opencode.jsonc opencode.jsonc` 로 다시 가져온다. |
| OpenCode 가 `AGENTS.md` 를 따르지 않는 것 같다 | 파일이 맨 위 폴더에 있는지 본다. OpenCode 는 시작할 때 읽으므로 `/exit` 뒤 다시 연다. 대화가 길어졌으면 `/new` 로 새로 시작한다. |
| 권한 규칙이 기대대로 막지 않는다 | 설정을 바꾼 뒤 OpenCode 를 다시 열었는지 본다. 그래도 그대로면 강사에게 알린다. 규칙의 `resource` 무늬가 맞지 않는 경우다. |
| AI 의 답이 중간에 끊긴다 | 네트워크나 사용 한도 문제다. 같은 요청을 다시 보낸다. |
| OpenCode 화면의 글자가 깨진다 | Windows Terminal 을 쓴다(시작 메뉴에서 "터미널"). 창이 너무 작으면 넓힌다. |

**모델을 바꾸려면.** 두 군데를 바꾼다.

- `ask_ai.py` 가 쓰는 모델: `.env` 의 `OPENROUTER_MODEL` → **[PS]** `docker compose up -d`
- OpenCode 가 쓰는 모델: `opencode.jsonc` 의 `"model"` (`openrouter/` 뒤에 모델 이름) → OpenCode 를 다시 연다

## 5. 서버 (FastAPI)

| 증상 | 원인과 해결 |
|---|---|
| 브라우저가 "연결할 수 없음" | 코드 오류로 서버가 켜지지 못했다. `docker compose logs app --tail 30` 에서 `Error` 가 든 줄과 줄 번호를 찾는다. |
| `SyntaxError`, `IndentationError` | 오타나 들여쓰기 문제. 로그가 알려 주는 파일과 줄을 본다. |
| `ModuleNotFoundError: No module named 'app.…'` | 파일 이름이 다르거나 `app/__init__.py` 가 없다. |
| `{"detail":"Not Found"}` (404) | 그 주소에 연결된 함수가 없다. 주소 오타, 저장 안 함. |
| `{"detail":"Method Not Allowed"}` (405) | 주소는 있는데 그 방식의 함수가 없다. |
| 422 | 요청이 허용된 모양이나 규칙에 맞지 않는다. 응답의 `loc` 과 `msg` 를 읽는다. |
| 500 | 서버 코드가 오류를 냈다. `docker compose logs app --tail 30` 의 `Traceback` 마지막 줄을 읽는다. |
| 메모가 자꾸 사라진다 (6교시까지) | 메모리 저장소라서 서버가 다시 켜질 때마다 비워진다. 정상이다. |

## 6. 데이터베이스 연결 (8교시부터)

| 증상 | 원인과 해결 |
|---|---|
| `Name or service not known`, `could not translate host name "db"` | 컨테이너 밖에서 실행했거나, 주소의 호스트를 `localhost` 로 적었다. 컨테이너에서는 `db` 다. |
| `connection refused` | DB 가 꺼져 있다. `docker compose ps` 로 `db` 가 `healthy` 인지 본다. |
| `KeyError: 'DATABASE_URL'` | 환경 변수가 없다. dev 컨테이너 안에서 실행한다. |
| 서버 로그에 "테이블이 없다"는 말 | 서버가 켜질 때 저장 표를 만드는 일이 실행되지 않았다. **[PS]** `docker compose restart app` 후 다시 본다. 계속되면 AI 에게 로그 마지막 줄을 붙여 준다. |
| 테스트가 "테스트용 데이터베이스를 찾을 수 없다"고 한다 | 테스트 전용 데이터베이스 조건(8교시 지시서 5번)이 빠졌다. AI 에게 그 줄을 가리켜 고치게 한다. 직접 고치지 않는다. |
| 서버 로그에 값과 자리 개수가 맞지 않는다는 말 | 저장 코드의 실수다. 로그 마지막 줄을 AI 에게 붙여 준다. 직접 고치지 않는다. |
| 테스트를 돌리면 진짜 메모가 사라진다 | 테스트가 `memo_db` 에서 돈다. `conftest.py` 가 `TEST_DATABASE_URL` 로 바꿔 끼우는지 본다. |

**DB 를 처음 상태로 되돌리려면.** 메모가 모두 사라진다.

**[PS]**

```powershell
docker compose down
Remove-Item -Recurse -Force .\data\postgres
docker compose up -d
```

메모만 비우고 싶다면 위의 방법으로 데이터 폴더를 지우는 것이 가장 확실하다. 지우기 전에 메모를 다시 만들 수 있는지 먼저 생각한다.

## 7. 테스트와 검증

| 증상 | 원인과 해결 |
|---|---|
| `pytest: command not found` | 윈도우에서 쳤다. dev 컨테이너에서 친다. |
| `fixture 'client' not found` | `tests/conftest.py` 가 없거나 `client` 함수가 없다. |
| 따로 돌리면 통과, 함께 돌리면 실패 | 테스트끼리 데이터를 공유한다. `conftest.py` 가 테스트마다 저장소를 비우는지 본다. |
| `ruff` 가 `F401 imported but unused` | 가져오고 쓰지 않은 import 가 있다. 그 줄을 지운다. |
| `ruff` 가 `F821 undefined name` | 정의하지 않은 이름을 썼다. 오타이거나 import 를 빠뜨렸다. |
| `verify.sh` 는 통과하는데 동작이 요구사항과 다르다 | 그 요구사항을 확인하는 테스트가 없다. 테스트를 추가한다(11교시). |

## 8. Git

| 증상 | 원인과 해결 |
|---|---|
| `Please tell me who you are` | 이름·메일을 정하지 않았다. `git config user.name "이름"`, `git config user.email "메일"`. |
| `detected dubious ownership` | 컨테이너의 Git 이 폴더를 믿지 못한다. 이미지에 설정이 들어 있으니 `docker compose up -d --build` 로 다시 만든다. |
| 커밋이 취소된다 | `pre-commit` 이 검증 실패를 잡았다. `[pre-commit]` 위의 출력을 읽고 고친다. |
| 커밋할 때 `[pre-commit]` 이 나오지 않는다 | 훅이 꺼져 있다. `git config core.hooksPath .githooks`. |
| 윈도우에서 커밋하면 훅이 실패한다 | 윈도우에서는 훅이 dev 컨테이너에게 검증을 시킨다. 컨테이너가 켜져 있어야 한다. 커밋은 dev 컨테이너에서 하는 것을 권한다. |
| 아무것도 안 고쳤는데 모든 파일이 바뀐 것으로 나온다 | 줄바꿈 설정이 어긋났다. `.gitattributes` 가 있는지 본다. |
| `git diff` 화면에서 빠져나오지 못한다 | `q` 를 누른다. |
| 실수로 `git restore .` 를 했다 | 커밋하지 않은 변경은 되살릴 수 없다. VS Code 에 파일이 열려 있었다면 Ctrl+Z 를 해 본다. |
| `git push` 가 `403` | `origin` 이 강사 저장소다. 12교시 5단계를 한다. |

## 9. 화면 (10교시부터)

| 증상 | 원인과 해결 |
|---|---|
| 고쳤는데 화면이 그대로다 | 브라우저가 옛 파일을 기억한다. **Ctrl+F5**. |
| 꾸밈이 없고 버튼이 동작하지 않는다 | `app.js`·`style.css` 가 404 다. F12 → Network 에서 확인하고 경로를 본다. |
| 버튼을 눌러도 아무 일이 없다 | F12 → Console 의 빨간 글씨를 읽는다. |
| 저장하면 화면이 깜빡이고 주소에 `?` 가 붙는다 | `event.preventDefault()` 가 없다. |
| 시각이 9시간 어긋난다 | 서버는 세계 표준시로 준다. 화면에서 `toLocaleString("ko-KR")` 로 바꾼다. |

---

## 그래도 안 될 때 — 처음부터 다시

소스는 Git 에, 하네스는 `harness/` 에 있으므로 실행 환경은 언제든 새로 만들 수 있다.

**[PS]**

```powershell
cd C:\harness-crud-lab
docker compose down
docker compose up -d --build
docker compose ps
```

코드가 엉켰으면 그 교시의 시작 상태로 맞춘다. (어느 체크포인트인지는 [`commands.md`](commands.md) 9절의 표를 본다.)

**[dev]**

```bash
sh scripts/checkpoint.sh 08 --force
sh scripts/verify.sh
```
