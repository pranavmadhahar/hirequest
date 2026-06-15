# api/interview.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.db import get_db
from src.db.crud import get_history, save_answer, format_history_for_prompt
from src.schemas.schemas import InterviewRequest, AnswerRequest, InterviewResponse
from src.services.router_chain import router_chain
from src.middleware.vectorstore import get_resume_context

router = APIRouter()

@router.post("/interview/{candidate_id}/question")
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
