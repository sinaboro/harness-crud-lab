# 12교시. GitHub 저장 및 발표

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | 최종 프로젝트 (내 GitHub 저장소 + 발표) |
| 시작 상태 | 11교시를 마친 상태 (모든 테스트가 통과하고 커밋되어 있다) |

11교시 결과가 없으면 **[dev]** `sh scripts/checkpoint.sh 11` 로 가져온다.

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
                                                                              └─ Git 에 저장 → GitHub 로
```

## 학습 목표

1. 커밋 기록을 읽고, 프로젝트가 만들어진 과정을 설명한다.
2. 올리면 안 되는 것(`.env`, DB 데이터)이 빠져 있는지 확인한다.
3. 내 GitHub 저장소를 만들어 결과물을 올린다(push).
4. 저장소를 새로 내려받아, 다른 사람이 따라 할 수 있는지 확인한다.
5. 작업 기록을 바탕으로 "AI 에게 맡기고 내가 통제한 과정"을 발표한다.

---

## 1. 개념

### 커밋과 푸시

| | 하는 일 | 어디에 저장되는가 |
|---|---|---|
| 커밋(commit) | 지금 상태를 기록으로 남긴다 | 내 PC (`C:\harness-crud-lab\.git`) |
| 푸시(push) | 내 PC 의 커밋을 인터넷의 저장소로 보낸다 | GitHub |

3교시부터 해 온 커밋은 모두 내 PC 에만 있다. PC 가 고장 나면 함께 사라진다. 푸시하면 GitHub 에 사본이 생긴다.

### 원격 저장소

`git clone` 으로 내려받은 저장소는 원래 주소를 `origin` 이라는 이름으로 기억한다. 지금 `origin` 은 강사의 저장소(`sinaboro/harness-crud-lab`)다. 거기에는 올릴 권한이 없다.

그래서 **내 저장소를 새로 만들고**, `origin` 이 그곳을 가리키게 바꾼다.

```text
 지금:    origin → github.com/sinaboro/harness-crud-lab      (강사 저장소. 올릴 수 없다)

 바꾼 뒤: upstream → github.com/sinaboro/harness-crud-lab    (강사 저장소. 이름만 바꿔 남겨 둔다)
          origin   → github.com/내아이디/my-memo-crud        (내 저장소. 여기에 올린다)
