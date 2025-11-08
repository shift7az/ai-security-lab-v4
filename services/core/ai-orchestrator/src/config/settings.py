"""
Configuration Settings for AI Security Lab v4.0
Environment-based configuration using Pydantic Settings
"""

from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    
    app_name: str = "AI Security Lab v4.0 - AI Orchestrator"
    app_version: str = "4.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # ========================================================================
    # Database Configuration (TimescaleDB)
    # ========================================================================
    
    database_host: str = Field(default="timescaledb", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="security_events", env="DATABASE_NAME")
    database_user: str = Field(default="security", env="DATABASE_USER")
    database_password: str = Field(default="", env="DATABASE_PASSWORD")
    database_min_pool_size: int = Field(default=5, env="DATABASE_MIN_POOL_SIZE")
    database_max_pool_size: int = Field(default=20, env="DATABASE_MAX_POOL_SIZE")
    
    # ========================================================================
    # Redis Configuration
    # ========================================================================
    
    redis_host: str = Field(default="redis-stack", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    
    # ========================================================================
    # Frigate Configuration
    # ========================================================================
    
    frigate_url: str = Field(default="http://frigate-plus:5000", env="FRIGATE_URL")
    frigate_api_key: str = Field(default="", env="FRIGATE_API_KEY")
    frigate_timeout: int = Field(default=10, env="FRIGATE_TIMEOUT")
    
    # ========================================================================
    # Threat Detector Configuration
    # ========================================================================
    
    threat_detector_url: str = Field(
        default="http://threat-detector:8001",
        env="THREAT_DETECTOR_URL"
    )
    threat_detector_enabled: bool = Field(default=True, env="THREAT_DETECTOR_ENABLED")
    threat_detector_timeout: int = Field(default=30, env="THREAT_DETECTOR_TIMEOUT")
    
    # ========================================================================
    # AI Orchestrator Configuration
    # ========================================================================
    
    max_concurrent_analyses: int = Field(default=10, env="MAX_CONCURRENT_ANALYSES")
    detection_queue_size: int = Field(default=1000, env="DETECTION_QUEUE_SIZE")
    result_queue_size: int = Field(default=1000, env="RESULT_QUEUE_SIZE")
    worker_count: int = Field(default=5, env="WORKER_COUNT")
    
    # ========================================================================
    # API Configuration
    # ========================================================================
    
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=1, env="API_WORKERS")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # ========================================================================
    # Logging Configuration
    # ========================================================================
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_to_file: bool = Field(default=False, env="LOG_TO_FILE")
    log_file_path: str = Field(default="logs/orchestrator.log", env="LOG_FILE_PATH")
    
    # ========================================================================
    # Monitoring Configuration
    # ========================================================================
    
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")
    jaeger_host: str = Field(default="tempo", env="JAEGER_HOST")
    jaeger_port: int = Field(default=6831, env="JAEGER_PORT")
    
    # ========================================================================
    # Storage Configuration
    # ========================================================================
    
    minio_endpoint: str = Field(default="minio:9000", env="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="", env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="", env="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    minio_bucket: str = Field(default="security-footage", env="MINIO_BUCKET")
    
    # ========================================================================
    # Feature Flags
    # ========================================================================
    
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    enable_batch_processing: bool = Field(default=True, env="ENABLE_BATCH_PROCESSING")
    enable_auto_response: bool = Field(default=False, env="ENABLE_AUTO_RESPONSE")
    
    # ========================================================================
    # Performance Configuration
    # ========================================================================
    
    gpu_enabled: bool = Field(default=True, env="GPU_ENABLED")
    gpu_device_id: int = Field(default=0, env="GPU_DEVICE_ID")
    batch_size: int = Field(default=8, env="BATCH_SIZE")
    inference_timeout: int = Field(default=30, env="INFERENCE_TIMEOUT")
    
    # ========================================================================
    # Pydantic Configuration
    # ========================================================================
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields
    
    # ========================================================================
    # Computed Properties
    # ========================================================================
    
    @property
    def database_url(self) -> str:
        """Get full database connection URL."""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
    
    @property
    def redis_url(self) -> str:
        """Get full Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def get_log_level(self) -> str:
        """Get log level adjusted for environment."""
        if self.is_development and self.debug:
            return "DEBUG"
        return self.log_level
