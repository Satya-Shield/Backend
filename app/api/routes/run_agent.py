from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
import logging

from app.agent import misinformation_combating_agent
from app.services  import extract_claims_from_text
from app.api.models import (
    AgentRequest,
    AgentResponse
)

router = APIRouter()

@router.post("/run_agent", response_model=List[AgentResponse])
async def search_companies(request: AgentRequest) -> List[AgentResponse]:
    try:
        claims = extract_claims_from_text(request.query)
        initial_state = {
            "claims": claims,
            "evidence": {},
            "result": {}
        }

        res = misinformation_combating_agent.invoke(initial_state)
        response = [{"claim": key, **val} for key, val in res['result'].items()]
        return response
    except Exception as e:
        logging.error(f"Error in run_agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
