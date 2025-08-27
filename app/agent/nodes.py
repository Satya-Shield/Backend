import os, requests
from langchain_core.prompts import ChatPromptTemplate
from app.agent.tools import tavily
# from app.core.settings import llm #in settings.py

from pydantic import BaseModel
from google import genai

from app.agent.state import State
from app.utils import read_prompt
from app.core import get_settings
from app.models import client

settings = get_settings()
client = genai.Client()

def extract_claims(state: State):
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=f"Extract all claims from this text:\n {state['input_text']}"
    )

    return {
        "claims": response.parsed
    }


def evidence_retrieval(state: State):
    evidence = {}

    for claim in state["claims"]:
        fact_url = (
            f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
            f"?query={claim}&key={settings.factcheck_api_key}"
        )
        fact_res = requests.get(fact_url).json()

        if fact_res:
            evidence[claim] = {"factcheck": fact_res}
        else:
            response = tavily.invoke(claim)
            state["evidence"][claim] = {"factcheck":response}

    return {
        "evidence": evidence
    }


# def tools_check(state: State):
#     for claim, evi in state.get("evidence",{}).items():
#         if not evi.get("factcheck"):
#             response = tavily.invoke(claim)
#             state["evidence"][claim] = {"factcheck":response}


def verdict_and_explainer(state: State):
    verdicts = {}
    explanations = {}

    for claim, evi in state.get("evidence", {}).items():
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a fact-checking assistant."),
            ("human", "Claim: {claim} Evidence: {evi} 1. Provide a clear verdict (True/False/Uncertain) 2. Confidence Score(0-100) and also 3. educate user on the underlying reasons a piece of content might be misleading."),
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

if __name__ == '__main__':
    response = tavily.invoke("paris is capital of india")
    print(response)