```

### 푸시는 어디에서 하는가

커밋은 dev 컨테이너에서 했다. 푸시는 **윈도우 PowerShell** 에서 한다. GitHub 로그인 창이 윈도우에서 뜨고, 로그인 정보도 윈도우에 저장되기 때문이다. 컨테이너에는 내 GitHub 로그인 정보가 없다. AI 에이전트가 그 정보를 쓸 수도 없다.

---

## 따라 하기

### 1단계. 마지막 검증 (10분)

올리기 전에 처음부터 끝까지 다시 확인한다.

**[dev]**

```bash
git status
sh scripts/verify.sh
```

- [ ] `nothing to commit, working tree clean`
- [ ] "검증 통과"

`harness/VERIFY_CHECKLIST.md` 의 5단계(직접 실행해 본다)를 한 번 더 한다. 브라우저에서 http://localhost:8000 을 열어 쓰기·수정·삭제를 한다.

### 2단계. 커밋 기록 읽기 (15분)

**[dev]**

```bash
git log --oneline
```

맨 위가 가장 최근이다. 아래에서 위로 읽으면 프로젝트가 자란 순서다. 내 기록은 대략 이런 모양일 것이다. (맨 아래 몇 줄은 강사가 만든 출발점이다.)

```text
(번호) 11교시: 공백 제목 버그 수정 (R6)
(번호) 10교시: 웹 화면 연결 (R7, N6)
(번호) 9교시: 메모 수정·삭제 구현, CRUD 완성 (R4, R5)
(번호) 8교시: 저장소를 PostgreSQL 로 교체 (N1, N2, N4)
(번호) 6교시: 메모 만들기·보기 초안 (R1, R2, R3, R6)
(번호) 5교시: 하네스 세우기 (AGENTS.md, 권한 규칙)
(번호) 4교시: 메모 만들기·목록 보기(메모리 저장) 추가
(번호) 3교시: /hello 주소와 테스트 추가
```

**커밋 하나는 검증을 통과한 지점 하나다.** 5교시 이후의 모든 커밋은 `pre-commit` 을 통과했다.

교시마다 무엇이 바뀌었는지 본다. 8교시 커밋을 예로 든다.

**[dev]**

```bash
git show --stat (8교시 커밋의 번호)
```

그 커밋에서 바뀐 파일 목록이 나온다. `tests/test_memos.py` 가 **없는지** 확인한다. 8교시의 조건("테스트는 한 글자도 바꾸지 않는다")이 기록으로 남아 있는 것이다.

프로젝트가 얼마나 자랐는지도 본다.

**[dev]**

```bash
git diff --stat (3교시 커밋의 번호) HEAD -- app tests
```

3교시부터 지금까지 `app` 과 `tests` 에서 바뀐 양이 나온다. 이 중 내가 손으로 친 줄은 얼마나 되는가? 나머지는 AI 가 썼고, **나는 그것을 읽고 검증했다.**

### 3단계. 올리면 안 되는 것 확인하기 (10분)

GitHub 에 올린 것은 누구나 볼 수 있다. 올리고 나서 지워도 기록에 남는다. **올리기 전에** 확인한다.

**(1) Git 이 관리하는 파일 목록에 비밀이 없는가**

**[dev]**

```bash
git ls-files | grep -i "env"
```

```text
.env.example
```

`.env.example` **한 줄만** 나와야 한다. `.env` 가 보이면 멈추고 강사에게 알린다.

**[dev]**

```bash
git ls-files | grep "^data/"
```

아무것도 출력되지 않아야 한다. DB 데이터 폴더는 올리지 않는다.

**(2) 커밋 기록 전체에 키가 들어간 적이 없는가**

**[dev]**

```bash
git log -p --all | grep -c "sk-or-v1-[A-Za-z0-9]\{20,\}"
```

`0` 이 나와야 한다. API 키처럼 생긴 글자가 지금까지의 어떤 커밋에도 없다는 뜻이다.

`0` 이 아니면 **푸시하지 않는다.** 그 키는 이미 기록에 남았으므로 OpenRouter 의 Keys 화면에서 그 키를 지우고 새로 만든다. 그리고 강사와 함께 기록을 정리한다.

**(3) 코드에 비밀번호가 없는가**

**[dev]**

```bash
grep -rn "memo1234" app/ tests/
```

아무것도 출력되지 않아야 한다. (`docker-compose.yml` 과 `.env.example` 의 `memo1234` 는 실습용 기본값이다. 실제 서비스에서는 이런 값도 올리지 않는다.)

### 4단계. 내 프로젝트의 README 쓰기 (20분)

지금 `README.md` 는 이 **과정**의 안내문이다. 내 저장소의 첫 화면에는 내 **프로젝트**의 소개가 있어야 한다.

과정 안내문은 이름을 바꿔 남겨 둔다.

**[dev]**

```bash
git mv README.md COURSE.md
```

VS Code 에서 새 `README.md` 를 만든다. 아래 틀을 채운다. **이 문서는 AI 에게 시키지 않고 내가 쓴다.** 3일 동안 한 일을 내 말로 정리하는 것이 이 과정의 마지막 학습이다.

```markdown
# 메모 CRUD — AI 에이전트와 함께 만든 첫 웹 서비스

(한두 문장 소개: 무엇을 하는 서비스인가)

## 기능
- (R1~R7 을 내 말로)

## 실행 방법
1. Docker Desktop 을 설치한다.
2. 이 저장소를 내려받는다.
3. `.env.example` 을 복사해 `.env` 를 만든다.
4. `docker compose up -d --build`
5. 브라우저에서 http://localhost:8000

## 만든 방법 — 하네스 엔지니어링
코드의 대부분은 AI 에이전트(OpenCode + OpenRouter)가 썼고, 나는 아래 장치로 그 작업을 통제했다.

| 요소 | 파일 | 한 일 |
|---|---|---|
| 규칙 | AGENTS.md | (내 말로) |
| 권한 | opencode.jsonc | (내 말로) |
| 검증 | scripts/verify.sh, tests/, .githooks/pre-commit | (내 말로) |

## API
| 하는 일 | 방식·주소 | 성공 | 실패 |
|---|---|---|---|
(9교시 6단계에서 만든 표)

## 테스트
(테스트 개수, 실행 방법, 요구사항과 테스트의 대응)

## 배운 것
(harness/WORKLOG.md 에서 세 가지를 골라)

