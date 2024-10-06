from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # Base directory path
    BASE_DIR: Path = Path(__file__).resolve().parent

    # Database settings
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/shop.db"

# Global settings
settings = Settings()
