"""
main.py - AI 에이전트에게 맡겨 만든 메모 API 초안 (6교시)

이 파일이 보여 주는 개념
  1) 요구사항 명세의 R1(만들기)·R2(목록)·R3(한 건 보기)·R6(입력 규칙)을 구현했다.
  2) 저장소는 아직 메모리(딕셔너리)다. → 서버를 껐다 켜면 사라진다. (8교시에 DB 로 바꾼다)
  3) 없는 메모를 찾으면 404, 입력이 잘못되면 422 를 돌려준다.

주소 목록
  GET    /health        서버가 살아 있는지 확인
  GET    /hello         인사말 (3교시)
  POST   /memos         메모 만들기      (Create)
  GET    /memos         메모 목록 보기   (Read)
  GET    /memos/{id}    메모 한 건 보기  (Read)
"""

from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException

from app.schemas import MemoIn, MemoOut

app = FastAPI(title="메모 CRUD")

# 메모 저장소: {번호: 메모} 모양의 딕셔너리. 번호로 바로 찾을 수 있다.
memos: dict[int, dict] = {}
# 다음에 만들 메모의 번호. 메모를 지워도 번호가 다시 쓰이지 않게 따로 센다.
next_id = 1


def reset_store() -> None:
    """저장소를 비운다. 테스트가 매번 깨끗한 상태에서 시작하려고 쓴다."""
    global next_id
    memos.clear()
    next_id = 1


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
    global next_id  # 함수 밖의 next_id 를 바꾸겠다는 표시
    now = datetime.now(UTC)  # 지금 시각
    new_memo = {
        "id": next_id,
        "title": memo.title,
        "content": memo.content,
        "created_at": now,
        "updated_at": now,
    }
    memos[next_id] = new_memo
    next_id += 1
    return new_memo


# ---------- Read: 목록 보기 ----------
@app.get("/memos", response_model=list[MemoOut])
def list_memos() -> list[dict]:
    # 최신 메모가 위에 오도록 번호를 거꾸로 정렬한다.
    return sorted(memos.values(), key=lambda memo: memo["id"], reverse=True)


# ---------- Read: 한 건 보기 ----------
@app.get("/memos/{memo_id}", response_model=MemoOut)
def get_memo(memo_id: int) -> dict:
    if memo_id not in memos:  # 그런 번호가 없으면
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")
    return memos[memo_id]
