# 10교시. HTML·JS 화면 연결

| | |
|---|---|
| 시간 | 2시간 |
| 실습 결과 | 웹에서 CRUD 실행 (브라우저 화면에서 메모를 쓰고, 보고, 고치고, 지운다) |
| 시작 상태 | 9교시를 마친 상태 (CRUD API 가 완성되어 커밋되어 있다) |

9교시 결과가 없으면 **[dev]** `sh scripts/checkpoint.sh 09` 로 가져온다.

## 수업의 흐름에서 이번 교시의 위치

```text
 ① 요구사항 작성 → ② AI 에게 지시 → ③ 하네스로 제어 → ④ 실행·테스트 → ⑤ 수정·재검증·저장
 └────────── 이번 교시: 네 번째 바퀴. 테스트가 보지 못하는 것을 사람이 확인한다 ──────────┘
```

## 학습 목표

1. HTML·CSS·자바스크립트가 각각 맡는 일을 구분한다.
2. 화면의 버튼이 `fetch` 를 거쳐 API 로 이어지는 흐름을 설명한다.
3. 브라우저 개발자 도구로 화면이 보내는 요청을 직접 본다.
4. 자동 테스트가 확인하지 못하는 것을 수동 점검표로 확인한다.
5. 사용자가 쓴 글이 화면에 **글자 그대로** 보이는 것을 직접 확인한다. (그 이유는 `textContent` 한 줄에 있다)

---

## 1. 개념

### 세 가지 파일

| 파일 | 맡는 일 | 비유 |
|---|---|---|
| `index.html` | 화면의 뼈대. 입력 칸, 버튼, 목록 자리 | 집의 골조 |
| `style.css` | 꾸미기. 색, 크기, 간격 | 도배와 페인트 |
| `app.js` | 동작. 버튼을 누르면 무슨 일이 일어나는가 | 전기와 배관 |

`style.css` 가 없어도 메모장은 동작한다. `app.js` 가 없으면 버튼을 눌러도 아무 일도 일어나지 않는다.

### 화면과 API 는 어떻게 이어지는가

지금까지 `/docs` 화면이나 `curl` 로 API 를 불렀다. 이제 그 일을 **자바스크립트가 대신** 한다.

```text
 [브라우저]                                      [app 컨테이너]            [db 컨테이너]
  사용자가 "저장" 버튼을 누른다
        │
        ▼
  app.js:  fetch("/memos", { method: "POST", body: … })
        │        HTTP 요청 (curl 로 보내던 것과 똑같다)
        └──────────────────────────────────────▶  create_memo()  ──▶  메모 저장 (8교시)
                                                        │
        ┌───────────────── 201 + JSON ◀─────────────────┘
        ▼
  app.js:  목록을 다시 불러와 화면에 그린다
```

`fetch` 는 자바스크립트에서 HTTP 요청을 보내는 함수다. `curl` 과 짝지어 보면 읽힌다.

| | `curl` (4교시) | `fetch` (이번 교시) |
|---|---|---|
| 주소 | `http://app:8000/memos` | `"/memos"` |
| 방식 | `-X POST` | `method: "POST"` |
| 머리말 | `-H "Content-Type: application/json"` | `headers: { "Content-Type": "application/json" }` |
| 본문 | `-d '{"title": "장보기"}'` | `body: JSON.stringify({ title: "장보기" })` |

**API 는 하나도 바뀌지 않는다.** 9교시까지 만든 것을 그대로 쓴다. 화면은 API 를 부르는 또 하나의 손님일 뿐이다.

### 자동 테스트가 보지 못하는 것

`pytest` 는 서버에 요청을 보내고 응답을 확인한다. **브라우저를 열지 않는다.** 그래서 다음은 확인하지 못한다.

- 버튼을 눌렀을 때 정말 요청이 나가는가
- 저장한 뒤 목록이 새로 그려지는가
- 오류 문구가 화면에 보이는가
- 글자가 상자 밖으로 삐져나오지 않는가

