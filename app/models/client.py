from google import genai
from app.core import get_settings

settings = get_settings()
client = genai.Client()