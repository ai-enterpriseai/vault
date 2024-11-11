import logging
import sys
import streamlit as st

from typing import Dict, Callable

from sections import vault, data, settings

class VaultApp:
    """
    Main application class for the Vault App.
    """
    def __init__(self):
        self.pages: Dict[str, Callable] = {
            "Bot": vault.VaultAI,
            "Data": data.DataLoader,
            "Settings": settings.SettingsApp,
        }
        self.setup_logging()

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def set_page_config(self) -> None:
        """
        Set the page configuration for the Streamlit app.
        """
        try:
            st.set_page_config(page_title="AI Use Cases - LLM for Business", page_icon=":speech_balloon:", layout="wide")
        except Exception as e:
            logging.error(f"Unexpected error setting page config: {e}")
            sys.exit(1)

    def show_sidebar(self) -> str:
        """
        Show the sidebar and return the user's selection.
        """
        try:
            st.sidebar.image("logo.png", width=300)
        except FileNotFoundError as e:
            logging.error(f"Error loading logo: {e}")
        except Exception as e:
            logging.error(f"Unexpected error loading logo: {e}")

        try:
            st.sidebar.title("AI Use Case App")
            st.sidebar.text("Explore knowledge base")
            st.sidebar.title("Navigation")
            selection: str = st.sidebar.radio("Go to", list(self.pages.keys()))
            return selection
        except Exception as e:
            logging.error(f"Unexpected error showing sidebar: {e}")
            return ""

    def hide_st_style(self) -> None:
        """
        Hide the default Streamlit style elements.
        """
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
            logging.error(f"Unexpected error hiding Streamlit style: {e}")

    def run(self) -> None:
        """
        Run the Vault App.
        """
        self.set_page_config()
        selection: str = self.show_sidebar()
        try:
            page_class = self.pages[selection]
            page_instance = page_class()
            page_instance.show()  # Call the show method with the instance
        except KeyError as e:
            logging.error(f"Invalid page selection: {e}")
        except Exception as e:
            logging.error(f"Unexpected error showing page: {e}")
        self.hide_st_style()

if __name__ == "__main__":
    app = VaultApp()
    app.run()