"""
summary_chain.py
================

This module defines the summary chain used by the interview
simulation backend service. It condenses the candidate's Q&A
history into a recruiter‑friendly wrap‑up with strengths,
areas for improvement, and overall impression.
"""

# load API key from .env
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# llm model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Strict schema for summary output
class InterviewSummarySchema(BaseModel):
    strengths: list[str] = Field(..., description="Candidate strengths")
    improvements: list[str] = Field(..., description="Areas for improvement")
    overall: str = Field(..., description="Overall impression")

parser = JsonOutputParser(pydantic_object=InterviewSummarySchema)

# Prompt template
summary_prompt = ChatPromptTemplate.from_template(
    """You are summarizing a structured interview for the role: {role}.
    Interview history:
    {history}

    Provide a recruiter‑friendly summary in JSON with keys:
    strengths (list), improvements (list), overall (string).
    """
)

# Chain definition
summary_chain = RunnableSequence(
        {
            "role": lambda x: x.get("role", ""),
            "history": lambda x: x.get("history", "")
        },
        summary_prompt,
        llm,
        parser
)
