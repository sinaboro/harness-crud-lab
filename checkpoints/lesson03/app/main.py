"""
main.py - /hello 주소를 더한 단계 (3교시)

이 파일이 보여 주는 개념
  1) @app.get("주소") 를 함수 위에 붙이면, 그 주소로 온 요청을 그 함수가 처리한다.
  2) 함수의 인자(name)는 주소 뒤의 ?name=값 에서 온다. 이것을 "쿼리 파라미터"라고 한다.
  3) 함수가 돌려준 딕셔너리는 JSON 으로 바뀌어 브라우저에 전달된다.
"""

from fastapi import FastAPI

# 앱(서버) 만들기. title 은 문서 화면(/docs) 맨 위에 보이는 이름이다.
app = FastAPI(title="메모 CRUD")


@app.get("/health")
def health() -> dict:
    """서버가 살아 있는지 확인하는 주소"""
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str = "하네스") -> dict:
    """/hello?name=철수 처럼 부르면 이름을 넣어 인사한다."""
    # name: str = "하네스" → 글자(str)를 받고, 안 주면 "하네스"를 쓴다는 뜻
    return {"message": f"안녕하세요, {name}!"}
