"""
db.py - PostgreSQL 과 대화하는 부분만 모아 둔 파일

이 파일이 보여 주는 개념
  1) 접속 주소(DATABASE_URL)는 코드에 적지 않고 "환경 변수"에서 읽는다.
  2) 연결(connection)은 필요할 때 열고, 일이 끝나면 바로 닫는다.
  3) 테이블은 서버가 켜질 때 "없으면 만든다"(CREATE TABLE IF NOT EXISTS).
"""

import os

import psycopg
from psycopg.rows import dict_row

# 7교시에 psql 로 직접 쳐 본 것과 같은 SQL 이다. 코드 안에 그대로 들어 있다.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memos (
    id          SERIAL PRIMARY KEY,                    -- 1, 2, 3 ... 자동으로 붙는 번호
    title       VARCHAR(100) NOT NULL,                 -- 제목(최대 100자, 비어 있을 수 없음)
    content     TEXT NOT NULL DEFAULT '',              -- 내용(없으면 빈 문자열)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),    -- 만든 시각
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()     -- 마지막으로 고친 시각
);
"""


def get_database_url() -> str:
    """환경 변수에서 접속 주소를 읽는다. (docker-compose.yml 이 넣어 준다)"""
    # 함수 안에서 읽는 이유: 테스트가 주소를 테스트용 DB 로 바꿔 끼울 수 있게 하려고.
    return os.environ["DATABASE_URL"]


def get_conn() -> psycopg.Connection:
    """DB 연결을 하나 연다. 결과 행은 {"열이름": 값} 딕셔너리로 받는다."""
    return psycopg.connect(get_database_url(), row_factory=dict_row)


def init_db() -> None:
    """memos 테이블이 없으면 만든다. 이미 있으면 아무 일도 하지 않는다."""
    # with 블록을 빠져나올 때 자동으로 저장(commit)하고 연결을 닫는다.
    with get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)
