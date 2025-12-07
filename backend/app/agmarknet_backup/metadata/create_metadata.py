import json
import re
from pathlib import Path
from collections import Counter

DISTRICTS_FILE = Path("districts.json")

def clean_text(name: str) -> str:
    """
    Convert market name into a probable district name.
    """
    # Step 1: Strip "APMC" and anything after
    name = name.split("APMC")[0].strip()

    # Step 2: Remove parentheses
    name = re.sub(r"\(.*?\)", "", name)

    # Step 3: Remove multiple spaces
    name = re.sub(r"\s+", " ", name)

    # Step 4: Remove generic words
    blacklist = [
        "Krushi", "Krishi", "Market", "Agro", "Agriculture",
        "Private", "Produce", "Utpanna", "Bazar", "Bazaar",
        "Farm", "Company", "Co", "Ltd", "Limited", "Khajgi",
        "Samiti", "Yard"
    ]
    tokens = [t for t in name.split() if t not in blacklist]
    name = " ".join(tokens).strip()

    # Step 5: Title case
    return name.title()


def main():
    print("🔍 Loading districts.json...")
    districts = json.loads(DISTRICTS_FILE.read_text())

    updated = []

    for d in districts:
        district_id = d["district_id"]
        market_names = [m["mkt_name"] for m in d["markets"]]

        # Clean each market name into a candidate district name
        candidates = [clean_text(m) for m in market_names if clean_text(m)]

        if not candidates:
            district_name = f"District {district_id}"
        else:
            # Use the MOST FREQUENT candidate
            district_name = Counter(candidates).most_common(1)[0][0]

        print(f"✔ district_id={district_id} → {district_name}")

        updated.append({
            "district_id": district_id,
            "district_name": district_name,
            "markets": d["markets"]
        })

    # Save updated version
    DISTRICTS_FILE.write_text(json.dumps(updated, indent=2, ensure_ascii=False))
    print("\n🎉 districts.json updated with district_name for all entries!")

if __name__ == "__main__":
    main()
