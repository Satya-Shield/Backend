import string
from typing import List
from io import BytesIO
from PIL import Image
import time
from fastapi import (
    APIRouter, 
    HTTPException, 
    UploadFile, 
    File,
)
from app.core import logger
from google.cloud import vision
from google.oauth2 import service_account
import numpy as np
from transformers import pipeline
router = APIRouter()

@router.post("/read_deepfake", response_model=str)
async def read_deepfake(
    file: UploadFile = File(...)
):
    try:
        start_time = time.monotonic()

        image_data = await file.read()
        # image = Image.open(BytesIO(image_data))
        SERVICE_ACCOUNT_FILE = "app/api/routes/ss.json"
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

        client = vision.ImageAnnotatorClient(credentials=credentials)

        image = vision.Image(content=image_data)
        response = client.web_detection(image=image)
        web_detection = response.web_detection

        if web_detection.pages_with_matching_images:
            weights = np.array([4.854692, -1.400546, 0.531892, -2.534283])
            intercept = -1.89660461  # bias term

            def get_fake_probability(model_output):
                labels = {item['label'].lower(): item['score'] for item in model_output}

                if any(k in labels for k in ['fake', 'deepfake', 'manipulated-images']):
                    for key in ['fake', 'deepfake', 'manipulated-images']:
                        if key in labels:
                            return labels[key]
                for key in ['real', 'non-manipulated-images', 'realism']:
                    if key in labels:
                        return 1 - labels[key]
                return 0.5

            models = {
                "Chiara2": "franibm/autotrain-Chiara2",
                "OpenDeepfake": "prithivMLmods/open-deepfake-detection",
                "GlassFine": "CodyNeo/glass_fine_tuned_deepfake_detection",
                "Dima806": "dima806/deepfake_vs_real_image_detection",
            }
            # path = r"D:\project\New folder\deepfake\WhatsApp Image 2025-10-23 at 00.26.33_8bc6fcdc.jpg"

            p_fakes = []
            for name, model_name in models.items():
                detector = pipeline("image-classification", model=model_name)
                result = detector(Image.open(BytesIO(image_data)))
                p_fake = get_fake_probability(result)
                print(f"{name:15s} → FAKE Probability: {p_fake:.4f}")
                p_fakes.append(p_fake)

            scores = np.array(p_fakes)

            logit = np.dot(scores, weights) + intercept
            fake_prob = 1 / (1 + np.exp(-logit))

            print(f"Fake Prob: {fake_prob}")

            final_label = "FAKE" if fake_prob > 0.55 else "REAL"
            return final_label            
        else:
            return "FAKE"
    except Exception as e:
        logger.error(f"Error in read_image_file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Total response time: {duration:.2f} seconds")