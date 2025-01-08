import streamlit as st
from typing import List

from pipeline.utils.configs import PipelineConfig
from pipeline.utils.logging import setup_logger

from utils.loader import DocumentsLoader
from utils.configs import replace_api_keys

logger = setup_logger(__name__)

class DataLoader:
    """Class for loading and indexing data from various sources."""
    
    def __init__(self, config: PipelineConfig):
        self.config = replace_api_keys(config)
        self.docs_loader = DocumentsLoader(config)
        logger.info("DataLoader initialized")
        st.success("Successfully initialized loader")

    async def load_vault(self) -> None:
        """Load and index documents from the VAULT."""
        try:
            if st.button("Load VAULT"):
                with st.spinner("Loading and indexing the VAULT..."):
                    await self.docs_loader.delete_index()
                    st.success(f"Cleaned index, loading now...")
                    docs = await self.docs_loader.load_vault()
                    await self.index_docs(docs)
                st.success(f"Loaded and indexed {len(docs)} documents from the VAULT.")
        except Exception as e:
            logger.error(f"Error loading VAULT: {e}")
            st.error("Failed to load VAULT")

    async def load_file(self) -> None:
        """Load and index a file uploaded by the user."""
        try:
            uploaded_file = st.file_uploader("Choose a file to upload")
            if st.button("Load File") and uploaded_file is not None:
                with st.spinner("Loading and indexing file..."):
                    docs = await self.docs_loader.load_file(uploaded_file)
                    await self.index_docs(docs)
                st.success(f"Loaded and indexed {uploaded_file.name}")
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            st.error("Failed to load file")

    async def load_directory(self) -> None:
        """Load and index documents from a directory specified by the user."""
        try:
            directory = st.text_input("Enter directory path to load:")
            if st.button("Load Directory") and directory:
                with st.spinner("Loading and indexing directory..."):
                    docs = await self.docs_loader.load_directory(directory)
                    await self.index_docs(docs)
                st.success(f"Loaded and indexed directory: {directory}")
        except Exception as e:
            logger.error(f"Error loading directory: {e}")
            st.error("Failed to load directory")

    async def index_docs(self, docs: List[str]) -> None:
        """Index loaded documents using the loader's index method."""
        try:
            await self.docs_loader.index_docs(docs)
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise

    async def show(self) -> None:
        """Show the data loading section in the Streamlit app."""
        try:
            st.title("load data")
            await self.load_vault()
            await self.load_file() 
            await self.load_directory()
        except Exception as e:
            logger.error(f"Error showing data loader: {e}")
            st.error("An error occurred. Please check the logs.")
