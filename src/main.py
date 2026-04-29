from datetime import datetime, timezone
import sqlite3
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.middleware.cors import CORSMiddleware

from .db import SqlWrapper


from .models import Tasks, TasksCreate, TasksRead, TasksUpdate

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

db = SqlWrapper("task_manager_db", models=[Tasks])


@app.exception_handler(RequestValidationError)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Input validation failed"},
    )


@app.get("/")
async def root():
    return {"message": "Hello world"}


# Lists all tasks
@app.get("/tasks", response_model=list[TasksRead])
async def get_tasks():
    try:
        return db.query("SELECT * FROM tasks")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Creates a task
@app.post("/tasks", response_model=TasksRead, status_code=201)
async def create_tasks(task_in: TasksCreate):
    now = datetime.now(timezone.utc).isoformat()
    sql = "INSERT INTO tasks (title, description, completed, created_at, updated_at) VALUES (?, ?, ?, ?, ?)"
    params = (task_in.title, task_in.description, task_in.completed, now, now)
    try:
        last_id = db.execute(sql, params)
        created_task = db.query("SELECT * FROM tasks WHERE id = ?", (last_id,))

        if not created_task:
            raise HTTPException(
                status_code=500, detail="Record saved but could not get retrived."
            )
        return created_task[0]

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Get a single task
@app.get("/tasks/{id}", response_model=TasksRead)
async def get_task(id: int):
    try:
        results = db.query("SELECT *FROM tasks WHERE id = ?", (id,))

        if not results:
            raise HTTPException(status_code=404, detail=f"Task with id {id} not found")
        return results[0]

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Updates a task
@app.put("/tasks/{id}", response_model=TasksRead)
async def update_task(id: int, task_up: TasksUpdate):

    try:
        exists = db.query("SELECT *FROM tasks WHERE id = ?", (id,))
        if not exists:
            raise HTTPException(status_code=404, detail=f"Task with id {id} not found")

        update_data = task_up.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided")

        items_to_update = []
        params = []

        for k, v in update_data.items():
            items_to_update.append(f"{k} = ?")
            params.append(v)

        items_to_update.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())

        params.append(
            id,
        )

        sql = f"UPDATE tasks SET {', '.join(items_to_update)} WHERE id = ?"
        db.execute(sql, tuple(params))

        updated_task = db.query("SELECT * FROM tasks WHERE id = ?", (id,))
        return updated_task[0]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/tasks/{id}")
async def delete_task(id: int):
    try:
        exists = db.query("SELECT *FROM tasks WHERE id = ?", (id,))
        if not exists:
            raise HTTPException(status_code=404, detail=f"Task with id {id} not found")

        db.execute("DELETE FROM tasks WHERE id=?", (id,))

        return {"message": f"task {id} deleted successfully"}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
