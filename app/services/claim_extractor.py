from app.utils import read_prompt
from app.models import client

def extract_claims_from_text(text: str) -> list[str]:
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=f"Extract all claims from this text:\n {text}"
    )

    return response.parsed

def extract_claims_from_image(image, query: str) -> list[str]:
    system_prompt = read_prompt("extract_claim_system_prompt")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
        contents=[
            image, 
            f"Extract all readable text from this image. This query was provided along with the image: {query}"
        ]
    )

    return response.parsed