이번 교시의 검증은 **자동 테스트 + 사람의 수동 점검표** 두 겹이다. 하네스의 "검증"에 사람의 눈이 들어가야 하는 자리가 있다.

---

## 따라 하기

### 1단계. ①② 요구사항과 지시서 읽기 (10분)

`harness/REQUIREMENTS.md` 의 **R7** 과 **N6** 을 읽는다.

`harness/tasks/10_web_page.md` 를 읽는다. 이번 지시서에서 눈여겨볼 곳:

- **4. 하지 말 것** — 프레임워크·외부 라이브러리·CDN 금지. AI 는 화면을 만들라고 하면 React 나 Bootstrap 을 가져오려는 경향이 있다. 그러면 내가 읽어야 할 것이 몇 배로 늘어난다.
- **5. 구현 조건** — 화면의 구성과 동작이 문장으로 적혀 있다. 화면은 "어떻게 생겨야 하는가"를 말로 정해 주지 않으면 매번 전혀 다른 것이 나온다.
- **6. 완료 조건** — 다섯 개 중 두 개에 "(사람이 확인한다)"가 붙어 있다. AI 가 확인할 수 없는 조건이다.

### 2단계. ②③ 지시하고 계획 검토하기 (15분)

**[dev]**

```bash
git status
sh scripts/verify.sh
opencode
```

**[AI]**

```text
harness/tasks/10_web_page.md 를 읽고 그 지시대로 작업해 줘. AGENTS.md 의 작업 절차를 따라, 먼저 계획만 말하고 내 승인을 기다려.
```

**계획 검토 체크리스트**

- [ ] 새 파일이 `app/static/` 아래 세 개(`index.html`, `app.js`, `style.css`)인가?
- [ ] React, Vue, jQuery, Bootstrap, Tailwind, CDN 이라는 낱말이 **없는가?**
- [ ] `/memos` API 를 고치거나 새 API 를 만들겠다는 말이 **없는가?**
- [ ] 사용자 글을 `textContent` 로 넣겠다고 했는가?
- [ ] `GET /` 의 테스트를 추가하겠다고 했는가?
- [ ] `npm`, `node` 를 설치하거나 실행하겠다는 말이 **없는가?**

맞으면 `진행`.

AI 가 `curl http://app:8000/` 로 화면이 내려오는지 확인할 수 있다. 하지만 **AI 는 브라우저를 열어 볼 수 없다.** AI 의 보고에 "화면에서 정상 동작을 확인했습니다"라는 말이 있다면, 무엇으로 확인했는지 되묻는다.

### 3단계. ④ 검증 1 — 기계가 확인하는 것 (10분)

**[dev]** (다른 셸)

```bash
sh scripts/verify.sh
```

완성 예시의 결과:

```text
..................                                                       [100%]
18 passed in 1.77s
```

**[dev]**

```bash
git status
git diff --stat
git diff tests/ | grep "^-" | grep -v "^---"
```

- [ ] 새 파일은 `app/static/` 아래 세 개다.
- [ ] 바뀐 파일은 `app/main.py`, `tests/test_memos.py` 다.
- [ ] 셋째 명령은 아무것도 출력하지 않는다. (기존 테스트가 지워지지 않았다)

**금지한 것이 들어오지 않았는지 검사한다.**

**[dev]**

```bash
grep -n "innerHTML" app/static/app.js
grep -n -i "cdn\|https://\|http://" app/static/index.html app/static/app.js
```

- [ ] 첫째 명령: 출력이 없다. (`innerHTML` 을 쓰지 않았다)
- [ ] 둘째 명령: 출력이 없다. (외부에서 가져오는 것이 없다)

**화면 파일이 내려오는지 확인한다.**

**[dev]**

```bash
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" http://app:8000/
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" http://app:8000/static/app.js
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" http://app:8000/static/style.css
```

