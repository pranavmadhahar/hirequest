from langchain_core.runnables import RunnableLambda
from domain_chains import load_domain_chain
from src.crud import get_history, format_history_for_prompt

def route_by_role(inputs, db):
    role = inputs.get("role", "")
    resume_context = inputs.get("resume_context", "")
    candidate_id = inputs.get("candidate_id")

    # Fetch raw history from DB (list of dicts)
    records = get_history(db, candidate_id)

    # Format into string transcript for prompt injection
    history_str = format_history_for_prompt(records)

    if role == "ML":
        chain = load_domain_chain("ML")
    elif role == "Advanced_ML":
        chain = load_domain_chain("Advanced_ML")
    elif role == "Data_Science":
        chain = load_domain_chain("Data_Science")
    else:
        raise ValueError(f"Unsupported role: {role}")

    return chain.invoke({
        "role": role,
        "resume_context": resume_context,
        "history": history_str
    })

# Router chain definition
router_chain = RunnableLambda(route_by_role)
