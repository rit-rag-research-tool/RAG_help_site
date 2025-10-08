# RAG System Project

This project implements a Retrieval-Augmented Generation (RAG) system that integrates a Node.js backend with a Python module. The system utilizes OpenAI's GPT-5 API for generating responses based on retrieved data.

## Project Structure

```
rag-system-project
├── client
│   ├── public
│   │   ├──index.html
│   ├── src
# RAG_help_site — simplified

This repo has been simplified for development: the React client talks directly to the Python FastAPI backend. The Node/Express layer is archived (see `server/node/ARCHIVED.txt`).

Architecture now:

- `client/` — React frontend (Create React App). Dev server runs on http://localhost:3000 and proxies API calls to the Python backend.
- `server/python/` — FastAPI backend exposing `/rag` on http://127.0.0.1:8000.

Goals of simplification:

- Remove the Node proxy/middleware to reduce complexity.
- Avoid header/cookie issues by defaulting the client to not send cookies.
- Keep the Node code archived in case you want to restore it later.

Prerequisites

- Node.js and npm installed
- Python 3.10+ installed
- An OpenAI API key (set in `OPENAI_API_KEY`)

Quick start (two PowerShell terminals)

1) Start the Python backend (FastAPI)

Open a PowerShell terminal and run:

```powershell
cd C:\Users\Rae\Desktop\RAG_help_site\server\python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Either set the env var here or create server/python/.env with OPENAI_API_KEY
$env:OPENAI_API_KEY = "your_real_key_here"
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

2) Start the React client

Open a second PowerShell terminal and run:

```powershell
cd C:\Users\Rae\Desktop\RAG_help_site\client
npm install
npm start
```

Notes

- `client/package.json` proxies to `http://localhost:8000` so requests to `/rag` from the client reach the Python backend in development.
- The client fetch has been updated to omit credentials (no cookies) and to check `res.ok` before parsing JSON.
- The Node layer is left in `server/node/` but marked archived in `server/node/ARCHIVED.txt`.

Where to look to verify everything is up

- Browser: http://localhost:3000 — use the chat UI.
- Python terminal: Uvicorn logs; endpoint: http://127.0.0.1:8000/rag
- Browser DevTools Network tab: inspect POST /rag and the JSON response with `answer`.

Troubleshooting

- If `uvicorn` fails to start: confirm you activated the virtualenv and installed requirements.
- If OpenAI errors occur: ensure `OPENAI_API_KEY` is set.
- If the UI shows "Backend error" or similar: open DevTools → Network and inspect the response status and body.

If you want, I can fully remove the `server/node` folder instead of archiving it — say the word and I'll delete it.
