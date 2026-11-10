"""
conftest.py - 모든 테스트가 함께 쓰는 준비물 (6교시: 메모리 저장소용)

이 파일이 보여 주는 개념
  1) TestClient 는 서버를 실제로 띄우지 않고도 API 를 불러 볼 수 있게 해 주는 "가짜 브라우저"다.
  2) 테스트 하나가 시작될 때마다 저장소를 비운다. 그래야 테스트끼리 서로 영향을 주지 않는다.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_store


@pytest.fixture
def client():
    """테스트 함수가 인자로 client 를 받으면, 깨끗한 저장소와 연결된 클라이언트를 준다."""
    reset_store()  # 앞 테스트가 남긴 메모를 지운다
    with TestClient(app) as test_client:
        yield test_client
