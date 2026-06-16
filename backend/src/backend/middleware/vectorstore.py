"""
vectorstore.py

Resume retrieval utilities.

Responsibilities:
- Load candidate-specific FAISS indexes
- Perform semantic similarity search
- Return retrieval context for interview generation

The retrieved context is used to ground interview
questions in the candidate's actual resume content.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def get_resume_context(
    candidate_id: int,
    role: str,
    k: int = 10,
) -> str:
    """
    Retrieve resume context relevant to the target role.

    Args:
        candidate_id:
            Candidate identifier.

        role:
            Interview role used as the retrieval query.

        k:
            Number of chunks to retrieve.

    Returns:
        str:
            Concatenated resume context assembled from
            the top-k retrieved chunks.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        f"../../assets/vectorstores/Candidate_Resumes/{candidate_id}",
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retrieved_docs = vectorstore.similarity_search(
        role,
        k=k,
    )

    return "\n".join(
        doc.page_content
        for doc in retrieved_docs
    )