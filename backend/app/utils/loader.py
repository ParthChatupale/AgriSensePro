import json
import os
from functools import lru_cache

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CROP_METADATA_FILE = os.path.join(DATA_DIR, "crops_metadata.json")


@lru_cache(maxsize=1)
def load_crop_metadata() -> dict:
    """Load crop metadata from JSON with caching."""
    if not os.path.exists(CROP_METADATA_FILE):
        return {}
    with open(CROP_METADATA_FILE, "r", encoding="utf-8") as fp:
        return json.load(fp)
