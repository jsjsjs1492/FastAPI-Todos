from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
from datetime import date, datetime

app = FastAPI()

# Data model
class TodoItem(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    completed: bool = False
    priority: str = "medium"  # high, medium, low
    due_date: Optional[date] = None

# File path for storing todos
TODOS_FILE = "todos.json"

# Helper functions for data persistence
def load_todos():
    if not os.path.exists(TODOS_FILE):
        return []
    with open(TODOS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_todos(todos):
    with open(TODOS_FILE, "w") as f:
        # Convert date objects to strings for JSON serialization
        serializable_todos = []
        for todo in todos:
            todo_copy = dict(todo)
            if "due_date" in todo_copy and todo_copy["due_date"] is not None:
                if isinstance(todo_copy["due_date"], date):
                    todo_copy["due_date"] = todo_copy["due_date"].isoformat()
            serializable_todos.append(todo_copy)
        json.dump(serializable_todos, f)

# API endpoints
@app.get("/todos", response_model=List[TodoItem])
def get_todos():
    return load_todos()

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo_by_id(todo_id: int):
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    
    # Generate new ID
    new_id = 1
    if todos:
        new_id = max(todo["id"] for todo in todos) + 1
    
    todo_dict = todo.dict()
    todo_dict["id"] = new_id
    
    todos.append(todo_dict)
    save_todos(todos)
    return todo_dict

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            # Preserve the ID
            updated_dict = updated_todo.dict()
            updated_dict["id"] = todo_id
            todos[i] = updated_dict
            save_todos(todos)
            return updated_dict
    
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            del todos[i]
            save_todos(todos)
            return {"message": "To-Do item deleted"}
    
    # Changed to 404 to match test expectations
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}/complete", response_model=TodoItem)
def toggle_complete(todo_id: int):
    todos = load_todos()
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            # Toggle the completed status
            todo["completed"] = not todo["completed"]
            save_todos(todos)
            return todo
    
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.get("/todos/overdue", response_model=List[TodoItem])
def get_overdue_todos():
    todos = load_todos()
    today = date.today()
    
    overdue_todos = []
    for todo in todos:
        if (todo.get("due_date") and 
            not todo.get("completed") and 
            datetime.fromisoformat(todo["due_date"]).date() < today):
            overdue_todos.append(todo)
    
    return overdue_todos

@app.put("/todos/{todo_id}/priority", response_model=TodoItem)
def update_priority(todo_id: int, priority: str):
    if priority not in ["high", "medium", "low"]:
        raise HTTPException(status_code=400, detail="Invalid priority value")
    
    todos = load_todos()
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todo["priority"] = priority
            save_todos(todos)
            return todo
    
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.put("/todos/{todo_id}/due-date", response_model=TodoItem)
def update_due_date(todo_id: int, due_date: Optional[date] = None):
    todos = load_todos()
    
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todo["due_date"] = due_date.isoformat() if due_date else None
            save_todos(todos)
            return todo
    
    raise HTTPException(status_code=404, detail="To-Do item not found")