# README for Python RAG System

This directory contains the Python implementation of the Retrieval-Augmented Generation (RAG) system, which integrates with OpenAI's GPT-5 API. Below are the details for setting up and using the Python components of the project.

## Project Structure

- `rag/`: Contains the core functionality of the RAG system.
  - `__init__.py`: Marks the directory as a Python package.
  - `retriever.py`: Implements the retrieval logic for fetching data from specified sources.
  - `generator.py`: Implements the generation logic for interacting with OpenAI's GPT-5 API.

## Setup Instructions

1. **Install Python**: Ensure you have Python 3.7 or higher installed on your machine.

2. **Create a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   Navigate to the `backend/python` directory and run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Make sure to set up your environment variables as specified in the `.env` file located in the root of the project. This includes your OpenAI API key.

## Usage

To use the RAG system, you will typically interact with the Node.js backend, which will call the Python functions for data retrieval and response generation. Ensure that the Node.js server is running and properly configured to communicate with the Python backend.

## Additional Information

For more details on the individual components, refer to the respective files in the `rag` directory.