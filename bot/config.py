"""
Configuration management with validation
"""

import os
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """
    Bot configuration with validation
    """
    
    model_config = ConfigDict(validate_assignment=True)
    
    # === TELEGRAM API ===
    API_ID: int = Field(..., description="Telegram API ID")
    API_HASH: str = Field(..., description="Telegram API Hash")
    
    # === CHANNELS ===
    SOURCE_CHANNELS: List[str] = Field(
        default_factory=list,
        description="Source channels to monitor"
    )
    TARGET_CHANNEL: str = Field(..., description="Target channel for forwarding")
    
    # === FILTERING ===
    MAX_POSTS_PER_DAY: int = Field(default=0, ge=0)
    KEYWORDS: List[str] = Field(
        default_factory=list,
        description="Keywords to filter messages"
    )
    SPAM_KEYWORDS: List[str] = Field(
        default_factory=list,
        description="Spam keywords to reject messages"
    )
    
    # === AI (Optional) ===
    GROQ_API_KEY: Optional[str] = Field(default=None, description="Groq API key for AI tagging")
    
    # === BOT API (Optional) ===
    BOT_TOKEN: Optional[str] = Field(default=None, description="Bot API token for review mode")
    REVIEW_CHANNEL_ID: Optional[str] = Field(
        default=None,
        description="Review channel ID or username"
    )
    
    # === MONITORING ===
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    METRICS_PORT: int = Field(default=8080, ge=1024, le=65535)
    
    # === ENVIRONMENT ===
    ENVIRONMENT: str = Field(default="development", pattern="^(development|production)$")
    DATABASE_PATH: str = Field(default="bot.db", description="SQLite database path")
    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    
    @field_validator('API_ID', mode='before')
    @classmethod
    def validate_api_id(cls, v):
        """Validate API_ID is set and valid"""
        if isinstance(v, str):
            v = int(v) if v.isdigit() else 0
        if not v or v == 0:
            raise ValueError("API_ID must be set and non-zero")
        return v
    
    @field_validator('API_HASH')
    @classmethod
    def validate_api_hash(cls, v):
        """Validate API_HASH is set"""
        if not v or v == '':
            raise ValueError("API_HASH must be set")
        return v
    
    @field_validator('TARGET_CHANNEL')
    @classmethod
    def validate_target_channel(cls, v):
        """Validate target channel format"""
        if not v:
            raise ValueError("TARGET_CHANNEL must be set")
        if not v.startswith('@') and not v.lstrip('-').isdigit():
            raise ValueError("TARGET_CHANNEL must start with @ or be a numeric ID")
        return v
    
    @field_validator('SOURCE_CHANNELS', mode='before')
    @classmethod
    def parse_source_channels(cls, v):
        """Parse source channels from comma-separated string"""
        if isinstance(v, str):
            return [ch.strip() for ch in v.split(',') if ch.strip()]
        return v
    
    @field_validator('SOURCE_CHANNELS')
    @classmethod
    def validate_source_channels(cls, v):
        """Validate source channels are set"""
        if not v:
            raise ValueError("SOURCE_CHANNELS must contain at least one channel")
        return v
    
    @field_validator('KEYWORDS', mode='before')
    @classmethod
    def parse_keywords(cls, v):
        """Parse keywords from comma-separated string"""
        if isinstance(v, str):
            return [kw.strip() for kw in v.split(',') if kw.strip()]
        return v
    
    @field_validator('KEYWORDS')
    @classmethod
    def validate_keywords(cls, v):
        """Allow empty keywords"""
        return v
    
    @field_validator('SPAM_KEYWORDS', mode='before')
    @classmethod
    def parse_spam_keywords(cls, v):
        """Parse spam keywords from comma-separated string"""
        if isinstance(v, str):
            return [kw.strip() for kw in v.split(',') if kw.strip()]
        return v
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Create config from environment variables
        
        Returns:
            Config instance
        """
        return cls(
            API_ID=os.getenv('API_ID', '0'),
            API_HASH=os.getenv('API_HASH', ''),
            SOURCE_CHANNELS=os.getenv('SOURCE_CHANNELS', ''),
            TARGET_CHANNEL=os.getenv('TARGET_CHANNEL', ''),
            MAX_POSTS_PER_DAY=int(os.getenv('MAX_POSTS_PER_DAY', '5')),
            KEYWORDS=os.getenv('KEYWORDS', ''),
            SPAM_KEYWORDS=os.getenv('SPAM_KEYWORDS', ''),
            GROQ_API_KEY=os.getenv('GROQ_API_KEY'),
            BOT_TOKEN=os.getenv('BOT_TOKEN'),
            REVIEW_CHANNEL_ID=os.getenv('REVIEW_CHANNEL_ID'),
            SENTRY_DSN=os.getenv('SENTRY_DSN'),
            METRICS_PORT=int(os.getenv('METRICS_PORT', '8080')),
            ENVIRONMENT=os.getenv('ENVIRONMENT', 'development'),
            DATABASE_PATH=os.getenv('DATABASE_PATH', 'bot.db'),
            LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO'),
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
