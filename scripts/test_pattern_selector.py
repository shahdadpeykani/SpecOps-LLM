import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.pattern_selector import PatternSelector

def test_selector():
    print("Initializing PatternSelector...")
    try:
        selector = PatternSelector()
    except Exception as e:
        print(f"Failed to initialize PatternSelector: {e}")
        return

    test_cases = [
        {
            "query": "I need to ensure only one instance of the registry exists per port.",
            "expected_keyword": "Singleton" 
        },
        {
            "query": "I need to separate the data access logic from the business logic to make testing easier.",
            "expected_keyword": "Repository"
        },
        {
            "query": "I need a way to notify multiple customers when a product comes back in stock.",
            "expected_keyword": "Observer"
        }
    ]
    
    for case in test_cases:
        query = case['query']
        print(f"\n--- Testing Requirement: '{query}' ---")
        patterns = selector.select_patterns(query, n_results=1)
        
        if not patterns:
            print("FAILED: No patterns found.")
            continue
            
        top_match = patterns[0]
        name = top_match.get('name', 'Unknown')
        source = top_match.get('source', 'Unknown')
        desc = top_match.get('description', '')
        
        print(f"Top Match: {name}")
        print(f"Source: {source}")
        
        # Simple verification
        # Note: 'source' usually contains the filename like 'Singleton_Pattern.pdf'
        if case['expected_keyword'].lower() in source.lower() or case['expected_keyword'].lower() in name.lower():
            print("SUCCESS: Expected pattern found.")
        else:
            print(f"WARNING: Expected '{case['expected_keyword']}' but got '{name}'/'{source}'.")

if __name__ == "__main__":
    test_selector()
