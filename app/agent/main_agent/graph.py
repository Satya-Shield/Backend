from langgraph.graph import StateGraph, START, END
from app.agent.main_agent.state import State
from app.agent.main_agent.nodes import ( 
    evidence_retrieval, 
    verdict_and_explainer,
    confidence_scorer,
    final_verdict
)

builder = StateGraph(State)

builder.add_node("evidence_retrieval",evidence_retrieval)
builder.add_node("verdict_and_explainer",verdict_and_explainer)
builder.add_node("confidence_scorer",confidence_scorer)
builder.add_node("final_verdict",final_verdict)

builder.add_edge(START, "evidence_retrieval")
builder.add_edge("evidence_retrieval", "verdict_and_explainer")
builder.add_edge("evidence_retrieval", "confidence_scorer")
builder.add_edge("confidence_scorer", "final_verdict")
    
builder.add_edge("verdict_and_explainer", "final_verdict")
builder.add_edge("final_verdict", END)

misinformation_combating_agent = builder.compile()