## 과정 안내
이 프로젝트는 harness-crud-lab 과정의 결과물이다. 과정 안내는 COURSE.md 에 있다.
```

초안을 다 쓴 뒤 AI 에게 **검토만** 시킨다.

**[dev]**

```bash
python scripts/ask_ai.py --file README.md "이 README 를 처음 보는 사람 입장에서 읽고, 실행 방법에서 빠진 단계나 모호한 문장이 있으면 지적만 해 줘. 고쳐 쓰지는 마."
```

지적 중 맞는 것만 내가 고친다.

커밋한다.

**[dev]**

```bash
sh scripts/verify.sh
git add -A
git status
git commit -m "12교시: 프로젝트 README 작성"
```

### 5단계. GitHub 에 올리기 (20분)

**(1) 내 저장소 만들기**

1. 브라우저에서 https://github.com 에 로그인한다.
2. 오른쪽 위 **+** → **New repository**.
3. Repository name: `my-memo-crud` (원하는 이름)
4. **Public** 을 고른다.
5. "Add a README file", ".gitignore", "license" 는 **모두 선택하지 않는다.** (빈 저장소여야 한다)
6. **Create repository** 를 누른다.
7. 다음 화면에 나오는 주소(`https://github.com/내아이디/my-memo-crud.git`)를 복사한다.

**(2) 원격 저장소 바꾸기**

여기부터는 **윈도우 PowerShell** 에서 한다.

**[PS]**

```powershell
cd C:\harness-crud-lab
git remote -v
```

`origin` 이 `sinaboro/harness-crud-lab` 을 가리키고 있다.

**[PS]**

```powershell
git remote rename origin upstream
git remote add origin https://github.com/내아이디/my-memo-crud.git
git remote -v
```

`내아이디` 자리에 내 GitHub 아이디를 넣는다. 마지막 명령의 결과에 `origin` 이 내 저장소로, `upstream` 이 강사 저장소로 나오면 된다.

**(3) 올리기**

**[PS]**

```powershell
git push -u origin main
```

처음 올릴 때 GitHub 로그인 창이 뜬다. 브라우저로 로그인한다. 올라간 커밋 수와 함께 `main -> main` 이 나오면 성공이다.

- `-u origin main` — "앞으로 이 브랜치는 `origin` 의 `main` 과 짝이다"라고 기억시킨다. 다음부터는 `git push` 만 쳐도 된다.

**(4) 확인**

브라우저에서 내 저장소(`https://github.com/내아이디/my-memo-crud`)를 연다.

- [ ] 4단계에서 쓴 README 가 첫 화면에 보인다.
- [ ] 파일 목록에 `.env` 가 **없다.** `.env.example` 은 있다.
- [ ] 파일 목록에 `data` 폴더가 **없다.**
- [ ] 커밋 수를 누르면 교시별 커밋이 보인다.

### 6단계. 다른 사람이 따라 할 수 있는가 (15분)

내 PC 에서 되는 것과 **다른 사람의 PC 에서 되는 것**은 다르다. 내 저장소를 다른 폴더에 새로 내려받아 README 대로 해 본다.

지금 켜져 있는 컨테이너를 먼저 내린다. (같은 8000 번 포트를 쓰기 때문이다)

**[PS]**

```powershell
cd C:\harness-crud-lab
docker compose down
```

새로 내려받아 켠다.

**[PS]**

