from app.utils import read_prompt
from app.models import client
from app.core import logger

def extract_claims_from_text(text: str) -> list[str]:
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=f"Extract all claims from this text:\n {text}",
        
    )

    claims = response.parsed
    logger.info(f"Extracted {len(claims)} claims")

    return claims

def extract_claims_from_image(image, query: str) -> list[str]:
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=[
            image, 
            f"Extract all claims from this image. This query was provided along with the image: {query}"
        ]
    )

    claims = response.parsed
    logger.info(f"Extracted {len(claims)} claims")

    return claims

def extract_claims_from_video(video, query: str) -> list[str]:
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=[
            video, 
            f"Extract all claims from this video. This query was provided along with the video: {query}"
        ]
    )

    claims = response.parsed
    logger.info(f"Extracted {len(claims)} claims")

    return claims