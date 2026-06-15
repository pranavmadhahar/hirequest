# api/interview.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.db import get_db
from src.db.crud import get_history, save_answer
from src.schemas.schemas import InterviewRequest, AnswerRequest, InterviewResponse
from src.services.router_chain import router_chain

router = APIRouter()

@router.post("/answer")
def submit_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    # Save candidate's answer to last question
    save_answer(db, req.candidate_id, req.role, req.question, req.answer)
    return {"status": "answer saved"}

@router.post("/interview/{candidate_id}/question")
def next_question(candidate_id: int, req: InterviewRequest, db: Session = Depends(get_db)):
    history = get_history(db, req.candidate_id)

    payload = {
        "role": req.role,
        "resume_context": req.resume_context,
        "history": history
    }

    result = router_chain.invoke(payload)

    # Save new question (answer=None initially)
    save_answer(db, candidate_id, req.role, result["question"], None)

    return InterviewResponse(**result)
