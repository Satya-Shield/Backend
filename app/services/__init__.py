from app.services.claim_extractor import *
from app.services.deepfake_detection import *
from app.services.confidence_scorer import ConfidenceScoring

__all__ = [
    extract_claims_from_image,
    extract_claims_from_text,
    extract_claims_from_video_url,
    ConfidenceScoring,
    detect_deepfake
]