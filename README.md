# Task Manager Intern App

Build a simple Task Manager a REST API in Python using FastAPI, storing data in SQLite, with html, js frontend.

## Prerequisites:
1. Install uv tool:

```bash
# Using pip
pip install uv

# Using Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Create and activate virtual environment:
```bash 
# Using uv (creates and activates by default)
uv venv

# Using virtualenv (macOS/Linux)
macOS/Linux: python -m venv .venv && source .venv/bin/activate 

# Using virtualenv (Windows)
(PowerShell): .venv\Scripts\Activate.ps1
```

## Run project
1. Unzip the app
```bash
unzip karanja_andrew_taskmanager.zip
```
2. Navigate to the project
```bash
cd  task-manager
```

3. Install packages
```bash
# 3.1 Using uv
uv sync

# 3.2 Using uv requirements.txt
uv pip install -r requirements.txt 

# 3.3 Using pip
pip install -r requirements.txt
```

4. Run the app
```bash
uv run fastapi dev
```

### Considerations I made:
Since use of orm(sqlalchemy or any wrappers/helpers) was strictly discouraged, I decided to create a custom db wrapper using [sqlite3](src/db.py). This file converts python pydantic type to pure sqlite types
```python
    def _map_type(self, py_type) -> str:
        if hasattr(py_type, "__args__"):
            py_type = py_type.__args__[0]

        mappings = {int: "INTEGER", str: "TEXT", bool: "INTEGER", float: "REAL", bytes: "BLOB"} # add other types if need be

        return mappings.get(py_type, "TEXT")
```

### Challenges I encounted:
1. Python is not a core language that I use as a daily driver, thus I struggled with recalling documentation.
2. FastAPI is heavily batteries included, thus it contains some add-ons that make dev-exp easy. For example, defining db and initializing the tables on the fly is already just plug and play.
```python
from sqlmodel import create_engine

sqlite_url = "sqlite:///./database.db"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
```

### Future Add-ons
1. Adding authentication and rate-limiting would be a nice touch