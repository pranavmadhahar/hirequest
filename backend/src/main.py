# backend/src/main.py
from fastapi import FastAPI
from src.db.db import Base, engine
from src.api import candidate, interview

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Mount routers
app.include_router(candidate.router, prefix="/candidate", tags=["candidate"])
app.include_router(interview.router, prefix="/interview", tags=["interview"])
