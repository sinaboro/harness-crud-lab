"""
test_health.py - 가장 작은 테스트

이 파일이 보여 주는 개념
  테스트는 "이렇게 부르면 → 이런 답이 와야 한다"를 코드로 적어 둔 것이다.
  assert 뒤의 식이 참이면 통과, 거짓이면 실패다.
"""


def test_health(client):
    response = client.get("/health")  # GET /health 를 부른다
    assert response.status_code == 200  # 성공(200)이어야 한다
    assert response.json() == {"status": "ok"}  # 답의 내용도 정확히 같아야 한다
