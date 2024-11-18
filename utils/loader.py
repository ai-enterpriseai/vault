from pathlib import Path 
from typing import List 

from pipeline.processor import Processor
from pipeline.embedder import DenseEmbedder, SparseEmbedder
from pipeline.indexer import Indexer

from pipeline.utils.configs import PipelineConfig
from pipeline.utils.types import ProcessedDocument
from pipeline.utils.logging import setup_logger

from utils.configs import replace_api_keys

logger = setup_logger(__name__)

class DocumentsLoader:
    """Class for loading and processing documents from various sources."""
    
    processor: Processor
    dense_embedder: DenseEmbedder
    sparse_embedder: SparseEmbedder
    index: Indexer

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the DocumentsLoader with configuration.
        
        Args:
            config: Pipeline configuration object
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config = replace_api_keys(config)
        self.processor = Processor(self.config.processor)
        self.dense_embedder = DenseEmbedder(self.config.embedder)
        self.sparse_embedder = SparseEmbedder(self.config.embedder)
        self.indexer = Indexer(
            config=self.config.indexer,
            dense_embedder=self.dense_embedder,
            sparse_embedder=self.sparse_embedder
        )
        logger.info("DocumentsLoader initialized")

    async def load_vault(self) -> List[ProcessedDocument]:
        """Load and process documents from the VAULT.
        
        Returns:
            List of processed documents
            
        Raises:
            FileNotFoundError: If VAULT directory cannot be accessed
            ProcessingError: If document processing fails
        """
        try:
            docs_path = Path.cwd().parent
            documents = await self.processor.load_documents(docs_path)
            processed_documents = []
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
            logger.info(f"Processed {len(processed_documents)} documents from VAULT")
            return processed_documents
        except Exception as e:
            logger.error(f"Error loading VAULT: {e}")
            raise

    async def load_file(self, file_path: Path) -> List[ProcessedDocument]:
        """Load and process a single file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of processed documents
            
        Raises:
            FileNotFoundError: If file does not exist
            ProcessingError: If document processing fails
        """
        try:
            documents = await self.processor.load_documents(file_path)
            processed_documents = []
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
            logger.info(f"Processed file: {file_path}")
            return processed_documents
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise

    async def load_directory(self, directory: Path) -> List[ProcessedDocument]:
        """Load and process documents from a directory.
        
        Args:
            directory: Path to the directory to process
            
        Returns:
            List of processed documents
            
        Raises:
            FileNotFoundError: If directory does not exist
            ProcessingError: If document processing fails
        """
        try:
            documents = await self.processor.load_documents(directory)
            processed_documents = []
            async for doc in self.processor.process_documents(documents):
                processed_documents.append(doc)
            logger.info(f"Processed directory: {directory}")
            return processed_documents
        except Exception as e:
            logger.error(f"Error loading directory {directory}: {e}")
            raise

    async def index_docs(self, documents: List[ProcessedDocument]) -> None:
        """Index documents using dense and sparse embeddings.
        
        Args:
            documents: List of documents to index
            
        Raises:
            IndexError: If indexing fails
            ValueError: If documents list is empty
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
            
        try:
            await self.indexer.initialize_collection()
            await self.indexer.index_documents(
                documents=documents,
            )
            logger.info(f"Successfully indexed {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
        finally:
            await self.indexer.close()

    async def delete_index(self) -> None:
        """Delete the vector index collection.
        
        Raises:
            IndexError: If deletion fails
        """
        try:
            await self.indexer.delete_collection()
            logger.info("Successfully deleted index collection")
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            raise