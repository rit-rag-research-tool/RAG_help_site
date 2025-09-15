# RAG System Node.js Backend

This README provides information about the Node.js backend of the Retrieval-Augmented Generation (RAG) system.

## Project Structure

The Node.js backend is organized as follows:

```
backend/node
├── src
│   ├── app.js          # Entry point of the application
│   ├── routes          # Contains route definitions
│   │   └── rag.js      # Routes for the RAG system
│   └── utils           # Utility functions
│       └── openai.js   # Functions for interacting with OpenAI's GPT-5 API
├── package.json        # NPM configuration file
└── README.md           # This file
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd rag-system-project/backend/node
   ```

2. **Install dependencies**:
   Ensure you have Node.js installed. Then run:
   ```
   npm install
   ```

3. **Environment Variables**:
   Create a `.env` file in the `backend/node` directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY='your_openai_api_key'
   ```

4. **Run the application**:
   Start the server with:
   ```
   node src/app.js
   ```

## Usage

The Node.js backend serves as an API for the RAG system. It handles incoming requests related to data retrieval and response generation. The main functionalities include:

- **Retrieval**: Fetching relevant data based on user queries.
- **Generation**: Using OpenAI's GPT-5 API to generate responses based on the retrieved data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.