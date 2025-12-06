"""
Daily Price Arrival Fetcher Test Script
"""

from app.agmarknet.fetchers.daily_price_arrival_fetcher import DailyPriceArrivalFetcher

fetcher = DailyPriceArrivalFetcher()

# ===== VALID TEST INPUTS =====
params = {
    "from_date": "2025-12-01",
    "to_date": "2025-12-02",
    "state": 20,               # Maharashtra
    "district": [338],         # Ahilyanagar
    "commodity": 15,           # Cotton
    "market": [100002],        # All markets
    "grade": [100003],         # All grades
    "variety": [],             # Let API auto-select
    "download_excel": False
}

print("\n==============================")
print("➡ Calling Agmarknet API")
print("==============================")
for key, value in params.items():
    print(f"{key}: {value}")

print("\n==============================")
print("➡ Fetching...")
print("==============================")

try:
    result = fetcher.fetch(
        from_date=params["from_date"],
        to_date=params["to_date"],
        state=params["state"],
        district=params["district"],
        commodity=params["commodity"],
        market=params["market"],
        grade=params["grade"],
        variety=params["variety"],
        download_excel=params["download_excel"],
    )

    print("\n==============================")
    print("➡ API Response:")
    print("==============================")
    print(result)

except Exception as e:
    print("\n❌ ERROR OCCURRED:")
    print(str(e))
