"""
crud.py

Database access helpers for interview management.

Responsibilities:
- Retrieve interview history
- Persist interview questions and answers
- Manage interview configuration
- Store and retrieve interview summaries
- Format interview transcripts for LLM prompts
"""

from sqlalchemy.orm import Session

from backend.db.models import (
    InterviewHistory,
    InterviewConfig,
    InterviewSummary,
)


def get_history(db: Session, candidate_id: int) -> list[dict]:
    """
    Retrieve a candidate's interview transcript ordered
    chronologically.

    Returns:
        List of question/answer dictionaries suitable for
        prompt construction and interview state tracking.
    """
    records = (
        db.query(InterviewHistory)
        .filter(
            InterviewHistory.candidate_id == candidate_id
        )
        .order_by(InterviewHistory.timestamp)
        .all()
    )

    return [
        {
            "question": r.question,
            "answer": r.answer,
        }
        for r in records
    ]


def format_history_for_prompt(
    records: list[dict],
) -> str:
    """
    Convert interview history into a prompt-friendly
    transcript format.

    Example:
        Q: What is Python? | A: A programming language
    """
    if not records:
        return ""

    return "\n".join(
        [
            f"Q: {r['question']} | A: {r['answer']}"
            for r in records
        ]
    )


def save_answer(
    db: Session,
    candidate_id: int,
    role: str,
    question: str,
    answer: str | None,
):
    """
    Persist an interview question/answer record.

    Questions are initially stored with answer=None
    and updated when the candidate responds.
    """
    record = InterviewHistory(
        candidate_id=candidate_id,
        question=question,
        answer=answer,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def save_interview_config(
    db: Session,
    candidate_id: int,
    role: str,
    n_questions: int,
):
    """
    Store interview configuration for a candidate session.
    """
    config = InterviewConfig(
        candidate_id=candidate_id,
        role=role,
        n_questions=n_questions,
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


def get_interview_config(
    db: Session,
    candidate_id: int,
    role: str,
):
    """
    Retrieve interview configuration for a candidate.
    """
    return (
        db.query(InterviewConfig)
        .filter_by(
            candidate_id=candidate_id,
            role=role,
        )
        .first()
    )


def save_interview_summary(
    db: Session,
    candidate_id: int,
    role: str,
    summary: str,
):
    """
    Persist the final interview evaluation summary.
    """
    record = InterviewSummary(
        candidate_id=candidate_id,
        role=role,
        summary=summary,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_interview_summary(
    db: Session,
    candidate_id: int,
    role: str,
):
    """
    Retrieve a previously generated interview summary.
    """
    return (
        db.query(InterviewSummary)
        .filter_by(
            candidate_id=candidate_id,
            role=role,
        )
        .first()
    )