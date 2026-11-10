"""
ask_ai.py - OpenRouter 를 통해 AI 모델에게 질문 하나를 보내고 답을 출력한다. (2교시)

이 파일이 보여 주는 개념
  1) AI 모델을 "부른다"는 것은 결국 인터넷 주소로 HTTP 요청(POST)을 보내는 일이다.
  2) API 키는 코드에 적지 않고 환경 변수(OPENROUTER_API_KEY)에서 읽는다.
  3) 이 스크립트는 "질문 → 답" 한 번으로 끝난다. 파일을 고치거나 명령을 실행하지 못한다.
     (그 일까지 하는 프로그램이 "에이전트"다. 이 과정에서는 OpenCode 를 쓴다.)

사용법 (dev 컨테이너 안에서)
  python scripts/ask_ai.py "FastAPI 가 뭐야? 두 문장으로 알려 줘"
  python scripts/ask_ai.py --file app/main.py "이 코드를 한 줄씩 설명해 줘"
  python scripts/ask_ai.py --model google/gemma-4-31b-it:free "안녕"
"""

import argparse
import os
import sys
from pathlib import Path

import httpx

# OpenRouter 의 채팅 주소. 어떤 회사의 모델이든 이 주소 하나로 부른다.
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-haiku-5.5"

# 상태 코드별 안내 문구 (자주 만나는 것만)
ERROR_HINTS = {
    401: "API 키가 틀렸습니다. .env 의 OPENROUTER_API_KEY 값을 확인하세요.",
    402: "크레딧이 부족합니다. https://openrouter.ai/credits 에서 잔액을 확인하세요.",
    404: "모델 이름이 틀렸습니다. https://openrouter.ai/models 에서 이름을 확인하세요.",
    429: "요청이 너무 많습니다(사용 한도). 잠시 뒤에 다시 시도하세요.",
}


def build_prompt(question: str, file_path: str | None) -> str:
    """질문 글을 만든다. --file 을 줬으면 파일 내용을 질문 아래에 붙인다."""
    if file_path is None:
        return question
    text = Path(file_path).read_text(encoding="utf-8")
    return f"{question}\n\n--- {file_path} ---\n{text}"


def ask(prompt: str, model: str, api_key: str) -> dict:
    """OpenRouter 에 요청을 보내고, 응답(JSON)을 딕셔너리로 돌려준다."""
    response = httpx.post(
        API_URL,
        # "나는 이 키의 주인입니다"라고 알리는 부분
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,  # 어떤 모델에게 물을지
            "messages": [
                # system: AI 에게 주는 기본 지시 / user: 내가 하는 질문
                {"role": "system", "content": "초보자에게 설명하듯 쉬운 한국어로 답한다."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=120,  # 답이 올 때까지 최대 120초 기다린다
    )
    if response.status_code != 200:
        hint = ERROR_HINTS.get(response.status_code, "응답 내용을 읽고 원인을 찾아보세요.")
        print(f"[실패] 상태 코드 {response.status_code}: {hint}")
        print(response.text[:500])
        sys.exit(1)
    return response.json()


def main() -> None:
    # 명령줄에서 받을 값들을 정한다.
    parser = argparse.ArgumentParser(description="OpenRouter 로 AI 모델에게 질문하기")
    parser.add_argument("question", help="AI 에게 할 질문")
    parser.add_argument("--file", help="질문과 함께 보낼 파일 경로")
    parser.add_argument("--model", help="사용할 모델 이름 (기본: .env 의 OPENROUTER_MODEL)")
    args = parser.parse_args()

    # 키와 모델을 환경 변수에서 읽는다. (.env → docker-compose.yml → 컨테이너의 환경 변수)
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    model = args.model or os.environ.get("OPENROUTER_MODEL") or DEFAULT_MODEL
    if not api_key:
        print("[실패] OPENROUTER_API_KEY 가 비어 있습니다.")
        print("  1) .env 파일에 키를 적었는지 확인하세요.")
        print("  2) 컨테이너를 다시 만드세요: docker compose up -d  (윈도우 PowerShell 에서)")
        sys.exit(1)

    data = ask(build_prompt(args.question, args.file), model, api_key)

    # 응답에서 필요한 부분만 꺼내 보여 준다.
    print(f"[모델] {data.get('model', model)}")
    print("[답변]")
    print(data["choices"][0]["message"]["content"])
    usage = data.get("usage", {})
    # 토큰: AI 가 글을 세는 단위. 보낸 양(prompt)과 받은 양(completion)에 따라 요금이 정해진다.
    print(f"[사용량] 보낸 토큰 {usage.get('prompt_tokens')} / 받은 토큰 {usage.get('completion_tokens')}")


if __name__ == "__main__":
    main()
