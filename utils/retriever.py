import logging
from typing import Optional

from pipeline.embedder import DenseEmbedder, SparseEmbedder
from pipeline.indexer import Indexer
from pipeline.retriever import Retriever

from pipeline.utils.model import QueryDecomposition 
from pipeline.utils.configs import IndexerConfig, EmbedderConfig, RetrieverConfig, PipelineConfig 
from pipeline.utils.logging import setup_logger

logger = setup_logger(__name__)

class ContextRetriever:
    """Retrieves and formats context for augmenting queries."""

    def __init__(self, config: PipelineConfig) -> None:
        """
        Initialize retriever with configuration.
        
        Args:
            config: Pipeline configuration including embedder, indexer, and retrieval settings
        """
        self.config = config
        
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

        logger.info("ContextRetriever initialized")

    async def get_context(self, query: str) -> str:
        """
        Retrieve relevant context and augment the query.
        
        Args:
            query: User query string
            
        Returns:
            str: Query augmented with relevant context, or original query if retrieval fails
            
        Raises:
            Exception: If retrieval process fails (caught and logged)
        """
        try:
            results = await self.retriever.retrieve(query)
            
            if not results:
                logger.warning(f"No context found for query: {query}")
                return query

            context = "\n\n---\n\n".join([doc.text for doc in results])
            augmented_query = f"<context>\n\n{context}\n\n</context>\n\n{query}"
            
            logger.info("Context successfully retrieved and query augmented")
            return augmented_query
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return query