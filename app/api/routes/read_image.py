from typing import List
from io import BytesIO
from PIL import Image
import requests
import time
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
from app.core import logger
from app.api.models import (
    AgentRequest,
    AgentResponse
)

router = APIRouter()

@router.post("/read_image_url", response_model=List[AgentResponse])
async def read_image_url(request: AgentRequest) -> List[AgentResponse]:
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {request.query} \n URL: {request.image}  \n\n")

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

        res = await misinformation_combating_agent.ainvoke(initial_state)
        response = [{"claim": key, **val} for key, val in res['result'].items()]

        logger.info(f"\n\n Response: {response}\n\n")
        return response
    except Exception as e:
        logger.error(f"Error in read_image_url: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")

@router.post("/read_image_file", response_model=List[AgentResponse])
async def read_image_file(
    query: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {query}\n\n")

        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        claims = extract_claims_from_image(image, query)
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
        logger.error(f"Error in read_image_file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")

