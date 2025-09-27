"""
Settings configuration for AI Security Lab v4.0 Threat Detector
"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database settings
    database_password: str = os.getenv("POSTGRES_PASSWORD", "secure-password")
    redis_password: str = os.getenv("REDIS_PASSWORD", "secure-password")

    # API settings
    frigate_api_key: str = os.getenv("PLUS_API_KEY", "")

    # Model settings
    model_cache_dir: str = "/models"
    weapon_detection_model: str = "yolov8n-weapon.pt"
    behavior_model: str = "behavior-lstm.pt"

    # Performance settings
    max_concurrent_analyses: int = 10
    analysis_timeout_seconds: int = 30
    cache_ttl_seconds: int = 3600

    # Alert settings
    alert_webhook_url: Optional[str] = os.getenv("ALERT_WEBHOOK_URL")
    alert_threshold_score: float = 0.7

    # GPU settings
    use_gpu: bool = os.getenv("USE_GPU", "true").lower() == "true"
    gpu_device_id: int = int(os.getenv("GPU_DEVICE_ID", "0"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
