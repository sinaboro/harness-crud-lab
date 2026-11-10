"""
main.py - 메모 API - 저장소를 PostgreSQL 로 바꾼 단계 (8교시)

이 파일이 보여 주는 개념
  1) 주소(URL) + 방식(GET/POST/PUT/DELETE) 하나가 함수 하나에 연결된다.
  2) 만들기는 INSERT, 보기는 SELECT 라는 SQL 과 짝을 이룬다. (고치기·지우기는 9교시)
  3) 없는 메모를 찾으면 404, 입력이 잘못되면 422 를 돌려준다.

주소 목록
  GET    /health        서버가 살아 있는지 확인
  GET    /hello         인사말 (3교시)
  POST   /memos         메모 만들기      (Create)
  GET    /memos         메모 목록 보기   (Read)
  GET    /memos/{id}    메모 한 건 보기  (Read)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.db import get_conn, init_db
from app.schemas import MemoIn, MemoOut


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
