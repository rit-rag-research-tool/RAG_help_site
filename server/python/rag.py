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
    Works with both plain text and HTML formatted responses.
    Expected bullet format (flexible):
      - Title — https://example.com
      - https://example.com
      Or HTML: <li>Title — https://example.com</li>
    """
    citations: List[Dict[str, str]] = []
    body = ans

    m = SOURCES_BLOCK.search(ans)
    if not m:
        return body, citations

    block = m.group(1).strip()
    
    # Remove HTML tags for parsing (like <ul>, <li>, <p>, etc.)
    import html
    block_clean = re.sub(r'<[^>]+>', '\n', block)  # Replace tags with newlines
    block_clean = html.unescape(block_clean)  # Decode HTML entities
    
    # Split to lines, ignore empty
    lines = [l.strip(" -*•\t") for l in block_clean.splitlines() if l.strip()]
    for line in lines:
        # find first URL in the line
        url_match = BARE_URL.search(line)
        if not url_match:
            continue
        url = url_match.group(0)
        # title is the line with url removed + separators trimmed
        title = line.replace(url, "").strip(" -—:()") or url
        # Clean up any remaining HTML entities or tags from title
        title = re.sub(r'<[^>]+>', '', title).strip()
        citations.append({"title": title, "url": url})

    # Remove the sources block from the main answer
    body = ans[:m.start()].rstrip()
    return body, citations

def retrieve_docs(query: str):
    """
    Retrieve relevant documents from Dropbox for the given query.
    Falls back to stub documents if Dropbox is not configured.
    """
    try:
        from dropbox_rag import get_dropbox_rag
        dropbox_rag = get_dropbox_rag()
        return dropbox_rag.search_documents(query, max_results=5)
    except Exception as e:
        print(f"⚠️  Error retrieving from Dropbox: {e}")
        print("   Falling back to stub documents")
        return ["Document 1: Placeholder content", "Document 2: Placeholder content"]

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
        "FORMATTING GUIDELINES - Use HTML for maximum readability:\n\n"
        "1. **Structure Your Response:**\n"
        "   - Start with a brief overview (1-2 sentences in a <p> tag)\n"
        "   - Break complex answers into clear sections with headings\n"
        "   - Use <br> or separate <p> tags for spacing between sections\n\n"
        "2. **Headings:** Use <h2> for main sections and <h3> for subsections\n"
        "   Example:\n"
        "   <h2>How to Connect</h2>\n"
        "   <h3>On iOS Devices</h3>\n\n"
        "3. **Emphasis:**\n"
        "   - Use <strong> or <b> for important terms, names, and key concepts\n"
        "   - Use <em> or <i> for secondary emphasis or definitions\n\n"
        "4. **Lists:**\n"
        "   - Use <ul> and <li> for unordered items or options\n"
        "   - Use <ol> and <li> for sequential steps or instructions\n"
        "   - Keep list items concise (1-2 sentences max)\n"
        "   Example:\n"
        "   <ol>\n"
        "     <li>First step here</li>\n"
        "     <li>Second step here</li>\n"
        "   </ol>\n\n"
        "5. **Paragraphs:**\n"
        "   - Wrap each paragraph in <p> tags\n"
        "   - Keep paragraphs short (2-4 sentences)\n"
        "   - Start new paragraphs for new ideas\n\n"
        "6. **Special Elements:**\n"
        "   - Use <blockquote> for important notes or warnings\n"
        "   - Use <code> for technical terms, commands, or file names\n"
        "   - Use <hr> to separate major sections if needed\n\n"
        "7. **Readability:**\n"
        "   - Write in a friendly, conversational tone\n"
        "   - Use short sentences when possible\n"
        "   - Avoid jargon unless necessary (then explain it)\n"
        "   - Use examples when helpful\n\n"
        "8. **NO inline links in the body** - citations go in the Sources section\n\n"
        "9. **Important:** Always return valid, well-formed HTML. Close all tags properly.\n\n"
        "CRITICAL - SOURCES SECTION:\n"
        "After your HTML formatted answer, you MUST add a plain text section titled 'Sources:'\n"
        "This section should be OUTSIDE of any HTML tags - just plain text.\n"
        "Format:\n"
        "Sources:\n"
        "Title — URL\n"
        "Another Title — URL\n\n"
        "Example:\n"
        "<p>Your HTML answer here...</p>\n\n"
        "Sources:\n"
        "RIT Wi-Fi Setup — https://help.rit.edu/sp?id=kb_article_view&sysparm_article=KB0040936\n"
        "Network Guide — https://rit.edu/its/networking\n\n"
        "List at least 1 source. Prefer authoritative sites. If you used web_search, include those sources."
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
