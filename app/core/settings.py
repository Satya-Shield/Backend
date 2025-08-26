import os
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

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