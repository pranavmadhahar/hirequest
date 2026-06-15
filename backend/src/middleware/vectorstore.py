"""
vectorstore.py
==============
Middleware utility for candidate resume retrieval.
Handles reloading FAISS vectorstore and returning top‑k chunks as context.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def get_resume_context(candidate_id: int, role: str, k: int = 10) -> str:
    """
    Reload candidate vectorstore and retrieve top‑k chunks relevant to role.

    Args:
        candidate_id (int): Candidate ID
        role (str): Role string used for similarity search
        k (int): Number of chunks to retrieve

    Returns:
        str: Concatenated resume context string
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        f"../../assets/vectorstores/Candidate_Resumes/{candidate_id}",
        embeddings
    )

    retrieved_docs = vectorstore.similarity_search(role, k=k)
    return "\n".join([doc.page_content for doc in retrieved_docs])
