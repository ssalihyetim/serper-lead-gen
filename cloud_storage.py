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
            # Remove None values to let DB use defaults
            row = {k: v for k, v in row.items() if v is not None}
            rows.append(row)

        # Insert in chunks of 500 to avoid payload limits
        inserted = 0
        chunk_size = 500
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            try:
                response = self.client.table("results").insert(chunk).execute()
                inserted += len(response.data)
            except Exception as e:
                print(f"[CloudStorage] save_results chunk {i} failed: {e}")

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
        """
        if not self.available or not search_id:
            return []
        try:
            response = (
                self.client.table("results")
                .select("*")
                .eq("search_id", search_id)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"[CloudStorage] get_results failed: {e}")
            return []

    def get_results_as_csv(self, search_id: str) -> Optional[str]:
        """
        Fetch results for a search and return as CSV string (for download).
        Returns None if unavailable or no results.
        """
        results = self.get_results(search_id)
        if not results:
            return None

        output = io.StringIO()
        fieldnames = [
            "domain", "url", "title", "description",
            "business_name", "phone", "address", "rating",
            "review_count", "category", "place_id",
            "city", "country", "query", "source", "position",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()

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
