# RAG System Project

This project implements a Retrieval-Augmented Generation (RAG) system that integrates a Node.js backend with a Python module. The system utilizes OpenAI's GPT-5 API for generating responses based on retrieved data.

## Project Structure

```
rag-system-project
├── backend
│   ├── node
│   │   ├── src
│   │   │   ├── app.js          # Entry point for the Node.js application
│   │   │   ├── routes
│   │   │   │   └── rag.js      # Routes for the RAG system
│   │   │   └── utils
│   │   │       └── openai.js   # Utility functions for OpenAI API interaction
│   │   ├── package.json        # npm configuration file
│   └── python
│       ├── rag
│       │   ├── __init__.py     # Marks the directory as a Python package
│       │   ├── retriever.py     # Implements retrieval logic
│       │   └── generator.py      # Implements generation logic using OpenAI API
│       ├── requirements.txt     # Python dependencies
│       └── README.md            # Documentation for the Python part
├── .env                         # Environment variables (e.g., OpenAI API key)
└── README.md                    # Overview of the entire project
```

## Setup Instructions

### Node.js Backend

1. Navigate to the `backend/node` directory.
2. Install dependencies:
   ```
   npm install
   ```
3. Start the server:
   ```
   node src/app.js
   ```

### Python Module

1. Navigate to the `backend/python` directory.
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

- The Node.js backend serves as the API layer, handling incoming requests and interacting with the Python module for data retrieval and response generation.
- The Python module contains the logic for retrieving data and generating responses using OpenAI's GPT-5 API.

## Architecture

The architecture of the RAG system consists of a Node.js server that communicates with a Python backend. The Node.js application handles API requests, while the Python module manages data retrieval and response generation, leveraging the capabilities of OpenAI's GPT-5 API.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.


## OPen Ai API
https://platform.openai.com/docs/guides/tools-web-search?api-mode=responses
