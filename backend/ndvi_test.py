import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt

INPUT_DIR = "input"
OUTPUT_DIR = "output/ndvi"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_band(path):
    """Load a TIFF band and return array."""
    with rasterio.open(path) as ds:
        return ds.read(1).astype("float32")


def compute_ndvi(red, nir):
    """Standard NDVI computation."""
    ndvi = (nir - red) / (nir + red + 1e-6)
    return np.clip(ndvi, -1, 1)


def save_ndvi(ndvi, out_path):
    """Save NDVI map with colormap."""
    plt.figure(figsize=(10, 10))
    plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="NDVI")
    plt.title("NDVI Map (Sentinel-2 L2A TIFF)")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def main():

    # Detect B04 and B08 TIFFs automatically
    files = os.listdir(INPUT_DIR)
    red_file = next((f for f in files if "B04" in f and f.endswith(".tiff")), None)
    nir_file = next((f for f in files if "B08" in f and f.endswith(".tiff")), None)

    if not red_file or not nir_file:
        print("[ERROR] Missing B04 or B08 TIFF input files!")
        return

    red_path = os.path.join(INPUT_DIR, red_file)
    nir_path = os.path.join(INPUT_DIR, nir_file)

    print(f"[OK] RED band: {red_path}")
    print(f"[OK] NIR band: {nir_path}")

    # Load bands
    red = load_band(red_path)
    nir = load_band(nir_path)

    print(f"[INFO] RED shape: {red.shape}, NIR shape: {nir.shape}")

    # Compute NDVI
    ndvi = compute_ndvi(red, nir)

    # Save output
    ndvi_png = os.path.join(OUTPUT_DIR, "ndvi_tiff.png")
    save_ndvi(ndvi, ndvi_png)
    np.save(os.path.join(OUTPUT_DIR, "ndvi_raw.npy"), ndvi)

    print("\n============================================================")
    print(" NDVI COMPUTATION COMPLETE (L2A TIFF)")
    print(f" Output saved at: {ndvi_png}")
    print("============================================================")


if __name__ == "__main__":
    main()
