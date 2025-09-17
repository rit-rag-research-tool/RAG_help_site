import os
from openai import OpenAI

# create client (reads OPENAI_API_KEY from env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve_docs(query):
    # Dummy retrieval — replace with real retrieval later
    return ["Document 1", "Document 2"]

def generate_answer(query):
    docs = retrieve_docs(query)
    context = "\n".join(docs)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the context to answer the user's question."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )

    # return the assistant content
    return resp.choices[0].message.content.strip()