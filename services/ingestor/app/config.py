"""
Configuration module for the Ingestor Service.
Uses pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Kafka Configuration
    kafka_bootstrap_servers: str = "kafka:9092"
    logs_topic: str = "logs-raw"
    
    # Application Configuration
    app_name: str = "NetSentinel Ingestor"
    app_version: str = "1.0.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
