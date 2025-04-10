import requests
from datetime import date

BASE_URL = "http://3.37.127.42:8000"  # 실제 서버 주소


def test_root_endpoint():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Todo App" in response.text or "To-Do List" in response.text


def test_crud_flow():
    # 1. 생성
    new_todo = {
        "title": "Integration Test",
        "description": "End-to-End test",
        "priority": "medium",
        "due_date": str(date.today())
    }
    response = requests.post(f"{BASE_URL}/todos", json=new_todo)
    assert response.status_code in [200, 201]
    created_todo = response.json()
    todo_id = created_todo.get("id")
    assert todo_id

    # 2. 단일 조회
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == new_todo["title"]

    # 3. 수정
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "completed": True,
        "priority": "high",
        "due_date": str(date.today())
    }
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["completed"] is True

    # 4. 우선순위 변경
    response = requests.put(f"{BASE_URL}/todos/{todo_id}/priority", json="low")
    assert response.status_code == 200
    assert response.json()["priority"] == "low"

    # 5. 마감일 제거
    response = requests.put(f"{BASE_URL}/todos/{todo_id}/due-date", json=None)
    assert response.status_code == 200
    assert response.json()["due_date"] is None

    # 6. 완료 토글
    response = requests.put(f"{BASE_URL}/todos/{todo_id}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is False  # 이전에 True였으므로 토글로 False 됨

    # 7. 삭제
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # 8. 삭제 확인
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 404


def test_overdue_filter():
    # 과거 할 일 생성
    past_date = str(date.today().replace(day=1))  # 그냥 예시로 1일로 고정
    todo = {
        "title": "Overdue Task",
        "description": "This is overdue",
        "priority": "medium",
        "due_date": past_date
    }
    create_response = requests.post(f"{BASE_URL}/todos", json=todo)
    assert create_response.status_code in [200, 201]
    todo_id = create_response.json()["id"]

    # 오버듀 조회
    response = requests.get(f"{BASE_URL}/todos/overdue")
    assert response.status_code == 200
    overdue_ids = [t["id"] for t in response.json()]
    assert todo_id in overdue_ids

    # 정리
    requests.delete(f"{BASE_URL}/todos/{todo_id}")
