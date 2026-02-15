import logging
from modules.search_engine import engine

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_search():
    query = '"Property Developer" "Kuala Lumpur" LinkedIn'
    print(f"Testing Hybrid Search Engine with query: {query}")
    
    try:
        results = engine.search(query, limit=5)
        
        if results:
            print("\nSUCCESS: Found " + str(len(results)) + " results.")
            for i, r in enumerate(results):
                try:
                    title = r['title'].encode('ascii', 'ignore').decode('ascii')
                    print(f"{i+1}. {title}")
                    print(f"   Link: {r['link']}")
                except:
                    print(f"{i+1}. [Encoded Title]")
                print("-" * 20)
        else:
            print("\nFAILURE: No results found from any provider.")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_search()
