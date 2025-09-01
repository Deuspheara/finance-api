from functools import lru_cache
from typing import Literal
from pydantic import Field, computed_field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False
    )
    
    # App Configuration
    APP_NAME: str = "FastAPI App"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Database Configuration
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis Configuration
    REDIS_URL: str = Field(..., description="Redis connection URL")
    REDIS_TIMEOUT: int = 5
    
    # Security Configuration
    SECRET_KEY: str = Field(..., min_length=32, description="Secret key for signing")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS Configuration
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = Field(default_factory=list)
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # or "console"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    @computed_field
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @computed_field
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @computed_field  
    @property
    def docs_url(self) -> str | None:
        return "/docs" if not self.is_production else None
        
    @computed_field
    @property 
    def redoc_url(self) -> str | None:
        return "/redoc" if not self.is_production else None

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()