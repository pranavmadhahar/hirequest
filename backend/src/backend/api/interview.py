# api/interview.py
from contextlib import closing

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.db.crud import get_history, save_answer, format_history_for_prompt, get_interview_config , save_interview_summary 
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
    # Pull history
    history = get_history(db, candidate_id)
    config = get_interview_config(db, candidate_id, req.role)

    # Decide mode
    mode = "summary" if len(history) >= config.n_questions else "question"

    retrieved_context = get_resume_context(req.candidate_id, req.role, k=10)
    payload = {
        "role": req.role,
        "resume_context": retrieved_context,
        "history": format_history_for_prompt(history),
        "mode": mode
    }

    result = router_chain.invoke(payload)

    if mode == "summary":
        strengths = result["strengths"]
        improvements = result["improvements"]
        overall = result["overall"]

        # Combine text
        summary_text = (
            f"Strengths: {', '.join(strengths)}\n"
            f"Improvements: {', '.join(improvements)}\n"
            f"Overall: {overall}"
        )
        # Save summary in DB
        save_interview_summary(db, candidate_id, req.role, summary_text)
        return {
            "status": "complete",
            "summary": summary_text,
            "closing": result.get("closing", f"Thank you, this concludes your {req.role} interview.")
        }
    else:
        save_answer(db, candidate_id, req.role, result["question"], None)
        return InterviewResponse(**result)

    