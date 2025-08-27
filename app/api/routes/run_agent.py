from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import logging

from app.agent import misinformation_combating_agent
from app.api.models import (
    AgentRequest,
    AgentResponse
)

router = APIRouter()

@router.post("/run_agent", response_model=Dict[str, AgentResponse])
async def search_companies(request: AgentRequest) -> Dict[str, AgentResponse]:
    try:
        initial_state = {
            "input_text": request.query,
            "claims": [],
            "evidence": {},
            "result": {}
        }

        res = misinformation_combating_agent.invoke(initial_state)
        return res['result']
    except Exception as e:
        logging.error(f"Error in run_agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

