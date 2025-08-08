"""Configuration settings for the application."""
import os
from functools import lru_cache
from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
        except Exception as e:
            # Check if .env file exists
            env_file = Path(__file__).parent.parent.parent / ".env"
            if not env_file.exists():
                raise ValueError(
                    "GEMINI_API_KEY not found. Please create a .env file in the root directory "
                    "with your Gemini API key: GEMINI_API_KEY=your_api_key_here"
                ) from e
            raise


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create a global instance
settings = get_settings()