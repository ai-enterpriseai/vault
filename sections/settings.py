import logging
import streamlit as st

from PIL import Image

class SettingsApp:
    def __init__(self):
        self.setup_logging()
        logging.info("SettingsApp instance created")

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def upload_logo(self) -> None:
        """
        Handle logo upload.
        """
        uploaded_logo = st.file_uploader("Upload Logo", type=["png"])
        if uploaded_logo is not None:
            try:
                logo = Image.open(uploaded_logo)
                logo.save("logo.png")
                st.success("Logo updated successfully!")
                logging.info("Logo updated successfully.")
            except Exception as e:
                st.error("Failed to update logo.")
                logging.error(f"Failed to update logo: {e}")

    def api_keys_section(self) -> None:
        """
        Display API keys fields.
        """
        self.openai_api_key = st.text_input("OpenAI API Key", type="password", value=st.secrets.get("OPENAI_API_KEY", ""))
        self.pinecone_api_key = st.text_input("Pinecone API Key", type="password", value=st.secrets.get("PINECONE_API_KEY", ""))
        self.pinecone_index_name = st.text_input("Pinecone Index Name", value=st.secrets.get("PINECONE_INDEX", ""))
        self.pinecone_cloud = st.text_input("Pinecone Cloud", value=st.secrets.get("PINECONE_CLOUD", "aws"))
        self.pinecone_region = st.text_input("Pinecone Region", value=st.secrets.get("PINECONE_REGION", ""))
        self.cohere_api_key = st.text_input("Cohere API Key", type="password", value=st.secrets.get("COHERE_API_KEY", ""))
    
    def show(self) -> None:
        """
        Display the settings page.
        """
        st.title("Settings")
        self.upload_logo()
        self.api_keys_section()

if __name__ == "__main__":
    settings_app = SettingsApp()
    settings_app.show()