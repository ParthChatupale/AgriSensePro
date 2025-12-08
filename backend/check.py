import rasterio

for band in ["input/B04.jp2", "input/B08.jp2"]:
    with rasterio.open(band) as ds:
        arr = ds.read(1)
        print("\nFILE:", band)
        print(" shape:", arr.shape)
        print(" min/max:", arr.min(), arr.max())
        print(" unique values (first 10):", sorted(list(set(arr.flatten())))[:10])