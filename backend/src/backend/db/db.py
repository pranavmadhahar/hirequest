"""
db.py

Database configuration and session management.

Provides:
- SQLAlchemy engine
- Session factory
- Declarative base class
- FastAPI database dependency
"""

from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv())

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:////data/interview.db"

# SQLAlchemy engine used for all database connections.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Session factory used throughout the application.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class inherited by all ORM models.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session.

    Ensures each request receives its own session and
    guarantees proper cleanup after request completion.

    Yields:
        Session:
            Active SQLAlchemy database session.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
