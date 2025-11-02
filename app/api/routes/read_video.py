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
from app.agent import misinformation_combating_agent
import tempfile
import time
import os

from app.core.settings import get_settings
from app.core import logger
from google import genai
from app.services.claim_extractor import (
    extract_claims_from_video_url, 
    extract_claims_from_video
)

router = APIRouter()

@router.post("/read_video_url")
async def read_video_url(request: AgentRequest):
    try:
        start_time = time.monotonic()
        logger.info(f"\n User Query: {request.query} \n URL: {request.video}  \n\n")
        claims = extract_claims_from_video_url(request.video, request.query)

        initial_state = {
            "claims": claims,
            "evidence": {},
            "result": {}
        }

        res = await misinformation_combating_agent.ainvoke(initial_state)
        response = [{"claim": key, **val} for key, val in res['claim_verdicts'].items()]

        claims = []
        for r in response:
            r['confidence_score'] = res['confidence_scores'][r['claim']]
            claims.append(r)
        
        final_res = {
            **res["overall"],
            "claims": claims
        }

        logger.info(f"\n\n Response: {final_res}\n\n")
        return final_res
    except Exception as e:
        logger.error(f"Error in read_video_url: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")    

@router.post("/read_video_file")
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
        response = [{"claim": key, **val} for key, val in res['claim_verdicts'].items()]

        claims = []
        for r in response:
            r['confidence_score'] = res['confidence_scores'][r['claim']]
            claims.append(r)
        
        final_res = {
            **res["overall"],
            "claims": claims
        }

        logger.info(f"\n\n Response: {final_res}\n\n")
        return final_res
    except Exception as e:
        logger.error(f"Error in read_video_file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")

