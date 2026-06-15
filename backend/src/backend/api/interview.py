# api/interview.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.db.crud import get_history, save_answer, format_history_for_prompt
from backend.schemas.schemas import InterviewRequest, AnswerRequest, InterviewResponse
from backend.services.router_chain import router_chain
from backend.middleware.vectorstore import get_resume_context

router = APIRouter()

@router.post("/answer")
def submit_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    # Save candidate's answer to last question
    save_answer(db, req.candidate_id, req.role, req.question, req.answer)
    return {"status": "answer saved"}

@router.post("/{candidate_id}/question")
def next_question(candidate_id: int, req: InterviewRequest, db: Session = Depends(get_db)):
    # Pull history from DB
    history = get_history(db, candidate_id)

    retrieved_context = get_resume_context(req.candidate_id, req.role, k=10)
    payload = {
        "role": req.role,
        "resume_context": retrieved_context,
        "history": format_history_for_prompt(history)
    }

    result = router_chain.invoke(payload)

    # Save new question (answer=None initially)
    save_answer(db, candidate_id, req.role, result["question"], None)

    return InterviewResponse(**result)
