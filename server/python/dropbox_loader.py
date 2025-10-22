# dropbox_loader.py
import io
import os
import re
from typing import Iterator, List, Dict, Optional, Tuple
import dropbox
from dropbox.files import FileMetadata, FolderMetadata
from bs4 import BeautifulSoup

# Optional readers
from pypdf import PdfReader
from docx import Document

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}

def _ext(path: str) -> str:
    return os.path.splitext(path.lower())[1]

def _is_supported(path: str) -> bool:
    return _ext(path) in SUPPORTED_EXTS

def _read_pdf(stream: io.BytesIO) -> str:
    reader = PdfReader(stream)
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(parts).strip()

def _read_docx(stream: io.BytesIO) -> str:
    doc = Document(stream)
    return "\n".join(p.text for p in doc.paragraphs).strip()

def _read_html(stream: io.BytesIO) -> str:
    html = stream.read().decode(errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    # Remove script/style
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    # collapse whitespace
    return re.sub(r"\s+", " ", text).strip()

def _read_plain(stream: io.BytesIO) -> str:
    return stream.read().decode(errors="ignore")

def _read_any(path: str, stream: io.BytesIO) -> str:
    e = _ext(path)
    if e == ".pdf":
        return _read_pdf(stream)
    if e == ".docx":
        return _read_docx(stream)
    if e in (".html", ".htm"):
        return _read_html(stream)
    return _read_plain(stream)  # .txt, .md, fallback

def walk_files(dbx: dropbox.Dropbox, root: str) -> Iterator[FileMetadata]:
    """Yield FileMetadata for supported files under a Dropbox path."""
    queue = [root]
    while queue:
        path = queue.pop()
        res = dbx.files_list_folder(path, recursive=False)
        for entry in res.entries:
            if isinstance(entry, FolderMetadata):
                queue.append(entry.path_lower)
            elif isinstance(entry, FileMetadata):
                if _is_supported(entry.name):
                    yield entry
        while res.has_more:
            res = dbx.files_list_folder_continue(res.cursor)
            for entry in res.entries:
                if isinstance(entry, FolderMetadata):
                    queue.append(entry.path_lower)
                elif isinstance(entry, FileMetadata):
                    if _is_supported(entry.name):
                        yield entry

def download_text(dbx: dropbox.Dropbox, path: str, max_bytes: int = 4_000_000) -> Optional[str]:
    """Download a file and return extracted text or None if empty/too big."""
    md, resp = dbx.files_download(path)
    data = resp.content
    if len(data) > max_bytes:
        return None
    buf = io.BytesIO(data)
    text = _read_any(path, buf)
    return text if text and text.strip() else None

def load_corpus_from_dropbox(
    access_token: str,
    root: str,
    max_bytes: int = 4_000_000
) -> List[Dict[str, str]]:
    """
    Returns a list of docs: [{"id": "...", "path": "...", "title": "...", "text": "..."}]
    """
    dbx = dropbox.Dropbox(access_token)
    docs: List[Dict[str, str]] = []

    for fm in walk_files(dbx, root):
        try:
            text = download_text(dbx, fm.path_lower, max_bytes=max_bytes)
            if not text:
                continue
            title = os.path.basename(fm.path_display or fm.name)
            docs.append({
                "id": fm.id,
                "path": fm.path_display or fm.path_lower,
                "title": title,
                "text": text,
            })
        except Exception:
            # Skip unreadable files; you could log here
            continue

    return docs
