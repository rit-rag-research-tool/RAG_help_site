"""
Quick test script for Dropbox RAG integration
Run this to verify your Dropbox connection and see loaded documents
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print(" Testing Dropbox RAG Integration")
print("=" * 60)

try:
    from dropbox_rag import get_dropbox_rag
    
    # Get the Dropbox RAG instance
    print("\n  Initializing Dropbox RAG...")
    dropbox_rag = get_dropbox_rag()
    
    # Get statistics
    print("\n  Getting statistics...")
    stats = dropbox_rag.get_stats()
    print(f"   Initialized: {stats['initialized']}")
    print(f"   Document count: {stats['document_count']}")
    print(f"   Total size: {stats['total_size']} bytes")
    print(f"   Folder path: {stats['folder_path']}")
    
    # Test search
    print("\n  Testing search functionality...")
    test_query = "RIT computer science"
    print(f"   Query: '{test_query}'")
    results = dropbox_rag.search_documents(test_query, max_results=3)
    print(f"   Results found: {len(results)}")
    
    if results:
        print("\n  Sample results:")
        for i, result in enumerate(results[:2], 1):
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"\n   Result {i}:")
            print(f"   {preview}")
    
    print("\n" + "=" * 60)
    if stats['initialized'] and stats['document_count'] > 0:
        print(" SUCCESS! Dropbox RAG is working correctly!")
    elif stats['initialized'] and stats['document_count'] == 0:
        print("  WARNING: Connected to Dropbox but no documents found")
        print(f"   Make sure you have files in: {stats['folder_path']}")
    else:
        print("  ERROR: Dropbox not initialized")
        print("   Check your .env file and DROPBOX_ACCESS_TOKEN")
    print("=" * 60)
    
except Exception as e:
    print(f"\n  ERROR: {e}")
    print("\n Troubleshooting steps:")
    print("   1. Check that .env file exists in server/python/")
    print("   2. Verify DROPBOX_ACCESS_TOKEN is set correctly")
    print("   3. Make sure the Dropbox folder exists")
    import traceback
    traceback.print_exc()
