from typing import List
from fastapi import (
    APIRouter, 
    HTTPException, 
    UploadFile, 
    File,
    Form
)
from app.api.models import (
    AgentRequest,
    AgentResponse
)
from app.agent import misinformation_combating_agent
import google.generativeai as genai
from app.core.settings import get_settings
import time
import asyncio
from app.core import logger

from app.services.claim_extractor import extract_claims_from_video

router = APIRouter()

@router.post("/read_video_file", response_model=List[AgentResponse])
async def read_video_file(
    query: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {query}\n\n")
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)

        with open(file.filename, "wb") as f:
            f.write(await file.read())

        video = genai.upload_file(path=file.filename, display_name=file.filename)

        # Wait for the file to be processed
        while video.state.name == "PROCESSING":
            await asyncio.sleep(10)
            video = genai.get_file(video.name)

        if video.state.name == "FAILED":
            raise HTTPException(status_code=500, detail="Video processing failed.")

        claims = extract_claims_from_video(video, query)
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
        logger.error(f"Error in read_video_file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")