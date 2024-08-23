import cohere
import logging
from typing import List

class CohereReranker:
    """
    A class to rerank text chunks based on their relevance to a given query.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the ChunkReranker with the Cohere API key.
        """
        self.client = cohere.Client(api_key)
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def rerank_chunks(self, query: str, chunks: List[str], top_n: int = 3) -> List[str]:
        """
        Rerank the given text chunks based on their relevance to the query.
        """
        try:
            results = self.client.rerank(
                query=query,
                documents=chunks,
                top_n=top_n,
                model="rerank-multilingual-v3.0"
            ) 

            top_chunks = sorted(
                results.results,
                key=lambda x: x.relevance_score,
                reverse=True
            )[:top_n]

            return [
                chunks[chunk.index]
                for chunk in top_chunks
                if chunk.index < len(chunks)
            ]
        except Exception as e:
            logging.error("An unexpected error occurred: %s", str(e))
            return []