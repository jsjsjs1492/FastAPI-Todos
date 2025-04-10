import requests

BASE_URL = "http://3.37.127.42:8000"
TEST_TODO_ID = 9999  # 테스트용 고유 ID (충돌 방지)

def test_full_todo_flow():
    # 1. 루트 엔드포인트 확인
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Todo App" in response.text

    # 2. 전체 TODO 조회
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # 3. TODO 생성
    new_todo = {
        "id": TEST_TODO_ID,
        "title": "Integration Test Todo",
        "description": "Created during CI integration test",
        "done": False
    }
    response = requests.post(f"{BASE_URL}/todos/", json=new_todo)
    assert response.status_code in [200, 201], f"Failed to create: {response.text}"

    # 4. 단일 TODO 조회
    response = requests.get(f"{BASE_URL}/todos/{TEST_TODO_ID}")
    assert response.status_code == 200
    assert response.json()["id"] == TEST_TODO_ID

    # 5. TODO 삭제
    response = requests.delete(f"{BASE_URL}/todos/{TEST_TODO_ID}")
    assert response.status_code == 200

    # 6. 삭제 확인
    response = requests.get(f"{BASE_URL}/todos/{TEST_TODO_ID}")
    assert response.status_code == 404
