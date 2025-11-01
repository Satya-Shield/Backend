from langgraph.graph import StateGraph, START, END
from app.agent.state import State
from app.agent.nodes import ( 
    evidence_retrieval, 
    verdict_and_explainer,
    confidence_scorer
)

builder = StateGraph(State)

builder.add_node("evidence_retrieval",evidence_retrieval)
builder.add_node("verdict_and_explainer",verdict_and_explainer)
builder.add_node("confidence_scorer",confidence_scorer)

builder.add_edge(START, "evidence_retrieval")
builder.add_edge("evidence_retrieval", [
    "verdict_and_explainer",
    "confidence_scorer"
])
builder.add_edge("verdict_and_explainer", END)

misinformation_combating_agent = builder.compile()
