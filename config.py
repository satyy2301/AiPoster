from pydantic import BaseModel
from pydantic_settings import BaseSettings
from enum import Enum
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    GNEWS_API_KEY: str
    OPENROUTER_API_KEY: str
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    TWITTER_ACCESS_TOKEN: str
    TWITTER_ACCESS_SECRET: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

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
settings = Settings()

assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY too short"
assert len(settings.ENCRYPTION_KEY) >= 32, "ENCRYPTION_KEY too short"