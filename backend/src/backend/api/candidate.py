"""
Candidate API module.
Handles candidate registration (resume upload + storage) and interview initiation.
Resumes are parsed, chunked, embedded, and stored in FAISS for retrieval.
Interview flow reloads candidate vectorstore and grounds questions in top‑k resume chunks.
"""

from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.db.models import Candidate
from backend.schemas.schemas import StartInterviewRequest, InterviewResponse
from backend.db.crud import save_answer, format_history_for_prompt
from backend.services.router_chain import router_chain
from backend.middleware.parser import parse_resume
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from backend.middleware.vectorstore import get_resume_context

router = APIRouter()

@router.post("/candidate")
async def register_candidate(
    name: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Parse resume into raw text + chunks
    resume_text, resume_chunks = await parse_resume(resume)

    # Persist candidate record
    candidate = Candidate(name=name, resume_text=resume_text, role=role)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Embed and store chunks in FAISS
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(resume_chunks, embedding=embeddings,
                                   metadatas=[{"candidate_id": candidate.id}])

    # Save vectorstore under Candidate_Resumes/{id}
    vectorstore.save_local(f"../../assets/vectorstores/Candidate_Resumes/{candidate.id}")

    return {"candidate_id": candidate.id}


@router.post("/interview")
def start_interview(req: StartInterviewRequest, db: Session = Depends(get_db)):
    # Reload candidate vectorstore
    retrieved_context = get_resume_context(req.candidate_id, req.role, k=10)
    # Build payload for interview chain
    payload = {
        "role": req.role,
        "resume_context": retrieved_context,
        "history": ""
    }
    result = router_chain.invoke(payload)

    # Log first question (answer=None initially)
    save_answer(db, req.candidate_id, req.role, result["question"], None)

    return InterviewResponse(**result)
