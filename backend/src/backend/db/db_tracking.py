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
from backend.schemas.schemas import (
    TablesResponse,
    TableRowsResponse,
    ResetResponse,
    DeleteDBResponse,
)

router = APIRouter()

@router.get("/tables", response_model=TablesResponse)
def list_tables(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    return {"tables": [row[0] for row in result]}

@router.get("/table/{table_name}", response_model=TableRowsResponse)
def view_table(table_name: str, db: Session = Depends(get_db)):
    result = db.execute(text(f"SELECT * FROM {table_name} LIMIT 20;"))
    rows = [dict(row._mapping) for row in result]
    return {"table": table_name, "rows": rows}

@router.post("/reset", response_model=ResetResponse)
def reset_database(db: Session = Depends(get_db)):
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        return {"status": "success", "message": "Database reset complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete-db", response_model=DeleteDBResponse)
def delete_database_file():
    db_path = engine.url.database
    if db_path and os.path.exists(db_path):
        os.remove(db_path)
        return {"status": "success", "message": f"Deleted {db_path}"}
    return {"status": "error", "message": f"Database file not found at {db_path}"}
