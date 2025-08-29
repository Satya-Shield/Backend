from typing import List
from io import BytesIO
from PIL import Image
import requests
import logging
from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    UploadFile, 
    File,
    Form
)

from app.agent import misinformation_combating_agent
from app.services import extract_claims_from_image
from app.api.models import (
    AgentRequest,
    AgentResponse
)

router = APIRouter()

@router.post("/read_image_url", response_model=List[AgentResponse])
async def read_image_url(request: AgentRequest) -> List[AgentResponse]:
    try:
        resp = requests.get(request.image)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download image")

        image = Image.open(BytesIO(resp.content))
        claims = extract_claims_from_image(image, request.query)

        initial_state = {
            "claims": claims,
            "evidence": {},
            "result": {}
        }

        res = misinformation_combating_agent.invoke(initial_state)
        agent_response = [{"claim": key, **val} for key, val in res['result'].items()]

        return agent_response
    except Exception as e:
        logging.error(f"Error in image_to_text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/read_image_file", response_model=List[AgentResponse])
async def read_image_file(
    query: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        claims = extract_claims_from_image(image, query)
        initial_state = {
            "claims": claims,
            "evidence": {},
            "result": {}
        }

        res = await misinformation_combating_agent.ainvoke(initial_state)
        agent_response = [{"claim": key, **val} for key, val in res['result'].items()]

        return agent_response
    except Exception as e:
        logging.error(f"Error in image_to_text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