```powershell
git clone https://github.com/내아이디/my-memo-crud.git C:\memo-check
cd C:\memo-check
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

`.env` 의 `OPENROUTER_API_KEY` 는 비워 둔다. 메모장을 실행하는 데는 AI 키가 필요 없다.

- [ ] 브라우저에서 http://localhost:8000 이 열린다.
- [ ] 메모를 쓰고, 고치고, 지울 수 있다.
- [ ] 메모 목록이 **비어 있는 상태**에서 시작한다. (DB 데이터는 올리지 않았으므로 새 PC 에는 새 DB 가 만들어진다)

테스트도 돌려 본다.

**[PS]**

```powershell
docker compose exec dev sh scripts/verify.sh
```

- [ ] "검증 통과"

**API 키 없이도, 내 PC 의 다른 폴더에서, 저장소에 올라간 것만으로 서비스가 뜨고 테스트가 통과한다.** 이것이 "재현할 수 있다"는 뜻이다.

README 의 실행 방법대로 했는데 빠진 단계가 있었다면, 돌아가서 README 를 고치고 다시 올린다.

뒷정리를 하고 원래 폴더로 돌아온다.

**[PS]**

```powershell
docker compose down
cd C:\harness-crud-lab
Remove-Item -Recurse -Force C:\memo-check
docker compose up -d
```

> `C:\memo-check` 에서는 `pre-commit` 훅이 꺼져 있다. `core.hooksPath` 설정은 Git 에 올라가지 않기 때문이다(5교시 5단계의 참고). 새로 내려받은 저장소에서 작업을 이어 가려면 `git config core.hooksPath .githooks` 를 다시 실행한다.

### 7단계. 발표 준비와 발표 (30분)

발표는 **5분**이다. "무엇을 만들었는가"보다 **"어떻게 통제했는가"** 를 말한다. `harness/WORKLOG.md` 를 펴 놓고 준비한다.

**발표 순서**

| 순서 | 시간 | 내용 | 보여 줄 것 |
|---|---|---|---|
| 1 | 30초 | 무엇을 만들었는가 | 브라우저에서 쓰기·수정·삭제 시연 |
| 2 | 1분 | AI 에게 어떻게 시켰는가 | 작업 지시서 하나(`harness/tasks/…`)의 "범위"와 "하지 말 것" |
| 3 | 1분 30초 | 하네스가 실제로 막거나 잡아낸 일 **하나** | `WORKLOG.md` 의 기록. 권한이 막은 명령, 계획에서 빼게 한 것, 테스트가 잡은 실수 중에서 |
| 4 | 1분 | 내가 이해한 코드 **한 군데** | 코드 대여섯 줄을 화면에 띄우고 한 줄씩 설명 |
| 5 | 30초 | 검증 | `sh scripts/verify.sh` 실행, `git log --oneline` |
| 6 | 30초 | 배운 것 한 가지, 아직 모르는 것 한 가지 | — |

**3번이 발표의 중심이다.** 좋은 예:

- "AI 의 계획에 삭제 API 가 들어 있어서 지시서 4번을 가리켜 빼게 했습니다."
- "8교시에 `git diff --stat` 을 보니 테스트 파일이 바뀌어 있었습니다. 되돌리게 하고 `app/` 만 고치게 했습니다."
- "9교시에 `WHERE` 를 일부러 지워 봤는데 테스트가 잡지 못했습니다. 메모 두 건으로 확인하는 테스트를 추가했습니다."
- "AI 가 `pip install` 을 실행하려 해서 거절했습니다."

**4번에서 고를 만한 코드**

- `conn.execute("… WHERE id = %s", (memo_id,))` — 자리표시자와 그 이유
- `if row is None: raise not_found()` — DB 는 "없다"를 오류로 알리지 않는다
- `@field_validator("title")` — 요구사항 한 줄이 코드가 된 곳
- `title.textContent = memo.title` — 사용자 글을 글자로만 다루는 이유

**듣는 사람이 할 질문** — 발표마다 하나씩 묻는다.

- "그 줄을 지우면 어떻게 되나요?"
- "AI 가 그렇게 하지 않았다는 것을 어떻게 확인했나요?"
- "그 테스트는 어떤 요구사항을 확인하나요?"

### 8단계. 돌아보기 (10분)

`harness/WORKLOG.md` 맨 아래에 적는다.

```markdown
## 과정을 마치며

### 1. 1교시의 나에게 "하네스 엔지니어링"을 한 문장으로 설명한다면

### 2. AI 가 가장 잘한 일과, 내가 반드시 확인해야 했던 일

### 3. 하네스의 다섯 요소 중 가장 효과가 컸던 것과 그 이유

### 4. 내 AGENTS.md 에 새로 넣고 싶은 규칙 한 줄 (3일 동안의 경험에서)

