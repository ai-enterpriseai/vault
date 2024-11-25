import streamlit as st

from pipeline.prompts.manager import PromptManager
from pipeline.utils.model import LLMClient
from pipeline.utils.configs import PipelineConfig
from pipeline.utils.types import ChatMessage
from pipeline.utils.logging import setup_logger

from utils.retriever import ContextRetriever
from utils.configs import replace_api_keys

logger = setup_logger(__name__)

class Vault:
    """AI assistant for workshop guidance and knowledge exploration."""
    
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize VaultAI with configuration."""
        self.config = replace_api_keys(config)
        self.retriever = ContextRetriever(self.config)
        self.prompt_manager = PromptManager(self.config.manager)
        self.llm = LLMClient(self.config.generator)

        # Initialize chat history
        if "messages" not in st.session_state:
            system_prompt = self.prompt_manager.format_template(
                template=self.config.manager.prompt #"system_workshop_assistant_de"
            )
            st.session_state.messages = [{"role": "system", "content": system_prompt}]
        self.messages = st.session_state.messages
        logger.info("VAULT instance created")

    async def handle_user_input(self, prompt: str) -> None:
        """Process user input with context retrieval."""
        try:
            context = await self.retriever.get_context(prompt)
            self.messages.append({"role": "user", "content": prompt})
            self.messages.append({"role": "context", "content": context})  # TODO role user or content 
            logger.info(f"Processed user input: {prompt[:100]}...")
        except Exception as e:
            logger.error(f"Error handling user input: {e}")
            raise

    def display_chat_history(self) -> None:
        """Display chat history in Streamlit interface."""
        try:
            for message in self.messages:
                if message["role"] in ["system"]:
                    continue
                if message["role"] in ["context"]:
                    continue
                if message["content"].startswith("<context>"): 
                    continue
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        except Exception as e:
            logger.error(f"Error displaying chat history: {e}")
            raise

    async def generate_assistant_response(self) -> None:
        """Generate and stream AI assistant response."""
        try:
            with st.chat_message("assistant"):
                response = ""
                resp_container = st.empty()
                
                chat_messages = [
                    ChatMessage(role=m["role"], content=m["content"])
                    for m in self.messages
                ]

                try:
                    async for chunk in await self.llm.generate(
                        messages=chat_messages,
                        stream=True
                    ):
                        response += chunk
                        resp_container.markdown(response)

                    self.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    logger.info("Generated assistant response successfully")

                except Exception as e:
                    logger.error(f"Error in response generation: {e}")
                    resp_container.error("Failed to generate response")
                    raise

        except Exception as e:
            logger.error(f"Error in assistant response handling: {e}")
            raise

    async def show(self) -> None:
        """Display main Streamlit interface."""
        try:
            st.title("talk to alan")

            if prompt := st.chat_input(
                placeholder="ask alan about ai",
                key="alan_chat_input"  # Add unique key here
            ):
                await self.handle_user_input(prompt)

            self.display_chat_history()

            if self.messages and self.messages[-1]["role"] != "assistant":
                await self.generate_assistant_response()

        except Exception as e:
            logger.error(f"Error in main interface: {e}")
            st.error("An error occurred. Please try again.")
