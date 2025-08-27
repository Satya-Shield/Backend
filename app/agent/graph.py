from langgraph.graph import StateGraph, START, END
from app.agent.state import State
from app.agent.nodes import extract_claims, evidence_retrieval, tools_check, verdict_and_explainer


def build_graph():
    #build the empty graph

    builder = StateGraph(State)


    #add all the nodes as node name and function name


    builder.add_node("extract_claims",extract_claims)
    builder.add_node("evidence_retrieval",evidence_retrieval)
    builder.add_node("tools_check", tools_check)
    builder.add_node("verdict_and_explainer",verdict_and_explainer)


    #schedule the flow of the graph

    builder.add_edge(START,"extract_claims")
    builder.add_edge("extract_claims","evidence_retrieval")
    builder.add_edge("evidence_retrieval","tools_check")
    builder.add_edge("tools_check","verdict_and_explainer")
    builder.add_edge("verdict_and_explainer",END)



    #compile the graph
    graph_builder = builder.compile()

    return graph_builder
