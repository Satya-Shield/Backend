import os, requests
from langchain_core.prompts import ChatPromptTemplate
from app.agent.state import State
from app.agent.tools import tavily
from app.core.settings import llm #in settings.py

def extract_claims(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a claim extraction assistant."),
        ("human", "Extract all claims from this text:{text}, the claims should be stored as str, str, ... and other than the claims nothing should be there.")
    ])

    chain = prompt | llm
    response = chain.invoke({"text":state["input_text"]})
    lines = response.content.split("\n")
    claims = [line.strip("- ").strip() for line in lines if line.strip()]


    state = {**state, "claims": claims}
    return state


def evidence_retrieval(state: State):
    factcheck_api_key = os.environ.get("GOOGLE_FACT_CHECK_API_KEY")
    kg_api_key = os.environ.get("GOOGLE_KG_API_KEY")

    evidence = {}

    for claim in state["claims"]:
        fact_url = (
            f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
            f"?query={claim}&key={factcheck_api_key}"
        )
        fact_res = requests.get(fact_url).json()



        if fact_res:
            evidence[claim] = {"factcheck":fact_res}

        else:
            evidence[claim] = {"factcheck":{}}

    return {**state, "evidence": evidence}


def tools_check(state: State):
    for claim,evi in state.get("evidence",{}).items():
        if not evi.get("factcheck"):
            response = tavily.invoke(claim)
            state["evidence"][claim] = {"factcheck":response}


def verdict_and_explainer(state: State):
    verdicts = {}
    explanations = {}

    for claim, evi in state.get("evidence", {}).items():
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a fact-checking assistant."),
            ("human", "Claim: {claim} Evidence: {evi} Provide a clear verdict (True/False/Uncertain) and also educate user on the underlying reasons a piece of content might be misleading."),
        ])

        # Bind the template with the LLM
        chain = prompt | llm

        # Provide the required variables to the prompt
        response = chain.invoke({"claim": claim, "evi": evi})

        text = response.content.strip()
        text_lower = text.lower()

        if text_lower.startswith("true"):
            verdicts[claim] = "True"
        elif text_lower.startswith("false"):
            verdicts[claim] = "False"
        else:
            verdicts[claim] = "Uncertain"

        explanations[claim] = text

    return {**state, "verdicts": verdicts, "explanations": explanations}
