from fastapi import FastAPI, Request
from rag import generate_answer

app = FastAPI()

@app.post("/rag")
async def rag_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    answer = generate_answer(query)
    return {"answer": answer}

#uvicorn main:app --reload - to start the server