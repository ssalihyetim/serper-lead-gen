#!/usr/bin/env python3
"""
Orchestrator for Two-Phase Lead Generation
Phase 1: Search API (web discovery)
Phase 2: Maps API (local business supplement)
"""

import sys
import os
from datetime import datetime
import csv

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

from serper_search_v2 import EnhancedSerperSearcher
from serper_maps import SerperMapsSearcher
from config.locations import get_cities
from config.queries import get_queries_by_priority, get_maps_queries
from utils.deduplicator import merge_csv_files


class LeadGenerationOrchestrator:
    """Orchestrates multi-phase search strategy"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = "results"

        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)

        # Results tracking
        self.phase1_file = None
        self.phase2_file = None
        self.final_file = None

    def print_banner(self, text: str):
        """Print formatted banner"""
        print("\n" + "="*70)
        print(text.center(70))
        print("="*70 + "\n")

    def run_phase1_search(self, keywords: list, cities: list, query_priority: str = "all",
                         gl: str = "us", hl: str = "en", results_per_query: int = 100):
        """
        Phase 1: Web Search API
        Discovers businesses through web search results

        Returns:
            Filename of Phase 1 results CSV
        """
        self.print_banner("PHASE 1: WEB SEARCH API")

        print("Configuration:")
        print(f"  Keywords: {len(keywords)}")
        print(f"  Cities: {len(cities)}")
        print(f"  Query priority: {query_priority}")
        print(f"  Results per query: {results_per_query}")

        query_count = len(get_queries_by_priority(query_priority))
        estimated_calls = len(keywords) * len(cities) * query_count * (results_per_query // 10)

        print(f"\nEstimated API calls: ~{estimated_calls}")
        print(f"Query variations: {query_count}")

        proceed = input("\nProceed with Phase 1? (Y/n): ").strip().lower()
        if proceed == 'n':
            print("Phase 1 cancelled.")
            return None

        # Initialize searcher
        searcher = EnhancedSerperSearcher(self.api_key)

        # Run searches
        for keyword in keywords:
            searcher.search_keyword_multi_location(
                keyword=keyword,
                cities=cities,
                query_priority=query_priority,
                gl=gl,
                hl=hl,
                results_per_query=results_per_query
            )

        # Show stats
        searcher.get_stats()

        # Export
        phase1_filename = f"{self.results_dir}/phase1_search_{self.timestamp}.csv"
        self.phase1_file = searcher.export_to_csv(phase1_filename)

        return self.phase1_file

    def analyze_phase1_coverage(self):
        """
        Analyze Phase 1 results to identify cities with low coverage
        Returns list of cities that need Maps supplementation
        """
        if not self.phase1_file:
            return []

        self.print_banner("PHASE 1 ANALYSIS")

        # Read Phase 1 results
        city_counts = {}
        total_results = 0

        try:
            with open(self.phase1_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_results += 1
                    city = row.get('city', 'Unknown')
                    city_counts[city] = city_counts.get(city, 0) + 1
        except Exception as e:
            print(f"Error reading Phase 1 results: {e}")
            return []

        # Calculate statistics
        print(f"Total results from Phase 1: {total_results}")
        print(f"Cities with results: {len(city_counts)}")

        if not city_counts:
            return []

        avg_results = total_results / len(city_counts)
        print(f"Average results per city: {avg_results:.1f}")

        # Find under-represented cities (below 50% of average)
        threshold = avg_results * 0.5
        underrepresented = []

        print(f"\nCity Coverage Analysis (threshold: {threshold:.1f}):")
        for city, count in sorted(city_counts.items(), key=lambda x: x[1]):
            status = "⚠️  LOW" if count < threshold else "✓ OK"
            print(f"  {city}: {count} results [{status}]")
            if count < threshold:
                underrepresented.append(city)

        print(f"\nCities needing Maps supplement: {len(underrepresented)}")

        return underrepresented

    def run_phase2_maps(self, keywords: list, cities: list = None,
                       gl: str = "us", hl: str = "en"):
        """
        Phase 2: Maps API
        Supplements Phase 1 with local business data

        Args:
            keywords: List of keywords
            cities: List of city dictionaries (if None, supplement all from Phase 1 analysis)
            gl: Country code
            hl: Language code

        Returns:
            Filename of Phase 2 results CSV
        """
        self.print_banner("PHASE 2: MAPS API SUPPLEMENT")

        if cities is None:
            # Analyze Phase 1 to determine which cities need supplementation
            underrepresented_city_names = self.analyze_phase1_coverage()

            if not underrepresented_city_names:
                print("\nAll cities have good coverage. Skipping Phase 2.")
                return None

            # Convert city names back to city dictionaries
            all_cities = get_cities(limit=50)
            cities = [c for c in all_cities if f"{c['city']}, {c['state']}" in underrepresented_city_names]

            if not cities:
                print("\nNo cities to supplement. Skipping Phase 2.")
                return None

        print(f"\nConfiguration:")
        print(f"  Keywords: {len(keywords)}")
        print(f"  Cities to supplement: {len(cities)}")
        print(f"  Maps queries: {len(get_maps_queries())}")

        estimated_calls = len(keywords) * len(cities) * len(get_maps_queries())
        print(f"\nEstimated API calls: {estimated_calls}")

        proceed = input("\nProceed with Phase 2? (Y/n): ").strip().lower()
        if proceed == 'n':
            print("Phase 2 cancelled.")
            return None

        # Initialize Maps searcher
        searcher = SerperMapsSearcher(self.api_key)

        # Run Maps searches
        for keyword in keywords:
            searcher.search_keyword_multi_location(
                keyword=keyword,
                cities=cities,
                gl=gl,
                hl=hl
            )

        # Show stats
        searcher.get_stats()

        # Export
        phase2_filename = f"{self.results_dir}/phase2_maps_{self.timestamp}.csv"
        self.phase2_file = searcher.export_to_csv(phase2_filename)

        return self.phase2_file

    def merge_results(self):
        """
        Merge Phase 1 and Phase 2 results with deduplication

        Returns:
            Filename of final merged results
        """
        self.print_banner("MERGING RESULTS")

        files_to_merge = []
        if self.phase1_file:
            files_to_merge.append(self.phase1_file)
        if self.phase2_file:
            files_to_merge.append(self.phase2_file)

        if not files_to_merge:
            print("No results to merge!")
            return None

        if len(files_to_merge) == 1:
            print(f"Only one phase completed. Using {files_to_merge[0]} as final results.")
            return files_to_merge[0]

        # Merge with domain-level deduplication
        final_filename = f"{self.results_dir}/final_merged_{self.timestamp}.csv"

        print(f"Merging {len(files_to_merge)} files...")
        print(f"  Phase 1: {self.phase1_file}")
        print(f"  Phase 2: {self.phase2_file}")

        total, unique, dupes = merge_csv_files(
            files_to_merge,
            final_filename,
            deduplicate_by='domain'
        )

        print(f"\nMerge Results:")
        print(f"  Total records: {total}")
        print(f"  Unique businesses: {unique}")
        print(f"  Duplicates removed: {dupes}")
        print(f"\n✓ Final results saved to: {final_filename}")

        self.final_file = final_filename
        return final_filename

    def run_full_pipeline(self, keywords: list, cities: list,
                         query_priority: str = "all",
                         gl: str = "us", hl: str = "en",
                         results_per_query: int = 100,
                         skip_phase2: bool = False):
        """
        Run complete two-phase pipeline

        Args:
            keywords: List of keywords to search
            cities: List of city dictionaries
            query_priority: Query priority level
            gl: Country code
            hl: Language code
            results_per_query: Results per search query
            skip_phase2: If True, skip Maps API phase

        Returns:
            Path to final results file
        """
        self.print_banner("FULL LEAD GENERATION PIPELINE")

        start_time = datetime.now()

        # Phase 1: Search API
        self.run_phase1_search(
            keywords=keywords,
            cities=cities,
            query_priority=query_priority,
            gl=gl,
            hl=hl,
            results_per_query=results_per_query
        )

        # Phase 2: Maps API (conditional)
        if not skip_phase2:
            self.run_phase2_maps(
                keywords=keywords,
                cities=None,  # Auto-determine from Phase 1 analysis
                gl=gl,
                hl=hl
            )
        else:
            print("\nPhase 2 skipped as requested.")

        # Merge results
        final_file = self.merge_results()

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        self.print_banner("PIPELINE COMPLETE")
        print(f"Duration: {duration:.1f} minutes")
        print(f"Final results: {final_file}")

        return final_file


def main():
    """Interactive orchestrator"""
    API_KEY = "7d96d845cbccec41f1f2b35b0d0da05cef94c149"

    orchestrator = LeadGenerationOrchestrator(API_KEY)

    print("="*70)
    print("TWO-PHASE LEAD GENERATION ORCHESTRATOR")
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
            continue
        keywords.append(keyword)

    if not keywords:
        print("No keywords entered. Exiting.")
        return

    # Configuration
    print("\n" + "="*70)
    print("CONFIGURATION")
    print("="*70)

    # Cities
    print("\nCity selection:")
    print("  1. Top 20 cities (recommended)")
    print("  2. Top 10 cities")
    print("  3. Top 5 cities")

    city_choice = input("\nSelect (1-3, default: 1): ").strip() or "1"

    city_limits = {"1": 20, "2": 10, "3": 5}
    cities = get_cities(limit=city_limits.get(city_choice, 20))

    # Query priority
    print("\nQuery priority:")
    print("  1. All queries (~35 variations)")
    print("  2. High priority (supplier signals, ~12)")
    print("  3. Medium priority (custom/print, ~13)")

    priority_choice = input("\nSelect (1-3, default: 2): ").strip() or "2"
    priority_map = {"1": "all", "2": "high", "3": "medium"}
    priority = priority_map.get(priority_choice, "high")

    # Other settings
    gl = input("\nCountry code (default: us): ").strip() or "us"
    hl = input("Language code (default: en): ").strip() or "en"
    results_input = input("Results per query (default: 100): ").strip()
    results = int(results_input) if results_input.isdigit() else 100

    # Phase 2 option
    skip_phase2_input = input("\nInclude Maps API Phase 2? (Y/n): ").strip().lower()
    skip_phase2 = skip_phase2_input == 'n'

    # Run pipeline
    orchestrator.run_full_pipeline(
        keywords=keywords,
        cities=cities,
        query_priority=priority,
        gl=gl,
        hl=hl,
        results_per_query=results,
        skip_phase2=skip_phase2
    )


if __name__ == "__main__":
    main()
