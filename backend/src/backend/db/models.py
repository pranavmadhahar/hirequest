"""
models.py

Database models for candidate registration and interview tracking.

Tables:
- Candidate: Candidate profile and resume data
- InterviewHistory: Question/answer transcript
- InterviewConfig: Interview session configuration
- InterviewSummary: Final interview evaluation
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from backend.db.db import Base


class Candidate(Base):
    """
    Candidate profile and resume information.
    """

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    resume_text = Column(Text)
    role = Column(String)

    history = relationship(
        "InterviewHistory",
        back_populates="candidate",
    )


class InterviewHistory(Base):
    """
    Stores the interview transcript as
    question/answer pairs.
    """

    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    candidate_id = Column(
        Integer,
        ForeignKey("candidates.id"),
        index=True,
    )

    question = Column(Text)
    answer = Column(Text)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    candidate = relationship(
        "Candidate",
        back_populates="history",
    )


class InterviewConfig(Base):
    """
    Interview settings associated with a
    candidate session.
    """

    __tablename__ = "interview_config"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)

    role = Column(String)
    n_questions = Column(Integer)


class InterviewSummary(Base):
    """
    Final interview evaluation generated
    after interview completion.
    """

    __tablename__ = "interview_summary"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)

    role = Column(String)
    summary = Column(Text)