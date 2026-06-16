from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.db.db import Base

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
    
class InterviewConfig(Base):
    __tablename__ = "interview_config"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)
    role = Column(String)
    n_questions = Column(Integer)

class InterviewSummary(Base):
    __tablename__ = "interview_summary"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, index=True)
    role = Column(String)
    summary = Column(Text)
