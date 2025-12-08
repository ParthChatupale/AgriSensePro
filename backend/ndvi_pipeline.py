#!/usr/bin/env python3
import os
import math
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv

from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    MimeType,
    CRS,
    BBox,
    DataCollection
)

from scipy.ndimage import zoom   # For visual upscaling

# --- Load ENV ---
load_dotenv()

CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID") or os.getenv("SENTINELHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET") or os.getenv("SENTINELHUB_CLIENT_SECRET")
INSTANCE_ID = os.getenv("SENTINEL_INSTANCE_ID") or os.getenv("SENTINELHUB_INSTANCE_ID", None)

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing SentinelHub credentials in .env")

config = SHConfig()
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
if INSTANCE_ID:
    config.instance_id = INSTANCE_ID

# --- Defaults ---
DEFAULT_RADIUS_M = 250         # your selected value
DEFAULT_DAYS_LOOKBACK = 7
OUTPUT_DIR = "output/ndvi"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Utility functions ---
def meters_to_deg_lat(m):
    return m / 111320.0

def meters_to_deg_lon(m, lat_deg):
    return m / (111320.0 * math.cos(math.radians(lat_deg)))

def build_bbox(lat, lon, radius_m):
    dlat = meters_to_deg_lat(radius_m)
    dlon = meters_to_deg_lon(radius_m, lat)
    return BBox(
        bbox=[lon - dlon, lat - dlat, lon + dlon, lat + dlat],
        crs=CRS.WGS84
    )

def compute_size_pixels(radius_m, resolution_m=10):
    side_m = radius_m * 2
    pix = int(math.ceil(side_m / resolution_m))
    return pix, pix

# Keep only vegetation pixels in SCL
VALID_SCL = {4}

EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "SCL"],
    output: { bands: 3, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  return [s.B04, s.B08, s.SCL];
}
"""

# --- Fetch B04, B08, SCL ---
def fetch_bands(lat, lon, radius_m=DEFAULT_RADIUS_M, date=None):
    bbox = build_bbox(lat, lon, radius_m)
    size = compute_size_pixels(radius_m, resolution_m=10)

    if date:
        t_from = date
        t_to = date
    else:
        today = datetime.utcnow().date()
        from_dt = today - timedelta(days=DEFAULT_DAYS_LOOKBACK)
        t_from = from_dt.strftime("%Y-%m-%d")
        t_to = today.strftime("%Y-%m-%d")

    request = SentinelHubRequest(
        evalscript=EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=(t_from, t_to)
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox,
        size=size,
        config=config,
    )

    print(f"[INFO] Fetching satellite data for bbox={bbox}, size={size} ...")
    data = request.get_data()
    if not data:
        raise RuntimeError("No satellite data returned")

    arr = data[0]  # H, W, 3
    red = arr[:, :, 0].astype("float32")
    nir = arr[:, :, 1].astype("float32")
    scl = arr[:, :, 2].astype("int32")
    return red, nir, scl, bbox

# --- NDVI ---
def compute_ndvi(red, nir):
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red + 1e-6)
    return np.clip(ndvi, -1, 1)

# --- Mask ---
def apply_scl_mask(ndvi, scl):
    mask = np.isin(scl, list(VALID_SCL))
    ndvi_masked = np.where(mask, ndvi, np.nan)
    return ndvi_masked, mask

# --- Visual upscale ---
def upscale_for_display(ndvi, upscale_factor=10):
    """
    Creates a smooth display-friendly version of NDVI.
    Only for visualization — NOT for analytics.
    """
    return zoom(ndvi, upscale_factor, order=3)

# --- Save helpers ---
def save_png(arr, path, cmap="RdYlGn", vmin=-1, vmax=1, alpha_mask=None):
    plt.figure(figsize=(8, 8))
    if alpha_mask is not None:
        rgba = plt.cm.get_cmap(cmap)((arr - vmin) / (vmax - vmin))
        rgba[..., 3] = np.where(alpha_mask, 1.0, 0.0)
        plt.imshow(rgba)
    else:
        plt.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label="NDVI")
    plt.axis("off")
    plt.savefig(path, bbox_inches="tight", dpi=150)
    plt.close()

def write_stats(ndvi, out_path):
    stats = {
        "min": float(np.nanmin(ndvi)),
        "max": float(np.nanmax(ndvi)),
        "mean": float(np.nanmean(ndvi)),
        "valid_pixels": int(np.sum(~np.isnan(ndvi))),
        "total_pixels": int(ndvi.size)
    }
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)
    return stats

# --- Main ---
def run_ndvi(lat, lon, radius_m=DEFAULT_RADIUS_M, date=None, out_prefix="ndvi"):
    # Fetch spectral bands
    red, nir, scl, bbox = fetch_bands(lat, lon, radius_m, date)
    print("[INFO] Bands downloaded.")

    # Compute NDVI
    ndvi = compute_ndvi(red, nir)

    # Native (10m)
    ndvi_native = ndvi.copy()

    # Masked NDVI (cloud/vegetation filtering)
    ndvi_masked, mask = apply_scl_mask(ndvi_native, scl)

    # Visual upscale
    ndvi_visual = upscale_for_display(ndvi_native, upscale_factor=10)

    # Save raw arrays
    np.save(os.path.join(OUTPUT_DIR, f"{out_prefix}_raw.npy"), ndvi_native)
    np.save(os.path.join(OUTPUT_DIR, f"{out_prefix}_masked_raw.npy"), ndvi_masked)
    np.save(os.path.join(OUTPUT_DIR, f"{out_prefix}_visual.npy"), ndvi_visual)

    # Save images
    save_png(ndvi_native, os.path.join(OUTPUT_DIR, f"{out_prefix}_native.png"))
    save_png(ndvi_masked, os.path.join(OUTPUT_DIR, f"{out_prefix}_masked.png"), alpha_mask=mask)
    save_png(ndvi_visual, os.path.join(OUTPUT_DIR, f"{out_prefix}_visual.png"))

    # Write stats for masked NDVI
    stats = write_stats(ndvi_masked, os.path.join(OUTPUT_DIR, f"{out_prefix}_stats.json"))

    print("\n=== NDVI OUTPUTS ===")
    print("Native (10m):        ", f"{out_prefix}_native.png")
    print("Masked NDVI:         ", f"{out_prefix}_masked.png")
    print("Visual NDVI:         ", f"{out_prefix}_visual.png")
    print("Raw NDVI array:      ", f"{out_prefix}_raw.npy")
    print("Visual NDVI array:   ", f"{out_prefix}_visual.npy")
    print("Stats JSON:          ", f"{out_prefix}_stats.json")
    print("=====================\n")

    print(json.dumps(stats, indent=2))
    return stats

# --- CLI ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automatic NDVI pipeline for Sentinel-2.")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS_M)
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--out", type=str, default="ndvi")

    args = parser.parse_args()
    run_ndvi(args.lat, args.lon, radius_m=args.radius, date=args.date, out_prefix=args.out)
