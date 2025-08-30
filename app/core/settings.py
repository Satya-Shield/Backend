from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import logging
import os

load_dotenv(override=True)

class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "Gen AI Exchange"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    factcheck_api_key: str = os.environ.get("GOOGLE_FACT_CHECK_API_KEY", "")
    tawily_api_key: str = os.getenv("TAWILY_API_KEY", "")
    debug: bool = bool(os.getenv("DEBUG", False))

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()

logging.basicConfig(
    # level=logging.INFO if not get_settings().debug else logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if not get_settings().debug else logging.DEBUG)

