import streamlit as st
from pathlib import Path
from typing import List, Optional, Dict, Any

from sequencer.runner import SequenceRunner 
from pipeline.utils.configs import PipelineConfig
from pipeline.utils.logging import setup_logger

from utils.configs import replace_runner_settings

logger = setup_logger(__name__)

BLUEPRINT_DIR = Path(__file__).parent.parent / "blueprints"

class Sequences:
    """Sequence runner section with tabs."""
    
    def __init__(self, config: PipelineConfig) -> None:
        """Initialize Sequences with configuration."""
        self.config = config
        self.models = [
            # "claude-3-5-sonnet-20241022",  # Anthropic
            "gpt-4o-2024-08-06",  # OpenAI
        ]
        self.runner = SequenceRunner()
        replace_runner_settings(self.runner)
        logger.info(self.runner.settings)
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        logger.info("Sequences instance created")

    async def run_sequence_and_display(
        self,
        runner, 
        sequence_file: Path,
        models: List[str],
        placeholders: Optional[Dict[str, Any]] = None,
        spinner_text: str = "Generating content...",
        clear_session_flag: Optional[str] = None
    ) -> None:
        """
        Generic helper to:
        1) Call `runner.run_sequence(...)` with a set of placeholders.
        2) Display results incrementally in Streamlit.
        3) (Optionally) clear a session state flag afterwards.
        
        Args:
            runner: Your SequenceRunner or wrapper with a `run_sequence` method.
            sequence_file: Path to the .md file containing the sequence.
            models: List of models to run.
            placeholders: Dict of placeholders to inject into the sequence (e.g. {"description": user_input}).
            spinner_text: Text to display in the Streamlit spinner.
            clear_session_flag: If provided, e.g. "calendar_clicked", set it to False after finishing.
        """
        # If no placeholders, use an empty dict
        placeholders = placeholders or {}
        
        # Create a placeholder for results in the UI
        result_area = st.empty()

        with st.spinner(spinner_text):
            try:
                # Launch the async sequence generator
                coroutine = runner.run_sequence(
                    sequence_file=sequence_file,
                    models=models,
                    num_runs=1,
                    **placeholders  # Unpack your placeholders
                )
                completed_results = []

                # Stream results as they come in
                async for results in coroutine:
                    with result_area.container():
                        completed_results.extend(results)
                        [st.write(r.response) for r in completed_results]
                    logger.info(f"Received results batch")

            except Exception as e:
                logger.error(f"Error during sequence generation: {e}")
                st.error("An error occurred while generating content.")
            finally:
                # If the caller wants us to clear a session flag, do it
                if clear_session_flag:
                    st.session_state[clear_session_flag] = False

    async def show_adwords_tab(self) -> None:
        """Display AdWords campaign tab interface."""
        try:
            st.header('Generate AdWord campaign texts')
            
            def on_generate_clicked():
                st.session_state.generate_clicked = True
                st.session_state.user_input = user_input

            user_input = st.text_area(
                label='Enter description here:',
                height=70,
                placeholder="""Enter your campaign description.
You can write multiple paragraphs.
Include product details, target audience, campaign goals, etc."""
            )

            st.button('generate ad texts', on_click=on_generate_clicked)

            if 'generate_clicked' in st.session_state and st.session_state.generate_clicked:
                logger.info("Generate clicked, using stored input")
                st.header('Campaign description')
                st.write(st.session_state.user_input)
                
                sequence_file = BLUEPRINT_DIR / "adwordscampaign.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"description": st.session_state.user_input}

                # Call the helper
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    clear_session_flag="generate_clicked"
                )

        except Exception as e:
            logger.error(f"Error in AdWords tab: {e}")
            st.error("An error occurred in the AdWords tab")

    async def show_calendar_tab(self) -> None:
        """Display content calendar tab interface."""
        try:
            st.header('Generate content calendar')
            
            def on_calendar_clicked():
                st.session_state.calendar_clicked = True
                st.session_state.calendar_input = user_input

            user_input = st.text_area(
                label='Enter audience and target topics:',
                height=70,
                placeholder="""Describe your target audience and main content topics.
Include key themes, content goals, target platforms, tone of voice, etc."""
            )

            st.button('generate content plan', on_click=on_calendar_clicked)

            if 'calendar_clicked' in st.session_state and st.session_state.calendar_clicked:
                logger.info("Calendar clicked, using stored input")
                st.header('Content brief')
                st.write(st.session_state.calendar_input)
                
                sequence_file = BLUEPRINT_DIR / "contentcalendar.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"description": st.session_state.user_input}
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    spinner_text="Generating calendar plan...",
                    clear_session_flag="calendar_clicked"
                )

        except Exception as e:
            logger.error(f"Error in Calendar tab: {e}")
            st.error("An error occurred in the Calendar tab")

    async def show(self) -> None:
        """Display main Sequences interface with tabs."""
        try:
            st.title("run sequences")

            tab1, tab2 = st.tabs(["AdWords", "Calendar"])
            with tab1:
                await self.show_adwords_tab()  
            with tab2:
                await self.show_calendar_tab()

        except Exception as e:
            logger.error(f"Error in main interface: {e}")
            st.error("An error occurred. Please try again.")