```text
200 text/html; charset=utf-8
200 text/javascript; charset=utf-8
200 text/css; charset=utf-8
```

### 4단계. ④ 검증 2 — 사람이 확인하는 것 (25분)

브라우저에서 http://localhost:8000 을 연다. 아래 점검표를 **순서대로** 한다. 하나라도 안 되면 5단계 뒤의 "화면이 이상할 때"로 간다.

**수동 점검표**

| 번호 | 할 일 | 기대하는 결과 | 확인 |
|---|---|---|---|
| 1 | 화면을 연다 | "메모장" 제목, 입력 칸 둘, 저장 버튼, 9교시에 남겨 둔 메모가 목록에 보인다 | [ ] |
| 2 | 제목 "회의", 내용 "오후 3시" 를 넣고 저장 | 새로 고침 없이 목록 **맨 위**에 나타난다. 입력 칸이 비워진다 | [ ] |
| 3 | 제목을 비운 채 저장 | 저장되지 않는다. 안내가 나온다 | [ ] |
| 4 | "회의" 메모의 수정 버튼 | 위 입력 칸에 "회의", "오후 3시" 가 채워진다. 버튼이 "수정 저장"으로 바뀐다 | [ ] |
| 5 | 내용을 "오후 4시" 로 바꾸고 수정 저장 | 목록의 내용이 바뀐다. 메모가 하나 더 생기지 **않는다** | [ ] |
| 6 | 수정 버튼을 누른 뒤 수정 취소 | 입력 칸이 비워지고 버튼이 "저장"으로 돌아온다 | [ ] |
| 7 | 삭제 버튼 | 정말 지울지 묻는다. 취소하면 그대로 있다 | [ ] |
| 8 | 삭제 버튼 → 확인 | 목록에서 사라진다 | [ ] |
| 9 | 브라우저를 새로 고친다(F5) | 2~8 의 결과가 그대로다 (DB 에 저장되었다) | [ ] |
| 10 | 내용에 여러 줄을 넣고 저장 | 줄바꿈이 그대로 보인다 | [ ] |
| 11 | 제목 칸에 `가` 를 100번 이어 붙인 글자를 넣고 저장 (메모장에 `가` 100개를 쳐서 복사한다) | 글자가 상자 밖으로 나가지 않는다 | [ ] |

**화면이 보내는 요청을 직접 본다.**

브라우저에서 **F12** 를 눌러 개발자 도구를 열고 **Network(네트워크)** 탭을 고른다. 그 상태에서 메모를 하나 저장한다.

목록에 요청 두 줄이 나타난다.

| 이름 | 방식 | 상태 | 뜻 |
|---|---|---|---|
| `memos` | POST | 201 | 저장 버튼이 보낸 요청 |
| `memos` | GET | 200 | 저장 뒤 목록을 다시 불러온 요청 |

POST 줄을 눌러 **Payload(페이로드)** 를 본다. 4교시에 `curl -d` 로 보내던 JSON 과 같은 모양이다. **Response(응답)** 에는 `curl` 로 보던 응답이 있다.

수정과 삭제도 해 보고, 각각 어떤 방식·주소·상태 코드가 나가는지 6단계의 표에 적는다.

**사용자 글이 글자로만 보이는가 — 직접 확인**

제목 칸에 아래를 그대로 넣고 저장한다. 글자 모양의 태그가 들어 있는 글이다.

```text
<b>굵게</b>
```

| 결과 | 뜻 |
|---|---|
| 목록에 `<b>굵게</b>` 가 **그대로 글자로** 보인다 (굵은 글씨가 아니다) | 정상이다. 사용자가 쓴 글은 글자로만 나온다 |
| "굵게"만 굵은 글씨로 보인다 | 이상하다. 강사에게 알린다. 이 과정의 화면은 그렇게 만들지 않는다 |

이 글이 글자로만 나오는 이유는 자바스크립트의 한 줄에 있다. 5단계 (3)~(4)에서 그 줄을 찾는다.

