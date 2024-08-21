import os
import logging
from typing import List, Optional, Tuple
import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_unstructured.document_loaders import UnstructuredLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class Unstructured(UnstructuredLoader):
    """Custom UnstructuredLoader. Useful for metadata loading but very slow, not used for this demo"""

    def __init__(self, *args, **kwargs):
        api_key = st.secrets["UNSTRUCTURED_API_KEY"]
        kwargs["api_key"] = api_key
        kwargs["partition_via_api"] = True
        super().__init__(*args, **kwargs)

class DocumentsLoader:
    """Loads documents from various sources."""
    def __init__(self):
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_vault(self) -> List[str]:
        """Load documents from the parent directory."""
        logging.info("Loading documents from the parent directory.")
        directory = os.path.abspath(os.path.join(os.getcwd(), ".."))
        loader = DirectoryLoader(directory, glob="**/*", loader_cls=UnstructuredFileLoader, use_multithreading=True, silent_errors=True, show_progress=True)
        docs = loader.load()
        logging.info(f"Loaded {len(docs)} documents from the parent directory.")
        return docs

    def load_file(self, uploaded_file) -> List[str]:
        """Load documents from an uploaded file."""
        logging.info(f"Loading document from uploaded file: {uploaded_file.name}")
        temp_file_path = f"temp_{uploaded_file.name}"
        try:
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
            loader = UnstructuredFileLoader(file_path=temp_file_path)
            docs = loader.load()
            logging.info(f"Loaded {len(docs)} documents from the uploaded file.")
        except Exception as e:
            logging.error(f"Error loading file: {str(e)}")
            docs = []
        finally:
            # Remove the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.info(f"Temporary file {temp_file_path} removed.")

        return docs

    def load_directory(self, directory: str) -> List[str]:
        """Load documents from a directory."""
        logging.info(f"Loading documents from directory: {directory}")
        loader = DirectoryLoader(directory, glob="**/*", loader_cls=UnstructuredFileLoader, use_multithreading=True, silent_errors=True, show_progress=True)
        docs = loader.load()
        logging.info(f"Loaded {len(docs)} documents from the directory.")
        return docs

