"""Application configuration settings"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = Field(default="Climate Intelligence Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=12000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    reload: bool = Field(default=True, env="RELOAD")
    
    # AI/LLM APIs
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    huggingface_api_token: Optional[str] = Field(default=None, env="HUGGINGFACE_API_TOKEN")
    cohere_api_key: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    replicate_api_token: Optional[str] = Field(default=None, env="REPLICATE_API_TOKEN")
    
    # Google Cloud
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_application_credentials: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    google_cloud_project: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    
    # Azure
    azure_openai_api_key: Optional[str] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(default="2023-12-01-preview", env="AZURE_OPENAI_API_VERSION")
    
    # Weather APIs
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    weatherapi_key: Optional[str] = Field(default=None, env="WEATHERAPI_KEY")
    climate_data_api_key: Optional[str] = Field(default=None, env="CLIMATE_DATA_API_KEY")
    
    # External Data APIs
    nasa_api_key: Optional[str] = Field(default=None, env="NASA_API_KEY")
    noaa_api_token: Optional[str] = Field(default=None, env="NOAA_API_TOKEN")
    world_bank_api_key: Optional[str] = Field(default=None, env="WORLD_BANK_API_KEY")
    carbon_interface_api_key: Optional[str] = Field(default=None, env="CARBON_INTERFACE_API_KEY")
    
    # Database
    database_url: str = Field(default="sqlite:///./climate_intelligence.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    mongodb_uri: str = Field(default="mongodb://localhost:27017/climate_intelligence", env="MONGODB_URI")
    
    # Vector Database
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    weaviate_url: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_gateway: str = Field(default="http://localhost:9091", env="PROMETHEUS_GATEWAY")
    grafana_api_key: Optional[str] = Field(default=None, env="GRAFANA_API_KEY")
    
    # Security
    jwt_secret_key: str = Field(default="jwt-secret-key", env="JWT_SECRET_KEY")
    encryption_key: str = Field(default="encryption-key", env="ENCRYPTION_KEY")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Feature Flags
    enable_real_time_data: bool = Field(default=True, env="ENABLE_REAL_TIME_DATA")
    enable_advanced_analytics: bool = Field(default=True, env="ENABLE_ADVANCED_ANALYTICS")
    enable_external_apis: bool = Field(default=True, env="ENABLE_EXTERNAL_APIS")
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Cache
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # File Upload
    max_file_size: str = Field(default="50MB", env="MAX_FILE_SIZE")
    allowed_file_types: List[str] = Field(
        default=["pdf", "docx", "txt", "md", "csv", "xlsx"], 
        env="ALLOWED_FILE_TYPES"
    )
    
    # Deployment
    environment: str = Field(default="development", env="ENVIRONMENT")
    docker_image_tag: str = Field(default="latest", env="DOCKER_IMAGE_TAG")
    kubernetes_namespace: str = Field(default="climate-intelligence", env="KUBERNETES_NAMESPACE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()