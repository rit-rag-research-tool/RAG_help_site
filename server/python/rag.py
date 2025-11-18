# rag.py
import os
import re
from typing import List, Dict, Tuple
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Central place to define allowed help domains ---
ALLOWED_HELP_DOMAINS = [
    # RIT (covers all subdomains)
    "rit.edu",

    # Slack help
    "slack.com",

    # Microsoft Office / Microsoft 365 help
    "support.microsoft.com",
    "learn.microsoft.com",
    "office.com",

    # Google help / Workspace
    "support.google.com",
    "workspace.google.com",
    "developers.google.com",

    # Adobe help
    "adobe.com",
    "helpx.adobe.com",
    "support.adobe.com",

    # General "help" sites (tweak to taste)
    "stackoverflow.com",
    "superuser.com",
    "serverfault.com",
]

# regex helpers
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
BARE_URL = re.compile(r"https?://\S+")
SOURCES_BLOCK = re.compile(r"(?is)\n+sources\s*:\s*(.+)$")  # everything after "Sources:"

def strip_inline_links(text: str) -> str:
    """Remove inline links from the answer body."""
    if not text:
        return text
    text = MD_LINK.sub(r"\1", text)  # [title](url) -> title
    text = BARE_URL.sub("", text)    # remove bare URLs
    return " ".join(text.split())

def parse_sources_block(ans: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Extract a 'Sources:' section from the end of ans, return (body_without_sources, citations[]).
    Expected bullet format (flexible):
      - Title — https://example.com
      - https://example.com
    """
    citations: List[Dict[str, str]] = []
    body = ans

    m = SOURCES_BLOCK.search(ans)
    if not m:
        return body, citations

    block = m.group(1).strip()
    # Split to lines, ignore empty
    lines = [l.strip(" -*•\t") for l in block.splitlines() if l.strip()]
    for line in lines:
        # find first URL in the line
        url_match = BARE_URL.search(line)
        if not url_match:
            continue
        url = url_match.group(0)
        # title is the line with url removed + separators trimmed
        title = line.replace(url, "").strip(" -—:()") or url
        citations.append({"title": title, "url": url})

    # Remove the sources block from the main answer
    body = ans[:m.start()].rstrip()
    return body, citations

def retrieve_docs(query: str):
    # Keep your own retrieval here (stubbed)
    return ["Document 1", "Document 2"]

def generate_answer(query: str):
    docs = retrieve_docs(query)
    context = "\n".join(docs)

    # Updated system message to explain domain restrictions and formatting
    system_msg = (
        "You are a helpful assistant with web_search access.\n"
        "When the answer involves public or recent facts, USE web_search.\n"
        "Your web_search tool is restricted to:\n"
        "• Rochester Institute of Technology sites (rit.edu)\n"
        "• Slack help\n"
        "• Microsoft / Office help\n"
        "• Google help / Workspace docs\n"
        "• Adobe help\n"
        "• A few general technical help sites (e.g., Stack Overflow)\n"
        "Prefer RIT pages when answering RIT-specific questions.\n\n"
        "FORMATTING GUIDELINES:\n"
        "• Use **bold** for emphasis and key terms\n"
        "• Use bullet points (- or •) for lists\n"
        "• Use numbered lists (1., 2., 3.) for steps or sequences\n"
        "• Break content into paragraphs (use double line breaks)\n"
        "• Use clear section headers when appropriate\n"
        "• Keep paragraphs concise (2-4 sentences max)\n"
        "• Do NOT put inline links in the body\n\n"
        "After the answer, add a section exactly titled 'Sources:' and list up to 6 items,\n"
        "one per line, in the format 'Title — URL'. Prefer authoritative sites.\n"
        "If you searched, include at least one source."
    )

    user_msg = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.responses.create(
        model="gpt-5",
        tools=[
            {
                "type": "web_search",
                "filters": {
                    # Only search these domains (and their subdomains)
                    "allowed_domains": ALLOWED_HELP_DOMAINS,
                },
            }
        ],
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        # temperature=0.2,
        # reasoning={"effort": "medium"},
        # Optional: if you want the full list of sources as a fallback:
        # include=["web_search_call.action.sources"],
    )

    # Raw text the model returned (may contain 'Sources:' section)
    raw_text = (getattr(response, "output_text", "") or "").strip()

    # Parse Sources block -> citations[], and remove it from body
    body, citations = parse_sources_block(raw_text)

    # Fallback: if no sources block, attempt to collect tool annotations (when present)
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

    # Finally, ensure no inline links remain in the body
    body = strip_inline_links(body)

    return {"text": body, "citations": citations[:6]}


# --- Title generation helpers ---

def _serialize_transcript(messages, limit_chars=2000, max_msgs=12) -> str:
    """
    Turn your UI messages into a compact transcript string.
    Keeps the last few turns and trims to ~limit_chars for cheap, fast titles.
    """
    role_map = {"User": "User", "RAG": "Assistant", "System": "System"}
    lines = []
    tail = messages[-max_msgs:] if messages else []
    for m in tail:
        r = role_map.get(m.get("role"), m.get("role", "User"))
        t = (m.get("text") or "").strip()
        if not t:
            continue
        # single-line for compactness
        t = " ".join(t.split())
        lines.append(f"{r}: {t}")
    s = "\n".join(lines)
    if len(s) > limit_chars:
        s = s[-limit_chars:]
    return s

def _postprocess_title(s: str) -> str:
    """Keep it safe and pretty: no quotes/emojis/trailing punctuation; cap length."""
    if not s:
        return "New chat"
    s = s.strip().strip('"').strip("'")
    # drop trailing punctuation and emojis
    s = s.rstrip(".!?:—- ")
    # hard cap
    if len(s) > 60:
        s = s[:57].rstrip() + "…"
    return s or "New chat"

def generate_title(messages):
    """
    Ask GPT for a concise, human-readable chat title (3–7 words).
    No schema—plain text for maximum compatibility.
    """
    transcript = _serialize_transcript(messages)

    # If we somehow have nothing yet, fall back immediately
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
            {
                "role": "user",
                "content": f"Conversation transcript:\n{transcript}\n\nTitle:",
            },
        ],
        temperature=0.2,
        # No tools, no JSON schema (to avoid 500s on picky SDKs)
    )

    raw = (getattr(response, "output_text", "") or "").strip()
    return _postprocess_title(raw)
