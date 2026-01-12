from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from enum import Enum
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    GNEWS_API_KEY: str = Field(default="", description="GNews API Key")
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key")
    TWITTER_API_KEY: str = Field(default="", description="Twitter API Key")
    TWITTER_API_SECRET: str = Field(default="", description="Twitter API Secret")
    TWITTER_ACCESS_TOKEN: str = Field(default="", description="Twitter Access Token")
    TWITTER_ACCESS_SECRET: str = Field(default="", description="Twitter Access Secret")
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, description="Supabase Key")
    SECRET_KEY: str = Field(default="fallback-secret-key-change-in-production", description="JWT Secret Key")
    ENCRYPTION_KEY: str = Field(default="fallback-encryption-key-change-in-production", description="Encryption Key")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

class TimeFrame(str, Enum):
    """Time frame options for news articles"""
    LAST_24H = "24h"
    LAST_WEEK = "week"
    LAST_MONTH = "month"

class UserInput(BaseModel):
    """Input model for the generate-and-post endpoint"""
    keywords: List[str]
    timeframe: TimeFrame = TimeFrame.LAST_24H
    tone: str = "neutral"

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": ["AI", "technology"],
                "timeframe": "24h",
                "tone": "professional"
            }
        }

# Initialize settings
try:
    settings = Settings()
    logger.info("Settings loaded successfully")
    
    # Log which settings are loaded (without sensitive data)
    logger.info(f"Supabase URL loaded: {bool(settings.SUPABASE_URL)}")
    logger.info(f"Supabase Key loaded: {bool(settings.SUPABASE_KEY)}")
    logger.info(f"GNews API Key loaded: {bool(settings.GNEWS_API_KEY)}")
    
except Exception as e:
    logger.error(f"Error loading settings: {e}")
    raise