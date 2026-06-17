"""
db_tracking.py
--------------

FastAPI router for database inspection and maintenance.

Endpoints:
- GET /db/tables → list all tables
- GET /db/table/{table_name} → view first 20 rows
- POST /db/reset → drop & recreate schema (dev/demo only)

Note:
Use `/reset` cautiously. It deletes all data and should be restricted in production.
"""
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.db.db import Base, engine, get_db
from backend.db import models  # noqa: F401 (needed for table registration)

router = APIRouter()

@router.get("/tables")
def list_tables(db: Session = Depends(get_db)):
    """Return all table names in the database."""
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    return {"tables": [row[0] for row in result]}

@router.get("/table/{table_name}")
def view_table(table_name: str, db: Session = Depends(get_db)):
    """Return first 20 rows from the given table."""
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 20;"))
    rows = [dict(row._mapping) for row in result]
    return {"table": table_name, "rows": rows}

# curl -X POST http://localhost:8000/db/reset
@router.post("/reset")
def reset_database(db: Session = Depends(get_db)): # noqa: F841
    """Drop and recreate all tables (dev/demo only)."""
    try:
        Base.metadata.drop_all(bind=engine)   # wipe schema + data
        Base.metadata.create_all(bind=engine) # rebuild from models
        return {"status": "success", "message": "Database reset complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# curl -X POST http://localhost:8000/db/delete-db
@router.post("/delete-db")
def delete_database_file():
    db_path = engine.url.database  # actual file path SQLAlchemy is using
    if db_path and os.path.exists(db_path):
        os.remove(db_path)
        return {"status": "success", "message": f"Deleted {db_path}"}
    return {"status": "error", "message": f"Database file not found at {db_path}"}


