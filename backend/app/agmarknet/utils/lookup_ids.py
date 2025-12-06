"""
lookup_ids.py
Utility to convert human-friendly names to Agmarknet metadata IDs.

Converts plain text values like "Maharashtra", "Cotton", "Akola" to their
corresponding IDs from metadata JSON files.
"""

import json
from pathlib import Path
from typing import Optional

# Resolve metadata directory path relative to this file
# __file__ is: backend/app/agmarknet/utils/lookup_ids.py
# parents[3] gives: backend/ (project root)
# Then: backend/app/agmarknet/metadata/
BASE_DIR = Path(__file__).resolve().parents[3]  # project root (backend/)
METADATA_DIR = BASE_DIR / "app" / "agmarknet" / "metadata"
DEFAULT_METADATA_DIR = str(METADATA_DIR)


def _load_json_file(path: Path) -> list:
    """Load JSON file and return as list."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class MetadataLookup:
    """
    Lookup utility to convert human-friendly names to Agmarknet IDs.
    
    Uses metadata JSON files to resolve:
    - State names → state_id
    - District names → district_id
    - Market names → market_id
    - Commodity names → commodity_id
    """
    
    def __init__(self, metadata_dir: Optional[str] = None):
        """
        Initialize MetadataLookup.
        
        Args:
            metadata_dir: Optional path to metadata directory. 
                         Defaults to app/agmarknet/metadata/
        """
        self.metadata_dir = Path(metadata_dir) if metadata_dir else Path(METADATA_DIR)
        
        # Expected metadata files
        self._files = {
            "states": "states.json",
            "districts": "districts.json",
            "markets": "markets.json",
            "commodities": "commodities.json",
            "grades": "grades.json",
        }
        
        self._data = {}
        self._load_all()
    
    def _load_all(self):
        """Load all metadata JSON files into memory."""
        for key, filename in self._files.items():
            filepath = self.metadata_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Metadata file not found: {filepath}")
            self._data[key] = _load_json_file(filepath)
    
    def get_state_id(self, name: str) -> int:
        """
        Get state ID from state name.
        
        Args:
            name: State name (e.g., "Maharashtra")
            
        Returns:
            State ID (integer)
            
        Raises:
            ValueError: If state not found
        """
        name_lower = name.strip().lower()
        
        for state in self._data["states"]:
            # Try common field names
            state_name = (
                state.get("state_name") or 
                state.get("name") or 
                state.get("state")
            )
            if state_name and state_name.lower() == name_lower:
                state_id = state.get("state_id") or state.get("id")
                if state_id:
                    return int(state_id)
        
        raise ValueError(f"State not found: {name}")
    
    def get_district_id(self, state_id: int, district_name: str) -> int:
        """
        Get district ID from district name and state ID.
        
        Args:
            state_id: State ID (integer) - used for validation if present in metadata
            district_name: District name (e.g., "Akola")
            
        Returns:
            District ID (integer)
            
        Raises:
            ValueError: If district not found
        """
        district_lower = district_name.strip().lower()
        
        for district in self._data["districts"]:
            # Check if district belongs to the specified state (if state_id field exists)
            dist_state_id = district.get("state_id") or district.get("state")
            if dist_state_id is not None and dist_state_id != state_id:
                continue
            
            # Try common field names
            dist_name = (
                district.get("district_name") or 
                district.get("name") or 
                district.get("district")
            )
            if dist_name and dist_name.lower() == district_lower:
                district_id = district.get("district_id") or district.get("id")
                if district_id:
                    return int(district_id)
        
        raise ValueError(f"District '{district_name}' not found in state ID {state_id}")
    
    def get_market_id(self, state_id: int, district_id: int, market_name: str) -> int:
        """
        Get market ID from market name, state ID, and district ID.
        
        Args:
            state_id: State ID (integer)
            district_id: District ID (integer)
            market_name: Market name (e.g., "Akola APMC")
            
        Returns:
            Market ID (integer)
            
        Raises:
            ValueError: If market not found
        """
        market_lower = market_name.strip().lower()
        
        for market in self._data["markets"]:
            # Check if market belongs to the specified state and district
            mkt_state_id = market.get("state_id") or market.get("state")
            mkt_district_id = market.get("district_id") or market.get("district")
            
            if mkt_state_id != state_id or mkt_district_id != district_id:
                continue
            
            # Try common field names
            mkt_name = (
                market.get("mkt_name") or 
                market.get("market_name") or 
                market.get("name") or
                market.get("mkt")
            )
            if mkt_name and mkt_name.lower() == market_lower:
                market_id = market.get("id") or market.get("market_id")
                if market_id:
                    return int(market_id)
        
        raise ValueError(
            f"Market '{market_name}' not found in state ID {state_id}, district ID {district_id}"
        )
    
    def get_commodity_id(self, name: str) -> int:
        """
        Get commodity ID from commodity name.
        
        Args:
            name: Commodity name (e.g., "Cotton")
            
        Returns:
            Commodity ID (integer)
            
        Raises:
            ValueError: If commodity not found
        """
        name_lower = name.strip().lower()
        
        for commodity in self._data["commodities"]:
            # Try common field names
            cmdt_name = (
                commodity.get("cmdt_name") or 
                commodity.get("commodity_name") or 
                commodity.get("name")
            )
            if cmdt_name and cmdt_name.lower() == name_lower:
                cmdt_id = commodity.get("cmdt_id") or commodity.get("id")
                if cmdt_id:
                    return int(cmdt_id)
        
        raise ValueError(f"Commodity not found: {name}")

