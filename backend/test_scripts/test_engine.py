#!/usr/bin/env python3
"""
test_engine.py
Standalone tester to validate rules against mock_real_data.json and crops_metadata.json
Place under backend/test_scripts/ and run: python test_scripts/test_engine.py
"""

import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]  # backend/
DATA_DIR = ROOT / "data"
RULES_DIR = ROOT / "rules"

# file paths (adjust if your layout differs)
MOCK_FILE = DATA_DIR / "mock_real_data.json"
CROPS_META = DATA_DIR / "crops_metadata.json"
PEST_RULES = RULES_DIR / "pest_rules.json"
IRR_RULES = RULES_DIR / "irrigation_rules.json"
MARKET_RULES = RULES_DIR / "market_rules.json"

OPS = {
    ">": lambda a, b: a is not None and a > b,
    "<": lambda a, b: a is not None and a < b,
    ">=": lambda a, b: a is not None and a >= b,
    "<=": lambda a, b: a is not None and a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "abs_gte": lambda a, b: a is not None and abs(a) >= b
}

def load_json(path: Path):
    if not path.exists():
        print(f"[ERROR] Missing: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_condition(feature_values, cond):
    feat = cond.get("feature")
    op = cond.get("op")
    val = cond.get("value")
    # feature might be nested, e.g., ndvi_change, temperature etc.
    feat_val = feature_values.get(feat)
    # if feature not present, return False (graceful)
    if feat_val is None:
        return False
    func = OPS.get(op)
    if not func:
        return False
    try:
        return func(feat_val, val)
    except Exception:
        return False

def evaluate_rule(rule, features):
    # rule["conditions"] is list of conditions; require all to be True
    conds = rule.get("conditions", [])
    for c in conds:
        if not evaluate_condition(features, c):
            return False
    return True

def make_features(location_record):
    """
    normalize feature dict used by rules evaluation
    """
    features = {}
    # weather
    weather = location_record.get("weather", {})
    features["temperature"] = weather.get("temperature")
    features["humidity"] = weather.get("humidity")
    features["rainfall"] = weather.get("rainfall")
    features["wind_speed"] = weather.get("wind_speed")
    # crop health
    ch = location_record.get("crop_health", {})
    features["ndvi"] = ch.get("ndvi")
    features["ndvi_change"] = ch.get("ndvi_change")
    features["soil_moisture"] = ch.get("soil_moisture")
    features["crop_stage_days"] = ch.get("crop_stage_days")
    # market
    market = location_record.get("market", {})
    features["price"] = market.get("price")
    features["price_change_percent"] = market.get("price_change_percent")
    # crop stage string is not always present; some rules may reference crop_stage
    # If 'crop_stage_days' exists and metadata is available you can map to stage later.
    return features

def run_test():
    mock = load_json(MOCK_FILE)
    crops_meta = load_json(CROPS_META)
    pest_rules = load_json(PEST_RULES)
    irr_rules = load_json(IRR_RULES)
    market_rules = load_json(MARKET_RULES)

    if not mock:
        print("Mock data missing, aborting.")
        return

    locations = mock.get("locations", [])
    results = []

    for loc in locations:
        features = make_features(loc)
        crop_key = loc.get("crop_health", {}).get("crop")
        state = loc.get("state")
        district = loc.get("district")
        ts = loc.get("timestamp")
        advisory = {
            "state": state,
            "district": district,
            "crop": crop_key,
            "timestamp": ts,
            "fired_rules": [],
            "recommendations": [],
            "rule_scores": {"pest": 0.0, "irrigation": 0.0, "market": 0.0}
        }

        # evaluate pest rules
        for k, r in (pest_rules or {}).items():
            if evaluate_rule(r, features):
                advisory["fired_rules"].append(r.get("description", k))
                advisory["recommendations"].append({"rec": r.get("recommendation"), "severity": r.get("severity")})
                advisory["rule_scores"]["pest"] = max(advisory["rule_scores"]["pest"], r.get("score", 0.0))

        # irrigation
        for k, r in (irr_rules or {}).items():
            if evaluate_rule(r, features):
                advisory["fired_rules"].append(r.get("description", k))
                advisory["recommendations"].append({"rec": r.get("recommendation"), "severity": r.get("severity")})
                advisory["rule_scores"]["irrigation"] = max(advisory["rule_scores"]["irrigation"], r.get("score", 0.0))

        # market
        for k, r in (market_rules or {}).items():
            if evaluate_rule(r, features):
                advisory["fired_rules"].append(r.get("description", k))
                advisory["recommendations"].append({"rec": r.get("recommendation"), "severity": r.get("severity")})
                advisory["rule_scores"]["market"] = max(advisory["rule_scores"]["market"], r.get("score", 0.0))

        # compute a simple combined rule_score
        # weight pest=0.5, irrigation=0.3, market=0.2 (example)
        combined_score = (
            advisory["rule_scores"]["pest"] * 0.5 +
            advisory["rule_scores"]["irrigation"] * 0.3 +
            advisory["rule_scores"]["market"] * 0.2
        )
        advisory["combined_score"] = round(combined_score, 2)
        results.append(advisory)

    # Print a compact report
    print("=== Fusion Engine Mock Test Report ===")
    print(f"Generated at: {mock.get('meta', {}).get('generated_at')}\n")
    for a in results:
        print(f"Location: {a['state']} / {a['district']}  Crop: {a['crop']}  TS: {a['timestamp']}")
        print(f"  Combined Score: {a['combined_score']}")
        if a["fired_rules"]:
            print("  Fired Rules:")
            for fr in a["fired_rules"]:
                print(f"    - {fr}")
            print("  Recommendations:")
            for rec in a["recommendations"]:
                print(f"    - ({rec['severity']}) {rec['rec']}")
        else:
            print("  No rules fired. Status: OK.")
        print("-" * 60)

if __name__ == "__main__":
    run_test()
