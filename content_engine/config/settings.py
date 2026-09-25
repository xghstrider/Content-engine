"""
Settings configuration for Content Engine
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProviderSettings(BaseSettings):
    """AI Provider Configuration"""
    
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_base_url: str = Field(default="https://api.anthropic.com", env="ANTHROPIC_BASE_URL")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-1.5-pro", env="GOOGLE_MODEL")
    
    local_model_path: Optional[str] = Field(default=None, env="LOCAL_MODEL_PATH")
    local_model_type: str = Field(default="llama", env="LOCAL_MODEL_TYPE")
    
    default_provider: str = Field(default="openai", env="DEFAULT_PROVIDER")


class PlatformSettings(BaseSettings):
    """Platform-specific settings"""
    
    twitter_max_length: int = Field(default=280, env="TWITTER_MAX_LENGTH")
    twitter_hashtag_limit: int = Field(default=5, env="TWITTER_HASHTAG_LIMIT")
    
    instagram_caption_length: int = Field(default=2200, env="INSTAGRAM_CAPTION_LENGTH")
    instagram_hashtag_limit: int = Field(default=30, env="INSTAGRAM_HASHTAG_LIMIT")
    
    facebook_post_length: int = Field(default=63206, env="FACEBOOK_POST_LENGTH")
    facebook_hashtag_limit: int = Field(default=20, env="FACEBOOK_HASHTAG_LIMIT")
    
    linkedin_post_length: int = Field(default=3000, env="LINKEDIN_POST_LENGTH")
    linkedin_hashtag_limit: int = Field(default=10, env="LINKEDIN_HASHTAG_LIMIT")
    
    pinterest_description_length: int = Field(default=500, env="PINTEREST_DESCRIPTION_LENGTH")
    snapchat_caption_length: int = Field(default=250, env="SNAPCHAT_CAPTION_LENGTH")


class CacheSettings(BaseSettings):
    """Caching configuration"""
    
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_dir: Path = Field(default=Path(".content_engine_cache"), env="CACHE_DIR")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    max_cache_size: int = Field(default=1000, env="MAX_CACHE_SIZE")


class Settings(BaseSettings):
    """Main Content Engine Settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application settings
    app_name: str = Field(default="Content Engine", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # AI Providers
    ai: AIProviderSettings = Field(default_factory=AIProviderSettings)
    
    # Platform settings
    platforms: PlatformSettings = Field(default_factory=PlatformSettings)
    
    # Cache settings
    cache: CacheSettings = Field(default_factory=CacheSettings)
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Template directories
    template_dirs: List[str] = Field(
        default_factory=lambda: ["templates", "./templates"],
        env="TEMPLATE_DIRS"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance"""
    global _settings
    _settings = None
