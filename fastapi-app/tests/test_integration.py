import requests

BASE_URL = "http://3.37.127.42:8000"  # 실제 EC2 서버의 주소와 포트

def test_root_endpoint():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Welcome! This is Todo App + pytest + request!" in response.text

def test_read_todos():
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_todo():
    new_todo = {
        "id": 1000,
        "title": "Integration Test Todo",
        "description": "Created during CI integration test",
        "done": False
    }
    response = requests.post(f"{BASE_URL}/todos/", json=new_todo)
    assert response.status_code in [200, 201]

def test_read_single_todo():
    response = requests.get(f"{BASE_URL}/todos/1000")
    assert response.status_code == 200
    assert response.json()["id"] == 1000

def test_delete_todo():
    response = requests.delete(f"{BASE_URL}/todos/1000")
    assert response.status_code == 200
