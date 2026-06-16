"""
schemas.py

Pydantic request and response models used by the
candidate registration and interview APIs.

These schemas define the contract between the
frontend and backend layers.
"""

from pydantic import BaseModel


# ------------------------------------------------------------------
# Interview Initialization
# ------------------------------------------------------------------

class StartInterviewRequest(BaseModel):
    """
    Request payload for starting a new interview session.
    """

    candidate_id: int
    role: str
    n_questions: int = 3


# ------------------------------------------------------------------
# Interview Answer Submission
# ------------------------------------------------------------------

class AnswerRequest(BaseModel):
    """
    Request payload for submitting a candidate's answer.
    """

    candidate_id: int
    role: str
    question: str
    answer: str


# ------------------------------------------------------------------
# Next Question Generation
# ------------------------------------------------------------------

class InterviewRequest(BaseModel):
    """
    Request payload for generating the next interview question.
    """

    candidate_id: int
    role: str


# ------------------------------------------------------------------
# Interview Response
# ------------------------------------------------------------------

class InterviewResponse(BaseModel):
    """
    Response returned by the interview generation chain.
    """

    question: str
    role: str
    domain: str
    context: str