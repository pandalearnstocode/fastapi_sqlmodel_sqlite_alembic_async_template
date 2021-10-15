from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession # this is new line
from app.db import init_db, get_session # init_db is a new function
from app.models import Task, TaskCreate

# Changes all the function has been changed to async
# session has been changed to AsyncSession

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/ping")
async def pong():
    return {"ping": "pong!"}

@app.post("/task/", response_model=Task)
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    task = Task(task_name=task.task_name)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task