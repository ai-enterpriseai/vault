import logging

from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder

from utils.loader import PineconeManager
from utils.reranker import CohereReranker

class ContextGenerator:
    def __init__(self, openai_api_key: str, pinecone_api_key: str, pinecone_index: str, cohere_api_key: str):
        self.dense_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.sparse_embeddings = BM25Encoder()
        self.pm = PineconeManager(api_key=pinecone_api_key, index_name=pinecone_index)
        self.rr = CohereReranker(api_key=cohere_api_key)
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_context(self, query: str) -> str:
        """
        Retrieves relevant context chunks from Pinecone and reranks them based on the query.
        Returns the augmented query with the context prepended.
        """
        try:
            result = self.pm.retrieve_documents(query, self.dense_embeddings, self.sparse_embeddings, k=10, alpha=0.5)
            chunks = [item[0] for item in result]
            reranked_chunks = self.rr.rerank_chunks(query, chunks)
            context = "\n\n---\n\n".join(reranked_chunks) + "\n\n-----\n\n"
            augmented_query = f"<context> \n\n{context}</context> \n\n{query}"
            logging.info(f"Context retrieved successfully.")
            return augmented_query
        except Exception as e:
            logging.error(f"Error retrieving context: {e}")
            return query