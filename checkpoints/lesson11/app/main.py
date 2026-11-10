"""
main.py - 메모 CRUD API (완성본)

이 파일이 보여 주는 개념
  1) 주소(URL) + 방식(GET/POST/PUT/DELETE) 하나가 함수 하나에 연결된다.
  2) CRUD 네 가지가 SQL 네 가지(INSERT/SELECT/UPDATE/DELETE)와 짝을 이룬다.
  3) 없는 메모를 찾으면 404, 입력이 잘못되면 422 를 돌려준다.

주소 목록
  GET    /health        서버가 살아 있는지 확인
  GET    /hello         인사말 (3교시)
  POST   /memos         메모 만들기      (Create)
  GET    /memos         메모 목록 보기   (Read)
  GET    /memos/{id}    메모 한 건 보기  (Read)
  PUT    /memos/{id}    메모 고치기      (Update)
  DELETE /memos/{id}    메모 지우기      (Delete)
  GET    /              웹 화면 (10교시)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import get_conn, init_db
from app.schemas import MemoIn, MemoOut

# 화면 파일(index.html, app.js, style.css)이 들어 있는 폴더
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버가 켜질 때 한 번 실행된다: 테이블이 없으면 만든다."""
    init_db()
    yield  # 여기서부터 서버가 요청을 받는다


app = FastAPI(title="메모 CRUD", lifespan=lifespan)


def not_found() -> HTTPException:
    """'그 번호의 메모가 없다'는 404 오류를 한 곳에서 만든다."""
    return HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")


@app.get("/health")
def health() -> dict:
    """서버가 살아 있는지 확인하는 주소"""
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str = "하네스") -> dict:
    """/hello?name=철수 처럼 부르면 이름을 넣어 인사한다."""
    return {"message": f"안녕하세요, {name}!"}


# ---------- Create: 메모 만들기 ----------
@app.post("/memos", response_model=MemoOut, status_code=201)
def create_memo(memo: MemoIn) -> dict:
    with get_conn() as conn:
        # %s 자리에 값이 안전하게 들어간다(SQL 을 문자열로 이어 붙이지 않는다).
        row = conn.execute(
            "INSERT INTO memos (title, content) VALUES (%s, %s) RETURNING *",
            (memo.title, memo.content),
        ).fetchone()
    return row


# ---------- Read: 목록 보기 ----------
@app.get("/memos", response_model=list[MemoOut])
def list_memos() -> list[dict]:
    with get_conn() as conn:
        # 최신 메모가 위에 오도록 id 를 거꾸로 정렬한다.
        return conn.execute("SELECT * FROM memos ORDER BY id DESC").fetchall()


# ---------- Read: 한 건 보기 ----------
@app.get("/memos/{memo_id}", response_model=MemoOut)
def get_memo(memo_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM memos WHERE id = %s", (memo_id,)).fetchone()
    if row is None:  # 그런 번호가 없으면
        raise not_found()
    return row


# ---------- Update: 고치기 ----------
@app.put("/memos/{memo_id}", response_model=MemoOut)
def update_memo(memo_id: int, memo: MemoIn) -> dict:
    with get_conn() as conn:
        # WHERE 가 없으면 모든 메모가 바뀐다. 반드시 id 로 한 건만 고른다.
        row = conn.execute(
            "UPDATE memos SET title = %s, content = %s, updated_at = now() "
            "WHERE id = %s RETURNING *",
            (memo.title, memo.content, memo_id),
        ).fetchone()
    if row is None:
        raise not_found()
    return row


# ---------- Delete: 지우기 ----------
@app.delete("/memos/{memo_id}", status_code=204)
def delete_memo(memo_id: int) -> None:
    with get_conn() as conn:
        row = conn.execute(
            "DELETE FROM memos WHERE id = %s RETURNING id", (memo_id,)
        ).fetchone()
    if row is None:
        raise not_found()
    # 204 는 "성공했고, 돌려줄 내용은 없음"이라는 뜻이라 아무것도 돌려주지 않는다.


# ---------- 웹 화면 ----------
@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """브라우저로 http://localhost:8000 에 들어오면 화면 파일을 보낸다."""
    return FileResponse(STATIC_DIR / "index.html")


# /static/app.js, /static/style.css 같은 파일을 그대로 내려 준다.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
