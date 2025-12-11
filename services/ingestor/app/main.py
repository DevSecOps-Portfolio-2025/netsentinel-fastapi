"""
FastAPI application for the Ingestor Service.
High-performance asynchronous log ingestion with Kafka.
"""
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config import settings
from app.schemas import LogCreate, LogResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global Kafka producer instance
kafka_producer: AIOKafkaProducer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifecycle manager for FastAPI application.
    Handles Kafka producer initialization and cleanup.
    """
    global kafka_producer
    
    # Startup: Initialize Kafka producer
    logger.info("Initializing Kafka producer...")
    try:
        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type="gzip",  # Compression (gzip available by default)
            acks='all'  # Wait for all replicas (durability)
        )
        await kafka_producer.start()
        logger.info(f"Kafka producer connected to {settings.kafka_bootstrap_servers}")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        kafka_producer = None
    
    yield
    
    # Shutdown: Close Kafka producer
    if kafka_producer:
        logger.info("Closing Kafka producer...")
        await kafka_producer.stop()
        logger.info("Kafka producer closed successfully")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    kafka_status = "connected" if kafka_producer else "disconnected"
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "kafka": kafka_status
    }


@app.post(
    "/api/v1/logs/ingest",
    response_model=LogResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest log entry",
    description="Asynchronously ingests a log entry into Kafka for processing"
)
async def ingest_log(log_entry: LogCreate):
    """
    Ingest a log entry into the processing pipeline.
    
    This endpoint is optimized for high throughput:
    - Fully asynchronous operation
    - Returns 202 Accepted immediately
    - Validates input with Pydantic
    - Handles Kafka failures gracefully
    """
    # Check if Kafka producer is available
    if not kafka_producer:
        logger.error("Kafka producer is not available")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Log ingestion service is temporarily unavailable. Kafka is not connected."
        )
    
    # Convert Pydantic model to dictionary
    log_data = log_entry.model_dump(mode='json')
    
    # Convert datetime to ISO format string for JSON serialization
    if 'timestamp' in log_data:
        log_data['timestamp'] = log_entry.timestamp.isoformat()
    
    try:
        # Send log to Kafka asynchronously
        # Fire-and-forget for maximum throughput (can be configured for delivery guarantees)
        await kafka_producer.send_and_wait(
            settings.logs_topic,
            value=log_data
        )
        
        logger.debug(f"Log ingested from source: {log_entry.source}, level: {log_entry.level}")
        
        return LogResponse(
            status="accepted",
            message="Log queued for processing"
        )
        
    except KafkaError as e:
        logger.error(f"Kafka error during log ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to queue log for processing: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during log ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the log"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