### 5. 다음에 혼자 만들어 보고 싶은 것
```

4번에 적은 규칙을 실제로 `AGENTS.md` 에 넣고 커밋·푸시한다. **하네스는 한 번 세우고 끝나는 것이 아니라, 겪은 일로부터 계속 고쳐 가는 것이다.**

**[dev]**

```bash
git add -A
git commit -m "12교시: 회고와 AGENTS.md 보완"
```

**[PS]**

```powershell
git push
```

---

## 이 다음에 — 스스로 해 볼 것

같은 방법으로 기능을 하나씩 더해 본다. **순서는 언제나 같다.** 요구사항을 쓰고 → 지시서를 쓰고 → 계획을 검토하고 → 검증하고 → 읽고 → 커밋한다.

| 해 볼 것 | 먼저 써야 하는 요구사항 | 조심할 점 |
|---|---|---|
| 메모 검색 (`GET /memos?q=우유`) | 무엇을 검색하는가(제목? 내용?), 결과가 없으면? | 검색어도 `%s` 자리표시자로 넣는다 |
| 완료 표시 (할 일 목록으로) | 새 열의 이름·타입·기본값 | 이미 있는 테이블을 바꾸는 방법이 필요하다 |
| 메모 개수 제한 (목록을 20개씩) | 몇 개씩, 다음 묶음은 어떻게 부르는가 | 기존 테스트가 깨지지 않아야 한다 |
| 다른 주제의 CRUD (도서 목록, 가계부) | R1~R7 을 새 주제로 다시 쓴다 | 새 폴더에서 하네스부터 세운다 |

마지막 줄을 권한다. `AGENTS.md`, `opencode.jsonc`, `scripts/verify.sh`, `.githooks/pre-commit`, `harness/TASK_TEMPLATE.md`, `harness/VERIFY_CHECKLIST.md` 는 주제가 바뀌어도 거의 그대로 쓸 수 있다. **3일 동안 만든 것 중 가장 오래 쓸 것은 메모장이 아니라 이 하네스다.**

## 하네스 관점 — 과정 전체를 돌아보며

| 교시 | 사람이 한 일 | AI 가 한 일 | 통제한 장치 |
|---|---|---|---|
| 1~2 | 개념, 환경 | 질문에 답 | 컨테이너, `.env` |
| 3~4 | `/hello`, GET·POST 를 손으로 | 코드 설명 | (없음 — 불편을 겪어 봄) |
| 5 | 규칙·권한·검증을 세움 | — | `AGENTS.md`, `opencode.jsonc`, `pre-commit` |
| 6 | 계획 승인, 검토 | 메모 초안 + 테스트 | 지시서, 권한, 검증 |
| 7 | SQL 을 손으로 | 질문에 답 | — |
| 8 | 테스트가 안 바뀌었는지 확인 | 저장소 교체 | "테스트는 그대로" |
| 9 | 지시서 작성, SQL 검사 | 수정·삭제 | "테스트는 추가만" |
| 10 | 수동 점검표 | 화면 | "사람이 확인한다" |
| 11 | 테스트를 먼저 씀 | 버그 수정 | "tests/ 는 금지" |
| 12 | README, 발표 | 검토 의견 | 올리기 전 확인 |

코드는 AI 가 더 많이 썼다. 그러나 **무엇을 만들지, 어디까지 허락할지, 결과를 받아들일지**는 처음부터 끝까지 사람이 정했다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `git push` 가 `Permission denied` 또는 `403` | `origin` 이 아직 강사 저장소다. `git remote -v` 로 확인하고 5단계 (2)를 한다. 또는 다른 GitHub 계정으로 로그인되어 있다. |
| `remote origin already exists` | `git remote rename origin upstream` 을 먼저 하지 않았다. |
| `Updates were rejected` | GitHub 저장소를 만들 때 README 등을 함께 만들었다. 저장소를 지우고 빈 저장소로 다시 만든다. |
| `src refspec main does not match any` | 브랜치 이름이 `main` 이 아니다. `git branch` 로 이름을 확인하고 그 이름으로 푸시한다. |
| dev 컨테이너에서 `git push` 를 했더니 로그인을 묻는다 | 푸시는 윈도우 PowerShell 에서 한다. |
| 윈도우에서 `git status` 를 하니 모든 파일이 바뀐 것으로 나온다 | 줄바꿈 설정이 어긋났다. `.gitattributes` 가 있는지 확인한다. 강사에게 알린다. |
| 6단계에서 `port is already allocated` | 원래 폴더의 컨테이너가 켜져 있다. `C:\harness-crud-lab` 에서 `docker compose down` 을 먼저 한다. |
| 6단계에서 컨테이너 이름이 겹친다는 오류 | `docker-compose.yml` 의 `name:` 이 같아서다. 위와 같이 원래 것을 먼저 내린다. |
| GitHub 에 `.env` 가 올라갔다 | 즉시 OpenRouter 에서 그 키를 지운다. 그다음 강사에게 알린다. 파일을 지우는 커밋만으로는 기록에서 사라지지 않는다. |

## 확인 문제

1. 커밋과 푸시의 차이를 "어디에 저장되는가"로 설명하시오.
2. 푸시하기 전에 확인해야 할 것 세 가지와, 각각을 확인하는 명령을 쓰시오.
3. API 키를 실수로 올렸다. 가장 먼저 해야 할 일은 무엇인가? 파일을 지우는 커밋을 올리는 것만으로 충분하지 않은 이유는?
4. `origin` 을 `upstream` 으로 이름을 바꾸고 새 `origin` 을 추가한 이유는 무엇인가?
5. 저장소를 다른 폴더에 새로 내려받아 실행해 본 것은 무엇을 확인하기 위해서인가?
6. 새로 내려받은 저장소에서 메모 목록이 비어 있는 이유를 `.gitignore` 와 바인드 마운트로 설명하시오.
7. 이 과정에서 AI 가 한 일과 사람이 한 일을 각각 세 가지씩 쓰시오.
8. 바이브 코딩과 하네스 엔지니어링의 차이를, 3일 동안 직접 겪은 일 하나를 예로 들어 설명하시오.
