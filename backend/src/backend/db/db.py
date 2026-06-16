"""
db.py

Database configuration and session management.

Provides:
- SQLAlchemy engine
- Session factory
- Declarative base class
- FastAPI database dependency
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./interview.db"


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