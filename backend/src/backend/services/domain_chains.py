
"""
domain_chains.py
================

This module defines the domain-specific retrieval chains used by the interview
simulation backend service. Each chain loads a FAISS vectorstore for a given
domain (ML, Data_Science, Advanced_ML), retrieves relevant context, and uses
an LLM to generate structured interview questions.
"""

# load API key from .env 
from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv())
# llm model
model="gpt-4o-mini"

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
        
            {
                "context": lambda x: format_docs(retriever.invoke(domain)),
                "role": lambda x: x.get("role", domain),
                "resume_context": lambda x: x.get("resume_context", ""),
                "history": lambda x: x.get("history", []),
                "domain": lambda x: domain
            },
            prompt,
            llm,
            parser
        
    )
    return chain
