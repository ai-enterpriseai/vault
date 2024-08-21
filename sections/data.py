import logging
import streamlit as st
from typing import List

from langchain_openai import OpenAIEmbeddings
from pinecone_text.sparse import BM25Encoder
from utils.loader import (
    DocumentsLoader,
    PineconeManager
)

class DataLoader:
    """
    Class for loading and indexing data from various sources.
    """
    def __init__(self):
        self.pm = PineconeManager(api_key=st.secrets["PINECONE_API_KEY"], index_name=st.secrets["PINECONE_INDEX"])
        self.pc = self.pm.pinecone
        self.index_name = st.secrets["PINECONE_INDEX"]
        self.dense_embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])
        self.sparse_embeddings = BM25Encoder()
        self.dl = DocumentsLoader()
        self.setup_logging()
        st.success("Successfully connected to Pinecone")

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_vault(self) -> None:
        """
        Load and index documents from the VAULT.
        """
        try:
            if st.button("Load VAULT"):
                with st.spinner("Loading and indexing the VAULT..."):
                    self.delete_index()
                    st.success(f"Cleaned index, loading now...")
                    docs = self.dl.load_vault()
                    self.load_and_index_docs(docs)
                st.success(f"Loaded and indexed {len(docs)} documents from the VAULT.")
        except Exception as e:
            logging.error(f"Error loading VAULT: {e}")

    def load_file(self) -> None:
        """
        Load and index a file uploaded by the user.
        """
        try:
            uploaded_file = st.file_uploader("Choose a file to upload")
            if st.button("Load File") and uploaded_file is not None:
                with st.spinner("Loading and indexing file..."):
                    docs = self.dl.load_file(uploaded_file)
                    self.load_and_index_docs(docs)
                st.success(f"Loaded and indexed {uploaded_file.name}")
        except Exception as e:
            logging.error(f"Error loading file: {e}")

    def load_directory(self) -> None:
        """
        Load and index documents from a directory specified by the user.
        """
        try:
            directory = st.text_input("Enter directory path to load:")
            if st.button("Load Directory") and directory:
                with st.spinner("Loading and indexing directory..."):
                    docs = self.dl.load_directory(directory)
                    self.load_and_index_docs(docs)
                st.success(f"Loaded and indexed {len(docs)} documents from {directory}")
        except Exception as e:
            logging.error(f"Error loading directory: {e}")

    def delete_index(self) -> None:
        """
        Delete all documents from the index.
        """
        try:
            self.pm._delete_all_from_index()
        except Exception as e:
            logging.error(f"Error deleting index: {e}")

    def load_and_index_docs(self, docs: List[str]) -> None:
        """
        Load and index a list of documents.
        """
        try:
            self.pm.load_and_index_docs(docs, self.dense_embeddings, self.sparse_embeddings)
        except Exception as e:
            logging.error(f"Error loading and indexing documents: {e}")

    def show(self) -> None:
        """
        Show the data loading section in the Streamlit app.
        """
        try:
            st.title("Load Data")
            self.pm._check_index_exists()
            self.load_vault()
            self.load_file()
            self.load_directory()
        except Exception as e:
            logging.error(f"Error showing data loader: {e}")

if __name__ == "__main__":
    data_loader = DataLoader()
    data_loader.show()