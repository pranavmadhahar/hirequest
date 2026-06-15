
"""
domain_chains.py
================

This module defines the domain-specific retrieval chains used by the interview
simulation backend service. Each chain loads a FAISS vectorstore for a given
domain (ML, Data_Science, Advanced_ML), retrieves relevant context, and uses
an LLM to generate structured interview questions.

Key Components:
---------------
- HuggingFaceEmbeddings: ensures embeddings match those used during FAISS build.
- FAISS vectorstore: domain-specific indexes stored under VECTORSTORES_DIR/domain.
- format_docs: converts retrieved Document objects into a clean string for prompts.
- InterviewQuestion schema: enforces structured JSON output for frontend/backend.
- JsonOutputParser: guarantees valid JSON responses matching the schema.
- load_domain_chain(domain): builds a RunnableSequence pipeline:
    retriever → format_docs → prompt → LLM → JSON parser.

Usage:
------
chain = load_domain_chain("ML")
result = chain.invoke({
    "role": "ML Engineer",
    "resume_context": "Worked on CNNs and NLP projects",
    "history": [{"question": "Explain supervised learning", "answer": "It uses labeled data"}]
})

Output:
-------
{
  "question": "Can you describe a real-world NLP project where you applied supervised learning, and explain how you evaluated its performance?",
  "role": "ML Engineer",
  "domain": "ML",
  "context": "Supervised learning uses labeled data..."
}

Notes:
------
- The schema can be simplified to only include `question` if frontend display
  is the sole requirement. Keep `role`, `domain`, and `context` for logs or backend traceability.
- Database storage should handle IDs and candidate answers; schema does not
  need to include serial numbers unless portable logs are required.
"""

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from assets.build.paths import VECTORSTORES_DIR

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def format_docs(docs):
    """Convert a list of Document objects into a single string for prompt injection."""
    return "\n\n".join([d.page_content for d in docs])

class InterviewQuestion(BaseModel):
    """Schema for structured interview question output."""
    question: str = Field(..., description="The next interview question")
    role: str = Field(..., description="Candidate role")
    domain: str = Field(..., description="Knowledge domain used")
    context: str = Field(..., description="Retrieved context grounding the question")

parser = JsonOutputParser(pydantic_object=InterviewQuestion)

def load_domain_chain(domain: str):
    """
    Load FAISS vectorstore for a given domain and build a retrieval chain.

    Args:
        domain (str): Domain name (e.g., "ML", "Data_Science", "Advanced_ML").

    Returns:
        RunnableSequence: A chain that retrieves domain-specific context,
        injects it into a structured prompt, and generates JSON output
        containing the next interview question.
    """
    domain_dir = VECTORSTORES_DIR / domain
    vectorstore = FAISS.load_local(
        str(domain_dir),
        embeddings,
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    prompt = ChatPromptTemplate.from_template(
        """You are simulating a structured interview for the role: {role}.
        Resume context: {resume_context}
        Previous Q&A: {history}

        You are an expert in {domain}.
        Use the following retrieved context to craft the next interview question:
        {context}

        Candidate role: {role}
        Respond ONLY in JSON with keys: question, role, domain, context."""
    )

    chain = RunnableSequence(
        steps=[
            {
                "context": lambda x: format_docs(retriever.invoke(x.get("resume_context", ""))),
                "role": lambda x: x.get("role", domain),
                "resume_context": lambda x: x.get("resume_context", ""),
                "history": lambda x: x.get("history", []),
                "domain": lambda x: domain
            },
            prompt,
            llm,
            parser
        ]
    )
    return chain
