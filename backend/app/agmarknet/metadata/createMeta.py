import json
import re
from collections import Counter
from pathlib import Path

AG_META_FILE = Path("agMeta.txt")                     # Your full metadata dump
OUTPUT_FILE = Path("districts.json")                 # Destination

def clean_name(name: str) -> str:
    """Extract base district name from market name."""
    # Remove suffix "APMC" and all text after it
    name = name.split("APMC")[0].strip()

    # Remove parentheses and contents
    name = re.sub(r"\(.*?\)", "", name)

    # Remove multiple spaces
    name = re.sub(r"\s+", " ", name)

    # Remove common words
    remove_words = [
        "Market", "Krishi", "Agriculture", "Agro", "Private",
        "Produce", "Utappan", "Utpan", "Bazaar", "Bazar",
        "Farm", "Yard", "Samiti", "Ltd", "Limited", "CoOp"
    ]

    tokens = [t for t in name.split() if t not in remove_words]
    cleaned = " ".join(tokens).strip()

    # Title case
    return cleaned.title()

def main():
    print("🔍 Loading agMeta...")
    raw = AG_META_FILE.read_text()
    data = json.loads(raw)

    districts_raw = data["district_data"]       # Your copy has district_id + markets
    fixed_output = []

    for district in districts_raw:
        district_id = district["district_id"]
        markets = district["markets"]

        cleaned_candidates = []

        for m in markets:
            cname = clean_name(m["mkt_name"])
            if cname:
                cleaned_candidates.append(cname)

        if not cleaned_candidates:
            district_name = f"District-{district_id}"
        else:
            # Most frequent cleaned name → strongest district identity
            district_name = Counter(cleaned_candidates).most_common(1)[0][0]

        fixed_output.append({
            "district_id": district_id,
            "district_name": district_name,
            "markets": markets
        })

        print(f"✔ {district_id} → {district_name}")

    # Save new districts.json
    OUTPUT_FILE.write_text(json.dumps(fixed_output, indent=2, ensure_ascii=False))
    print("\n🎉 Completed: districts.json has been rebuilt with district names!")

if __name__ == "__main__":
    main()
