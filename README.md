# Creating a minimal Fast API app for local development: FastAPI + SQLModel + SQLite + Alembic [Async version]

This is example template which can be used for local development.

## Workflow:

* write database models
* write database settings
* write endpoints
* test apis
* setup alembic
* change database models
* update apis
* run alembic migration
* test apis


## Detailed walk through

### Prerequisite:

* Anaconda
* DB browser for SQLite
* curl

### Project structure

```
.
├── app
│   ├── db.py : All the settings related to db will be here.
│   ├── __init__.py
│   ├── main.py : All endpoints will be defined here.
│   └── models.py : All the data models will be defined here.
└── database.db : This SQLite DB will be created and data will be stored here.

```

### Step 1: Setup development environment

```
conda create --name fastapi_sqlmodel python=3.8
conda activate fastapi_sqlmodel
pip install fastapi[all] sqlmodel alembic aiosqlite
```

### Step 2: Create models in `models.py`

```python
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    task_name: str

class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass
```


### Step 3: Create settings related to DB in `db.py`

```python
from sqlmodel import Session, SQLModel, create_engine
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Step 4: Define API endpoints in `main.py`

```python
from fastapi import FastAPI, Depends
from sqlmodel import Session
from app.db import create_db_and_tables, get_session
from app.models import Task, TaskCreate

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/ping")
def pong():
    return {"ping": "pong!"}

@app.post("/task/", response_model=Task)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```
### Step 5: Test API endpoints


```bash
uvicorn app.main:app --reload
curl -X POST http://127.0.0.1:8000/task/ -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"task_name": "just added task"}'
```

__Note:__

* a `database.db` file will be create in project root directory.
* after making the post call validate the db records are being updated using `DB browser for SQLite`

### Step 6: Setup alembic

#### Step 6a: Generate alembic settings

```bash
alembic init -t async alembic
```

#### Step 6b: Update alembic settings

* replace `sqlalchemy.url = driver://user:pass@localhost/dbname` in `alembic.ini` with `sqlite+aiosqlite:///database.db`.
* in `alembic/env.py` file add `from sqlmodel import SQLModel` in the import section.
* in `alembic/env.py` file add the following line in import section, `from app.models import Task`.
* in `alembic/env.py` change `target_metadata = None` to `target_metadata = SQLModel.metadata`.
* in `alembic/script.py.mako` add `import sqlmodel` in the import section.


#### Step 6c: Generate alembic migration settings

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### Step 7: Update data models in `models.py`

```python
from sqlmodel import SQLModel, Field
from typing import Optional # This is a new add line

class TaskBase(SQLModel):
    task_name: str
    task_description: Optional[str] = None # This is a new add line

class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)

class TaskCreate(TaskBase):
    pass
```

### Step 8: Update API endpoints in `main.py`

In this case, endpoints remains unchanged but in a realistic scenario endpoints has to be changed to take the new information into account.

### Step 9: Run DB migration

```bash
alembic revision --autogenerate -m "add description"
alembic upgrade head
```

### Step 10: Test updated API endpoints

```bash
uvicorn app.main:app --reload
curl -X POST http://127.0.0.1:8000/task/ -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"task_name": "just added task","task_description":"a newly created task"}'
```
* after making the post call validate the db records are being updated using `DB browser for SQLite`

### Reference:

* https://testdriven.io/blog/fastapi-sqlmodel/
* https://fastapi.tiangolo.com/advanced/async-sql-databases/
* https://github.com/encode/databases
* https://github.com/testdrivenio/fastapi-sqlmodel-alembic
* https://github.com/Lance0404/asiayo-rest-sql
* https://fastapi.tiangolo.com/tutorial/sql-databases/
* https://github.cdnweb.icu/smartgic/shortgic
* https://testdriven.io/blog/fastapi-sqlmodel/
* https://python.plainenglish.io/building-a-phone-directory-with-mysql-fastapi-and-angular-cd48673904f4
* https://alembic.sqlalchemy.org/en/latest/autogenerate.html
* https://towardsdatascience.com/build-an-async-python-service-with-fastapi-sqlalchemy-196d8792fa08
* https://hackernoon.com/how-to-set-up-fastapi-ormar-and-alembic