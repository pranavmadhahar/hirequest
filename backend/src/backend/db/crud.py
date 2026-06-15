# backend/src/crud.py
from sqlalchemy.orm import Session
from backend.db.models import InterviewHistory

def get_history(db: Session, candidate_id: str):
    records = db.query(InterviewHistory).filter(
        InterviewHistory.candidate_id == candidate_id
    ).order_by(InterviewHistory.timestamp).all()
    return [{"question": r.question, "answer": r.answer} for r in records]


def format_history_for_prompt(records: list[dict]) -> str:
    """Convert list of {question, answer} dicts into a readable string transcript."""
    if not records:
        return ""
    return "\n".join([f"Q: {r['question']} | A: {r['answer']}" for r in records])


def save_answer(db: Session, candidate_id: str, role: str, question: str, answer: str):
    record = InterviewHistory(
        candidate_id=candidate_id,
        question=question,
        answer=answer
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
