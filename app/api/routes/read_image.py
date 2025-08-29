from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
import logging
from io import BytesIO
from PIL import Image
import requests

from app.agent import misinformation_combating_agent
from app.api.models import (
    AgentRequest,
    AgentResponse
)

from app.core import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/read_image_url", response_model=List[AgentResponse])
async def image_to_text(request: AgentRequest) -> List[AgentResponse]:
    try:
        resp = requests.get(request.image)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download image")

        image = Image.open(BytesIO(resp.content))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, "Extract all readable text from this image."]
        )

        extracted_text = response.text.strip()

        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in image")

        #normal flow
        initial_state = {
            "input_text": extracted_text,
            "claims": [],
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
async def image_to_text(query: str, file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, "Extract all readable text from this image."]
        )

        extracted_text = response.text.strip()

        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in image")

        #normal flow
        initial_state = {
            "input_text": extracted_text,
            "claims": [],
            "evidence": {},
            "result": {}
        }

        res = misinformation_combating_agent.invoke(initial_state)
        agent_response = [{"claim": key, **val} for key, val in res['result'].items()]

        return agent_response

    except Exception as e:
        logging.error(f"Error in image_to_text: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