> 왜 중요한가: 메모장을 여러 사람이 함께 쓴다면, 한 사람이 넣은 글이 다른 사람의 브라우저에서 **코드로 실행**될 수 있다. 이것을 XSS 라고 한다. **사용자가 보낸 글은 언제나 글자로만 다룬다.** 확인이 끝나면 이 메모는 지운다.

### 5단계. ⑤ 코드 읽기 (25분)

완성 예시(`checkpoints/lesson10`)를 기준으로 읽는다.

**(1) 서버는 화면 파일을 어떻게 보내는가**

`app/main.py` 에는 세 가지 일이 적혀 있다. 코드를 읽지 않고 **무슨 일을 하는지**만 AI 에게 묻는다.

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. app/main.py 에서 주소 / 로 들어왔을 때와 /static/ 으로 들어왔을 때 각각 어떤 파일을 보내는지 초보자에게 두 문장으로 알려 줘.
```

- `/` 로 들어오면 `index.html` 을 보낸다. (API 가 아니라 화면이므로 `/docs` 목록에는 나오지 않는다.)
- `/static/…` 으로 들어오면 `app.js`, `style.css` 같은 파일을 그대로 보낸다.

**확인.** 브라우저에서 http://localhost:8000/static/style.css 를 열어 본다. 글자가 빽빽하게 나온다면 파일이 잘 보내진 것이다.

**(2) `index.html` — 뼈대**

```html
<form id="memo-form">
  <input id="title" type="text" placeholder="제목 (필수, 100자까지)" maxlength="100" required>
  <textarea id="content" placeholder="내용 (1000자까지)" maxlength="1000" rows="3"></textarea>
  <button id="save-button" type="submit">저장</button>
</form>

<p id="message" role="status"></p>
<ul id="memo-list"></ul>

<script src="/static/app.js"></script>
```

- `id="…"` — 자바스크립트가 이 요소를 찾을 때 쓰는 이름표다.
- `maxlength="100" required` — 브라우저가 먼저 막아 준다. 수동 점검표 3번에서 본 안내가 이것이다.
- `<ul id="memo-list"></ul>` — **비어 있다.** 목록은 `app.js` 가 채운다.

입력 규칙이 이제 세 겹이다: 브라우저(`maxlength`, `required`) → 서버(`MemoIn`) → DB(`NOT NULL`, `VARCHAR(100)`). 브라우저의 검사는 편의일 뿐이다. `curl` 로 직접 보내면 건너뛸 수 있으므로 서버의 검사가 반드시 있어야 한다.

**(3) `app.js` — 목록 불러오기**

```javascript
async function loadMemos() {
  const response = await fetch("/memos"); // GET 은 기본값이라 따로 적지 않는다
  const memos = await response.json();

  memoList.replaceChildren(); // 이전 목록을 비운다
  for (const memo of memos) {
    memoList.appendChild(makeMemoItem(memo));
  }
}
```

- `fetch("/memos")` — `curl -s http://app:8000/memos` 와 같은 일이다.
- `await` — "답이 올 때까지 기다린다". 요청은 시간이 걸리기 때문이다. `await` 를 쓰는 함수 앞에는 `async` 를 붙인다.
- `response.json()` — JSON 글자를 자바스크립트 객체로 바꾼다.
- `for (const memo of memos)` — 메모마다 한 번씩 되풀이한다.

**(4) `app.js` — 메모 한 건 그리기**

```javascript
const title = document.createElement("strong");
title.textContent = memo.title; // textContent: 글자를 글자 그대로 넣는다
```

4단계의 실험에서 `<b>굵게</b>` 가 글자 그대로 보인 이유가 이 줄이다.

**(5) `app.js` — 저장 버튼**

