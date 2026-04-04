"""
Cloud Storage module for B2B Lead Generation System.
Handles all Supabase operations: search tracking, result storage, and CSV export.

Usage:
    from cloud_storage import CloudStorage

    cs = CloudStorage()

    # Start a new search session
    search_id = cs.create_search(sector="lanyard", countries=["US", "DE"], search_type="Both")

    # Save results in batches
    cs.save_results(search_id, results_list)

    # Mark search as complete
    cs.complete_search(search_id, total_results=1500, api_calls=260)

    # Get past searches
    searches = cs.get_past_searches(limit=20)

    # Get results for a search
    results = cs.get_results(search_id)
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional
import csv
import io

# Ensure project root is in path so config imports work regardless of cwd
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

SUPABASE_URL = ""
SUPABASE_ANON_KEY = ""

# Priority 1: config file (local dev)
try:
    from config.supabase_config import SUPABASE_URL, SUPABASE_ANON_KEY
except ImportError:
    pass

# Priority 2: Streamlit secrets (cloud deploy)
if not SUPABASE_URL:
    try:
        import streamlit as st
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
        SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "")
    except Exception:
        pass

# Priority 3: environment variables
if not SUPABASE_URL:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class CloudStorage:
    """
    Supabase cloud storage for search sessions and results.
    Falls back gracefully if Supabase is unavailable.
    """

    def __init__(self):
        self.client: Optional[Client] = None
        self.available = False
        self._connect()

    def _connect(self):
        if not SUPABASE_AVAILABLE:
            print("[CloudStorage] supabase-py not installed. Run: pip install supabase")
            return
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            print("[CloudStorage] Supabase credentials not configured.")
            return
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            self.available = True
        except Exception as e:
            print(f"[CloudStorage] Connection failed: {e}")

    # =========================================================
    # SEARCH SESSION MANAGEMENT
    # =========================================================

    def create_search(
        self,
        sector: str,
        countries: list,
        queries: list = None,
        search_type: str = "Both",
        notes: str = None,
    ) -> Optional[str]:
        """
        Create a new search session record.
        Returns the UUID of the new search, or None on failure.
        """
        if not self.available:
            return None
        try:
            data = {
                "sector": sector,
                "countries": countries,
                "queries": queries or [],
                "search_type": search_type,
                "status": "running",
                "notes": notes,
            }
            response = self.client.table("searches").insert(data).execute()
            search_id = response.data[0]["id"]
            print(f"[CloudStorage] Search started: {search_id}")
            return search_id
        except Exception as e:
            print(f"[CloudStorage] create_search failed: {e}")
            return None

    def complete_search(
        self,
        search_id: str,
        total_results: int,
        api_calls_used: int,
        csv_filename: str = None,
        status: str = "completed",
    ) -> bool:
        """Mark a search session as completed."""
        if not self.available or not search_id:
            return False
        try:
            data = {
                "status": status,
                "completed_at": datetime.utcnow().isoformat(),
                "total_results": total_results,
                "api_calls_used": api_calls_used,
            }
            if csv_filename:
                data["csv_filename"] = csv_filename
            self.client.table("searches").update(data).eq("id", search_id).execute()
            print(f"[CloudStorage] Search completed: {search_id} ({total_results} results)")
            return True
        except Exception as e:
            print(f"[CloudStorage] complete_search failed: {e}")
            return False

    def fail_search(self, search_id: str, error_msg: str = None) -> bool:
        """Mark a search as failed/interrupted."""
        return self.complete_search(
            search_id,
            total_results=0,
            api_calls_used=0,
            status="interrupted" if not error_msg else "failed",
        )

    def update_search_count(self, search_id: str, total_results: int) -> bool:
        """Update running result count mid-search (for live progress)."""
        if not self.available or not search_id:
            return False
        try:
            self.client.table("searches").update(
                {"total_results": total_results}
            ).eq("id", search_id).execute()
            return True
        except Exception:
            return False

    # =========================================================
    # RESULT STORAGE
    # =========================================================

    def save_results(self, search_id: str, results: list) -> int:
        """
        Save a batch of results to Supabase.
        Results should be dicts with keys matching the results table columns.
        Returns number of rows inserted.
        """
        if not self.available or not search_id or not results:
            return 0

        rows = []
        for r in results:
            row = {
                "search_id": search_id,
                "domain": r.get("domain"),
                "url": r.get("url"),
                "title": r.get("title"),
                "description": r.get("description"),
                "business_name": r.get("business_name"),
                "phone": r.get("phone"),
                "address": r.get("address"),
                "rating": r.get("rating"),
                "review_count": r.get("review_count"),
                "category": r.get("category"),
                "place_id": r.get("place_id"),
                "city": r.get("city"),
                "country": r.get("country"),
                "query": r.get("query"),
                "source": r.get("source", "search"),
                "position": r.get("position"),
            }
            # Remove None and empty-string values; convert numeric fields properly
            NUMERIC_FIELDS = {"rating", "review_count", "position"}
            cleaned = {}
            for k, v in row.items():
                if v is None or v == "":
                    continue
                if k in NUMERIC_FIELDS:
                    try:
                        cleaned[k] = float(v) if k == "rating" else int(v)
                    except (ValueError, TypeError):
                        continue
                else:
                    cleaned[k] = v
            rows.append(cleaned)

        # Insert in chunks of 100 with retry logic
        inserted = 0
        last_error = None
        chunk_size = 100
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            for attempt in range(1, 4):  # 3 retries per chunk
                try:
                    response = self.client.table("results").insert(chunk).execute()
                    inserted += len(response.data)
                    break  # success
                except Exception as e:
                    last_error = f"{type(e).__name__}: {e}"
                    print(f"[CloudStorage] save_results chunk {i} failed (attempt {attempt}/3): {last_error}")
                    if attempt < 3:
                        wait = 2 ** attempt
                        print(f"[CloudStorage] Retrying in {wait}s...")
                        time.sleep(wait)
                    else:
                        import traceback
                        traceback.print_exc()

        if last_error:
            self._last_save_error = last_error

        print(f"[CloudStorage] Saved {inserted}/{len(results)} results for {search_id}")
        return inserted

    # =========================================================
    # QUERYING
    # =========================================================

    def get_past_searches(self, limit: int = 20) -> list:
        """
        Return the most recent searches, newest first.
        """
        if not self.available:
            return []
        try:
            response = (
                self.client.table("searches")
                .select("*")
                .order("started_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"[CloudStorage] get_past_searches failed: {e}")
            return []

    def get_results(self, search_id: str, limit: int = 50000) -> list:
        """
        Fetch all results for a given search session.
        Paginates automatically since Supabase REST API returns max 1000 rows per request.
        """
        if not self.available or not search_id:
            return []
        try:
            all_data = []
            page_size = 1000
            offset = 0
            while offset < limit:
                fetch_size = min(page_size, limit - offset)
                response = (
                    self.client.table("results")
                    .select("*")
                    .eq("search_id", search_id)
                    .range(offset, offset + fetch_size - 1)
                    .execute()
                )
                batch = response.data
                all_data.extend(batch)
                if len(batch) < fetch_size:
                    break  # No more rows
                offset += fetch_size
            print(f"[CloudStorage] Fetched {len(all_data)} results for {search_id[:8]}")
            return all_data
        except Exception as e:
            print(f"[CloudStorage] get_results failed: {e}")
            return []

    def get_merged_results_as_csv(self, search_ids: list) -> str:
        """
        Fetch results from multiple search sessions and merge into a single
        deduplicated CSV. Useful when the same campaign was split across
        multiple runs (interrupted + resumed as new search).
        """
        all_results = []
        for sid in search_ids:
            all_results.extend(self.get_results(sid))

        if not all_results:
            return None

        # Reuse the same dedup/filter logic from get_results_as_csv
        BLOCKED_DOMAINS = {
            "facebook.com", "instagram.com", "tiktok.com", "linkedin.com",
            "twitter.com", "x.com", "youtube.com", "pinterest.com", "snapchat.com",
            "reddit.com", "quora.com", "medium.com", "substack.com",
            "wikipedia.org", "wikihow.com", "glassdoor.com", "indeed.com",
            "tripadvisor.com", "trustpilot.com", "yelp.com",
            "nytimes.com", "bbc.com", "bbc.co.uk", "reuters.com",
            "forbes.com", "bloomberg.com", "cnbc.com", "theguardian.com",
            "businessinsider.com", "techcrunch.com", "entrepreneur.com",
        }
        BLOCKED_SUFFIXES = (".gov", ".gov.uk", ".gov.au", ".gouv.fr", ".gob.es")

        seen_domains = set()
        unique_results = []
        for row in all_results:
            domain = (row.get("domain") or "").strip().lower()
            if not domain:
                continue
            if domain in BLOCKED_DOMAINS:
                continue
            if any(domain.endswith(sfx) for sfx in BLOCKED_SUFFIXES):
                continue
            if domain not in seen_domains:
                seen_domains.add(domain)
                unique_results.append(row)

        output = io.StringIO()
        fieldnames = [
            "domain", "url", "title", "description",
            "business_name", "phone", "address", "rating",
            "review_count", "category", "place_id",
            "city", "country", "query", "source", "position",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique_results)
        print(f"[CloudStorage] Merged {len(search_ids)} searches → {len(unique_results)} unique domains")
        return output.getvalue()

    def get_results_as_csv(self, search_id: str) -> Optional[str]:
        """
        Fetch results for a search and return as CSV string (for download).
        Deduplicates by domain before export.
        Returns None if unavailable or no results.
        """
        results = self.get_results(search_id)
        if not results:
            return None

        # Domains to filter out post-search (social media, news, forums, government)
        BLOCKED_DOMAINS = {
            "facebook.com", "instagram.com", "tiktok.com", "linkedin.com",
            "twitter.com", "x.com", "youtube.com", "pinterest.com", "snapchat.com",
            "reddit.com", "quora.com", "medium.com", "substack.com",
            "wikipedia.org", "wikihow.com", "glassdoor.com", "indeed.com",
            "tripadvisor.com", "trustpilot.com", "yelp.com",
            "nytimes.com", "bbc.com", "bbc.co.uk", "reuters.com",
            "forbes.com", "bloomberg.com", "cnbc.com", "theguardian.com",
            "businessinsider.com", "techcrunch.com", "entrepreneur.com",
        }
        BLOCKED_SUFFIXES = (".gov", ".gov.uk", ".gov.au", ".gouv.fr", ".gob.es")

        # Deduplicate by domain and filter blocked sites (keep first occurrence)
        seen_domains = set()
        unique_results = []
        for row in results:
            domain = (row.get("domain") or "").strip().lower()
            if not domain:
                continue
            if domain in BLOCKED_DOMAINS:
                continue
            if any(domain.endswith(sfx) for sfx in BLOCKED_SUFFIXES):
                continue
            if domain not in seen_domains:
                seen_domains.add(domain)
                unique_results.append(row)

        output = io.StringIO()
        fieldnames = [
            "domain", "url", "title", "description",
            "business_name", "phone", "address", "rating",
            "review_count", "category", "place_id",
            "city", "country", "query", "source", "position",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(unique_results)
        return output.getvalue()

    def get_completed_cities(self, search_id: str, source: str = None) -> set:
        """
        Return set of 'City, COUNTRY' strings already saved for this search.

        Args:
            search_id: The search session UUID
            source: If provided, only return cities that have results with this source
                    ('search' for Search API, 'maps' for Maps API).
                    If None, returns all cities regardless of source.
        """
        if not self.available or not search_id:
            return set()
        try:
            query = self.client.table("results").select("city, source").eq("search_id", search_id)
            if source:
                query = query.eq("source", source)
            response = query.execute()
            return {r["city"] for r in response.data if r.get("city")}
        except Exception as e:
            print(f"[CloudStorage] get_completed_cities failed: {e}")
            return set()

    def get_search_stats(self) -> dict:
        """Return aggregate stats: total searches, total results, etc."""
        if not self.available:
            return {}
        try:
            searches = self.client.table("searches").select("total_results, status").execute()
            total_searches = len(searches.data)
            total_results = sum(r.get("total_results") or 0 for r in searches.data)
            completed = sum(1 for r in searches.data if r.get("status") == "completed")
            return {
                "total_searches": total_searches,
                "total_results": total_results,
                "completed_searches": completed,
            }
        except Exception as e:
            print(f"[CloudStorage] get_search_stats failed: {e}")
            return {}
