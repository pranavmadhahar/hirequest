from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.db.db import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    resume_text = Column(Text)
    role = Column(String)

    # relationship to InterviewHistory, one-to-many relationship
    history = relationship("InterviewHistory", back_populates="candidate")


class InterviewHistory(Base):
    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # relationship back to Candidate, many-to-one relationship
    candidate = relationship("Candidate", back_populates="history")
