# RAG Help Site

A Retrieval-Augmented Generation (RAG) chat application that combines web search with AI-powered responses. Built with React frontend and Python FastAPI backend, featuring real-time citations, conversation management, and favorites.

## Features

-  **RAG-powered responses** with web search and citations
-  **Conversation management** with auto-generated titles
-  **Favorites system** to organize important conversations
-  **Smart follow-up suggestions** based on conversation context
-  **Source citations** displayed in sidebar
-  **Local storage** for conversation persistence

## Project Structure

```
RAG_help_site/
├── client/                  # React frontend (Create React App)
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/
│   │   ├── App.js          # Main app component with conversation logic
│   │   ├── ChatBox.js      # Chat interface with placeholder questions
│   │   ├── Sidebar.js      # Sources & conversations with favorites tabs
│   │   ├── App.css
│   │   ├── index.css
│   │   └── index.js
│   └── package.json        # Proxies to http://localhost:8000
│
├── server/
│   ├── python/             # FastAPI backend (active)
│   │   ├── main.py         # FastAPI app with /rag and /title endpoints
│   │   ├── rag.py          # RAG logic and web search
│   │   ├── utils.py        # Utility functions
│   │   └── requirements.txt
│   │
│   └── node/               # Node.js layer (archived)
│       └── ARCHIVED.txt
│
├── run-dev.ps1             # PowerShell script to run both servers
└── README.md
```

## Prerequisites

- **Node.js** (v14+) and npm
- **Python** 3.10+
- **OpenAI API key** (required for GPT responses)

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the provided PowerShell script from the project root:

```powershell
.\run-dev.ps1
```

This will:
1. Set up Python virtual environment (first run only)
2. Install Python dependencies (first run only)
3. Start the FastAPI backend on `http://127.0.0.1:8000`
4. Install npm packages (first run only)
5. Start the React dev server on `http://localhost:3000`

**Note:** Update the `OPENAI_API_KEY` in `run-dev.ps1` with your actual API key before running.

For subsequent runs (skip installations):
```powershell
.\run-dev.ps1 -NoInstall
```

### Option 2: Manual Setup

#### 1. Start the Python Backend

Open a PowerShell terminal:

```powershell
cd server\python

# Create virtual environment (first time only)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Set your OpenAI API key
$env:OPENAI_API_KEY = "your_openai_api_key_here"

# Start the server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at `http://127.0.0.1:8000`

#### 2. Start the React Frontend

Open a second PowerShell terminal:

```powershell
cd client

# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

The app will automatically open at `http://localhost:3000`

## Architecture

### Frontend (React)
- **App.js**: Manages conversations, favorites, and GPT-powered title generation
- **ChatBox.js**: Handles message display and user input with smart follow-up suggestions
- **Sidebar.js**: Shows citations and conversations with "All" and "Favorites" tabs
- **Local Storage**: Conversations persist in `localStorage` as `conversations_v1`

### Backend (FastAPI/Python)
- **POST /rag**: Accepts `{ query: string }`, performs web search, generates AI response with citations
- **POST /title**: Accepts `{ messages: array }`, generates conversation title using GPT
- Uses OpenAI API for response generation
- Integrates web search for up-to-date information

### Communication
- Frontend proxies API requests to `http://localhost:8000` via `package.json` proxy setting
- CORS configured on backend for development
- Requests sent without credentials to avoid cookie issues

## Usage

1. **Start a conversation**: Type your question in the chat box
2. **View sources**: Citations appear in the right sidebar
3. **Favorite conversations**: Click the star icon next to any conversation
4. **Browse conversations**: Switch between "All" and "Favorites" tabs
5. **Quick follow-ups**: Click suggested follow-up questions when returning to a conversation
6. **New chat**: Click "New Chat" button to start fresh

## Environment Variables

Create a `.env` file in `server/python/` (optional, alternative to setting env vars):

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Troubleshooting

### Backend won't start
- Ensure Python virtual environment is activated
- Verify `requirements.txt` dependencies are installed
- Check that port 8000 is not already in use

### OpenAI errors
- Verify `OPENAI_API_KEY` is set correctly
- Ensure you have API credits available
- Check OpenAI service status

### Frontend shows "Backend error"
- Verify backend is running on port 8000
- Open DevTools → Network tab to inspect failed requests
- Check backend terminal for error logs

### Conversations not saving
- Check browser console for localStorage errors
- Ensure localStorage is enabled in your browser
- Try clearing `conversations_v1` from localStorage and refresh

## Development Notes

- The Node.js layer has been archived (see `server/node/ARCHIVED.txt`)
- React dev server hot-reloads on file changes
- FastAPI uses `--reload` flag for auto-restart on code changes
- Conversations are stored in browser localStorage only (no database)

## License

MIT
