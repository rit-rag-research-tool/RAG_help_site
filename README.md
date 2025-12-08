# RAG Help Site

A Retrieval-Augmented Generation (RAG) chat application that combines web search and Dropbox document retrieval with AI-powered responses. Built with React frontend and Python FastAPI backend, featuring real-time citations, conversation management, favorites, and domain-filtered web search.

## Features

-  **RAG-powered responses** with web search and Dropbox document retrieval
-  **Domain-filtered web search** restricted to trusted sources (RIT, Microsoft, Google, Slack, Adobe, Stack Overflow)
-  **Dropbox integration** for custom knowledge base documents
-  **Auto-generated conversation titles** using GPT-5
-  **Favorites system** with tabs to organize important conversations
-  **Smart follow-up suggestions** based on conversation context
-  **Source citations** displayed in sidebar with active tabs
-  **HTML-formatted responses** for better readability
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
│   │   ├── rag.py          # RAG logic, web search, and title generation
│   │   ├── dropbox_rag.py  # Dropbox document retrieval and search
│   │   ├── utils.py        # Utility functions
│   │   ├── .env            # Environment variables (API keys)
│   │   ├── requirements.txt
│   │   └── test_dropbox.py # Test script for Dropbox connection
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
- **OpenAI API key** (required for GPT-5 responses)
- **Dropbox access token** (optional, for custom document retrieval)

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

**Note:** Configure your API keys in `server/python/.env` before running (see Environment Variables section).

For subsequent runs (skip installations):
```powershell
.\run-dev.ps1 -NoInstall
```

**To restart servers after code changes:**
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

# Create .env file with your API keys (see Environment Variables section)
# Or set environment variables manually:
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

### Frontend (React 19.1.1)
- **App.js**: Manages conversations, favorites, and GPT-5-powered title generation
- **ChatBox.js**: Handles message display with HTML rendering and smart follow-up suggestions
- **Sidebar.js**: Shows citations and conversations with "All" and "Favorites" tabs
- **Local Storage**: Conversations persist in `localStorage` as `conversations_v1`
- **HTML Rendering**: Uses `dangerouslySetInnerHTML` for formatted responses

### Backend (FastAPI/Python)
- **POST /rag**: Accepts `{ query: string }`, retrieves Dropbox documents, performs domain-filtered web search, generates AI response with HTML formatting and citations
- **POST /title**: Accepts `{ messages: array }`, generates conversation title using GPT-5 (strips HTML for clean titles)
- **Domain Filtering**: Web search restricted to approved domains (RIT, Microsoft, Google, Slack, Adobe, Stack Overflow)
- **Dropbox Integration**: Loads and searches documents from `/RAG_Sources` folder
- **GPT-5 API**: Uses OpenAI's latest model for response generation
- **HTML Formatting**: Returns responses with proper HTML structure for better readability

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

Create a `.env` file in `server/python/` with the following variables:

```env
# Required: OpenAI API key for GPT-5
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Dropbox integration (if not provided, uses stub documents)
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token_here
DROPBOX_FOLDER_PATH=/RAG_Sources
```

**Note:** Do not use quotes around the values in the `.env` file.

### Getting a Dropbox Access Token

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Create a new app with "Full Dropbox" access
3. Generate an access token in the app settings
4. Add the token to your `.env` file
5. Create a `/RAG_Sources` folder in your Dropbox and add documents (supports .txt, .md, .html, .json, .csv)

### Supported Document Types

The Dropbox integration supports the following file types:
- Plain text (`.txt`)
- Markdown (`.md`)
- HTML (`.html`)
- JSON (`.json`)
- CSV (`.csv`)

## Testing Dropbox Integration

Test your Dropbox connection with the provided test script:

```powershell
cd server\python
.\.venv\Scripts\Activate.ps1
python test_dropbox.py
```

This will display:
- Number of documents loaded
- Total size of documents
- Sample search results

## Troubleshooting

### Backend won't start
- Ensure Python virtual environment is activated
- Verify `requirements.txt` dependencies are installed: `pip install -r requirements.txt`
- Check that port 8000 is not already in use: `netstat -ano | findstr ":8000"`
- Verify `.env` file exists in `server/python/` with valid `OPENAI_API_KEY`

### OpenAI errors
- Verify `OPENAI_API_KEY` is set correctly in `.env` (no quotes)
- Ensure you have API credits available
- Check OpenAI service status
- For "temperature not supported" errors: Ensure you're using the latest code (GPT-5 doesn't support temperature)

### Dropbox errors
- "expired_access_token": Generate a new access token in Dropbox App Console
- "AuthError": Verify `DROPBOX_ACCESS_TOKEN` in `.env` is correct (no quotes)
- If Dropbox fails to initialize, the app will fall back to stub documents and continue working
- Run `python test_dropbox.py` to verify your Dropbox setup

### Title not generating
- Check browser console (F12) for title generation logs
- Verify backend shows " Generated title:" in terminal
- Titles generate automatically after the first response in a new conversation
- If backend shows 500 error, check for API parameter errors in terminal

### Frontend shows "Backend error"
- Verify backend is running on port 8000
- Open DevTools → Network tab to inspect failed requests
- Check backend terminal for error logs
- Ensure `proxy` in `client/package.json` points to `http://localhost:8000`

### Conversations not saving
- Check browser console for localStorage errors
- Ensure localStorage is enabled in your browser
- Try clearing `conversations_v1` from localStorage and refresh
- Open DevTools → Application → Local Storage to inspect stored data

### Sources not appearing in sidebar
- Check that web search returns valid URLs
- Verify domain filtering is not blocking all results
- Sources appear in the "Sources" tab on the right sidebar
- Click the "Sources" tab to view citations

## Development Notes

### Technology Stack
- **Frontend**: React 19.1.1 with Create React App
- **Backend**: FastAPI with uvicorn
- **AI Model**: OpenAI GPT-5 via Responses API
- **Document Storage**: Dropbox SDK 12.0.2
- **Styling**: Custom CSS with CSS variables for theming

### Key Implementation Details
- The Node.js layer has been archived (see `server/node/ARCHIVED.txt`)
- React dev server hot-reloads on file changes
- FastAPI uses `--reload` flag for auto-restart on code changes
- Conversations are stored in browser localStorage only (no database)
- HTML responses use `dangerouslySetInnerHTML` for rendering
- Title generation strips HTML tags to ensure clean titles
- Domain filtering prevents web searches from untrusted sources
- Dropbox documents are chunked for better retrieval relevance

### Domain Filtering
Web searches are restricted to these approved domains:
- `rit.edu` (Rochester Institute of Technology)
- `microsoft.com` and `visualstudio.com`
- `google.com` and `github.com`
- `slack.com`
- `adobe.com`
- `stackoverflow.com`

To modify the allowed domains, edit `ALLOWED_HELP_DOMAINS` in `server/python/rag.py`.

### Response Formatting
- Responses are formatted with HTML for better readability
- Supports paragraphs, lists, bold text, headings, and links
- Source citations are automatically extracted and displayed in sidebar
- CSS inherits text color to maintain theme consistency

## Future Enhancements

Potential improvements for the project:
-  Refresh button for Dropbox documents
-  Vector embeddings for semantic document search
-  Export/import conversations
-  User authentication and cloud storage
-  Analytics dashboard for conversation insights
-  Additional document sources (Google Drive, OneDrive)
-  Customizable domain filters per conversation
-  Conversation sharing with unique URLs