class PineconeManager:
    """Manages Pinecone operations."""
    def __init__(self, api_key: str, index_name: str):
        self.api_key = api_key
        self.index_name = index_name
        self.pinecone = self._initialize_pinecone()
        self.setup_logging()

    def setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _initialize_pinecone(self) -> Optional[Pinecone]:
        """Initialize Pinecone connection."""
        logging.info("Initializing Pinecone connection.")
        try:
            pc = Pinecone(api_key=self.api_key)
            logging.info("Successfully connected to Pinecone")
            return pc
        except Exception as e:
            logging.error(f"Failed to initialize Pinecone: {str(e)}")
            return None

    def _check_index_exists(self) -> None:
        """Check if index exists, create if not."""
        logging.info(f"Checking if index '{self.index_name}' exists.")
        existing_indexes = [index['name'] for index in self.pinecone.list_indexes()]
        if self.index_name not in existing_indexes:
            logging.warning(f"Index '{self.index_name}' does not exist. Creating it now...")
            self.pinecone.create_index(
                name=self.index_name,
                dimension=1536,  # Dimension for the ADA embeddings
                metric='dotproduct',
                spec=ServerlessSpec(
                    cloud=st.secrets["PINECONE_CLOUD"],
                    region=st.secrets["PINECONE_REGION"]
                )
            )
            st.success(f"Created index '{self.index_name}'")
            logging.info(f"Created index '{self.index_name}'")
        else:
            st.info(f"Index '{self.index_name}' already exists.")
            logging.info(f"Index '{self.index_name}' already exists.")

    def _delete_all_from_index(self) -> None:
        """Delete all vectors from the index."""
        logging.info(f"Deleting all vectors from index '{self.index_name}'.")
        try:
            self.pinecone.delete(delete_all=True)
            logging.info(f"All vectors deleted from index '{self.index_name}'")
        except Exception as e:
            logging.error(f"Error deleting vectors from index '{self.index_name}': {str(e)}")

    def load_and_index_docs(self, docs: List[str], dense_embeddings, sparse_embeddings) -> None:
        """Load and index documents with both dense and sparse vectors."""
        logging.info("Loading and indexing documents.")
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            texts = text_splitter.split_documents(docs)

            # Extract text content and metadata
            texts_with_metadata = [(t.page_content, t.metadata) for t in texts]
            corpus = [t[0] for t in texts_with_metadata]

            # Generate dense embeddings
            dense_vectors = dense_embeddings.embed_documents([t[0] for t in texts_with_metadata])

            # Generate sparse embeddings
            sparse_embeddings.fit(corpus)
            sparse_vectors = sparse_embeddings.encode_documents([t[0] for t in texts_with_metadata])

            # Combine dense and sparse representations
            combined_vectors = [
                {
                    "id": f"doc_{i}",
                    "values": dense_vector,
                    "sparse_values": {"indices": sparse_vector["indices"], "values": sparse_vector["values"]},
                    "metadata": {**metadata[1], "text": text}
                }
                for i, (text, metadata, dense_vector, sparse_vector) in enumerate(zip(corpus, texts_with_metadata, dense_vectors, sparse_vectors))
            ]

            # Get Pinecone index
            index = self.pinecone.Index(self.index_name)

            # Batch the upserts
            batch_size = 100
            for i in range(0, len(combined_vectors), batch_size):
                try:
                    batch = combined_vectors[i:i + batch_size]
                    index.upsert(vectors=batch)
                    logging.info(f"Upserted batch {i // batch_size + 1} of {len(combined_vectors) // batch_size + 1}")
                except Exception as e:
                    logging.error(f"Error upserting batch {i // batch_size + 1}: {str(e)}")

            try:
                sparse_embeddings.dump("bm25_params.json")
            except Exception as e:
                logging.error(f"Error dumping bm25_params.json: {str(e)}")

            logging.info("Finished loading and indexing documents.")
        except Exception as e:
            logging.error(f"Error loading and indexing documents: {str(e)}")

    def retrieve_documents(self, query: str, dense_embeddings, sparse_embeddings, k: int = 10, alpha: Optional[float] = None) -> List[Tuple[str, float]]:
        """Hybrid search combining sparse and dense vectors."""
        logging.info(f"Retrieving documents for query: {query}")
        try:
            # Generate dense query vector
            dense_query = dense_embeddings.embed_query(query)

            # Load BM25 params from JSON
            try:
                sparse_embeddings.load("bm25_params.json")
            except FileNotFoundError:
                logging.error("bm25_params.json not found. Skipping sparse search.")
                sparse_query = None
            except Exception as e:
                logging.error(f"Error loading bm25_params.json: {str(e)}")
                sparse_query = None
            else:
                # Generate sparse query vector
                sparse_query = sparse_embeddings.encode_queries([query])[0]
                sparse_vector = {
                    "indices": sparse_query["indices"],
                    "values": sparse_query["values"]
                }

            # Get Pinecone index
            index = self.pinecone.Index(self.index_name)

            if sparse_query is not None and alpha is not None:
                # Perform hybrid search
                try:
                    results = index.query(
                        vector=dense_query,
                        sparse_vector=sparse_vector,
                        top_k=k,
                        alpha=alpha,
                        include_metadata=True
                    )
                except Exception as e:
                    logging.error(f"Error performing hybrid search: {str(e)}")
                    docs = []
            else:
                # Perform dense-only search
                try:
                    results = index.query(
                        vector=dense_query,
                        top_k=k,
                        include_metadata=True
                    )
                except Exception as e:
                    logging.error(f"Error performing dense search: {str(e)}")
                    docs = []

            # Extract results
            docs = [(match['metadata']['text'], match['score']) for match in results['matches']]
            logging.info(f"Retrieved {len(docs)} documents for query: {query}")
            return docs
        except Exception as e:
            logging.error(f"Error retrieving documents: {str(e)}")
            return []