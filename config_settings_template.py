"""
Configuration management for RAG Trading System.
Uses pydantic for validation and environment-based settings.
"""
from typing import Optional, List
from pydantic import BaseSettings, validator, PostgresDsn, Field
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Environment
    ENV: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Application
    APP_NAME: str = "RAG Trading System"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Server
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=5000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # Database
    DATABASE_URL: PostgresDsn = Field(..., env="DATABASE_URL")
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # Redis (optional, for Celery)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    MOCK_OPENAI: bool = Field(default=False, env="MOCK_OPENAI")
    
    # Gemini (alternative LLM)
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")
    
    # Trading
    TRADING_ENABLED: bool = Field(default=False, env="TRADING_ENABLED")
    DEFAULT_QUANTITY: float = Field(default=0.001, env="DEFAULT_QUANTITY")
    MAX_RISK_PERCENTAGE: float = Field(default=0.02, env="MAX_RISK_PERCENTAGE")  # 2%
    
    # Price Data
    BINANCE_API_BASE: str = "https://api.binance.com/api/v3"
    USE_MOCK_PRICE_DATA: bool = Field(default=True, env="USE_MOCK_PRICE_DATA")
    PRICE_UPDATE_INTERVAL: int = Field(default=3600, env="PRICE_UPDATE_INTERVAL")  # seconds
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="app.log", env="LOG_FILE")
    LOG_MAX_BYTES: int = Field(default=10_485_760, env="LOG_MAX_BYTES")  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5174", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Feature Flags
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    ENABLE_API_DOCS: bool = Field(default=True, env="ENABLE_API_DOCS")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # File Storage
    UPLOAD_FOLDER: str = Field(default="uploads", env="UPLOAD_FOLDER")
    MAX_UPLOAD_SIZE: int = Field(default=10_485_760, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "pdf"]
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("ENV")
    def validate_environment(cls, v):
        """Validate environment value"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v
    
    @validator("MAX_RISK_PERCENTAGE")
    def validate_risk(cls, v):
        """Validate risk percentage"""
        if not 0 < v <= 0.1:  # Max 10%
            raise ValueError("MAX_RISK_PERCENTAGE must be between 0 and 0.1")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENV == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL"""
        return str(self.DATABASE_URL)
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure single instance.
    """
    return Settings()


# Convenience aliases
settings = get_settings()
