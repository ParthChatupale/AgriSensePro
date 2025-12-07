"""
Daily Price & Arrival Fetcher
Agmarknet Tier-1 API Wrapper
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from app.agmarknet.utils.http_client import http_get

BASE_URL = "https://api.agmarknet.gov.in/v1/daily-price-arrival/report"


class DailyPriceArrivalFetcher:
    """
    Fetches daily price/arrival/both data from Agmarknet API.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # PUBLIC METHOD
    # ---------------------------------------------------------
    def fetch(
        self,
        from_date: str,
        to_date: str,
        state: int,
        district: int,
        commodity: int,
        market: Optional[List[int]] = None,
        grade: Optional[List[int]] = None,
        variety: Optional[List[int]] = None,
        download_excel: bool = False,
    ):
        """
        Fetches daily price-arrival data.

        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            state: State ID (integer)
            district: District ID (integer)
            commodity: Commodity ID (integer)
            market: List of market IDs (optional, defaults to empty list)
            grade: List of grade IDs (optional, defaults to empty list)
            variety: List of variety IDs (optional, defaults to empty list)
            download_excel: If True, download Excel file to /tmp

        Returns:
            success(bool), data(dict or str), message(str)
        """

        print("\n📌 Preparing request for Daily Price/Arrival API...\n")

        # Default empty lists if None
        market = market if market is not None else []
        grade = grade if grade is not None else []
        variety = variety if variety is not None else []

        # Build parameters matching Agmarknet API format
        params = {
            "from_date": from_date,
            "to_date": to_date,
            "data_type": 100006,  # "Both" (price + arrival)
            "group": 4,  # Fibre Crops group
            "commodity": commodity,
            "state": state,
            "district": json.dumps([district]),  # JSON-encoded array
            "market": json.dumps(market) if market else json.dumps([]),  # JSON-encoded array
            "grade": json.dumps(grade) if grade else json.dumps([]),  # JSON-encoded array
            "variety": json.dumps(variety) if variety else json.dumps([]),  # JSON-encoded array
            "download": "true" if download_excel else "false",
            "download_type": "excel" if download_excel else "",
        }

        print("➡ Calling API:")
        print(BASE_URL)
        print("\n➡ With parameters:")
        for k, v in params.items():
            print(f"  {k}: {v}")

        # ---------------------------------------------------------
        # MAKE REQUEST
        # ---------------------------------------------------------
        ok, response = http_get(BASE_URL, params=params)

        if not ok:
            return False, None, f"API Request Failed → {response}"

        # ---------------------------------------------------------
        # Handle Excel (binary) - save to /tmp
        # ---------------------------------------------------------
        if download_excel:
            if isinstance(response, bytes):
                # Generate filename
                filename = f"daily_price_arrival_{from_date}_{to_date}.xlsx"
                filepath = Path("/tmp") / filename
                
                # Ensure /tmp exists
                os.makedirs("/tmp", exist_ok=True)
                
                # Save file
                with open(filepath, "wb") as f:
                    f.write(response)
                
                return True, str(filepath), f"Excel file saved to {filepath}"
            else:
                return False, None, "Expected binary Excel data but received different format"

        # ---------------------------------------------------------
        # Handle JSON response
        # ---------------------------------------------------------
        if isinstance(response, dict):
            if not response.get("status"):
                return False, None, f"API Error: {response.get('message')}"
            return True, response.get("data", []), "Data fetched successfully."

        return False, None, "Unexpected response format."

