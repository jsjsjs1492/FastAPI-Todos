import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

class TodoItem(BaseModel):
    id : int
    title: str = Field(min_length=1)
    description: str
    completed : bool


TODO_FILE = "todo.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE,'r') as f:
            return json.load(f)
    return []

def save_todos(data):
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



app = FastAPI()

@app.get("/todos", response_model=list[TodoItem])
def get_todo():
    return load_todos()

# @app.post("/todos", response_model=TodoItem)
# def create_todo(Input_todo : TodoItem):
#     data = load_todos()
#     data.append(Input_todo.dic())
#     save_todos(data)
#     return Input_todo

@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()
    todos.append(todo.dict())
    save_todos(todos)
    return todo


@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo( todo_id : int ,updated_todo: TodoItem):
    data = load_todos()
    for todo in data:       
        if(todo['id'] == todo_id):
            todo.update(updated_todo.dic())
            save_todos(data)
            return updated_todo
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    data = load_todos()
    data = [todo for todo in data if todo["id"] != todo_id]

    save_todos(data)
    return {"message": "To-Do item deleted"}

    
    
   
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)

