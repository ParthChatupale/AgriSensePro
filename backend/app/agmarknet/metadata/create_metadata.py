"""
create_metadata.py
Extracts:
- commodities (only your selected 6)
- states (only Maharashtra)
- markets for Maharashtra
- district → markets mapping
- all grade mappings
"""

import json
from pathlib import Path

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------
MASTER_FILE = Path("agMeta.txt")
OUT_DIR = Path("agmarknet/metadata")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_STATE_ID = 20  # Maharashtra

# your 6 crops
TARGET_COMMODITIES = {
    15: "Cotton",
    1: "Wheat",
    3: "Rice",
    122: "Sugarcane",
    13: "Soybean",
    23: "Onion",
}


# --------------------------------------------------------------------
# LOAD MASTER JSON
# --------------------------------------------------------------------
def load_master():
    raw = MASTER_FILE.read_text(encoding="utf-8")
    root = json.loads(raw)

    if "data" not in root:
        raise RuntimeError("Missing `data` key in master file")

    return root["data"]


# --------------------------------------------------------------------
# PROCESS AND SAVE FILES
# --------------------------------------------------------------------
def write_json(name, data):
    path = OUT_DIR / name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✔ wrote {name} ({len(data)} records)")


def build_metadata(data):

    # -------------------------------------------
    # STATES → only Maharashtra
    # -------------------------------------------
    states = data["state_data"]
    mh_state = [s for s in states if s["state_id"] == TARGET_STATE_ID]
    write_json("states.json", mh_state)

    # -------------------------------------------
    # MARKETS → only Maharashtra
    # -------------------------------------------
    markets = data["market_data"]
    mh_markets = [m for m in markets if m["state_id"] == TARGET_STATE_ID]
    write_json("markets.json", mh_markets)

    # -------------------------------------------
    # DISTRICTS → build district → markets mapping
    # -------------------------------------------
    district_map = {}

    for m in mh_markets:
        d = m["district_id"]
        if d not in district_map:
            district_map[d] = {
                "district_id": d,
                "markets": []
            }
        district_map[d]["markets"].append({
            "id": m["id"],
            "mkt_name": m["mkt_name"]
        })

    districts = list(district_map.values())
    write_json("districts.json", districts)

    # -------------------------------------------
    # COMMODITIES → only your 6 required
    # -------------------------------------------
    cmdts = data["cmdt_data"]
    selected = []

    for c in cmdts:
        cid = c["cmdt_id"]
        if cid in TARGET_COMMODITIES:
            selected.append({
                "cmdt_id": cid,
                "cmdt_name": TARGET_COMMODITIES[cid],
                "cmdt_group_id": c["cmdt_group_id"]
            })

    write_json("commodities.json", selected)

    # -------------------------------------------
    # GRADES → store FULL grade list (unchanged)
    # -------------------------------------------
    grades = data["grade_data"]
    write_json("grades.json", grades)

    print("\n✔ ALL METADATA FILES GENERATED SUCCESSFULLY\n")


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------
if __name__ == "__main__":
    data = load_master()
    build_metadata(data)
