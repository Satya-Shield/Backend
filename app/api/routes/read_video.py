from typing import List, Annotated
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
import tempfile
from pathlib import Path
from app.agent import misinformation_combating_agent
from app.core.settings import get_settings
import time
import asyncio
import os
import tempfile
import httpx
import mimetypes
from app.core import logger
from google import genai

from app.services.claim_extractor import extract_claims_from_video

router = APIRouter()

# @router.post("/read_video_url", response_model=List[AgentResponse])
# async def read_video_url(request: AgentRequest) -> List[AgentResponse]:
    # temp_file_path = None
    # try:
    #     start_time = time.monotonic()
    #     logger.info(f"\n User Query: {request.query} \n URL: {request.video}  \n\n")
    #     settings = get_settings()
    #
    #     genai.configure(api_key=settings.gemini_api_key)

    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(request.video)
    #         response.raise_for_status()  # Raise an exception for bad status codes
    #         video_content = response.content

    #     # Guess mime type from URL
    #     mime_type, _ = mimetypes.guess_type(request.video)

    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
    #         temp_file.write(video_content)
    #         temp_file_path = temp_file.name

    #     video = genai.upload_file(
    #         path=temp_file_path,
    #         display_name=request.video,
    #         mime_type=mime_type
    #     )

    #     # Wait for the file to be processed
    #     while video.state.name == "PROCESSING":
    #         await asyncio.sleep(10)
    #         video = genai.get_file(video.name)

    #     if video.state.name == "FAILED":
    #         raise HTTPException(status_code=500, detail="Video processing failed.")

    #     claims = extract_claims_from_video(video, request.query)
    #     initial_state = {
    #         "claims": claims,
    #         "evidence": {},
    #         "result": {}
    #     }

    #     res = await misinformation_combating_agent.ainvoke(initial_state)
    #     response = [{"claim": key, **val} for key, val in res['result'].items()]

    #     logger.info(f"\n\n Response: {response}\n\n")
    #     return response
    # except httpx.HTTPStatusError as e:
    #     logger.error(f"Error downloading video: {e}")
    #     raise HTTPException(status_code=400, detail=f"Could not download video from URL: {request.video}")
    # except Exception as e:
    #     logger.error(f"Error in read_video_url: {e}")
    #     raise HTTPException(status_code=500, detail="Internal server error")
    # finally:
    #     if temp_file_path and os.path.exists(temp_file_path):
    #         os.remove(temp_file_path)
    #     end_time = time.monotonic()
    #     duration = end_time - start_time
    #     logger.info(f"Total response time: {duration:.2f} seconds")


@router.post("/read_video_file", response_model=List[AgentResponse])
async def read_video_file(
    query: Annotated[str, Form()],
    file: Annotated[UploadFile, File()]
):
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {query}\n\n")
        settings = get_settings()
        client = genai.Client(api_key=settings.gemini_api_key)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        myfile = client.files.upload(file=temp_path)
        print("Uploaded file:", myfile.name, "Status:", myfile.state)

        while True:
            status = client.files.get(name=myfile.name)
            if status.state == "ACTIVE":
                print("File is ACTIVE.")
                break
            elif status.state == "FAILED":
                raise Exception("File processing failed.")
            else:
                print("Waiting for file to become ACTIVE... (current state:", status.state, ")")
                time.sleep(3)

        claims = extract_claims_from_video(status, query)
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")

