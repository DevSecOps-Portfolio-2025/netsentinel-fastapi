"""
Pydantic schemas for log ingestion.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    """Schema for incoming log entries."""
    
    timestamp: datetime = Field(
        ...,
        description="Log timestamp in ISO 8601 format"
    )
    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source system or application name"
    )
    level: str = Field(
        ...,
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log severity level"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Log message content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata as key-value pairs"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "timestamp": "2025-12-11T10:30:00Z",
                "source": "web-api",
                "level": "ERROR",
                "message": "Database connection timeout",
                "metadata": {
                    "user_id": "12345",
                    "endpoint": "/api/users",
                    "duration_ms": 5000
                }
            }
        }
    }


class LogResponse(BaseModel):
    """Response schema for successful log ingestion."""
    
    status: str = Field(default="accepted")
    message: str = Field(default="Log queued for processing")
