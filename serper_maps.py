#!/usr/bin/env python3
"""
Serper Maps API Integration
Finds local businesses using Google Maps data via Serper API
"""

import requests
import csv
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime

# Add config and utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from config.queries import get_maps_queries
from config.locations import get_cities, get_city_string
from utils.deduplicator import Deduplicator


class SerperMapsSearcher:
    """Google Maps business search via Serper API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/maps"
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        self.deduplicator = Deduplicator()
        self.all_results: List[Dict] = []
        self.api_call_count = 0

    def search_maps(self, query: str, location: str = "", gl: str = "us",
                    hl: str = "en", page: int = 1) -> Dict:
        """
        Search Google Maps via Serper API

        Args:
            query: Search query (e.g., "lanyard supplier")
            location: Location string (e.g., "New York, NY")
            gl: Country code
            hl: Language code
            page: Page number for pagination (default: 1)

        Returns:
            API response dictionary
        """
        # Build query with location
        full_query = f"{query} in {location}" if location else query

        payload = {
            "q": full_query,
            "gl": gl,
            "hl": hl,
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
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Error: {e}")
            return {}

    def extract_maps_results(self, places: List[Dict], query: str,
                            city: str) -> List[Dict]:
        """
        Extract and format Maps API results

        Args:
            places: List of place results from API
            query: Search query used
            city: City searched

        Returns:
            List of formatted business results
        """
        results = []

        for place in places:
            # Extract key information
            title = place.get('title', '')
            address = place.get('address', '')
            phone = place.get('phoneNumber', '')
            website = place.get('website', '')
            rating = place.get('rating', '')
            reviews = place.get('reviews', 0)
            category = place.get('category', '')
            place_id = place.get('placeId', '')

            # Use website as primary dedup key, fall back to place_id
            dedup_key = website if website else f"place_id:{place_id}"

            # Skip if duplicate
            if not self.deduplicator.add_url(dedup_key):
                continue

            # Extract domain from website if available
            domain = ''
            if website:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(website)
                    domain = parsed.netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                except:
                    pass

            result = {
                'business_name': title,
                'address': address,
                'phone': phone,
                'website': website,
                'domain': domain,
                'rating': rating,
                'review_count': reviews,
                'category': category,
                'city': city,
                'query': query,
                'place_id': place_id,
                'source': 'maps'
            }
            results.append(result)

        return results

    def search_location(self, keyword: str, city_dict: Dict,
                       gl: str = "us", hl: str = "en",
                       silent: bool = False) -> int:
        """
        Search Maps for a keyword in a specific location

        Args:
            keyword: Base keyword
            city_dict: City dictionary with 'city' and 'state' keys
            gl: Country code
            hl: Language code
            silent: Suppress output

        Returns:
            Number of results found
        """
        city_str = get_city_string(city_dict, format="full")
        query_templates = get_maps_queries()

        if not silent:
            print(f"  Searching Maps: {city_str}")

        location_results = 0

        for query_template in query_templates:
            query = query_template.format(keyword=keyword)

            if not silent:
                print(f"    → {query}")

            response = self.search_maps(
                query=query,
                location=city_str,
                gl=gl,
                hl=hl
            )

            if not response:
                continue

            # Extract places
            places = response.get('places', [])

            if places:
                results = self.extract_maps_results(places, query, city_str)
                self.all_results.extend(results)
                location_results += len(results)

                if not silent:
                    print(f"      ✓ Found {len(results)} new businesses")

        return location_results

    def search_keyword_multi_location(self, keyword: str, cities: List[Dict],
                                     gl: str = "us", hl: str = "en"):
        """
        Search Maps across multiple locations

        Args:
            keyword: Base keyword
            cities: List of city dictionaries
            gl: Country code
            hl: Language code
        """
        total_cities = len(cities)
        query_count = len(get_maps_queries())

        print(f"\n{'='*70}")
        print(f"MAPS SEARCH: '{keyword}'")
        print(f"{'='*70}")
        print(f"Cities: {total_cities} | Query variations: {query_count}")
        print(f"{'='*70}\n")

        initial_count = len(self.all_results)

        for idx, city in enumerate(cities, 1):
            print(f"[City {idx}/{total_cities}] {get_city_string(city)}")
            self.search_location(keyword, city, gl, hl)

        new_results = len(self.all_results) - initial_count

        print(f"\n{'='*70}")
        print(f"MAPS SUMMARY: '{keyword}'")
        print(f"{'='*70}")
        print(f"New businesses found: {new_results}")
        print(f"Total businesses: {len(self.all_results)}")
        print(f"API calls: {self.api_call_count}")
        print(f"{'='*70}\n")

    def export_to_csv(self, filename: str = None):
        """
        Export Maps results to CSV

        Args:
            filename: Output filename
        """
        if not self.all_results:
            print("\n⚠️  No results to export!")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/maps_results_{timestamp}.csv"

        # Ensure results directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        fieldnames = [
            'business_name', 'address', 'phone', 'website', 'domain',
            'rating', 'review_count', 'category', 'city', 'query',
            'place_id', 'source'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_results)

            print(f"\n✓ Successfully exported {len(self.all_results)} businesses to '{filename}'")
            return filename
        except IOError as e:
            print(f"\n✗ Error writing to file: {e}")
            return None

    def get_stats(self):
        """Print statistics"""
        if not self.all_results:
            return

        # Count businesses with websites
        with_website = sum(1 for r in self.all_results if r.get('website'))
        with_phone = sum(1 for r in self.all_results if r.get('phone'))

        # Category breakdown
        category_counts = {}
        for r in self.all_results:
            cat = r.get('category', 'Unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # City breakdown
        city_counts = {}
        for r in self.all_results:
            city = r.get('city', 'Unknown')
            city_counts[city] = city_counts.get(city, 0) + 1

        print("\n" + "="*70)
        print("MAPS SEARCH STATISTICS")
        print("="*70)
        print(f"Total businesses found: {len(self.all_results)}")
        print(f"  - With website: {with_website} ({with_website/len(self.all_results)*100:.1f}%)")
        print(f"  - With phone: {with_phone} ({with_phone/len(self.all_results)*100:.1f}%)")
        print(f"\nTotal API calls: {self.api_call_count}")

        print(f"\nTop 5 Categories:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {cat}: {count} businesses")

        print(f"\nTop 10 Cities:")
        for city, count in sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {city}: {count} businesses")
        print("="*70)


def main():
    """Main function"""
    API_KEY = "7d96d845cbccec41f1f2b35b0d0da05cef94c149"

    searcher = SerperMapsSearcher(API_KEY)

    print("="*70)
    print("SERPER MAPS API - LOCAL BUSINESS SEARCH")
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

    # City selection
    print("\n" + "="*70)
    print("CITY SELECTION")
    print("="*70)
    print("  1. Top 20 cities")
    print("  2. Top 10 cities")
    print("  3. Top 5 cities")

    choice = input("\nSelect option (1-3, default: 2): ").strip() or "2"

    if choice == "1":
        cities = get_cities(limit=20)
    elif choice == "3":
        cities = get_cities(limit=5)
    else:
        cities = get_cities(limit=10)

    print(f"\nSelected {len(cities)} cities")

    # Other settings
    gl = input("\nCountry code (default: us): ").strip() or "us"
    hl = input("Language code (default: en): ").strip() or "en"

    # Summary
    query_count = len(get_maps_queries())
    print("\n" + "="*70)
    print("SEARCH PLAN")
    print("="*70)
    print(f"Keywords: {len(keywords)}")
    print(f"Cities: {len(cities)}")
    print(f"Maps queries per city: {query_count}")
    print(f"Estimated API calls: {len(keywords) * len(cities) * query_count}")
    print("="*70)

    proceed = input("\nProceed? (Y/n): ").strip().lower()
    if proceed == 'n':
        print("Cancelled.")
        return

    # Execute
    print("\n" + "="*70)
    print("STARTING MAPS SEARCHES...")
    print("="*70)

    for keyword in keywords:
        searcher.search_keyword_multi_location(
            keyword=keyword,
            cities=cities,
            gl=gl,
            hl=hl
        )

    # Stats and export
    searcher.get_stats()

    custom_filename = input("\nEnter output filename (press Enter for default): ").strip()
    searcher.export_to_csv(custom_filename if custom_filename else None)


if __name__ == "__main__":
    main()