```javascript
form.addEventListener("submit", async (event) => {
  event.preventDefault(); // 폼이 페이지를 새로 고치지 않게 막는다

  const body = { title: titleInput.value, content: contentInput.value };
  // 수정 중이면 PUT, 아니면 POST
  const url = editingId === null ? "/memos" : `/memos/${editingId}`;
  const method = editingId === null ? "POST" : "PUT";

  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    showMessage(await readError(response));
    return;
  }
  stopEdit();
  await loadMemos(); // 목록을 다시 불러와 방금 바뀐 내용을 보여 준다
});
```

- `addEventListener("submit", …)` — "폼이 제출되면 이 함수를 실행해라".
- `editingId` — 지금 수정 중인 메모의 번호. `null` 이면 새 메모다. **저장 버튼 하나가 POST 와 PUT 을 겸한다.** 수동 점검표 5번("메모가 하나 더 생기지 않는다")이 이 줄을 확인한 것이다.
- `조건 ? A : B` — 조건이 참이면 A, 아니면 B.
- `response.ok` — 상태 코드가 2xx 이면 참이다. 422 나 404 면 거짓이다.

**(6) AI 에게 묻기**

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. app/static/app.js 에서 "수정" 버튼을 누른 순간부터 "수정 저장"을 눌러 목록이 다시 그려질 때까지, 실행되는 함수와 보내지는 HTTP 요청을 순서대로 번호를 붙여 알려 줘.
```

**[AI]**

```text
파일은 고치지 말고 설명만 해 줘. event.preventDefault() 를 지우면 저장 버튼을 눌렀을 때 화면에서 어떤 일이 벌어져?
```

둘째 질문의 답은 실험으로 확인한다. 그 줄을 지우고(주석으로 바꾸고) 브라우저를 새로 고친 뒤 저장을 눌러 본다. 확인했으면 Ctrl+Z 로 되돌린다.

### 6단계. 화면 ↔ API 한 장으로 (5분)

개발자 도구의 Network 탭에서 본 것으로 채운다.

| 화면에서 하는 일 | 나가는 요청 (방식·주소) | 상태 코드 | 화면에 무엇이 바뀌는가 |
|---|---|---|---|
| 화면을 연다 | `GET /memos` | | 목록이 그려진다 |
| 저장 | | | |
| 수정 저장 | | | |
| 삭제 | | | |

`harness/WORKLOG.md` 의 10교시 기록에 붙인다.

### 7단계. ⑤ 기록하고 저장하기 (5분)

**[dev]**

```bash
git add -A
git status
git commit -m "10교시: 웹 화면 연결 (R7, N6)"
```

OpenCode 를 `/exit` 로 닫는다.

---

## 화면이 이상할 때 — 오류를 AI 에게 전달하는 법

서버 쪽 오류는 `verify.sh` 의 출력을 붙여 주면 됐다. 화면 쪽 오류는 **브라우저가 알려 주는 것**을 붙여 준다.

1. F12 → **Console(콘솔)** 탭. 빨간 글씨가 있으면 그것이 오류다. 전체를 복사한다.
2. F12 → **Network** 탭. 빨간 줄(실패한 요청)의 방식·주소·상태 코드를 적는다.
3. **무엇을 했더니, 무엇을 기대했는데, 무엇이 일어났는지**를 함께 적는다.

**[AI]**

```text
화면에서 문제가 있어.
- 한 일: 메모의 "수정" 버튼을 누르고 내용을 바꾼 뒤 "수정 저장"을 눌렀다.
- 기대한 것: 그 메모의 내용이 바뀐다.
- 일어난 일: 같은 제목의 메모가 하나 더 생겼다.
- Network 탭: PUT 이 아니라 POST /memos 201 이 나갔다.
- Console 탭: 오류 없음.
원인을 먼저 설명하고, 내가 "진행"이라고 하면 고쳐 줘.
```

"수정이 안 돼요"와 비교해 본다. AI 가 추측할 필요가 없다.

## 하네스 관점 — 이번 교시에서 본 것

- **검증에는 사람의 자리가 있다.** `pytest` 18개가 통과해도 버튼이 동작하는지는 알 수 없다. 자동 테스트가 못 보는 것은 점검표로 사람이 본다. "자동으로 확인되는 것"과 "사람이 확인해야 하는 것"의 경계를 아는 것이 중요하다.
- **AI 가 확인할 수 없는 것을 확인했다고 말하게 두지 않는다.** AI 는 브라우저를 열 수 없다. 지시서의 완료 조건에 "(사람이 확인한다)"를 따로 적어 둔 이유다.
- **금지는 검사할 수 있게 쓴다.** "`innerHTML` 을 쓰지 않는다"는 `grep` 한 줄로 확인된다. "안전하게 만든다"는 확인할 수 없다. 규칙은 확인할 수 있는 문장으로 쓴다.
- **좋은 오류 보고가 좋은 수정을 만든다.** 한 일·기대·실제·증거. 사람 개발자에게 버그를 알릴 때와 똑같다.

## 자주 만나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `http://localhost:8000` 이 `{"detail":"Not Found"}` | `GET /` 가 연결되지 않았다. `/docs` 가 아니라 `curl -s -o /dev/null -w "%{http_code}\n" http://app:8000/` 로 확인한다. |
| 화면은 나오는데 꾸밈이 없고 버튼이 동작하지 않는다 | `app.js`, `style.css` 를 못 가져왔다. Network 탭에서 두 파일이 404 인지 본다. `index.html` 의 경로(`/static/…`)와 `app.mount` 를 확인한다. |
| 고쳤는데 화면이 그대로다 | 브라우저가 옛 파일을 기억하고 있다. **Ctrl+F5**(강력 새로 고침)를 누른다. |
| 저장을 누르면 화면이 깜빡이고 주소 끝에 `?` 가 붙는다 | `event.preventDefault()` 가 없다. |
| Console 에 `Cannot read properties of null` | 자바스크립트가 찾는 `id` 가 HTML 에 없다. 이름이 서로 같은지 본다. |
| 목록에 `[object Object]` 가 보인다 | 객체를 통째로 글자로 넣었다. `memo.title` 처럼 항목을 꺼내야 한다. |
| 시각이 9시간 어긋난다 | 서버는 세계 표준시(UTC)로 준다. 화면에서 `new Date(…).toLocaleString("ko-KR")` 로 바꿔 보여 준다. |
| `RuntimeError: Directory '…/static' does not exist` | `app/static` 폴더가 없거나 경로가 틀렸다. `ls app/static` 으로 확인한다. |

