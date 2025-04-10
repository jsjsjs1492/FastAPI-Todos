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

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test"

def test_create_todo():
    todo = {"title": "Test", "description": "Test description", "completed": False}
    response = client.post("/todos", json=todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_create_todo_invalid():
    todo = {"title": "Test"}  # Missing required description field
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    updated_todo = {"title": "Updated", "description": "Updated description", "completed": True}
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"

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
    
    # Verify todo was actually deleted
    todos = load_todos()
    assert len(todos) == 0
    
def test_delete_todo_not_found():
    # Fixed: Should expect 404 for non-existent todo
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_todo_by_id():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test"

def test_get_todo_by_id_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404

def test_toggle_complete():
    todo = TodoItem(id=1, title="Test", description="Test description", completed=False)
    save_todos([todo.dict()])
    
    # Toggle to completed
    response = client.put("/todos/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True
    
    # Toggle back to not completed
    response = client.put("/todos/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is False