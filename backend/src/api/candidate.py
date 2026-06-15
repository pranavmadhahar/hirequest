# api/candidate.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.db import get_db
from src.db.models import Candidate
from src.schemas.schemas import CandidateRequest, StartInterviewRequest, InterviewResponse
from src.db.crud import save_answer
from src.services.router_chain import router_chain

router = APIRouter()

@router.post("/candidate")
def register_candidate(req: CandidateRequest, db: Session = Depends(get_db)):
    candidate = Candidate(name=req.name, resume_text=req.resume_text, role=req.role)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return {"candidate_id": candidate.id}

@router.post("/interview")
def start_interview(req: StartInterviewRequest, db: Session = Depends(get_db)):
    payload = {
        "role": req.role,
        "resume_context": req.resume_context,
        "history": []
    }
    result = router_chain.invoke(payload)

    # Save first question (answer=None initially)
    save_answer(db, req.candidate_id, req.role, result["question"], None)

    return InterviewResponse(**result)