## 확인 문제

1. HTML, CSS, 자바스크립트 중 하나를 지웠을 때 각각 어떤 일이 생기는가?
2. `fetch("/memos", { method: "POST", … })` 를 같은 일을 하는 `curl` 명령으로 바꿔 쓰시오.
3. 화면을 만들면서 `/memos` API 를 고칠 필요가 없었던 이유는 무엇인가?
4. `pytest` 가 모두 통과했는데 화면의 저장 버튼이 동작하지 않을 수 있는가? 이유를 쓰시오.
5. 제목에 `<b>굵게</b>` 를 넣었을 때 `textContent` 와 `innerHTML` 은 각각 어떻게 보여 주는가? 왜 한쪽이 위험한가?
6. 입력 규칙이 브라우저·서버·DB 세 곳에 있다. 브라우저의 검사만 있으면 안 되는 이유를 `curl` 을 예로 들어 설명하시오.
7. 저장 버튼 하나가 새 메모 저장과 수정 저장을 겸한다. 코드는 둘을 무엇으로 구분하는가?
8. "수정이 안 돼요"라는 보고를 AI 가 바로 고칠 수 있는 보고로 고쳐 쓰시오. (한 일·기대·실제·증거)

## 다음 교시

[11교시. 자동 테스트와 오류 수정](11_자동_테스트와_오류_수정.md) — 버그를 찾아 실패하는 테스트로 붙잡고, AI 에게 고치게 한다.
