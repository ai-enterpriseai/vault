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
            
            def on_adwords_clicked():
                st.session_state.adwords_clicked = True
                st.session_state.adwords_input = user_input

            user_input = st.text_area(
                label='Enter description here:',
                height=70,
                placeholder="""Enter your campaign description.
You can write multiple paragraphs.
Include product details, target audience, campaign goals, etc."""
            )

            st.button('generate ad texts', on_click=on_adwords_clicked)

            if 'adwords_clicked' in st.session_state and st.session_state.adwords_clicked:
                logger.info("Generate clicked, using stored input")
                st.header('Results')
                
                sequence_file = BLUEPRINT_DIR / "adwordscampaign.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"description": st.session_state.adwords_input}
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    clear_session_flag="adwords_clicked"
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
                st.header('Results')
                
                sequence_file = BLUEPRINT_DIR / "contentcalendar.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"description": st.session_state.calendar_input}
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

    async def show_solver_tab(self) -> None:
        """Display problem solver tab interface."""
        try:
            st.header('Solve coding errors')
            
            def on_solver_clicked():
                if not user_input.strip():
                    st.error("Please enter a problem description")
                    return
                st.session_state.solver_clicked = True
                st.session_state.solver_input = user_input

            user_input = st.text_area(
                label='Paste your code:',
                height=70,
                placeholder="""Paste your code, error message, problem description here."""
            )

            st.button('solve problem', on_click=on_solver_clicked)

            if 'solver_clicked' in st.session_state and st.session_state.solver_clicked:
                logger.info("Solver clicked, using stored input")
                st.header('Results')
                
                sequence_file = BLUEPRINT_DIR / "solver.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"error": st.session_state.solver_input}
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    spinner_text="Analyzing and solving...",
                    clear_session_flag="solver_clicked"
                )
                st.success("Problem analysis completed successfully!")

        except Exception as e:
            logger.error(f"Error in Solver tab: {e}")
            st.error("An error occurred in the Solver tab")

    async def show_tester_tab(self) -> None:
        """Display test case generator tab interface."""
        try:
            st.header('Generate tests')
            
            def on_tester_clicked():
                if not user_input.strip():
                    st.error("Please paste your code")
                    return
                st.session_state.tester_clicked = True
                st.session_state.tester_input = user_input

            user_input = st.text_area(
                label='Paste your code:',
                height=70,
                placeholder="""Paste your code to write tests for."""
            )

            st.button('generate tests', on_click=on_tester_clicked)

            if 'tester_clicked' in st.session_state and st.session_state.tester_clicked:
                logger.info("Tester clicked, using stored input")
                st.header('Results')
                
                sequence_file = BLUEPRINT_DIR / "tester.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {"code": st.session_state.tester_input}
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    spinner_text="Generating test cases...",
                    clear_session_flag="tester_clicked"
                )
                st.success("Test cases generated successfully!")

        except Exception as e:
            logger.error(f"Error in Tester tab: {e}")
            st.error("An error occurred in the Tester tab")

    async def show_generator_tab(self) -> None:
        """Display code generator tab interface."""
        try:
            st.header('Generate code template')
            
            def on_generator_clicked():
                if not user_input1.strip():
                    st.error("Please enter requirements")
                    return
                if not user_input2.strip():
                    st.error("Please enter code examples")
                    return
                st.session_state.generator_clicked = True
                st.session_state.generator_requirements = user_input1
                st.session_state.generator_examples = user_input2

            user_input1 = st.text_area(
                label='Enter requirements:',
                height=70,
                placeholder="""Describe the code you want to generate.
Include programming language, framework preferences.
Specify functionality, inputs, outputs, and any special requirements."""
            )
            user_input2 = st.text_area(
                label='Paste code examples:',
                height=70,
                placeholder="""Paste your existing code as an example."""
            )

            st.button('generate code', on_click=on_generator_clicked)

            if 'generator_clicked' in st.session_state and st.session_state.generator_clicked:
                logger.info("Generator clicked, using stored input")
                st.header('Results')
                
                sequence_file = BLUEPRINT_DIR / "generator.md"
                logger.info(f"Using sequence file: {sequence_file}")
                
                placeholders = {
                    "requirements": st.session_state.generator_requirements,
                    "examples": st.session_state.generator_examples
                }
                await self.run_sequence_and_display(
                    runner=self.runner,
                    sequence_file=sequence_file,
                    models=self.models,
                    placeholders=placeholders,
                    spinner_text="Generating code template...",
                    clear_session_flag="generator_clicked"
                )
                st.success("Code template generated successfully!")

        except Exception as e:
            logger.error(f"Error in Generator tab: {e}")
            st.error("An error occurred in the Generator tab")

    async def show(self) -> None:
        """Display main Sequences interface with tabs."""
        try:
            st.title("run sequences")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Solver",
                "Tester",
                "Coder",
                "AdWords",
                "Calendar"
            ])
            
            with tab1:
                await self.show_solver_tab()
            with tab2:
                await self.show_tester_tab()
            with tab3:
                await self.show_generator_tab()
            with tab4:
                await self.show_adwords_tab()
            with tab5:
                await self.show_calendar_tab()

        except Exception as e:
            logger.error(f"Error in main interface: {e}")
            st.error("An error occurred. Please try again.")