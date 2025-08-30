from fastapi import APIRouter, HTTPException
from typing import List
import time

from app.agent import misinformation_combating_agent
from app.services  import extract_claims_from_text
from app.core import logger
from app.api.models import (
    AgentRequest,
    AgentResponse
)

router = APIRouter()

@router.post("/run_agent", response_model=List[AgentResponse])
async def search_companies(request: AgentRequest) -> List[AgentResponse]:
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {request.query}\n\n")

        claims = extract_claims_from_text(request.query)
        initial_state = {
            "claims": claims,
            "evidence": {},
            "result": {}
        }

        res = await misinformation_combating_agent.ainvoke(initial_state)
        response = [{"claim": key, **val} for key, val in res['result'].items()]

        logger.info(f"\n\n Response: {response}\n\n")
        return response
    except Exception as e:
        logger.error(f"Error in run_agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")
