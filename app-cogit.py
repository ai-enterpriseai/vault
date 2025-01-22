import asyncio
import streamlit as st
from typing import Dict, Callable

from pipeline.utils.logging import setup_logger
from pipeline.utils.configs import (
    PipelineConfig
)

from sections import vault, sequences, data 

logger = setup_logger(__name__)

class App:
    """Main application class for the App."""
    
    def __init__(self, config: dict) -> None:
        """
        Initialize the App with configuration.
        
        Args:
            config: Application configuration dictionary
        
        Raises:
            ValueError: If config is None or empty
        """
        if not config:
            raise ValueError("Configuration cannot be empty")
        self.config = PipelineConfig(**config["pipeline"])
        self.pages: Dict[str, Callable] = {
            "assistant": vault.Vault,
            "sequencer": sequences.Sequences,
            "data": data.DataLoader,
        }
        logger.info("App initialized successfully")

    def set_page_config(self) -> None:
        """Set the page configuration for the Streamlit app."""
        try:
            st.set_page_config(
                page_title="cogit - a new way to interact with computers", 
                page_icon="favicon.png", 
                layout="wide"
            )
        except Exception as e:
            logger.error(f"Unexpected error setting page config: {e}")
            raise RuntimeError

    def show_sidebar(self) -> str:
        """Show the sidebar and return the user's selection."""
        try:
            st.sidebar.image("logo.png", width=300)
        except FileNotFoundError as e:
            logger.error(f"Error loading logo: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading logo: {e}")

        try:
            st.sidebar.title("cogit app")
            st.sidebar.text("explore knowledge base")
            st.sidebar.title("navigation")
            selection: str = st.sidebar.radio("go to", list(self.pages.keys()))
            return selection
        except Exception as e:
            logger.error(f"Unexpected error showing sidebar: {e}")
            return ""

    def hide_st_style(self) -> None:
        """Hide the default Streamlit style elements."""
        hide_st_style: str = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
        try:
            st.markdown(hide_st_style, unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Unexpected error hiding Streamlit style: {e}")

    async def run(self) -> None:
        """Run the App asynchronously."""
        self.set_page_config()
        self.hide_st_style()
        selection: str = self.show_sidebar()
        
        try:
            page_class = self.pages[selection]
            page_instance = page_class(self.config)
            await page_instance.show()
        except KeyError as e:
            logger.error(f"Invalid page selection: {e}")
        except Exception as e:
            logger.error(f"Unexpected error showing page: {e}")

def main():
    """Main entry point for the application."""
    try:
        from utils.configs import load_config
        config = load_config()
        
        app = App(config)
        asyncio.run(app.run())
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        st.error("Failed to start application: Missing required modules")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        st.error("Failed to start application: Invalid configuration")
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred while starting the application")

if __name__ == "__main__":
    main()