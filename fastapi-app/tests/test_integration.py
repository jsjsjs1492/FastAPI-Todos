import requests
from datetime import date

BASE_URL = "http://3.37.127.42:8000"
TEST_TODO_ID = 9999  # 테스트용 고유 ID (단, 서버에서 ID를 수동으로 넣는 게 안될 수도 있음)

def test_full_todo_flow():
    # 1. 루트 엔드포인트 확인
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Todo App" in response.text or "To-Do List" in response.text

    # 2. 전체 TODO 조회
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # 3. TODO 생성
    new_todo = {
        "title": "Integration Test Todo",
        "description": "Created during CI integration test",
        "priority": "low",
        "due_date": str(date.today())
    }
    response = requests.post(f"{BASE_URL}/todos", json=new_todo)
    assert response.status_code in [200, 201], f"Failed to create: {response.text}"
    
    created_todo = response.json()
    todo_id = created_todo.get("id")
    assert todo_id, "No ID returned from creation"

    # 4. 단일 TODO 조회
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == new_todo["title"]

    # 5. TODO 삭제
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200

    # 6. 삭제 확인
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 404
