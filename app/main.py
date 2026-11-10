"""
main.py - 가장 작은 FastAPI 서버 (과정의 출발점)

이 파일이 보여 주는 개념
  1) FastAPI() 로 "앱"을 하나 만든다.
  2) @app.get("주소") 를 함수 위에 붙이면, 그 주소로 온 요청을 그 함수가 처리한다.
  3) 함수가 돌려준 딕셔너리는 JSON 으로 바뀌어 브라우저에 전달된다.

3교시부터 이 파일에 기능을 하나씩 더해 간다.
"""

from fastapi import FastAPI

# 앱(서버) 만들기. title 은 문서 화면(/docs) 맨 위에 보이는 이름이다.
app = FastAPI(title="메모 CRUD")


@app.get("/health")
def health() -> dict:
    """서버가 살아 있는지 확인하는 주소"""
    return {"status": "ok"}
