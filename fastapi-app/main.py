import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

# To-Do 항목 데이터 모델
class TodoItem(BaseModel):
    id: Optional[int] = None   # id는 자동 생성
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    completed: bool = False
    priority: str = "medium"  # 우선순위: high, medium, low
    due_date: Optional[date] = None  # 마감일

TODO_FILE = "todo.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                todos = json.load(f)
                # Convert string dates back to date objects
                for todo in todos:
                    if todo.get("due_date"):
                        todo["due_date"] = datetime.fromisoformat(todo["due_date"]).date()
                return todos
        except json.JSONDecodeError:
            return []
    return []

def save_todos(data):
    # Convert date objects to strings for JSON serialization
    serializable_data = []
    for todo in data:
        todo_copy = dict(todo)
        if todo_copy.get("due_date") and not isinstance(todo_copy["due_date"], str):
            todo_copy["due_date"] = todo_copy["due_date"].isoformat()
        serializable_data.append(todo_copy)
    
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=4, ensure_ascii=False)


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (OPTIONS 포함)
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

@app.get("/todos", response_model=List[TodoItem])
def get_todo():
    return load_todos()

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    new_id = max([t["id"] for t in todos], default=0) + 1  # 새로운 ID 생성
    todo.id = new_id
    todos.append(todo.dict())
    save_todos(todos)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update(updated_todo.dict(exclude={"id"}))  # id 제외하고 업데이트
            save_todos(todos)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    new_todos = [todo for todo in todos if todo["id"] != todo_id]
    if len(new_todos) == len(todos):
        raise HTTPException(status_code=404, detail="To-Do item not found")
    save_todos(new_todos)
    return {"message": "To-Do item deleted"}

@app.put("/todos/{todo_id}/complete")
def complete_todo(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}/priority")
def update_priority(todo_id: int, priority: str):
    if priority not in ["high", "medium", "low"]:
        raise HTTPException(status_code=400, detail="Priority must be high, medium, or low")
    
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["priority"] = priority
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}/due-date")
def update_due_date(todo_id: int, due_date: Optional[date] = None):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["due_date"] = due_date
            save_todos(todos)
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.get("/todos/overdue")
def get_overdue_todos():
    todos = load_todos()
    today = date.today()
    overdue_todos = [todo for todo in todos if todo.get("due_date") and 
                     not todo["completed"] and 
                     datetime.fromisoformat(todo["due_date"]).date() < today]
    return overdue_todos

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo_by_id(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")