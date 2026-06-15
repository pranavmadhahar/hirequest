# backend/src/schemas.py
from pydantic import BaseModel
from typing import Optional, List

# ---- Candidate APIs ----
class StartInterviewRequest(BaseModel):
    candidate_id: int
    role: str
    

# ---- Interview APIs ----
class AnswerRequest(BaseModel):
    candidate_id: int
    role: str
    question: str
    answer: str

class InterviewRequest(BaseModel):
    candidate_id: int
    role: str

class InterviewResponse(BaseModel):
    question: str
    role: str
    domain: str
    context: str
