/*
  app.js - 화면과 API 를 이어 주는 자바스크립트 (10교시)

  이 파일이 보여 주는 개념
    1) fetch() 로 서버 API 를 부른다. /docs 에서 손으로 하던 일을 코드가 대신한다.
    2) 화면의 버튼 하나가 CRUD 하나에 연결된다.
         저장 버튼  → POST /memos   (수정 중이면 PUT /memos/{id})
         화면 열기  → GET /memos
         삭제 버튼  → DELETE /memos/{id}
    3) 사용자가 쓴 글은 textContent 로 넣는다. (innerHTML 로 넣으면 글 속의 태그가 실행될 수 있다)
*/

const form = document.getElementById("memo-form");
const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const saveButton = document.getElementById("save-button");
const cancelButton = document.getElementById("cancel-button");
const message = document.getElementById("message");
const memoList = document.getElementById("memo-list");

// 지금 수정 중인 메모 번호. null 이면 "새 메모 쓰는 중"이라는 뜻이다.
let editingId = null;

// 안내 문구를 화면에 보여 준다.
function showMessage(text) {
  message.textContent = text;
}

// 서버가 오류를 돌려줬을 때, 사람이 읽을 문장으로 바꾼다.
async function readError(response) {
  const body = await response.json().catch(() => null);
  if (body && typeof body.detail === "string") return body.detail; // 404 등
  if (body && Array.isArray(body.detail)) return "입력 값을 확인해 주세요. (제목은 1~100자)"; // 422
  return `요청에 실패했습니다. (상태 코드 ${response.status})`;
}

// ---------- Read: 목록을 불러와 화면에 그린다 ----------
async function loadMemos() {
  const response = await fetch("/memos"); // GET 은 기본값이라 따로 적지 않는다
  const memos = await response.json();

  memoList.replaceChildren(); // 이전 목록을 비운다
  for (const memo of memos) {
    memoList.appendChild(makeMemoItem(memo));
  }
  if (memos.length === 0) showMessage("아직 메모가 없습니다. 첫 메모를 써 보세요.");
}

// 메모 한 건을 <li> 로 만든다.
function makeMemoItem(memo) {
  const item = document.createElement("li");

  const title = document.createElement("strong");
  title.textContent = memo.title; // textContent: 글자를 글자 그대로 넣는다

  const content = document.createElement("p");
  content.textContent = memo.content;

  const time = document.createElement("small");
  time.textContent = `#${memo.id} · ${new Date(memo.updated_at).toLocaleString("ko-KR")}`;

  const editButton = document.createElement("button");
  editButton.textContent = "수정";
  editButton.addEventListener("click", () => startEdit(memo));

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "삭제";
  deleteButton.addEventListener("click", () => deleteMemo(memo.id));

  item.append(title, content, time, editButton, deleteButton);
  return item;
}

// ---------- Create / Update: 저장 버튼 ----------
form.addEventListener("submit", async (event) => {
  event.preventDefault(); // 폼이 페이지를 새로 고치지 않게 막는다

  const body = { title: titleInput.value, content: contentInput.value };
  // 수정 중이면 PUT, 아니면 POST
  const url = editingId === null ? "/memos" : `/memos/${editingId}`;
  const method = editingId === null ? "POST" : "PUT";

  const response = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" }, // "JSON 을 보냅니다"라고 알린다
    body: JSON.stringify(body), // 자바스크립트 객체 → JSON 글자
  });

  if (!response.ok) {
    showMessage(await readError(response));
    return;
  }
  showMessage(editingId === null ? "저장했습니다." : "수정했습니다.");
  stopEdit();
  await loadMemos(); // 목록을 다시 불러와 방금 바뀐 내용을 보여 준다
});

// 수정 시작: 폼에 기존 내용을 채운다.
function startEdit(memo) {
  editingId = memo.id;
  titleInput.value = memo.title;
  contentInput.value = memo.content;
  saveButton.textContent = "수정 저장";
  cancelButton.hidden = false;
  titleInput.focus();
}

// 수정 끝: 폼을 비우고 "새 메모" 상태로 되돌린다.
function stopEdit() {
  editingId = null;
  form.reset();
  saveButton.textContent = "저장";
  cancelButton.hidden = true;
}

cancelButton.addEventListener("click", stopEdit);

// ---------- Delete: 삭제 버튼 ----------
async function deleteMemo(id) {
  if (!confirm(`#${id} 메모를 지울까요?`)) return; // 되돌릴 수 없으니 한 번 묻는다

  const response = await fetch(`/memos/${id}`, { method: "DELETE" });
  if (!response.ok) {
    showMessage(await readError(response));
    return;
  }
  showMessage("삭제했습니다.");
  if (editingId === id) stopEdit(); // 수정하던 메모를 지웠다면 폼도 비운다
  await loadMemos();
}

// 화면이 열리면 목록부터 불러온다.
loadMemos();
