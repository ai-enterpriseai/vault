"""
Health check endpoints
"""

from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "VAULT_APP v2.0 API",
        "docs": "/docs",
        "health": "/health"
    }