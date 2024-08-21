# VAULT_APP

VAULT_APP is a Streamlit application that allows users to explore and interact with an AI assistant called VAULT.AI. The application provides a user-friendly interface for loading and indexing data from various sources, such as files, directories, and a predefined vault. Users can then engage in a conversational interface with VAULT.AI, which retrieves relevant context from the indexed data and generates responses based on the user's queries.

## Features

- Load and index data from files, directories, or a predefined vault
- Conversational interface with VAULT.AI for asking questions and receiving contextual responses
- Hybrid search combining sparse and dense vector representations for efficient context retrieval
- Reranking of retrieved context chunks based on relevance to the user's query
- Settings page for configuring API keys and uploading a custom logo

## Installation

1. Create a virtual environment:

`python -m venv vault`

2. Clone the repository:

`git clone https://github.com/ai-enterpriseai/vault.git`

3. Install the required dependencies:

`pip install -r requirements.txt`

4. Set up the required API keys and configurations in the `.streamlit/secrets-example.toml` file, and rename it to `secrets.toml`

## Usage

1. Run the Streamlit application:

2. Navigate through the different sections of the application using the sidebar:
   - **Vault**: Interact with VAULT.AI by asking questions and receiving contextual responses.
   - **Data**: Load and index data from various sources.
   - **Settings**: Configure API keys and upload a custom logo.

3. Explore the features and functionalities of VAULT.AI by following the on-screen instructions.

## Warning 

Some functionality won't run as this repo is a part of a larger package. Here it is used to serve a [demo Streamlit app](https://vaultai.streamlit.app/).