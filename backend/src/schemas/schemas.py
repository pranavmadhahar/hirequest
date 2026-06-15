# backend/src/schemas.py
from pydantic import BaseModel
from typing import Optional, List

# ---- Candidate APIs ----
class CandidateRequest(BaseModel):
    name: str
    resume_text: str
    role: str

class StartInterviewRequest(BaseModel):
    candidate_id: int
    role: str
    resume_context: str

# ---- Interview APIs ----
class AnswerRequest(BaseModel):
    candidate_id: int
    role: str
    question: str
    answer: str

class InterviewRequest(BaseModel):
    candidate_id: int
    role: str
    resume_context: str
    latest_answer: Optional[str] = None

class InterviewResponse(BaseModel):
    question: str
    role: str
    domain: str
    context: str
