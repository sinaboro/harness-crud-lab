"""
conftest.py - 모든 테스트가 함께 쓰는 준비물

이 파일이 보여 주는 개념
  TestClient 는 서버를 실제로 띄우지 않고도 API 를 불러 볼 수 있게 해 주는 "가짜 브라우저"다.
  테스트 함수가 인자로 client 를 받으면, pytest 가 아래 함수를 실행해 그 결과를 넣어 준다.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """테스트에서 쓸 클라이언트를 만들어 준다."""
    with TestClient(app) as test_client:
        yield test_client
