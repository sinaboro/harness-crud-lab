"""
conftest.py - 모든 테스트가 함께 쓰는 준비물

이 파일이 보여 주는 개념
  1) 테스트는 "테스트 전용 DB"(memo_test)에서만 돈다. 진짜 메모(memo_db)는 건드리지 않는다.
  2) 테스트 하나가 시작될 때마다 테이블을 비운다. 그래야 테스트끼리 서로 영향을 주지 않는다.
  3) TestClient 는 서버를 실제로 띄우지 않고도 API 를 불러 볼 수 있게 해 준다.
"""

import os

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.conninfo import conninfo_to_dict

# docker-compose.yml 이 dev 컨테이너에 넣어 준 두 주소
MAIN_URL = os.environ["DATABASE_URL"]  # 평소에 쓰는 DB (memo_db)
TEST_URL = os.environ["TEST_DATABASE_URL"]  # 테스트 전용 DB (memo_test)

# 앱이 테스트 전용 DB 를 보게 주소를 바꿔 끼운다. (app 을 불러오기 전에 해야 한다)
os.environ["DATABASE_URL"] = TEST_URL

from app.db import get_conn
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """테스트 전용 DB 가 없으면 만든다. 테스트 전체에서 딱 한 번 실행된다."""
    test_db_name = conninfo_to_dict(TEST_URL)["dbname"]
    # CREATE DATABASE 는 autocommit 상태에서만 실행할 수 있다.
    with psycopg.connect(MAIN_URL, autocommit=True) as conn:
        exists = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (test_db_name,)
        ).fetchone()
        if not exists:
            conn.execute(f'CREATE DATABASE "{test_db_name}"')


@pytest.fixture
def client():
    """테스트 함수가 인자로 client 를 받으면, 깨끗한 DB 와 연결된 클라이언트를 준다."""
    # with 를 쓰면 서버가 켜질 때 하는 일(lifespan → 테이블 만들기)이 함께 실행된다.
    with TestClient(app) as test_client:
        with get_conn() as conn:
            # 메모를 모두 지우고 번호도 1번부터 다시 시작하게 한다.
            conn.execute("TRUNCATE TABLE memos RESTART IDENTITY")
        yield test_client
