import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List
from typing import Optional

# To-Do 항목 데이터 모델
class TodoItem(BaseModel):
    id: Optional[int] = None   # id는 자동 생성
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    completed: bool = False

TODO_FILE = "todo.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_todos(data):
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


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

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")