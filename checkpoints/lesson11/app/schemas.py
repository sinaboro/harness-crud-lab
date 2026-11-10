"""
schemas.py - 주고받는 데이터의 "모양"을 정해 둔 파일

이 파일이 보여 주는 개념
  1) 요청(클라이언트 → 서버)과 응답(서버 → 클라이언트)의 모양을 클래스로 적는다.
  2) 모양에 맞지 않는 요청은 FastAPI 가 알아서 422 오류로 돌려보낸다.
     → 요구사항 명세의 "입력 규칙"이 이 파일에 코드로 옮겨져 있다.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class MemoIn(BaseModel):
    """메모를 만들거나 고칠 때 클라이언트가 보내는 데이터"""

    # 제목: 반드시 있어야 하고 1~100자
    title: str = Field(min_length=1, max_length=100)
    # 내용: 안 보내면 빈 문자열, 최대 1000자
    content: str = Field(default="", max_length=1000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        """11교시에 추가: 공백만 있는 제목("   ")은 받지 않는다."""
        stripped = value.strip()  # 앞뒤 공백을 잘라 낸다
        if not stripped:
            raise ValueError("제목은 공백만으로 채울 수 없습니다.")
        return stripped  # 잘라 낸 값으로 저장한다


class MemoOut(BaseModel):
    """서버가 돌려주는 메모 한 건"""

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
