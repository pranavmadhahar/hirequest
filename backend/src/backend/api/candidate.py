"""
candidate.py

Candidate-facing API endpoints.

Responsibilities:
- Register candidates and persist profile information
- Parse and embed uploaded resumes
- Create candidate-specific FAISS vector stores
- Start interview sessions
- Initialize interview state and configuration

Interview Flow:
1. Candidate uploads resume and selects a role
2. Resume is parsed and chunked
3. Chunks are embedded and stored in a candidate-specific vector store
4. Interview session retrieves relevant resume context
5. Question generation is grounded on retrieved resume content
"""

from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from backend.db.db import get_db
from backend.db.models import Candidate
from backend.schemas.schemas import (
    StartInterviewRequest,
    InterviewResponse,
)
from backend.db.crud import (
    save_answer,
    format_history_for_prompt,
    save_interview_config,
    get_interview_config,
)
from backend.services.router_chain import router_chain
from backend.middleware.parser import parse_resume
from backend.middleware.vectorstore import get_resume_context

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


router = APIRouter()


@router.post("/")
async def register_candidate(
    name: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Register a new candidate and create a resume vector store.

    Processing Steps:
    1. Parse uploaded resume
    2. Persist candidate record
    3. Generate embeddings for resume chunks
    4. Create candidate-specific FAISS index
    5. Return candidate metadata

    Args:
        name:
            Candidate name.

        role:
            Target interview role.

        resume:
            Uploaded resume file.

        db:
            Active database session.

    Returns:
        dict:
            Candidate identifier and display name.
    """

    # Extract raw resume text and retrieval-ready chunks.
    resume_text, resume_chunks = await parse_resume(resume)

    # Persist candidate profile information.
    candidate = Candidate(
        name=name,
        resume_text=resume_text,
        role=role,
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Generate semantic embeddings for resume chunks
    # to support retrieval-augmented interview generation.
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    metadatas = [
        {"candidate_id": candidate.id}
        for _ in resume_chunks
    ]

    vectorstore = FAISS.from_texts(
        resume_chunks,
        embedding=embeddings,
        metadatas=metadatas,
    )

    # Store vector index under a candidate-specific directory
    # so interview sessions can be reconstructed later.
    vectorstore.save_local(
        f"../../assets/vectorstores/Candidate_Resumes/{candidate.id}"
    )

    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
    }


@router.post("/interview")
def start_interview(
    req: StartInterviewRequest,
    db: Session = Depends(get_db),
):
    """
    Start a new interview session.

    The interview engine retrieves relevant resume content
    and uses it as grounding context for generating the
    opening interview question.

    Args:
        req:
            Interview initialization request.

        db:
            Active database session.

    Returns:
        InterviewResponse:
            First interview question and associated metadata.
    """

    # Retrieve the most relevant resume chunks
    # for interview grounding.
    retrieved_context = get_resume_context(
        req.candidate_id,
        req.role,
        k=10,
    )

    payload = {
        "role": req.role,
        "resume_context": retrieved_context,
        "history": "",
    }

    result = router_chain.invoke(payload)

    # Persist the generated question immediately so the
    # interview transcript remains complete even if the
    # user disconnects before answering.
    save_answer(
        db,
        req.candidate_id,
        req.role,
        result["question"],
        None,
    )

    # Store interview configuration for later validation
    # and completion checks.
    save_interview_config(
        db,
        req.candidate_id,
        req.role,
        req.n_questions,
    )

    return InterviewResponse(**result)