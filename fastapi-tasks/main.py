from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

# class for Creating Tasks
class TaskCreate(BaseModel):
    title: str
    description: str | None = None  # pipe operator (|) allows optional fields with NOne as a default value.
    completed: bool = False         # this line is necessary to be able to update "completed": true, so that a task is updated as "completed".

class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool = False

# --- HElPER FUNCTIONS ---

def load_tasks():
    tasks_list = []

    if not os.path.exists("tasks.txt"):
        print(f"DEBUG: File 'tasks.txt' not found. Returning empty list.")
        return []

    try:
        with open("tasks.txt", "r") as f:

            for line in f:
                clean_line = line.strip()
                if clean_line:  # if line is not empty
                    tasks_list.append(json.loads(clean_line)) # converts JSON lines into --> Python dictionary.
                # .loads() reads each line in the loop, strips whitespace, and parses the JSON. 

        print(f"DEBUG: Successfully loaded {len(tasks_list)} tasks.")
        return tasks_list
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"DEBUG: Error loading file: {e}. Returning empty list.")
        return []

# Writes your entire task list back to the file. 
def save_tasks(tasks):
    with open("tasks.txt",  "w") as f_out:
        for task in tasks:
            json_line = json.dumps(task)
            f_out.write(json_line + "\n")

        print(f"DEBUG: Tasks successfully saved to 'tasks.txt'. Total tasks: {len(tasks)}")

def get_next_id(tasks):
    if not tasks:
        return 1
    next_id = max(t['id'] for t in tasks) + 1
    print(f"DEBUG: Generated next sequential ID: {next_id}") 
    return next_id

# --- ENDPOINTS ---

# GET /
# Performs "Health Check"
@app.get("/")
def get_root():
    print("DEBUG: Root health check performed.")
    return {"status": "healthy", "message": "FastAPI Task Management System is running."}

# GET /tasks
@app.get("/tasks", response_model=list[Task])
def get_tasks(completed: bool | None = None):
    tasks = load_tasks()

    if completed is not None:       # check if user added a filter to the URL
        print(f"DEBUG: Filtering tasks by completed={completed}")
        return [t for t in tasks if t['completed'] == completed]  
    return tasks

# GET /tasks/stats
@app.get("/tasks/stats")
def get_summary():
    tasks = load_tasks()
    total = len(tasks)
    completed = len([t for t in tasks if t['completed']])   
    pending = total - completed
    percent = (completed / total * 100) if total > 0 else 0
    return {
        "total_tasks": total,
        "completed_count": completed,
        "pending_count": pending,
        "completion_percentage": f"{percent:.2f}%"
    }

# GET /tasks/{id}
@app.get("/tasks/{id}", response_model=Task)
def get_task_by_id(id: int):
    print(f"DEBUG: Searching for Task ID: {id}")
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == id:
            print(f"DEBUG: Task {id} found.")
            return t
    print(f"DEBUG: Task {id} not found.")
    raise HTTPException(status_code=404, detail="Task not found")

# POST /tasks
@app.post("/tasks", response_model=Task)
def create_task(task_in: TaskCreate):
    tasks = load_tasks()
    new_task = {
        "id": get_next_id(tasks),
        "title": task_in.title,
        "description": task_in.description,
        "completed": False
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"DEBUG: New task created: {new_task['title']} (ID: {new_task['id']})")
    return new_task

# PUT /tasks/{id}
# no print yet
@app.put("/tasks/{id}", response_model=Task)
def modify_task(id: int, task_update: TaskCreate):
    tasks = load_tasks()
    for t in tasks:
        if t['id'] == id:
            t.update(task_update.dict(exclude_unset=True))  # .dict() deperecated, better to use .model_dump(). but for this lab it should have backwards compatability.
            save_tasks(tasks)
            print(f"DEBUG: Task {id} successfully updated.") # ADD THIS
            return t
    print(f"DEBUG: Update failed. Task {id} not found in storage.")
    raise HTTPException(status_code=404, detail="Task not found")

# DELETE /tasks/{id}
@app.delete("/tasks/{id}")
def remove_task(id: int):
    print(f"DEBUG: Attempting to delete Task ID: {id}")
    tasks = load_tasks()
    initial_len = len(tasks)
    tasks = [t for t in tasks if t['id'] != id]
    if len(tasks) == initial_len:
        print(f"DEBUG: Delete failed. Task {id} does not exist.")
        raise HTTPException(status_code=404, detail="Task not found")
    save_tasks(tasks)
    print(f"DEBUG: Task {id} deleted successfully.")
    return {"message": "Task deleted successfully"}

# DELETE /tasks
@app.delete("/tasks")
def delete_all_tasks():
    print("DEBUG: Request received to clear all tasks.")
    save_tasks([])  # rewrites the entire file as empty.
    print("DEBUG: All tasks cleared from tasks.txt.")
    return {"message": "All tasks cleared"}