"""
main.py - GET 과 POST 를 손으로 만들어 본 단계 (4교시)

이 파일이 보여 주는 개념
  1) GET 은 "보여 줘", POST 는 "이걸 새로 만들어 줘"라는 요청이다.
  2) POST 로 보낸 데이터(JSON)는 클래스(MemoIn)로 모양을 정해 두면 FastAPI 가 검사해 준다.
  3) 지금은 메모를 파이썬 리스트(메모리)에 넣는다. → 서버를 껐다 켜면 사라진다!
     (그래서 7~8교시에 PostgreSQL 이 필요해진다)
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="메모 CRUD")

# 메모를 담아 둘 리스트. 서버가 켜져 있는 동안에만 유지된다.
memos: list[dict] = []


class MemoIn(BaseModel):
    """메모를 만들 때 클라이언트가 보내는 데이터의 모양"""

    title: str  # 제목: 글자여야 하고, 반드시 보내야 한다
    content: str = ""  # 내용: 안 보내면 빈 문자열


@app.get("/health")
def health() -> dict:
    """서버가 살아 있는지 확인하는 주소"""
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str = "하네스") -> dict:
    """/hello?name=철수 처럼 부르면 이름을 넣어 인사한다."""
    return {"message": f"안녕하세요, {name}!"}


@app.post("/memos", status_code=201)
def create_memo(memo: MemoIn) -> dict:
    """메모 만들기. 성공하면 201(Created)과 함께 만든 메모를 돌려준다."""
    new_memo = {
        "id": len(memos) + 1,  # 번호는 1, 2, 3 ... 순서대로
        "title": memo.title,
        "content": memo.content,
    }
    memos.append(new_memo)  # 리스트에 넣는다
    return new_memo


@app.get("/memos")
def list_memos() -> list[dict]:
    """메모 목록 보기"""
    return memos
