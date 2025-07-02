"""
Context retrieval utilities for VAULT_APP v2.0 backend
Migrated from Streamlit application and adapted for FastAPI
"""

from typing import List, Dict, Any, Optional

try:
    from pipeline.embedder import DenseEmbedder, SparseEmbedder
    from pipeline.indexer import Indexer
    from pipeline.retriever import Retriever
    from pipeline.utils.model import QueryDecomposition 
    from pipeline.utils.configs import PipelineConfig
    from pipeline.utils.types import RetrievedDocument
    PIPELINE_AVAILABLE = True
except ImportError:
    # Fallback for when pipeline packages aren't available
    DenseEmbedder = None
    SparseEmbedder = None
    Indexer = None
    Retriever = None
    QueryDecomposition = None
    PipelineConfig = None
    RetrievedDocument = None
    PIPELINE_AVAILABLE = False

from core.logging import get_logger
from core.exceptions import RetrievalError
from utils.configs import replace_api_keys

logger = get_logger(__name__)


class ContextRetriever:
    """Retrieves and formats context for augmenting queries with RAG."""

    def __init__(self, config: PipelineConfig) -> None:
        """
        Initialize retriever with configuration.
        
        Args:
            config: Pipeline configuration including embedder, indexer, and retrieval settings
            
        Raises:
            RetrievalError: If initialization fails
        """
        if not PIPELINE_AVAILABLE:
            raise RetrievalError("Pipeline components not available")
            
        try:
            self.config = replace_api_keys(config)
            
            # Initialize components
            self.dense_embedder = DenseEmbedder(self.config.embedder)
            self.sparse_embedder = SparseEmbedder(self.config.embedder)
            self.indexer = Indexer(
                config=self.config.indexer,
                dense_embedder=self.dense_embedder,
                sparse_embedder=self.sparse_embedder
            )
            
            # Initialize retriever with config parameters
            self.retriever = Retriever(
                config=self.config.retriever,
                vector_index=self.indexer,
                llm_client=QueryDecomposition(self.config.generator)
            )
            
            logger.info("ContextRetriever initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ContextRetriever: {e}")
            raise RetrievalError(f"Initialization failed: {e}")

    async def get_context(self, query: str, max_length: int = 4000) -> str:
        """
        Retrieve relevant context and augment the query.
        
        Args:
            query: User query string
            max_length: Maximum length of context to retrieve
            
        Returns:
            str: Query augmented with relevant context, or original query if retrieval fails
            
        Raises:
            RetrievalError: If retrieval process fails critically
        """
        try:
            if not query.strip():
                logger.warning("Empty query provided")
                return query
            
            results = await self.retriever.retrieve(query)
            
            if not results:
                logger.warning(f"No context found for query: {query[:100]}...")
                return query

            # Join context with separators
            context_parts = []
            total_length = 0
            
            for doc in results:
                doc_text = doc.text if hasattr(doc, 'text') else str(doc)
                if total_length + len(doc_text) > max_length:
                    # Truncate if too long
                    remaining = max_length - total_length
                    if remaining > 100:  # Only add if substantial text remains
                        context_parts.append(doc_text[:remaining] + "...")
                    break
                context_parts.append(doc_text)
                total_length += len(doc_text)
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Fix the XML tag formatting (was malformed in original)
            augmented_query = f"<context>\n{context}\n</context>\n\n{query}"
            
            logger.info(f"Context successfully retrieved ({len(results)} documents, {total_length} chars)")
            return augmented_query
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            # For non-critical errors, return original query
            return query

    async def get_context_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents without formatting as context.
        
        Args:
            query: User query string
            top_k: Number of top documents to retrieve
            
        Returns:
            List of document dictionaries with metadata
            
        Raises:
            RetrievalError: If retrieval fails
        """
        try:
            if not query.strip():
                return []
            
            results = await self.retriever.retrieve(query)
            
            documents = []
            for i, doc in enumerate(results[:top_k]):
                doc_dict = {
                    "rank": i + 1,
                    "text": doc.text if hasattr(doc, 'text') else str(doc),
                    "score": getattr(doc, 'score', 0.0),
                    "metadata": getattr(doc, 'metadata', {}),
                    "id": getattr(doc, 'id', f"doc_{i}")
                }
                documents.append(doc_dict)
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            raise RetrievalError(f"Failed to retrieve documents: {e}")

    async def search_similar(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar documents with optional filtering.
        
        Args:
            query: Search query
            filters: Optional filters to apply
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            # This would need to be implemented with filtering support in the retriever
            results = await self.retriever.retrieve(query)
            
            similar_docs = []
            for i, doc in enumerate(results[:top_k]):
                similar_docs.append({
                    "id": getattr(doc, 'id', f"doc_{i}"),
                    "text": doc.text if hasattr(doc, 'text') else str(doc),
                    "score": getattr(doc, 'score', 0.0),
                    "metadata": getattr(doc, 'metadata', {}),
                    "preview": (doc.text[:200] + "...") if hasattr(doc, 'text') and len(doc.text) > 200 else (doc.text if hasattr(doc, 'text') else "")
                })
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise RetrievalError(f"Similarity search failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the retrieval system.
        
        Returns:
            Dictionary with health status and metrics
        """
        health_status = {
            "pipeline_available": PIPELINE_AVAILABLE,
            "embedder_ready": self.dense_embedder is not None and self.sparse_embedder is not None,
            "indexer_ready": self.indexer is not None,
            "retriever_ready": self.retriever is not None,
            "status": "healthy"
        }
        
        # Test basic retrieval if components are ready
        if health_status["retriever_ready"]:
            try:
                # Try a simple test query
                test_results = await self.retriever.retrieve("test query")
                health_status["last_test"] = "success"
                health_status["test_results_count"] = len(test_results) if test_results else 0
            except Exception as e:
                health_status["status"] = "degraded"
                health_status["last_test"] = f"failed: {str(e)}"
        else:
            health_status["status"] = "unavailable"
        
        return health_status

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get retrieval system statistics.
        
        Returns:
            Dictionary with system statistics
        """
        stats = {
            "embedder_model": getattr(self.config.embedder, 'dense_model_name', 'unknown'),
            "embedding_dimension": getattr(self.config.embedder, 'dense_model_dimension', 768),
            "top_k": getattr(self.config.retriever, 'top_k', 25),
            "reranker_enabled": hasattr(self.config.retriever, 'reranker'),
            "reranker_top_k": getattr(getattr(self.config.retriever, 'reranker', None), 'top_k', 0)
        }
        
        return stats

    async def cleanup(self) -> None:
        """Cleanup resources used by the retriever."""
        try:
            if self.indexer:
                await self.indexer.close()
            logger.info("ContextRetriever cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during retriever cleanup: {e}")


# Factory function for FastAPI dependency injection
async def create_context_retriever(config: PipelineConfig) -> ContextRetriever:
    """
    Create and return a ContextRetriever instance.
    
    Args:
        config: Pipeline configuration
        
    Returns:
        Initialized ContextRetriever instance
    """
    return ContextRetriever(config)