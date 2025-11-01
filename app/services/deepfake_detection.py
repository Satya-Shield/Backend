from google.oauth2 import service_account
from transformers import pipeline
from google.cloud import vision
from io import BytesIO
from PIL import Image
import numpy as np

from app.core import get_settings
settings = get_settings()

def detect_deepfake(image_data): 
    SERVICE_ACCOUNT_FILE = settings.cloud_vision_credentials
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

        final_label = False if fake_prob > 0.55 else True
        return final_label            
    else:
        return False