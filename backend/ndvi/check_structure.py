import os

paths = [
    "backend/ndvi/pipeline",
    "backend/ndvi/jobs",
    "backend/ndvi/api",
    "backend/ndvi/data/ndvi_jobs"
]

print("Checking NDVI module structure...\n")
for p in paths:
    print(p, "OK" if os.path.exists(p) else "MISSING")

