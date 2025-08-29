from pydantic import BaseModel
from google import genai
from typing import List
import requests
import logging

from app.agent.tools import tavily
from app.agent.state import State
from app.utils import read_prompt
from app.core import get_settings
from app.models import client

settings = get_settings()

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
            evidence[claim] = {"factcheck":response}

    logging.info(f"{evidence}\n\n\n")

    return {
        "evidence": evidence
    }

def verdict_and_explainer(state: State):
    result = {}
    system_prompt = read_prompt("explainer_system_prompt")

    class Result(BaseModel):
        verdict: str               # One of: Supported, Refuted, Uncertain, Needs Context
        confidence: int            # Integer from 0–100
        explanation: str           # 120–180 words explanation with citations
        sources: List[str]         # List of source URLs or identifiers
        techniques: List[str]      # Manipulative techniques detected
        checklist: List[str]       # 3-step user action checklist

    for claim, evi in state['evidence'].items():
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": Result
            },
            contents=f"Claim: {claim} Evidence: {evi} 1. Provide a clear verdict 2. Confidence Score(0-100) 3. educate user on the underlying reasons a piece of content might be misleading. 4. Manipulative techniques (if any)"
        )

        result[claim] = response.parsed.dict()

    return {
        "result": result
    }

if __name__ == '__main__':
    response = tavily.invoke("paris is capital of india")
    print(response)