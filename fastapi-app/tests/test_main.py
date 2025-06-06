import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전 초기화
    save_todos([])
    yield
    # 테스트 후 정리
    save_todos([])

# 상태 관리 테스트
def test_load_save_todos():
    # 빈 상태에서 시작
    todos = load_todos()
    assert todos == []
    
    # 데이터 저장
    test_data = [{"id": 1, "title": "Test", "description": "Test description", "completed": False, "priority": "high", "due_date": None, "category": "general"}]
    save_todos(test_data)
    
    # 데이터 로드 확인
    loaded_data = load_todos()
    assert loaded_data == test_data

# 데이터 모델링 테스트
def test_todo_item_model():
    # 기본 모델 생성
    todo = TodoItem(title="Test", description="Test description")
    assert todo.id is None
    assert todo.title == "Test"
    assert todo.description == "Test description"
    assert todo.completed is False
    assert todo.priority == "medium"  # 기본값 확인
    assert todo.due_date is None
    assert todo.category == "general"  # 기본 카테고리 확인
    
    # 모든 필드 지정
    today = date.today()
    todo_full = TodoItem(
        id=1, 
        title="Full Test", 
        description="Full description", 
        completed=True, 
        priority="high",
        due_date=today,
        category="work"
    )
    assert todo_full.id == 1
    assert todo_full.title == "Full Test"
    assert todo_full.description == "Full description"
    assert todo_full.completed is True
    assert todo_full.priority == "high"
    assert todo_full.due_date == today
    assert todo_full.category == "work"

# API CRUD 테스트
def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False, priority="high", category="work")
    save_todos([todo.dict()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"
    assert response.json()[0]["priority"] == "high"
    assert response.json()[0]["category"] == "work"

def test_get_todo_by_id():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False, category="home")
    save_todos([todo.dict()])
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
    assert response.json()["category"] == "home"

def test_get_todo_by_id_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404

def test_create_todo():
    todo = {
        "title": "New Todo", 
        "description": "New description", 
        "priority": "low", 
        "due_date": str(date.today()),
        "category": "personal"
    }
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["title"] == "New Todo"
    assert response.json()["priority"] == "low"
    assert response.json()["due_date"] is not None
    assert response.json()["category"] == "personal"

def test_create_todo_invalid():
    # 필수 필드 누락
    todo = {"title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422
    
    # 잘못된 우선순위
    todo = {"title": "Test", "description": "Test", "priority": "invalid"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    updated_todo = {
        "title": "Updated", 
        "description": "Updated description", 
        "completed": True,
        "priority": "high",
        "due_date": str(date.today()),
        "category": "study"
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["priority"] == "high"
    assert response.json()["due_date"] is not None
    assert response.json()["category"] == "study"

def test_update_todo_not_found():
    updated_todo = {"title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/999", json=updated_todo)
    assert response.status_code == 404

def test_delete_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
    
    # 삭제 확인
    todos = load_todos()
    assert len(todos) == 0

def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_priority():
    todo = TodoItem(id=1, title="Test", description="Test description", priority="medium")
    save_todos([todo.dict()])
    
    # JSON 객체로 보내기
    response = client.put("/todos/1/priority", json={"priority": "high"})
    assert response.status_code == 200
    assert response.json()["priority"] == "high"
    
    # 잘못된 우선순위
    response = client.put("/todos/1/priority", json={"priority": "invalid"})
    assert response.status_code == 400
    
def test_update_due_date():
    todo = TodoItem(id=1, title="Test", description="Test description")
    save_todos([todo.dict()])
    
    today = date.today()
    response = client.put("/todos/1/due-date", json=str(today))
    assert response.status_code == 200
    assert response.json()["due_date"] is not None
    
    # 날짜 제거
    response = client.put("/todos/1/due-date", json=None)
    assert response.status_code == 200
    assert response.json()["due_date"] is None

def test_toggle_complete():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    
    # 완료로 변경
    response = client.put("/todos/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True
    
    # 미완료로 변경
    response = client.put("/todos/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is False

def test_get_overdue_todos():
    # 오늘 할 일
    todo1 = TodoItem(
        id=1, 
        title="Today", 
        description="Today's task", 
        due_date=date.today()
    )
    
    # 지난 할 일
    todo2 = TodoItem(
        id=2, 
        title="Overdue", 
        description="Overdue task", 
        due_date=date.today() - timedelta(days=1)
    )
    
    # 미래 할 일
    todo3 = TodoItem(
        id=3, 
        title="Future", 
        description="Future task", 
        due_date=date.today() + timedelta(days=1)
    )
    
    # 마감일 없는 할 일
    todo4 = TodoItem(
        id=4, 
        title="No Due Date", 
        description="Task without due date"
    )
    
    save_todos([todo1.dict(), todo2.dict(), todo3.dict(), todo4.dict()])
    
    response = client.get("/todos/overdue")
    assert response.status_code == 200
    overdue_todos = response.json()
    
    # 지난 할 일만 반환되어야 함
    assert len(overdue_todos) == 1
    assert overdue_todos[0]["id"] == 2
    assert overdue_todos[0]["title"] == "Overdue"

def test_update_category():
    todo = TodoItem(id=1, title="Test", description="Test description", category="general")
    save_todos([todo.dict()])
    
    # JSON 객체로 보내기
    response = client.put("/todos/1/category", json={"category": "work"})
    assert response.status_code == 200
    assert response.json()["category"] == "work"
    
    # 빈 카테고리는 general로 설정
    response = client.put("/todos/1/category", json={"category": ""})
    assert response.status_code == 200
    assert response.json()["category"] == "general"