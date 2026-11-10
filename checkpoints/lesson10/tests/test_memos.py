"""
test_memos.py - 메모 CRUD 테스트

이 파일이 보여 주는 개념
  1) 요구사항 명세(harness/REQUIREMENTS.md)의 번호(R1, R2 ...)마다 테스트가 있다.
     → "요구사항을 지켰는가?"를 사람이 눈으로 보지 않고 명령 한 줄로 확인한다.
  2) 정상 경우뿐 아니라 "잘못된 경우"(없는 번호, 빈 제목)도 테스트한다.
"""


def make_memo(client, title="장보기", content="우유, 달걀"):
    """테스트에서 자주 쓰는 '메모 한 건 만들기'를 함수로 빼 두었다."""
    response = client.post("/memos", json={"title": title, "content": content})
    assert response.status_code == 201
    return response.json()


# ---------- R1. 메모 만들기 ----------
def test_create_memo(client):
    memo = make_memo(client)
    assert memo["id"] == 1  # 첫 메모의 번호는 1
    assert memo["title"] == "장보기"
    assert memo["content"] == "우유, 달걀"
    assert "created_at" in memo and "updated_at" in memo  # 시각이 함께 온다


def test_create_memo_without_content(client):
    # 내용을 안 보내면 빈 문자열로 저장된다.
    response = client.post("/memos", json={"title": "제목만"})
    assert response.status_code == 201
    assert response.json()["content"] == ""


# ---------- R2. 목록 보기 ----------
def test_list_memos_empty(client):
    response = client.get("/memos")
    assert response.status_code == 200
    assert response.json() == []  # 메모가 없으면 빈 목록


def test_list_memos_newest_first(client):
    make_memo(client, title="첫째")
    make_memo(client, title="둘째")
    titles = [memo["title"] for memo in client.get("/memos").json()]
    assert titles == ["둘째", "첫째"]  # 나중에 쓴 메모가 위에 온다


# ---------- R3. 한 건 보기 ----------
def test_get_memo(client):
    created = make_memo(client)
    response = client.get(f"/memos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "장보기"


def test_get_memo_not_found(client):
    response = client.get("/memos/999")  # 없는 번호
    assert response.status_code == 404
    assert response.json() == {"detail": "메모를 찾을 수 없습니다."}


# ---------- R4. 고치기 ----------
def test_update_memo(client):
    created = make_memo(client)
    response = client.put(
        f"/memos/{created['id']}", json={"title": "장보기(수정)", "content": "우유"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "장보기(수정)"
    # 다시 조회해도 바뀐 내용이 남아 있어야 한다(진짜로 저장되었는지 확인).
    assert client.get(f"/memos/{created['id']}").json()["content"] == "우유"


def test_update_memo_not_found(client):
    response = client.put("/memos/999", json={"title": "없음", "content": ""})
    assert response.status_code == 404


def test_update_memo_empty_title(client):
    # 고칠 때도 입력 규칙(R6)이 똑같이 적용된다.
    created = make_memo(client)
    response = client.put(f"/memos/{created['id']}", json={"title": "", "content": ""})
    assert response.status_code == 422
    # 실패한 수정은 저장되지 않아야 한다.
    assert client.get(f"/memos/{created['id']}").json()["title"] == "장보기"


# ---------- R5. 지우기 ----------
def test_delete_memo(client):
    created = make_memo(client)
    response = client.delete(f"/memos/{created['id']}")
    assert response.status_code == 204  # 성공했고 돌려줄 내용은 없음
    # 지운 뒤에는 조회되지 않아야 한다.
    assert client.get(f"/memos/{created['id']}").status_code == 404


def test_delete_memo_not_found(client):
    assert client.delete("/memos/999").status_code == 404


# ---------- R6. 입력 규칙 ----------
def test_create_memo_empty_title(client):
    response = client.post("/memos", json={"title": "", "content": "제목 없음"})
    assert response.status_code == 422  # 입력이 규칙에 맞지 않음


def test_create_memo_title_too_long(client):
    response = client.post("/memos", json={"title": "가" * 101})
    assert response.status_code == 422  # 제목은 100자까지


def test_create_memo_content_too_long(client):
    response = client.post("/memos", json={"title": "긴 내용", "content": "가" * 1001})
    assert response.status_code == 422  # 내용은 1000자까지



# ---------- R7. 웹 화면 ----------
def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "메모장" in response.text  # 화면에 '메모장'이라는 글자가 있다
