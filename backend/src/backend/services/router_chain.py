
"""
router_chain.py
===============

Dispatches candidate context (resume, role, history) to the correct domain chain
(ML, Advanced_ML, Data_Science) using function-based routing.

The router_chain takes the payload from FastAPI (including role, resume_context,
and history) and invokes the appropriate domain chain defined in domain_chains.py.
"""

# load API key from .env 
from dotenv import load_dotenv, find_dotenv 
load_dotenv(find_dotenv())
# llm model
model="gpt-4o-mini"

from langchain_core.runnables import RunnableLambda
from backend.services.domain_chains import load_domain_chain

def route_by_role(inputs):
    role = inputs.get("role", "")
    resume_context = inputs.get("resume_context", "")
    history = inputs.get("history", [])

    if role == "ML":
        chain = load_domain_chain("ML")
    elif role == "Advanced_ML":
        chain = load_domain_chain("Advanced_ML")
    elif role == "Data_Science":
        chain = load_domain_chain("Data_Science")
    else:
        raise ValueError(f"Unsupported role: {role}")

    # Pass the candidate context into the chosen domain chain
    return chain.invoke({
        "role": role,
        "resume_context": resume_context,
        "history": history
    })

# Router chain definition
router_chain = RunnableLambda(route_by_role)
