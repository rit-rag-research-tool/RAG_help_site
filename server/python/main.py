from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from rag import generate_answer, generate_title
import traceback

# Auto-load environment variables from server/python/.env if present
load_dotenv()

app = FastAPI()


@app.post("/rag")
async def rag_endpoint(request: Request):
    try: 
        data = await request.json()
        query = data.get("query", "")
        result = generate_answer(query)
        return {"answer": result["text"], "citations": result.get("citations", [])}
    except Exception as e:
        # Print full traceback to your server console to diagnose quickly
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "detail": str(e)},
        )

@app.post("/title")
async def title_endpoint(request: Request):
    try:
        data = await request.json()
        # Expect: {"messages": [{role:'User'|'RAG'|'System', text:'...'}, ...]}
        msgs = data.get("messages", []) or []
        title = generate_title(msgs)
        return {"title": title}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "internal_error", "detail": str(e)})

# Start with:
# uvicorn main:app --host 127.0.0.1 --port 8000 --reload