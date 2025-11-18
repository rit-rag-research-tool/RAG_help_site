"""
Test script to verify domain filtering in RAG implementation
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_rag_endpoint():
    """Test the /rag endpoint with domain filtering"""
    
    test_queries = [
        {
            "name": "RIT-specific query",
            "query": "What are the requirements for the Computer Science program at RIT?",
            "expected_domains": ["rit.edu"]
        },
        {
            "name": "Office help query",
            "query": "How do I create a pivot table in Excel?",
            "expected_domains": ["support.microsoft.com", "learn.microsoft.com", "office.com"]
        },
        {
            "name": "Slack help query",
            "query": "How do I set up Slack notifications?",
            "expected_domains": ["slack.com"]
        }
    ]
    
    print("🧪 Testing Domain Filtering Integration\n")
    print("=" * 60)
    
    for test in test_queries:
        print(f"\n📝 Test: {test['name']}")
        print(f"   Query: {test['query']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/rag",
                json={"query": test["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                citations = data.get("citations", [])
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📄 Answer length: {len(answer)} chars")
                print(f"   🔗 Citations found: {len(citations)}")
                
                if citations:
                    print(f"   📚 Sources:")
                    for i, cite in enumerate(citations[:3], 1):
                        url = cite.get("url", "")
                        title = cite.get("title", "No title")
                        print(f"      {i}. {title}")
                        print(f"         {url}")
                        
                        # Check if domain matches expected
                        for expected_domain in test["expected_domains"]:
                            if expected_domain in url:
                                print(f"         ✅ Domain match: {expected_domain}")
                                break
                else:
                    print(f"   ⚠️  No citations returned")
                    
            else:
                print(f"   ❌ Error: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Testing complete!\n")

if __name__ == "__main__":
    print("Checking if backend is available...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!\n")
            test_rag_endpoint()
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running!")
        print("   Please start the backend with: .\run-dev.ps1")
        print("   Or manually: cd server\\python && uvicorn main:app --reload")
