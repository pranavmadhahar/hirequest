"""
main.py

FastAPI application entrypoint.

Responsibilities:
- Initialize the FastAPI application
- Configure middleware
- Create database tables
- Register API routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import candidate, interview
from backend.db.db import Base, engine


# Create FastAPI application instance.
app = FastAPI()


# Configure Cross-Origin Resource Sharing (CORS)
# to allow frontend applications to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database schema.
Base.metadata.create_all(bind=engine)


# Register API routers.
app.include_router(
    candidate.router,
    prefix="/candidate",
    tags=["candidate"],
)

app.include_router(
    interview.router,
    prefix="/interview",
    tags=["interview"],
)