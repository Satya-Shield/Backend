from pydantic import BaseModel
from datetime import datetime
from typing import List
import asyncio
import os

from app.services import ConfidenceScoring
from app.core import get_settings, logger
from app.agent.state import State
from app.utils import read_prompt
from app.models import client
from app.agent.tools import *

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
        response = tavily.invoke(claim)
        evidence[claim] = {"factcheck":response}

    await asyncio.gather(*[get_evidence(claim) for claim in state['claims']])

    logger.debug(f"{evidence}\n\n")

    return {
        "evidence": evidence
    }

async def verdict_and_explainer(state: State):
    logger.info("Reasoning final verdict...")

    result = {}
    system_prompt = read_prompt("explainer_system_prompt")

    class Result(BaseModel):
        verdict: str               # One of: Supported, Refuted, Uncertain, Needs Context
        explanation: str           # 120–180 words explanation with citations
        sources: List[str]         # List of source URLs or identifiers
        techniques: List[str]      # Manipulative techniques detected
        checklist: List[str]       # 3-step user action checklist

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
    
    await asyncio.gather(*[get_verdict(claim) for claim in state['claims']])

    # for claim, evi in state['evidence'].items():
    #     await get_verdict(claim, evi) 

    return {
        "claim_verdicts": result
    }

async def confidence_scorer(state: State): 
    logger.info("Calculating the confidence for the veridcts...")

    result = {}
    system_prompt = read_prompt("confidence_scoring_features_prompt")

    class Result(BaseModel):
        keywords: List[str]
        reasoning_summary: str
        sources: str
        confidence: int

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "confidence_model_lgbm.joblib")

    scorer = ConfidenceScoring(MODEL_OUT=MODEL_PATH)

    async def get_score(claim, evi):
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            config={
                "system_instruction": system_prompt,
                "response_mime_type": "application/json",
                "response_schema": Result
            },
            contents=f"Claim: {claim} Evidence: {evi} Todays date is {datetime.now()}"
        )

        res = response.parsed.model_dump()

        result[claim] = scorer.predict(
            news_text=claim,
            keywords=res['keywords'],
            reasoning_summary=res['reasoning_summary'],
            sources=res['sources'],
            llm_confidence=res['confidence'],
        )
    
    await asyncio.gather(*[get_score(claim) for claim in state['claims']])

    # for claim, evi in state['evidence'].items():
    #     await get_score(claim, evi) 

    return {
        "confience_scores": result
    }

async def final_verdict(state: State):
    class Result(BaseModel):
        verdict: bool
        summary: str

    async def get_score(claim, evi):
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            config={
                "response_mime_type": "application/json",
                "response_schema": Result
            },
            contents=f"These are the claims: {state['claims']}. Combine all the claims and give me a final overall verdict and summary of 50-80 words of all the claims combined."
        )

        res = response.parsed.model_dump()
        
        return {
            "overall": res
        }