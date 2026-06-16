"""
summary_chain.py

Interview summary generation chain.

This chain converts a completed interview transcript into a
structured recruiter-facing assessment containing:

- Candidate strengths
- Areas for improvement
- Overall evaluation

The output is validated through a Pydantic schema to ensure
consistent JSON responses from the LLM.
"""

from dotenv import load_dotenv, find_dotenv

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# Load environment variables required by OpenAI.
load_dotenv(find_dotenv())


# Shared LLM instance used for summary generation.
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
)


class InterviewSummarySchema(BaseModel):
    """
    Structured output returned by the summary chain.

    Used by the JSON parser to validate LLM responses
    before they are returned to the API layer.
    """

    strengths: list[str] = Field(
        ...,
        description="Candidate strengths",
    )

    improvements: list[str] = Field(
        ...,
        description="Areas for improvement",
    )

    overall: str = Field(
        ...,
        description="Overall interview assessment",
    )


parser = JsonOutputParser(
    pydantic_object=InterviewSummarySchema
)


# Prompt designed to produce recruiter-friendly
# interview feedback in a structured JSON format.
summary_prompt = ChatPromptTemplate.from_template(
    """
    You are summarizing a structured interview
    for the role: {role}.

    Interview history:
    {history}

    Provide a recruiter-friendly summary in JSON
    with the following keys:

    - strengths (list)
    - improvements (list)
    - overall (string)
    """
)


summary_chain = RunnableSequence(
    {
        "role": lambda x: x.get("role", ""),
        "history": lambda x: x.get("history", ""),
    },
    summary_prompt,
    llm,
    parser,
)