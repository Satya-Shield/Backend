from openai import OpenAI
from app.core import get_settings

settings = get_settings()

client = OpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)