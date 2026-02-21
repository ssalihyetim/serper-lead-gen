#!/usr/bin/env python3
"""
Enhanced Serper API Search Script with Location Support
Searches multiple keywords across multiple cities using comprehensive query variations
"""

import requests
import csv
import sys
import os
from typing import List, Dict, Set, Optional
from datetime import datetime
from urllib.parse import urlparse

# Add config and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from config.queries import get_all_search_queries, get_queries_by_priority
from config.locations import get_cities, get_city_string
from config.exclusions import get_exclusion_string
from utils.deduplicator import Deduplicator


class EnhancedSerperSearcher:
    """Enhanced searcher with location and comprehensive query support"""

    def __init__(self, api_key: str, enable_checkpoints: bool = True):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        self.autocomplete_url = "https://google.serper.dev/autocomplete"
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        self.deduplicator = Deduplicator()
        self.all_results: List[Dict] = []
        self.api_call_count = 0
        self.related_searches: Dict[str, List[str]] = {}  # Store related searches by query

        # Checkpoint system for data loss prevention
        self.enable_checkpoints = enable_checkpoints
        self.checkpoint_file = None
        self.checkpoint_interval = 50  # Save every 50 results
        self.last_checkpoint_count = 0

    def search(self, query: str, gl: str = "us", hl: str = "en", num: int = 10, page: int = 1) -> Dict:
        """
        Perform a search query using Serper API.

        Args:
            query: Search query string
            gl: Country code (default: us)
            hl: Language code (default: en)
            num: Number of results per page (default: 10, max: 100)
            page: Page number for pagination (default: 1)

        Returns:
            API response as dictionary
        """
        payload = {
            "q": query,
            "gl": gl,
            "hl": hl,
            "num": num,
            "page": page
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            self.api_call_count += 1
            data = response.json()

            # Capture related searches if available
            if 'relatedSearches' in data and data['relatedSearches']:
                self.related_searches[query] = [
                    item.get('query', '') for item in data['relatedSearches']
                ]

            return data
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Error: {e}")
            return {}

    def get_autocomplete_suggestions(self, partial_query: str, gl: str = "us") -> List[str]:
        """
        Get Google autocomplete suggestions for a partial query

        Args:
            partial_query: Partial search query (e.g., "lanyard sup")
            gl: Country code (default: us)

        Returns:
            List of autocomplete suggestions as strings
        """
        payload = {
            "q": partial_query,
            "gl": gl
        }

        try:
            response = requests.post(
                self.autocomplete_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            self.api_call_count += 1
            data = response.json()

            # Extract suggestions - they come as list of dicts with 'value' key
            suggestions = data.get('suggestions', [])
            if isinstance(suggestions, list):
                # Extract 'value' from each dict
                return [s.get('value', s) if isinstance(s, dict) else s for s in suggestions]
            return []

        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Autocomplete Error: {e}")
            return []

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''

    def extract_results(self, data: List[Dict], query: str, source_type: str,
                       city: Optional[str] = None) -> List[Dict]:
        """
        Extract results from API response with deduplication

        Args:
            data: List of result items from API
            query: The search query used
            source_type: Type of result (organic/ads/shopping)
            city: City/location string if applicable

        Returns:
            List of extracted and deduplicated results
        """
        results = []

        for item in data:
            url = item.get('link', '')

            # Skip if URL is empty or duplicate
            if not url or not self.deduplicator.add_url(url):
                continue

            result = {
                'url': url,
                'domain': self.extract_domain(url),
                'title': item.get('title', ''),
                'description': item.get('snippet', ''),
                'source_type': source_type,
                'query': query,
                'city': city or '',
                'position': item.get('position', '')
            }
            results.append(result)

        return results

    def search_single_query(self, query: str, gl: str = "us", hl: str = "en",
                           total_results: int = 100, city: Optional[str] = None,
                           silent: bool = False) -> int:
        """
        Search a single query with pagination

        Args:
            query: Full search query
            gl: Country code
            hl: Language code
            total_results: Target number of results
            city: City/location string
            silent: If True, suppress output

        Returns:
            Number of unique results found
        """
        if not silent:
            print(f"    Searching: '{query[:80]}...'")

        results_per_page = 10
        total_pages = min((total_results + results_per_page - 1) // results_per_page, 10)

        page_results = 0

        for page in range(1, total_pages + 1):
            response = self.search(query, gl, hl, results_per_page, page)

            if not response:
                continue

            # Process organic results
            organic = response.get('organic', [])
            if organic:
                results = self.extract_results(organic, query, 'organic', city)
                self.all_results.extend(results)
                page_results += len(results)

            # Process ads (usually only on first page)
            if page == 1:
                ads = response.get('ads', [])
                if ads:
                    results = self.extract_results(ads, query, 'ads', city)
                    self.all_results.extend(results)
                    page_results += len(results)

                shopping = response.get('shopping', [])
                if shopping:
                    results = self.extract_results(shopping, query, 'shopping', city)
                    self.all_results.extend(results)
                    page_results += len(results)

            # If fewer results than expected, we've reached the end
            if len(organic) < results_per_page:
                break

        if not silent:
            print(f"      → Found {page_results} new results")

        # Check if checkpoint should be saved
        self.check_and_save_checkpoint()

        return page_results

    def search_keyword_multi_location(self, keyword: str, cities: List[Dict],
                                     query_priority: str = "all", gl: str = "us",
                                     hl: str = "en", results_per_query: int = 100):
        """
        Search a keyword across multiple locations with query variations

        Args:
            keyword: Base keyword to search
            cities: List of city dictionaries
            query_priority: Query priority level ('high', 'medium', 'industry', 'all')
            gl: Country code
            hl: Language code
            results_per_query: Results per query variation
        """
        # Get query variations
        query_templates = get_queries_by_priority(query_priority)
        exclusions = get_exclusion_string(include_b2b_directories=True)

        total_cities = len(cities)
        total_queries = len(query_templates)
        total_combinations = total_cities * total_queries

        print(f"\n{'='*70}")
        print(f"KEYWORD: '{keyword}'")
        print(f"{'='*70}")
        print(f"Cities: {total_cities} | Query variations: {total_queries} | Total: {total_combinations}")
        print(f"{'='*70}\n")

        combination_count = 0
        initial_result_count = len(self.all_results)

        # For each city
        for city_idx, city in enumerate(cities, 1):
            city_str = get_city_string(city, format="full")
            city_name = city['city']

            print(f"[City {city_idx}/{total_cities}] {city_str}")

            # For each query variation
            for query_idx, query_template in enumerate(query_templates, 1):
                combination_count += 1

                # Build full query: "{query_template} {city} {exclusions}"
                query_text = query_template.format(keyword=keyword)
                full_query = f"{query_text} {city_name} {exclusions}"

                # Search
                self.search_single_query(
                    query=full_query,
                    gl=gl,
                    hl=hl,
                    total_results=results_per_query,
                    city=city_str,
                    silent=False
                )

        # Summary for this keyword
        new_results = len(self.all_results) - initial_result_count
        print(f"\n{'='*70}")
        print(f"KEYWORD SUMMARY: '{keyword}'")
        print(f"{'='*70}")
        print(f"Total combinations processed: {combination_count}")
        print(f"New unique results: {new_results}")
        print(f"Total unique results so far: {len(self.all_results)}")
        print(f"API calls made: {self.api_call_count}")
        print(f"{'='*70}\n")

    def save_checkpoint(self):
        """
        Save results to checkpoint file incrementally
        Prevents data loss if process crashes or computer sleeps
        """
        if not self.enable_checkpoints:
            return

        if not self.all_results:
            return

        # Initialize checkpoint file on first save
        if not self.checkpoint_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.checkpoint_file = f"results/checkpoint_search_{timestamp}.csv"
            os.makedirs("results", exist_ok=True)

        # Determine which results are new since last checkpoint
        new_results = self.all_results[self.last_checkpoint_count:]

        if not new_results:
            return

        fieldnames = ['domain', 'url', 'title', 'description', 'source_type', 'query', 'city', 'position']
        file_exists = os.path.exists(self.checkpoint_file)

        try:
            with open(self.checkpoint_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_results)

            self.last_checkpoint_count = len(self.all_results)
            print(f"      💾 Checkpoint saved: {len(new_results)} new results ({len(self.all_results)} total)")

        except Exception as e:
            print(f"      ⚠️  Checkpoint save failed: {e}")

    def check_and_save_checkpoint(self):
        """Check if checkpoint should be saved based on interval"""
        if not self.enable_checkpoints:
            return

        results_since_checkpoint = len(self.all_results) - self.last_checkpoint_count

        if results_since_checkpoint >= self.checkpoint_interval:
            self.save_checkpoint()

    def export_to_csv(self, filename: str = None):
        """
        Export all results to CSV

        Args:
            filename: Output filename (default: auto-generated with timestamp)
        """
        # Save final checkpoint before export
        if self.enable_checkpoints:
            self.save_checkpoint()

        if not self.all_results:
            print("\n⚠️  No results to export!")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/search_results_{timestamp}.csv"

        # Ensure results directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        fieldnames = ['domain', 'url', 'title', 'description', 'source_type', 'query', 'city', 'position']

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_results)

            print(f"\n✓ Successfully exported {len(self.all_results)} results to '{filename}'")

            # Show checkpoint file info if exists
            if self.checkpoint_file and os.path.exists(self.checkpoint_file):
                print(f"💾 Checkpoint file: '{self.checkpoint_file}' (can be deleted)")

            return filename
        except IOError as e:
            print(f"\n✗ Error writing to file: {e}")
            return None

    def export_related_searches(self, filename: str = None):
        """
        Export related searches to CSV

        Args:
            filename: Output filename (default: auto-generated with timestamp)
        """
        if not self.related_searches:
            print("\n⚠️  No related searches captured!")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/related_searches_{timestamp}.csv"

        # Ensure results directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        fieldnames = ['original_query', 'related_search']

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for original_query, related_list in self.related_searches.items():
                    for related in related_list:
                        writer.writerow({
                            'original_query': original_query,
                            'related_search': related
                        })

            total_related = sum(len(v) for v in self.related_searches.values())
            print(f"\n✓ Successfully exported {total_related} related searches to '{filename}'")
            return filename
        except IOError as e:
            print(f"\n✗ Error writing to file: {e}")
            return None

    def print_related_searches(self):
        """Print related searches summary"""
        if not self.related_searches:
            return

        print("\n" + "="*70)
        print("RELATED SEARCHES")
        print("="*70)
        print(f"Total queries with related searches: {len(self.related_searches)}")

        # Show a few examples
        print(f"\nShowing first 5 examples:")
        for i, (query, related) in enumerate(list(self.related_searches.items())[:5], 1):
            print(f"\n{i}. Query: '{query}'")
            print(f"   Related searches ({len(related)}):")
            for r in related:
                print(f"     - {r}")

        print("="*70)

    def get_stats(self):
        """Print detailed statistics"""
        if not self.all_results:
            return

        organic = sum(1 for r in self.all_results if r['source_type'] == 'organic')
        ads = sum(1 for r in self.all_results if r['source_type'] == 'ads')
        shopping = sum(1 for r in self.all_results if r['source_type'] == 'shopping')

        # City breakdown
        city_counts = {}
        for r in self.all_results:
            city = r.get('city', 'Unknown')
            city_counts[city] = city_counts.get(city, 0) + 1

        print("\n" + "="*70)
        print("FINAL SEARCH STATISTICS")
        print("="*70)
        print(f"Total unique results: {len(self.all_results)}")
        print(f"  - Organic: {organic}")
        print(f"  - Ads: {ads}")
        print(f"  - Shopping: {shopping}")
        print(f"\nTotal unique URLs: {self.deduplicator.get_unique_count()}")
        print(f"Total unique domains: {self.deduplicator.get_unique_domains_count()}")
        print(f"Total API calls: {self.api_call_count}")
        print(f"\nTop 10 Cities by Results:")
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {city}: {count} results")
        print("="*70)

        # Print related searches if available
        if self.related_searches:
            self.print_related_searches()


def main():
    """Main function"""
    API_KEY = "7d96d845cbccec41f1f2b35b0d0da05cef94c149"

    searcher = EnhancedSerperSearcher(API_KEY)

    print("="*70)
    print("ENHANCED SERPER API MULTI-LOCATION SEARCH")
    print("="*70)

    # Get keywords
    print("\nEnter keywords to search (one per line).")
    print("Press Enter twice when done:\n")

    keywords = []
    while True:
        keyword = input().strip()
        if not keyword:
            if keywords:
                break
            else:
                continue
        keywords.append(keyword)

    if not keywords:
        print("No keywords entered. Exiting.")
        return

    # Configuration
    print("\n" + "="*70)
    print("CONFIGURATION")
    print("="*70)

    # City selection
    print("\nCity targeting options:")
    print("  1. Top 20 cities (recommended)")
    print("  2. Top 10 cities (pilot)")
    print("  3. Top 5 cities (test)")
    print("  4. Custom tier selection")

    city_choice = input("\nSelect option (1-4, default: 1): ").strip() or "1"

    if city_choice == "1":
        cities = get_cities(limit=20)
    elif city_choice == "2":
        cities = get_cities(limit=10)
    elif city_choice == "3":
        cities = get_cities(limit=5)
    elif city_choice == "4":
        tier = input("Enter tier (1-4): ").strip()
        if tier.isdigit():
            cities = get_cities(tier=int(tier))
        else:
            cities = get_cities(limit=20)
    else:
        cities = get_cities(limit=20)

    print(f"\nSelected {len(cities)} cities")

    # Query priority
    print("\nQuery priority:")
    print("  1. All queries (~35 variations)")
    print("  2. High priority only (supplier signals, ~12 queries)")
    print("  3. Medium priority (custom/print, ~13 queries)")
    print("  4. Industry specific (~10 queries)")

    priority_choice = input("\nSelect option (1-4, default: 1): ").strip() or "1"

    priority_map = {
        "1": "all",
        "2": "high",
        "3": "medium",
        "4": "industry"
    }
    priority = priority_map.get(priority_choice, "all")

    # Other settings
    gl = input("\nCountry code (default: us): ").strip() or "us"
    hl = input("Language code (default: en): ").strip() or "en"
    results_input = input("Results per query (default: 100): ").strip()
    results_per_query = int(results_input) if results_input.isdigit() else 100

    # Summary
    from config.queries import get_queries_by_priority
    query_count = len(get_queries_by_priority(priority))

    print("\n" + "="*70)
    print("SEARCH PLAN SUMMARY")
    print("="*70)
    print(f"Keywords: {len(keywords)}")
    print(f"Cities: {len(cities)}")
    print(f"Query variations: {query_count}")
    print(f"Total combinations: {len(keywords) * len(cities) * query_count}")
    print(f"Estimated API calls: ~{len(keywords) * len(cities) * query_count * (results_per_query // 10)}")
    print("="*70)

    proceed = input("\nProceed with search? (Y/n): ").strip().lower()
    if proceed == 'n':
        print("Search cancelled.")
        return

    # Execute searches
    print("\n" + "="*70)
    print("STARTING SEARCHES...")
    print("="*70)

    for keyword in keywords:
        searcher.search_keyword_multi_location(
            keyword=keyword,
            cities=cities,
            query_priority=priority,
            gl=gl,
            hl=hl,
            results_per_query=results_per_query
        )

    # Show stats and export
    searcher.get_stats()

    custom_filename = input("\nEnter output filename (press Enter for default): ").strip()
    searcher.export_to_csv(custom_filename if custom_filename else None)


if __name__ == "__main__":
    main()
