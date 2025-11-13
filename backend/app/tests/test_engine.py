"""Quick manual test for the Fusion Engine metadata helpers."""
from __future__ import annotations

import json
import os
import sys
from pprint import pprint

CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.fusion_engine import build_advisory_from_features  # type: ignore  # pylint: disable=wrong-import-position
from app.utils.loader import load_crop_metadata  # type: ignore  # pylint: disable=wrong-import-position

DATA_FILE = os.path.join(BACKEND_DIR, "data", "mock_test.json")


def main() -> None:
    crop_meta = load_crop_metadata()
    with open(DATA_FILE, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    for crop, features in payload.items():
        print(f"\n=== Testing {crop.upper()} ===")
        meta = crop_meta.get(crop, {})
        if not meta:
            print("No metadata found; skipping")
            continue

        advisory_fields, score, fired, breakdown = build_advisory_from_features(crop, features)
        print("Score:", score)
        print("Summary:", advisory_fields["summary"])
        print("Severity:", advisory_fields["severity"])
        print("Alerts:")
        pprint(advisory_fields["alerts"])
        print("Metrics:")
        pprint(advisory_fields["metrics"])
        print("Rules fired:")
        pprint(fired)
        print("Breakdown:")
        pprint(breakdown)


if __name__ == "__main__":  # pragma: no cover
    main()
