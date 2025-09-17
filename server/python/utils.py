def clean_text(text):
    """Remove unwanted characters and whitespace from text."""
    return text.strip()

def format_documents(docs):
    """Format a list of documents into a single context string."""
    return "\n".join(docs)

# Add more utility functions as needed for preprocessing, logging, etc.