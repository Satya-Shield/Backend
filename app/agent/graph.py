from langgraph.graph import StateGraph, START, END
from app.agent.state import State
from app.agent.nodes import ( 
    extract_claims, 
    evidence_retrieval, 
    verdict_and_explainer
)


builder = StateGraph(State)

builder.add_node("extract_claims",extract_claims)
builder.add_node("evidence_retrieval",evidence_retrieval)
builder.add_node("verdict_and_explainer",verdict_and_explainer)

builder.add_edge(START, "extract_claims")
builder.add_edge("extract_claims", "evidence_retrieval")
builder.add_edge("evidence_retrieval", "verdict_and_explainer")
builder.add_edge("verdict_and_explainer", END)

misinformation_combating_agent = builder.compile()

if __name__ == '__main__':
    initial_state = {
        "input_text": "Paris is capital of India",
        "claims": [],
        "evidence": {},
        "result": {}
    }

    res = misinformation_combating_agent.invoke(initial_state)
    print(res['result'])