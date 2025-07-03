from fastapi import FastAPI
from fastapi import HTTPException


app = FastAPI()

# In-memory item list
tasks = []

# POST route to add an item (via query param)
@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.post("/tasks")
def add_task(task: str):
    tasks.append(task)
    return f"Task {task} added"

@app.get("/task/{task_id}")
def get_task(task_id: int):
    if task_id < 0 or task_id >= len(tasks):
       
       raise HTTPException(status_code=404, detail="Task not found: Client Issue")
    task = tasks[task_id]
    return {"task": task}
   

@app.put("/tasks/{task_id}")
def update_task(task_id: int, new_task: str):
    if task_id < 0 or task_id >= len(tasks):
       raise HTTPException(status_code=404, detail="Task not found: Client Issue")
    
    tasks[task_id] = new_task
    return f"New task list: {tasks}"

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id < 0 or task_id >= len(tasks):
       
       raise HTTPException(status_code=404, detail="Task not found: Client Issue")
    tasks.remove(tasks[task_id])
    return f"task has been deletd"