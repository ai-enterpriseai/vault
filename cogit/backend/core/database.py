"""
Database connection and initialization for VAULT_APP v2.0
Handles Qdrant vector database connections, health checks, and connection pooling
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.http.exceptions import UnexpectedResponse
    QDRANT_AVAILABLE = True
except ImportError:
    QdrantClient = None
    models = None
    UnexpectedResponse = Exception
    QDRANT_AVAILABLE = False

from core.config import get_settings
from core.logging import get_logger
from core.exceptions import DatabaseConnectionError, DatabaseInitializationError

logger = get_logger(__name__)


class QdrantDatabase:
    """Qdrant vector database manager with connection pooling and health checks."""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.settings = get_settings()
        self.is_connected = False
        self.connection_pool_size = 10
        
    async def initialize(self) -> None:
        """Initialize database connection and verify health."""
        if not QDRANT_AVAILABLE:
            logger.warning("Qdrant client not available - running in mock mode")
            return
            
        try:
            logger.info(f"Connecting to Qdrant at {self.settings.QDRANT_URL}")
            
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=self.settings.QDRANT_URL,
                api_key=self.settings.QDRANT_API_KEY,
                timeout=30.0
            )
            
            # Test connection
            await self.health_check()
            
            # Initialize collections if needed
            await self.ensure_collections_exist()
            
            self.is_connected = True
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseInitializationError(f"Database initialization failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health and return status."""
        if not self.client:
            return {"status": "disconnected", "error": "No client connection"}
            
        try:
            # Qdrant health check
            health_info = self.client.get_collections()
            
            return {
                "status": "healthy",
                "connection": "active",
                "collections": len(health_info.collections),
                "url": self.settings.QDRANT_URL
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy", 
                "error": str(e),
                "connection": "failed"
            }
    
    async def ensure_collections_exist(self) -> None:
        """Ensure required collections exist in Qdrant."""
        if not self.client:
            return
            
        try:
            required_collections = [
                {
                    "name": self.settings.QDRANT_COLLECTION_NAME,
                    "vectors_config": models.VectorParams(
                        size=768,  # Default embedding dimension
                        distance=models.Distance.COSINE
                    )
                }
            ]
            
            existing_collections = self.client.get_collections()
            existing_names = [col.name for col in existing_collections.collections]
            
            for collection_config in required_collections:
                if collection_config["name"] not in existing_names:
                    logger.info(f"Creating collection: {collection_config['name']}")
                    
                    self.client.create_collection(
                        collection_name=collection_config["name"],
                        vectors_config=collection_config["vectors_config"]
                    )
                    
                    logger.info(f"Collection {collection_config['name']} created successfully")
                else:
                    logger.info(f"Collection {collection_config['name']} already exists")
                    
        except Exception as e:
            logger.error(f"Error ensuring collections exist: {e}")
            raise DatabaseInitializationError(f"Failed to create collections: {e}")
    
    async def close(self) -> None:
        """Close database connections."""
        try:
            if self.client:
                # Qdrant client doesn't have explicit close method
                self.client = None
                
            self.is_connected = False
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    def get_client(self) -> QdrantClient:
        """Get Qdrant client instance."""
        if not self.is_connected:
            raise DatabaseConnectionError("Database not connected")
        return self.client


# Global database instance
_database: Optional[QdrantDatabase] = None


def get_database() -> QdrantDatabase:
    """Get global database instance."""
    global _database
    if _database is None:
        _database = QdrantDatabase()
    return _database


async def initialize_database() -> None:
    """Initialize database connection."""
    database = get_database()
    await database.initialize()


async def close_database() -> None:
    """Close database connection."""
    global _database
    if _database:
        await _database.close()
        _database = None


@asynccontextmanager
async def get_db_session():
    """Get database session context manager."""
    database = get_database()
    try:
        yield database
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


# Dependency for FastAPI endpoints
async def get_database_dependency() -> QdrantDatabase:
    """FastAPI dependency to get database instance."""
    return get_database()