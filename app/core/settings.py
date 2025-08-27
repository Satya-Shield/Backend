import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import logging

load_dotenv(override=True)

# os.environ["GOOGLE_FACT_CHECK_API_KEY"] = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
# os.environ["GOOGLE_KG_API_KEY"] = os.getenv("GOOGLE_KG_API_KEY")
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
# # LLM setup

class Settings(BaseSettings):
    """Application settings.

    Attributes:
        app_name: Name of the application
        gemini_api_key: Gemini API key
        debug: Debug mode flag
    """
    app_name: str = "Gen AI Exchange"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    debug: bool = bool(os.getenv("DEBUG", False))

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()

logging.basicConfig(
    level=logging.INFO if not get_settings().debug else logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
