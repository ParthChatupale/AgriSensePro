"""
lookup.py
Utility to resolve human-friendly names (state, district, market, commodity, grade)
to the IDs present in the metadata JSON files that you generated.

Usage (examples at bottom) show how to call functions programmatically or via CLI.
No network calls. Uses only local JSON files under app/agmarknet/metadata/.
"""

import json
import os
import argparse
from pathlib import Path
from difflib import get_close_matches
from typing import List, Dict, Any, Optional

# Resolve metadata directory path relative to this file
# __file__ is: backend/app/agmarknet/utils/lookup.py
# parents[3] gives: backend/ (directory containing app/)
# Then: backend/app/agmarknet/metadata/
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
METADATA_DIR = BASE_DIR / "app" / "agmarknet" / "metadata"
DEFAULT_METADATA_DIR = str(METADATA_DIR)

def _load_json_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class MetadataLookup:
    def __init__(self, metadata_dir: Optional[str] = None):
        self.metadata_dir = metadata_dir or DEFAULT_METADATA_DIR
        # expected files (adjust names if your create_metadata.py emits different filenames)
        self._files = {
            "states": "states.json",
            "districts": "districts.json",
            "markets": "markets.json",
            "commodities": "commodities.json",
            "grades": "grades.json",
        }
        self._data = {}
        self._load_all()

    def _full_path(self, key: str) -> str:
        return str(Path(self.metadata_dir) / self._files[key])

    def _load_all(self):
        for key, fname in self._files.items():
            p = Path(self.metadata_dir) / fname
            if not p.exists():
                raise FileNotFoundError(f"Metadata file not found: {p}")
            self._data[key] = _load_json_file(str(p))

    # -------------------------
    # Generic helpers
    # -------------------------
    def _search_by_key(self, collection: str, key_name: str, query: str, n: int = 5) -> List[Dict[str, Any]]:
        """Return items whose key_name best matches query. Uses case-insensitive substring match first,
           then difflib close matches if none found."""
        q = query.strip().lower()
        items = self._data.get(collection, [])
        # exact substring matches (preferred)
        subs = [it for it in items if key_name in it and q in str(it[key_name]).lower()]
        if subs:
            return subs
        # else try fuzzy on the key values
        candidates = [str(it.get(key_name, "")) for it in items]
        close = get_close_matches(query, candidates, n=n, cutoff=0.6)
        results = [it for it in items if str(it.get(key_name, "")) in close]
        return results

    # -------------------------
    # Specific lookups
    # -------------------------
    def find_state(self, name: str) -> List[Dict[str, Any]]:
        """Return matching state objects (with state_id and state_name)."""
        # varying metadata may use 'state_name' or 'name' field; try both
        items = self._data["states"]
        # try common field names:
        for field in ("state_name", "name", "state"):
            found = [it for it in items if field in it and name.strip().lower() in str(it[field]).lower()]
            if found:
                return found
        # fallback fuzzy
        return self._search_by_key("states", "state_name", name)

    def find_commodity(self, name: str) -> List[Dict[str, Any]]:
        items = self._data["commodities"]
        for field in ("cmdt_name", "commodity_name", "name"):
            found = [it for it in items if field in it and name.strip().lower() in str(it[field]).lower()]
            if found:
                return found
        return self._search_by_key("commodities", "cmdt_name", name)

    def find_district(self, state_id: Optional[int], name: str) -> List[Dict[str, Any]]:
        items = self._data["districts"]
        q = name.strip().lower()
        if state_id is not None:
            found = [it for it in items if (it.get("state_id") == state_id or it.get("state") == state_id) and q in str(it.get("district_name", "")).lower()]
            if found:
                return found
        # fallback to global search
        for field in ("district_name", "name"):
            found = [it for it in items if field in it and q in str(it[field]).lower()]
            if found:
                return found
        return self._search_by_key("districts", "district_name", name)

    def find_markets(self, state_id: Optional[int]=None, district_id: Optional[int]=None, name: Optional[str]=None) -> List[Dict[str, Any]]:
        items = self._data["markets"]
        results = items
        if state_id is not None:
            results = [it for it in results if it.get("state_id") == state_id or it.get("state") == state_id]
        if district_id is not None:
            # some metadata uses 'district_id' others 'district'
            results = [it for it in results if (it.get("district_id") == district_id or it.get("district") == district_id)]
        if name:
            q = name.strip().lower()
            results = [it for it in results if q in str(it.get("mkt_name", it.get("market_name", it.get("mkt", "")))).lower()]
        return results

    def find_grade(self, commodity_id: Optional[int]=None, grade_name: Optional[str]=None) -> List[Dict[str, Any]]:
        items = self._data["grades"]
        res = items
        if commodity_id is not None:
            # sometimes grade entries have cmdt_id lists or cmdt_id single
            def matches_cmdt(it):
                v = it.get("cmdt_id")
                if isinstance(v, list):
                    return commodity_id in v
                return v == commodity_id
            res = [it for it in res if matches_cmdt(it)]
        if grade_name:
            q = grade_name.strip().lower()
            res = [it for it in res if q in str(it.get("grade_name", "")).lower()]
        return res

# -------------------------
# CLI convenience
# -------------------------
def pretty_print_hits(items: List[Dict[str, Any]], limit: int = 10):
    if not items:
        print("  -> No matches found.")
        return
    for i, it in enumerate(items[:limit], start=1):
        print(f"  {i}. {json.dumps(it, ensure_ascii=False)}")
    if len(items) > limit:
        print(f"  ... {len(items)-limit} more matches")

def cli():
    parser = argparse.ArgumentParser(description="Lookup IDs in metadata JSON (states, commodities, districts, markets, grades).")
    parser.add_argument("--metadata-dir", type=str, default=None, help="Path to metadata folder (contains states.json etc).")
    parser.add_argument("--state", type=str, help="State name to look up.")
    parser.add_argument("--commodity", type=str, help="Commodity name to look up.")
    parser.add_argument("--district", type=str, help="District name to look up (works better with --state-id).")
    parser.add_argument("--state-id", type=int, help="State ID to narrow district/market search.")
    parser.add_argument("--district-id", type=int, help="District ID to narrow market search.")
    parser.add_argument("--market-name", type=str, help="Market name substring to search.")
    parser.add_argument("--grade", type=str, help="Grade name to search.")
    args = parser.parse_args()

    L = MetadataLookup(args.metadata_dir)
    print(f"Using metadata_dir: {L.metadata_dir}\n")

    if args.state:
        print(f"Searching state for: {args.state}")
        hits = L.find_state(args.state)
        pretty_print_hits(hits)
    if args.commodity:
        print(f"\nSearching commodity for: {args.commodity}")
        hits = L.find_commodity(args.commodity)
        pretty_print_hits(hits)
    if args.district:
        print(f"\nSearching district for: {args.district} (state_id={args.state_id})")
        hits = L.find_district(args.state_id, args.district)
        pretty_print_hits(hits)
    if args.market_name or args.state_id or args.district_id:
        print(f"\nSearching markets (state_id={args.state_id}, district_id={args.district_id}, name={args.market_name})")
        hits = L.find_markets(state_id=args.state_id, district_id=args.district_id, name=args.market_name)
        pretty_print_hits(hits, limit=20)
    if args.grade:
        print(f"\nSearching grade for: {args.grade} (commodity_id not provided)")
        hits = L.find_grade(grade_name=args.grade)
        pretty_print_hits(hits)

if __name__ == "__main__":
    cli()
