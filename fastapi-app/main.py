import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# To-Do 항목에 대한 데이터 모델 정의
class TodoItem(BaseModel):
    id: int  # 할 일 ID (고유한 값)
    title: str = Field(..., min_length=1)  # 제목, 최소 1글자
    description: str = Field(..., min_length=1)  # 설명, 최소 1글자
    completed: bool  # 완료 여부

TODO_FILE = "todo.json"  # To-Do 데이터가 저장될 파일

# 저장된 할 일 목록을 불러오는 함수
def load_todos():
    if os.path.exists(TODO_FILE):  # 파일이 존재하는지 확인
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)  # JSON 파일에서 데이터 로드
        except json.JSONDecodeError:  # JSON 파싱 오류 처리
            return []  # 파싱 오류가 나면 빈 리스트 반환
    return []  # 파일이 없으면 빈 리스트 반환

# 할 일 목록을 파일에 저장하는 함수
def save_todos(data):
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)  # JSON 형식으로 저장

app = FastAPI()  # FastAPI 앱 인스턴스 생성

# 모든 할 일 항목을 불러오는 API
@app.get("/todos", response_model=list[TodoItem])
def get_todo():
    return load_todos()  # 할 일 목록 반환

# 새로운 할 일을 추가하는 API
@app.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoItem):
    todos = load_todos()  # 현재 할 일 목록 불러오기
    # id를 가장 큰 값 + 1로 설정
    new_id = max([t['id'] for t in todos], default=0) + 1
    todo.id = new_id  # 새 할 일의 id를 새로 생성된 id로 설정
    todos.append(todo.dict())  # 새로운 할 일 추가
    save_todos(todos)  # 파일에 저장
    return todo  # 추가된 할 일 반환

# 특정 ID의 할 일을 수정하는 API
@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, updated_todo: TodoItem):
    todos = load_todos()  # 할 일 목록 불러오기
    for todo in todos:
        if todo['id'] == todo_id:  # 해당 ID의 할 일 찾기
            todo.update(updated_todo.dict())  # 할 일 수정
            save_todos(todos)  # 수정된 목록 저장
            return updated_todo  # 수정된 할 일 반환
    raise HTTPException(status_code=404, detail="To-Do item not found")  # 할 일이 없으면 404 오류 반환

# 특정 ID의 할 일을 삭제하는 API
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    todos = load_todos()  # 할 일 목록 불러오기
    new_todos = [todo for todo in todos if todo["id"] != todo_id]  # 해당 ID의 할 일 삭제
    if len(new_todos) == len(todos):  # 삭제된 항목이 없다면 오류 발생
        raise HTTPException(status_code=404, detail="To-Do item not found")
    save_todos(new_todos)  # 새로운 목록 저장
    return {"message": "To-Do item deleted"}  # 삭제된 메시지 반환

# 할 일 완료/취소 API
@app.put("/todos/{todo_id}/complete")
def complete_todo(todo_id: int):
    todos = load_todos()  # 할 일 목록 불러오기
    for todo in todos:
        if todo['id'] == todo_id:  # 해당 ID의 할 일 찾기
            todo['completed'] = not todo['completed']  # 완료 상태 반전
            save_todos(todos)  # 수정된 목록 저장
            return todo  # 수정된 할 일 반환
    raise HTTPException(status_code=404, detail="To-Do item not found")  # 할 일이 없으면 404 오류 반환

# HTML 페이지를 반환하는 루트 경로
@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())  # HTML 파일 읽어 반환
    except FileNotFoundError:  # HTML 파일이 없으면 오류 발생
        raise HTTPException(status_code=404, detail="HTML file not found")
