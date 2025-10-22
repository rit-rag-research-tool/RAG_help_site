# rag.py
import os
import re
import math
from typing import List, Dict, Tuple
from openai import OpenAI
from dropbox_loader import load_corpus_from_dropbox

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- regex helpers (unchanged) ---
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
BARE_URL = re.compile(r"https?://\S+")
SOURCES_BLOCK = re.compile(r"(?is)\n+sources\s*:\s*(.+)$")

def strip_inline_links(text: str) -> str:
    if not text:
        return text
    text = MD_LINK.sub(r"\1", text)
    text = BARE_URL.sub("", text)
    return " ".join(text.split())

def parse_sources_block(ans: str) -> Tuple[str, List[Dict[str, str]]]:
    citations: List[Dict[str, str]] = []
    body = ans
    m = SOURCES_BLOCK.search(ans)
    if not m:
        return body, citations
    block = m.group(1).strip()
    lines = [l.strip(" -*•\t") for l in block.splitlines() if l.strip()]
    for line in lines:
        url_match = BARE_URL.search(line)
        if not url_match:
            continue
        url = url_match.group(0)
        title = line.replace(url, "").strip(" -—:()") or url
        citations.append({"title": title, "url": url})
    body = ans[:m.start()].rstrip()
    return body, citations

# --- Simple in-memory index ---
_CORPUS: List[Dict[str, str]] = []
_CHUNKS: List[Dict[str, str]] = []  # {"chunk_id","doc_id","title","path","text"}
_EMBS: List[List[float]] = []
_READY: bool = False

def _chunk(text: str, title: str, path: str, doc_id: str, max_len: int = 1200, overlap: int = 150):
    """Very simple character-based chunking."""
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + max_len)
        piece = text[i:j]
        if piece.strip():
            chunks.append({
                "chunk_id": f"{doc_id}:{i}",
                "doc_id": doc_id,
                "title": title,
                "path": path,
                "text": piece.strip()
            })
        i = j - overlap
        if i <= 0:
            i = j
    return chunks

def _cos(a: List[float], b: List[float]) -> float:
    num = 0.0
    da = 0.0
    db = 0.0
    for x, y in zip(a, b):
        num += x * y
        da += x * x
        db += y * y
    if da == 0 or db == 0:
        return 0.0
    return num / math.sqrt(da * db)

def _embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    res = client.embeddings.create(
        model="text-embedding-3-large",
        input=texts
    )
    return [d.embedding for d in res.data]

def _ensure_index():
    global _READY, _CORPUS, _CHUNKS, _EMBS
    if _READY:
        return
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    root = os.getenv("DROPBOX_ROOT", "/")
    max_bytes = int(os.getenv("DOC_MAX_BYTES", "4000000"))

    if not token:
        # No Dropbox configured; keep a trivial corpus (optional)
        _CORPUS = []
        _CHUNKS = []
        _EMBS = []
        _READY = True
        return

    # 1) Load corpus from Dropbox
    _CORPUS = load_corpus_from_dropbox(token, root, max_bytes=max_bytes)

    # 2) Chunk
    all_chunks: List[Dict[str, str]] = []
    for d in _CORPUS:
        all_chunks.extend(_chunk(d["text"], d["title"], d["path"], d["id"]))
    _CHUNKS = all_chunks

    # 3) Embed chunks
    _EMBS = _embed_texts([c["text"] for c in _CHUNKS])

    _READY = True

def retrieve_docs(query: str, k: int = 8) -> List[Dict[str, str]]:
    """
    Returns top-k chunks: [{"title","path","text"}].
    Falls back to empty list if no Dropbox configured or no chunks.
    """
    _ensure_index()
    if not _CHUNKS or not _EMBS:
        return []

    q_emb = _embed_texts([query])[0]
    scored = []
    for emb, ch in zip(_EMBS, _CHUNKS):
        scored.append(( _cos(q_emb, emb), ch ))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [t[1] for t in scored[:k]]

def _format_context(chunks: List[Dict[str, str]]) -> str:
    """
    Lightly format chunks with titles so the model can cite intelligently.
    """
    lines = []
    for i, ch in enumerate(chunks, 1):
        lines.append(f"[{i}] Title: {ch['title']} | Path: {ch['path']}\n{ch['text']}\n")
    return "\n---\n".join(lines)

def generate_answer(query: str):
    chunks = retrieve_docs(query, k=8)
    context = _format_context(chunks) if chunks else "No local corpus available."

    system_msg = (
        "You are a helpful assistant with web_search access. "
        "When the answer involves public or recent facts, USE web_search. "
        "Do NOT put inline links in the body. "
        "After the answer, add a section exactly titled 'Sources:' and list up to 6 items, "
        "one per line, in the format 'Title — URL'. Prefer authoritative sites. "
        "If you searched, include at least one source. "
        "If local context is provided, prefer citing those sources by their titles if relevant."
    )

    user_msg = f"Local Context Chunks (for reference):\n{context}\n\nQuestion: {query}"

    response = client.responses.create(
        model="gpt-5",
        tools=[{"type": "web_search"}],
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    raw_text = (getattr(response, "output_text", "") or "").strip()
    body, citations = parse_sources_block(raw_text)

    if not citations:
        try:
            for block in response.output:
                if getattr(block, "type", "") == "message":
                    for part in getattr(block, "content", []):
                        for ann in getattr(part, "annotations", []) or []:
                            if ann.get("type") == "url_citation" and ann.get("url"):
                                citations.append({"title": ann.get("title"), "url": ann.get("url")})
        except Exception:
            pass

    body = strip_inline_links(body)

    return {"text": body, "citations": citations[:6]}

# ----- Title generation (unchanged) -----

def _serialize_transcript(messages, limit_chars=2000, max_msgs=12) -> str:
    role_map = {"User": "User", "RAG": "Assistant", "System": "System"}
    lines = []
    tail = messages[-max_msgs:] if messages else []
    for m in tail:
        r = role_map.get(m.get("role"), m.get("role", "User"))
        t = (m.get("text") or "").strip()
        if not t:
            continue
        t = " ".join(t.split())
        lines.append(f"{r}: {t}")
    s = "\n".join(lines)
    if len(s) > limit_chars:
        s = s[-limit_chars:]
    return s

def _postprocess_title(s: str) -> str:
    if not s:
        return "New chat"
    s = s.strip().strip('"').strip("'")
    s = s.rstrip(".!?:—- ")
    if len(s) > 60:
        s = s[:57].rstrip() + "…"
    return s or "New chat"

def generate_title(messages):
    transcript = _serialize_transcript(messages)
    if not transcript:
        return "New chat"

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": (
                    "You generate short sidebar titles for chat conversations.\n"
                    "Rules:\n"
                    "• 3–7 words\n"
                    "• Title Case\n"
                    "• No quotes, no emojis\n"
                    "• No trailing punctuation\n"
                    "• Be specific (use key nouns), avoid dates unless central\n"
                    "Return ONLY the title text."
                ),
            },
            {"role": "user", "content": f"Conversation transcript:\n{transcript}\n\nTitle:"},
        ],
        temperature=0.2,
    )
    raw = (getattr(response, "output_text", "") or "").strip()
    return _postprocess_title(raw)
