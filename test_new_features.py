#!/usr/bin/env python3
"""
Test script for new Serper API features:
- Related Searches capture
- Autocomplete suggestions
"""

from serper_search_v2 import EnhancedSerperSearcher

def test_autocomplete():
    """Test autocomplete suggestions"""
    API_KEY = "7d96d845cbccec41f1f2b35b0d0da05cef94c149"
    searcher = EnhancedSerperSearcher(API_KEY)

    print("="*70)
    print("TEST 1: AUTOCOMPLETE SUGGESTIONS")
    print("="*70)

    # Test autocomplete
    partial_query = "custom lanyard"
    print(f"\nTesting autocomplete for: '{partial_query}'")
    suggestions = searcher.get_autocomplete_suggestions(partial_query)

    if suggestions:
        print(f"\nFound {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("No suggestions found")

    print("\n" + "="*70)

def test_related_searches():
    """Test related searches capture"""
    API_KEY = "7d96d845cbccec41f1f2b35b0d0da05cef94c149"
    searcher = EnhancedSerperSearcher(API_KEY)

    print("\nTEST 2: RELATED SEARCHES CAPTURE")
    print("="*70)

    # Perform a search to capture related searches
    query = "custom lanyard manufacturer"
    print(f"\nSearching for: '{query}'")
    print("This will capture related searches automatically...")

    result_count = searcher.search_single_query(
        query=query,
        total_results=10,
        silent=False
    )

    print(f"\nFound {result_count} results")

    # Check if related searches were captured
    if query in searcher.related_searches:
        related = searcher.related_searches[query]
        print(f"\nCaptured {len(related)} related searches:")
        for i, related_query in enumerate(related, 1):
            print(f"  {i}. {related_query}")
    else:
        print("\nNo related searches captured for this query")

    # Export related searches
    if searcher.related_searches:
        print("\nExporting related searches to CSV...")
        searcher.export_related_searches()

    print("\n" + "="*70)

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TESTING NEW SERPER API FEATURES")
    print("="*70 + "\n")

    # Test 1: Autocomplete
    test_autocomplete()

    # Test 2: Related Searches
    test_related_searches()

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
