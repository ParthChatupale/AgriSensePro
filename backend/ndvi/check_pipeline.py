import os
import sys

# Absolute path to backend folder
BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))

# Add backend root to Python path
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

# Now import the NDVI pipeline
from ndvi.pipeline.ndvi_pipeline import run_ndvi

print("Running NDVI pipeline test...\n")

out = run_ndvi(
    lat=34.1526,
    lon=77.5771,
    radius_m=250,
    out_prefix="check_test"
)

print("\nNDVI pipeline finished successfully!")
print("Output directory:", out["output_dir"])

