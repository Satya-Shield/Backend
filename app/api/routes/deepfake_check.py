from fastapi import (
    HTTPException, 
    UploadFile, 
    APIRouter, 
    File,
)
import time

from app.services import detect_deepfake
from app.core import logger

router = APIRouter()

@router.post("/detect_deepfake")
async def detect_deepfake_api(
    file: UploadFile = File(...)
):
    try:
        start_time = time.monotonic()

        image_data = await file.read()
        res = detect_deepfake(image_data)

        return {
            "result": res
        }

    except Exception as e:
        logger.error(f"Error in detect_deepfake: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")