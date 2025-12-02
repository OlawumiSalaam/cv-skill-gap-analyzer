"""
Configuration management for CV Job Analyzer.
Uses pydantic-settings for environment variable validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    
    
    # API Keys
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    serper_api_key: str = Field(..., alias="SERPER_API_KEY")
    
    
    # Application
    app_name: str = Field(default="CV Job Analyzer", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Groq Settings
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    groq_temperature: float = Field(default=0.3, alias="GROQ_TEMPERATURE")
    groq_max_tokens: int = Field(default=2000, alias="GROQ_MAX_TOKENS")
    
    # Serper Settings
    serper_num_results: int = Field(default=5, alias="SERPER_NUM_RESULTS")
    
    # File Upload
    max_file_size_mb: int = Field(default=10, alias="MAX_FILE_SIZE_MB")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def load_settings() -> Settings:
    """Force reload settings from environment."""
    global settings
    settings = Settings()
    return settings