from pydantic import BaseModel
from typing import List
import requests
import asyncio

from app.core import get_settings, logger
from app.agent.tools import *
from app.agent.state import State
from app.utils import read_prompt
from app.models import client

settings = get_settings()

async def evidence_retrieval(state: State):
    logger.info("Getting evidences...")

    evidence = {}

    async def get_evidence(claim):
        # fact_url = (
        #     f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
        #     f"?query={claim}&key={settings.factcheck_api_key}"
        # )
        # fact_res = requests.get(fact_url).json()

        # if fact_res:
        #     evidence[claim] = {"factcheck": fact_res}
        # else:
        logger.info("wimipedia Searching.....\n\n")
        response = tavily.invoke(claim)
        evidence[claim] = {"factcheck":response}

    await asyncio.gather(*[get_evidence(claim) for claim in state['claims']])

    logger.info(f"{evidence}\n\n")

    return {
        "evidence": evidence
    }

async def verdict_and_explainer(state: State):
    logger.info("Reasoning final verdict...")

    result = {}
    system_prompt = read_prompt("explainer_system_prompt")

    class Result(BaseModel):
        verdict: str               # One of: Supported, Refuted, Uncertain, Needs Context
        confidence: int            # Integer from 0–100
        explanation: str           # 120–180 words explanation with citations
        sources: List[str]         # List of source URLs or identifiers
        techniques: List[str]      # Manipulative techniques detected
        checklist: List[str]       # 3-step user action checklist

    from datetime import datetime
    async def get_verdict(claim, evi):
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": Result
            },
            contents=f"Claim: {claim} Evidence: {evi} 1. Provide a clear verdict 2. Confidence Score(0-100) 3. educate user on the underlying reasons a piece of content might be misleading. 4. Manipulative techniques (if any) Todays date is {datetime.now()}"
        )

        result[claim] = response.parsed.dict()
    
    
    await asyncio.gather(*[get_verdict(claim, evi) for claim, evi in state['evidence'].items()])

    return {
        "result": result
    }
