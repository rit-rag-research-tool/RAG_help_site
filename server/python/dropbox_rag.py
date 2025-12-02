"""
Dropbox RAG Integration
Loads documents from Dropbox and provides search functionality for RAG.
"""
import os
import re
from typing import List, Dict
import dropbox
from dropbox.exceptions import AuthError, ApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DropboxRAG:
    """Manages document retrieval from Dropbox for RAG queries."""
    
    def __init__(self):
        """Initialize Dropbox client and document cache."""
        self.access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        self.folder_path = os.getenv("DROPBOX_FOLDER_PATH", "/RAG_Sources")
        self.dbx = None
        self.documents = []  # Cache of loaded documents
        self.initialized = False
        
        if not self.access_token or self.access_token == "your_dropbox_access_token_here":
            print("  Warning: DROPBOX_ACCESS_TOKEN not set in .env file")
            print("   RAG will fall back to stub documents")
            return
            
        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            # Test the connection
            self.dbx.users_get_current_account()
            print(f" Connected to Dropbox successfully")
            self.initialized = True
        except AuthError as e:
            print(f" Dropbox authentication failed: {e}")
            print("   Please check your DROPBOX_ACCESS_TOKEN in .env")
        except Exception as e:
            print(f" Dropbox connection error: {e}")
    
    def load_documents(self) -> int:
        """
        Load all documents from Dropbox folder into memory cache.
        Returns the number of documents loaded.
        """
        if not self.initialized:
            print("  Dropbox not initialized, skipping document load")
            return 0
        
        try:
            print(f" Loading documents from Dropbox folder: {self.folder_path}")
            self.documents = []
            
            # List all files in the folder recursively
            result = self.dbx.files_list_folder(self.folder_path, recursive=True)
            
            file_count = 0
            while True:
                for entry in result.entries:
                    # Only process text files
                    if isinstance(entry, dropbox.files.FileMetadata):
                        if self._is_text_file(entry.name):
                            try:
                                # Download file content
                                _, response = self.dbx.files_download(entry.path_lower)
                                content = response.content.decode('utf-8')
                                
                                # Store document with metadata
                                self.documents.append({
                                    'path': entry.path_lower,
                                    'name': entry.name,
                                    'content': content,
                                    'size': entry.size,
                                })
                                file_count += 1
                                print(f"   ✓ Loaded: {entry.name} ({entry.size} bytes)")
                            except Exception as e:
                                print(f"   ✗ Failed to load {entry.name}: {e}")
                
                # Check if there are more files
                if not result.has_more:
                    break
                result = self.dbx.files_list_folder_continue(result.cursor)
            
            print(f" Loaded {file_count} documents from Dropbox")
            return file_count
            
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                print(f" Folder not found: {self.folder_path}")
                print(f"   Please create this folder in Dropbox or update DROPBOX_FOLDER_PATH in .env")
            else:
                print(f" Dropbox API error: {e}")
            return 0
        except Exception as e:
            print(f" Error loading documents: {e}")
            return 0
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is a supported text format."""
        text_extensions = ['.txt', '.md', '.html', '.json', '.csv']
        return any(filename.lower().endswith(ext) for ext in text_extensions)
    
    def search_documents(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search through cached documents for relevant content.
        Uses simple keyword matching (can be enhanced with embeddings later).
        
        Args:
            query: Search query
            max_results: Maximum number of document chunks to return
            
        Returns:
            List of relevant document chunks
        """
        if not self.documents:
            print("  No documents loaded, using stub documents")
            return [
                "Document 1: This is a placeholder document. Please configure Dropbox.",
                "Document 2: Add your scraped content to Dropbox to use real documents."
            ]
        
        # Normalize query
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        # Score each document based on keyword matches
        scored_docs = []
        for doc in self.documents:
            content_lower = doc['content'].lower()
            
            # Calculate relevance score
            score = 0
            for word in query_words:
                # Count occurrences of each query word
                score += content_lower.count(word)
            
            if score > 0:
                # Split into chunks (paragraphs)
                chunks = self._split_into_chunks(doc['content'])
                
                # Score each chunk
                for chunk in chunks:
                    chunk_lower = chunk.lower()
                    chunk_score = sum(chunk_lower.count(word) for word in query_words)
                    
                    if chunk_score > 0:
                        scored_docs.append({
                            'chunk': chunk,
                            'score': chunk_score,
                            'source': doc['name']
                        })
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        
        results = []
        for item in scored_docs[:max_results]:
            results.append(f"[From {item['source']}]\n{item['chunk']}")
        
        if not results:
            print(f"  No relevant documents found for query: {query}")
            return ["No relevant documents found in Dropbox for this query."]
        
        print(f" Found {len(results)} relevant document chunks")
        return results
    
    def _split_into_chunks(self, content: str, chunk_size: int = 500) -> List[str]:
        """
        Split document content into manageable chunks.
        Tries to split on paragraph boundaries.
        """
        # Split on double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', content)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded documents."""
        return {
            'initialized': self.initialized,
            'document_count': len(self.documents),
            'total_size': sum(doc['size'] for doc in self.documents),
            'folder_path': self.folder_path
        }
    
    def refresh(self) -> int:
        """Refresh document cache from Dropbox."""
        print(" Refreshing documents from Dropbox...")
        return self.load_documents()


# Global instance (singleton pattern)
_dropbox_rag_instance = None

def get_dropbox_rag() -> DropboxRAG:
    """Get or create the global DropboxRAG instance."""
    global _dropbox_rag_instance
    if _dropbox_rag_instance is None:
        _dropbox_rag_instance = DropboxRAG()
        # Load documents on first initialization
        _dropbox_rag_instance.load_documents()
    return _dropbox_rag_instance