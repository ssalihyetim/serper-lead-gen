"""
Cross-API deduplication utilities
Handles deduplication across Search API and Maps API results
"""

import csv
from urllib.parse import urlparse
import re


class Deduplicator:
    """Handles URL and domain-based deduplication"""

    def __init__(self):
        self.seen_urls = set()
        self.seen_domains = set()
        self.url_to_record = {}  # Store first occurrence of each URL

    @staticmethod
    def extract_domain(url):
        """
        Extract clean domain from URL

        Args:
            url: Full URL string

        Returns:
            Domain string (e.g., 'example.com')
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix
            domain = re.sub(r'^www\.', '', domain)
            return domain.lower()
        except:
            return url.lower()

    @staticmethod
    def normalize_url(url):
        """
        Normalize URL for comparison

        Args:
            url: Full URL string

        Returns:
            Normalized URL string
        """
        try:
            # Remove trailing slashes, query params, fragments
            parsed = urlparse(url)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
            return normalized.lower()
        except:
            return url.lower()

    def add_url(self, url, record=None):
        """
        Add URL to deduplication tracker

        Args:
            url: URL to track
            record: Optional dict of record data to store

        Returns:
            True if URL is new, False if duplicate
        """
        normalized = self.normalize_url(url)

        if normalized in self.seen_urls:
            return False

        self.seen_urls.add(normalized)

        if record:
            self.url_to_record[normalized] = record

        return True

    def add_domain(self, domain):
        """
        Add domain to deduplication tracker

        Args:
            domain: Domain to track

        Returns:
            True if domain is new, False if duplicate
        """
        domain = domain.lower()

        if domain in self.seen_domains:
            return False

        self.seen_domains.add(domain)
        return True

    def is_duplicate_url(self, url):
        """Check if URL is duplicate"""
        normalized = self.normalize_url(url)
        return normalized in self.seen_urls

    def is_duplicate_domain(self, domain):
        """Check if domain is duplicate"""
        return domain.lower() in self.seen_domains

    def get_unique_count(self):
        """Get count of unique URLs tracked"""
        return len(self.seen_urls)

    def get_unique_domains_count(self):
        """Get count of unique domains tracked"""
        return len(self.seen_domains)


def deduplicate_csv(csv_path, output_path=None, key='url', keep='first'):
    """
    Deduplicate CSV file by specified key

    Args:
        csv_path: Input CSV file path
        output_path: Output CSV file path (if None, overwrites input)
        key: Column name to deduplicate by (default: 'url')
        keep: Which duplicate to keep - 'first' or 'last'

    Returns:
        Tuple of (total_rows, unique_rows, duplicates_removed)
    """
    seen = set()
    unique_rows = []
    total_rows = 0
    duplicates = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            total_rows += 1
            key_value = row.get(key, '').strip()

            if not key_value:
                continue

            # Normalize key for comparison
            if key == 'url':
                key_value = Deduplicator.normalize_url(key_value)
            elif key == 'domain':
                key_value = Deduplicator.extract_domain(key_value)

            if key_value not in seen:
                seen.add(key_value)
                unique_rows.append(row)
            else:
                duplicates += 1
                if keep == 'last':
                    # Replace previous occurrence
                    unique_rows = [r for r in unique_rows if
                                   Deduplicator.normalize_url(r.get(key, '')) != key_value]
                    unique_rows.append(row)

    # Write deduplicated results
    output = output_path or csv_path
    with open(output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    return total_rows, len(unique_rows), duplicates


def merge_csv_files(file_paths, output_path, deduplicate_by='url'):
    """
    Merge multiple CSV files and deduplicate

    Args:
        file_paths: List of CSV file paths to merge
        output_path: Output merged CSV file path
        deduplicate_by: Column to deduplicate by ('url' or 'domain')

    Returns:
        Tuple of (total_rows, unique_rows, duplicates_removed)
    """
    deduper = Deduplicator()
    all_rows = []
    fieldnames = None
    total_rows = 0

    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Use first file's fieldnames as base
                if fieldnames is None:
                    fieldnames = reader.fieldnames

                for row in reader:
                    total_rows += 1

                    # Check for duplicates
                    if deduplicate_by == 'url':
                        url = row.get('url', '').strip()
                        if url and deduper.add_url(url, record=row):
                            all_rows.append(row)
                    elif deduplicate_by == 'domain':
                        domain = row.get('domain', '').strip()
                        if domain and deduper.add_domain(domain):
                            all_rows.append(row)
                    else:
                        # No deduplication, just merge
                        all_rows.append(row)

        except FileNotFoundError:
            print(f"Warning: File not found - {file_path}")
            continue
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # Write merged results
    if all_rows and fieldnames:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

    duplicates = total_rows - len(all_rows)
    return total_rows, len(all_rows), duplicates


if __name__ == "__main__":
    # Test deduplicator
    deduper = Deduplicator()

    test_urls = [
        "https://example.com/page",
        "https://example.com/page/",
        "https://www.example.com/page",
        "https://example.com/other",
    ]

    print("Testing URL deduplication:")
    for url in test_urls:
        is_new = deduper.add_url(url)
        print(f"  {url} -> {'NEW' if is_new else 'DUPLICATE'}")

    print(f"\nUnique URLs: {deduper.get_unique_count()}")
    print(f"Unique Domains: {deduper.get_unique_domains_count()}")
