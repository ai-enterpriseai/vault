"""
Document loading and processing utilities for VAULT_APP v2.0 backend
Migrated from Streamlit application and adapted for FastAPI
"""

from pathlib import Path 
from typing import List, Union, BinaryIO, Optional

try:
    from pipeline.processor import Processor
    from pipeline.embedder import DenseEmbedder, SparseEmbedder
    from pipeline.indexer import Indexer
    from pipeline.utils.configs import PipelineConfig
    from pipeline.utils.types import ProcessedDocument
    PIPELINE_AVAILABLE = True
except ImportError:
    # Fallback for when pipeline packages aren't available
    Processor = None
    DenseEmbedder = None
    SparseEmbedder = None
    Indexer = None
    PipelineConfig = None
    ProcessedDocument = None
    PIPELINE_AVAILABLE = False

from core.logging import get_logger
from core.exceptions import DocumentProcessingError
from utils.configs import replace_api_keys

logger = get_logger(__name__)


class DocumentsLoader:
    """Class for loading and processing documents from various sources."""
    
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the DocumentsLoader with configuration.
        
        Args:
            config: Pipeline configuration object
            
        Raises:
            ValueError: If configuration is invalid
            DocumentProcessingError: If initialization fails
        """
        if not PIPELINE_AVAILABLE:
            raise DocumentProcessingError("Pipeline components not available")
            
        try:
            self.config = replace_api_keys(config)
            self.processor = Processor(self.config.processor)
            self.dense_embedder = DenseEmbedder(self.config.embedder)
            self.sparse_embedder = SparseEmbedder(self.config.embedder)
            self.indexer = Indexer(
                config=self.config.indexer,
                dense_embedder=self.dense_embedder,
                sparse_embedder=self.sparse_embedder
            )
            logger.info("DocumentsLoader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DocumentsLoader: {e}")
            raise DocumentProcessingError(f"Initialization failed: {e}")

    async def load_vault(self) -> List[ProcessedDocument]:
        """Load and process documents from the VAULT directory.
        
        Returns:
            List of processed documents
            
        Raises:
            DocumentProcessingError: If loading or processing fails
        """
        try:
            # Look for vault data in project root 
            docs_path = Path(__file__).parent.parent.parent
            documents = await self.processor.load_documents(docs_path)
            processed_documents = []
            
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
                
            logger.info(f"Processed {len(processed_documents)} documents from VAULT")
            return processed_documents
            
        except Exception as e:
            logger.error(f"Error loading VAULT: {e}")
            raise DocumentProcessingError(f"Failed to load VAULT: {e}")

    async def load_file(self, file_path: Union[Path, str, BinaryIO]) -> List[ProcessedDocument]:
        """Load and process a single file.
        
        Args:
            file_path: Path to the file, file path string, or file-like object
            
        Returns:
            List of processed documents
            
        Raises:
            DocumentProcessingError: If loading or processing fails
        """
        try:
            # Handle different input types
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            documents = await self.processor.load_documents(file_path)
            logger.info(f"Loaded file: {file_path}")
            
            processed_documents = []
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
                
            logger.info(f"Processed file: {file_path} ({len(processed_documents)} documents)")
            return processed_documents
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise DocumentProcessingError(f"Failed to load file {file_path}: {e}")

    async def load_directory(self, directory: Union[Path, str]) -> List[ProcessedDocument]:
        """Load and process documents from a directory.
        
        Args:
            directory: Path to the directory to process
            
        Returns:
            List of processed documents
            
        Raises:
            DocumentProcessingError: If loading or processing fails
        """
        try:
            if isinstance(directory, str):
                directory = Path(directory)
                
            if not directory.exists():
                raise FileNotFoundError(f"Directory does not exist: {directory}")
            if not directory.is_dir():
                raise ValueError(f"Path is not a directory: {directory}")
            
            documents = await self.processor.load_documents(directory)
            processed_documents = []
            
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
                
            logger.info(f"Processed directory: {directory} ({len(processed_documents)} documents)")
            return processed_documents
            
        except Exception as e:
            logger.error(f"Error loading directory {directory}: {e}")
            raise DocumentProcessingError(f"Failed to load directory {directory}: {e}")

    async def load_uploaded_file(self, file_content: bytes, filename: str, 
                                content_type: Optional[str] = None) -> List[ProcessedDocument]:
        """Load and process an uploaded file from FastAPI.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            content_type: MIME type of the file
            
        Returns:
            List of processed documents
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        try:
            # Create temporary file for processing
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
                tmp_file.write(file_content)
                tmp_path = Path(tmp_file.name)
            
            try:
                # Process the temporary file
                processed_documents = await self.load_file(tmp_path)
                logger.info(f"Processed uploaded file: {filename} ({len(processed_documents)} documents)")
                return processed_documents
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except OSError:
                    logger.warning(f"Failed to clean up temporary file: {tmp_path}")
                    
        except Exception as e:
            logger.error(f"Error processing uploaded file {filename}: {e}")
            raise DocumentProcessingError(f"Failed to process uploaded file {filename}: {e}")

    async def index_documents(self, documents: List[ProcessedDocument]) -> None:
        """Index documents using dense and sparse embeddings.
        
        Args:
            documents: List of documents to index
            
        Raises:
            DocumentProcessingError: If indexing fails
            ValueError: If documents list is empty
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
            
        try:
            await self.indexer.initialize_collection()
            await self.indexer.index_documents(documents=documents)
            logger.info(f"Successfully indexed {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise DocumentProcessingError(f"Failed to index documents: {e}")
        finally:
            try:
                await self.indexer.close()
            except Exception as e:
                logger.warning(f"Error closing indexer: {e}")

    async def delete_index(self) -> None:
        """Delete the vector index collection.
        
        Raises:
            DocumentProcessingError: If deletion fails
        """
        try:
            await self.indexer.delete_collection()
            logger.info("Successfully deleted index collection")
            
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            raise DocumentProcessingError(f"Failed to delete index: {e}")

    async def get_index_stats(self) -> dict:
        """Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
            
        Raises:
            DocumentProcessingError: If stats retrieval fails
        """
        try:
            # This would need to be implemented in the indexer
            # For now, return basic info
            stats = {
                "status": "active" if self.indexer else "inactive",
                "collection_name": getattr(self.config.indexer, 'collection_name', 'unknown'),
                "embedding_dimension": getattr(self.config.embedder, 'dense_model_dimension', 768)
            }
            
            logger.debug(f"Index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            raise DocumentProcessingError(f"Failed to get index stats: {e}")

    async def health_check(self) -> dict:
        """Check the health of the document processing pipeline.
        
        Returns:
            Dictionary with health status
        """
        health_status = {
            "pipeline_available": PIPELINE_AVAILABLE,
            "processor_ready": self.processor is not None,
            "embedder_ready": self.dense_embedder is not None and self.sparse_embedder is not None,
            "indexer_ready": self.indexer is not None,
            "status": "healthy"
        }
        
        # Check if any component is not ready
        if not all([health_status["pipeline_available"], 
                   health_status["processor_ready"],
                   health_status["embedder_ready"], 
                   health_status["indexer_ready"]]):
            health_status["status"] = "degraded"
        
        return health_status

    async def cleanup(self) -> None:
        """Cleanup resources used by the loader."""
        try:
            if self.indexer:
                await self.indexer.close()
            logger.info("DocumentsLoader cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function for FastAPI dependency injection
async def create_documents_loader(config: PipelineConfig) -> DocumentsLoader:
    """Create and return a DocumentsLoader instance.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        Initialized DocumentsLoader instance
    """
    return DocumentsLoader(config)