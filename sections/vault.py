import logging
import openai
import streamlit as st
from typing import List, Dict

from utils.generator import ContextGenerator

openai.api_key = st.secrets["OPENAI_API_KEY"]

class VaultAI:
    def __init__(self):
        self.setup_logging()  # Add this line to initialize logging
        # Initialize the chat messages history in the session state
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": self.get_system_prompt()}]
        self.messages = st.session_state.messages
        logging.info("VaultAI instance created")

    def setup_logging(self) -> None:
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_system_prompt(self) -> str:
        """Returns the system prompt for the AI assistant."""
        return """
        Du bist VAULT.AI, ein hilfreicher Assistent, der die Workshop-Teilnehmenden bei der Exploration von dem VAULT zum Thema GPT im Unternehmen unterstützt.

        Du verwendest ausschließlich die Informationen aus dem Kontext <context>, um die Antworten zu geben. 

        Dabei nutzt du im Detail die Kontextinformationen im <context> und achtest darauf, nur die wichtigsten Punkte zu erklären und besonders gut auf die Frage des Nutzers zu antworten.

        Am Anfang begrüßt du den Nutzer (kannst immer duzen!) und erklärst kurz über deine Funktionalitäten: 

        Hallo, ich bin VAULT.AI. <-- erkläre hier

        Ich kann zum Beispiel folgende Fragen beantworten: 

        - was ist InhouseGPT
        - was ist In-Context Learning
        - was denkst du zu BloombergGPT

        Mein Ziel ist, dich zu unterstützen, so dass du eine KI im eigenen Unternehmen entwickeln kannst!

        ***
        """

    def handle_user_input(self, prompt: str):
        """Handles user input by appending it to the chat history and augmenting it with context."""
        try:
            cg = ContextGenerator(openai_api_key = openai.api_key, pinecone_api_key = st.secrets["PINECONE_API_KEY"], pinecone_index = st.secrets["PINECONE_INDEX"], cohere_api_key=st.secrets["COHERE_API_KEY"])
            augmented_prompt = cg.get_context(prompt)
            self.messages.append({"role": "user", "content": prompt})
            self.messages.append({"role": "user", "content": augmented_prompt})
            logging.info(f"User input received: {prompt}")
        except Exception as e:
            logging.error(f"Unexpected error handling user input: {e}")

    def display_chat_history(self):
        """Displays the chat history in the Streamlit app."""
        try:
            for message in self.messages:
                if message["role"] == "system" or message["role"] == "context":
                    continue
                if message["content"].startswith("<context>"): 
                    continue
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        except Exception as e:
            logging.error(f"Unexpected error displaying chat history: {e}")

    def generate_assistant_response(self):
        """Generates a response from the AI assistant and appends it to the chat history."""
        try:
            with st.chat_message("assistant"):
                response = ""
                resp_container = st.empty()

                try:
                    # Create a stream for chat completions
                    stream = openai.chat.completions.create(
                        model="gpt-4o-2024-05-13", # local models can be served with vLLM with the same syntax 
                        messages=[{"role": m["role"], "content": m["content"]} for m in self.messages],
                        stream=True,
                    )

                    # Process each chunk as it arrives
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            response += chunk.choices[0].delta.content
                            resp_container.markdown(response)

                    message = {"role": "assistant", "content": response}
                    self.messages.append(message)
                    logging.info("Assistant response generated successfully")

                except Exception as e:
                    logging.error(f"Error generating assistant response: {e}")
                    resp_container.error("An error occurred while generating the response.")
        except Exception as e:
            logging.error(f"Unexpected error generating assistant response: {e}")
    
    def show(self):
        """Displays the Streamlit app for interacting with the AI assistant."""
        try:
            st.title("Talk to VAULT")

            # Prompt for user input
            if prompt := st.chat_input(placeholder="Ask questions about InhouseGPT"):
                self.handle_user_input(prompt)

            # Display chat messages from history on app rerun
            self.display_chat_history()

            # If last message is not from assistant, generate a new response
            if self.messages[-1]["role"] != "assistant":
                self.generate_assistant_response()
        except Exception as e:
            logging.error(f"Unexpected error showing VaultAI: {e}")
            
if __name__ == "__main__":
    vault_ai = VaultAI()
    vault_ai.show()