"""
NDVI Testing Module

This module provides comprehensive testing for NDVI image processing.
It tests NDVI computation on image files and verifies output generation.

----------------------------------------------------------
PLACE YOUR TEST IMAGES HERE:
    /input/

Accepted formats: .tif, .tiff, .jpeg, .jpg, .png

Run tests using:
    python ndvi_test.py
----------------------------------------------------------
"""

import os
import sys
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

# Try to import image processing libraries
try:
    import rasterio
    from rasterio.plot import show
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    print("[WARNING] rasterio not available. Install with: pip install rasterio")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("[WARNING] PIL/Pillow not available. Install with: pip install pillow")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output" / "ndvi"

# Supported image formats
SUPPORTED_FORMATS = {'.tif', '.tiff', '.jpeg', '.jpg', '.png'}


def process_ndvi_image(image_path: str) -> Optional[Dict]:
    """
    Process an image file to compute NDVI.
    
    This function:
    1. Loads the image (supports multi-band GeoTIFF or RGB images)
    2. Extracts NIR and Red bands
    3. Computes NDVI = (NIR - Red) / (NIR + Red)
    4. Generates output files: ndvi.png, rgb.png, ndvi_raw.npy
    5. Returns statistics: min, max, mean
    
    Args:
        image_path: Path to input image file
    
    Returns:
        Dictionary with keys: min, max, mean, output_dir, success
        Returns None if processing fails
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        return None
    
    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: {image_path.suffix}")
        return None
    
    try:
        # Create output directory
        image_name = image_path.stem
        output_dir = OUTPUT_DIR / image_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load image based on format
        if image_path.suffix.lower() in {'.tif', '.tiff'}:
            # GeoTIFF - use rasterio
            if not HAS_RASTERIO:
                logger.error("rasterio required for GeoTIFF files")
                return None
            
            with rasterio.open(image_path) as src:
                # Read all bands
                bands = src.read()
                n_bands = src.count
                
                # Determine band indices (common Sentinel-2: B04=Red, B08=NIR)
                # For standard RGB+NIR: assume bands are [R, G, B, NIR] or [B04, B08, ...]
                if n_bands >= 4:
                    # Assume Sentinel-2 format: [B02, B03, B04, B08, ...]
                    # Or standard: [R, G, B, NIR]
                    red_band = bands[2] if n_bands > 3 else bands[0]  # B04 or R
                    nir_band = bands[3] if n_bands > 3 else bands[-1]  # B08 or NIR
                elif n_bands == 3:
                    # RGB image - use R and G as approximation (not ideal)
                    logger.warning("RGB image detected. Using R and G bands as approximation.")
                    red_band = bands[0]  # R
                    nir_band = bands[1]   # G (approximation)
                else:
                    logger.error(f"Insufficient bands ({n_bands}). Need at least 3 bands.")
                    return None
                
                # Convert to float for calculation
                red_band = red_band.astype(np.float32)
                nir_band = nir_band.astype(np.float32)
                
                # Save RGB composite
                if n_bands >= 3:
                    rgb = np.dstack([bands[0], bands[1], bands[2]])
                    rgb_normalized = (rgb / rgb.max() * 255).astype(np.uint8)
                    rgb_image = Image.fromarray(rgb_normalized)
                    rgb_path = output_dir / "rgb.png"
                    rgb_image.save(rgb_path)
        
        else:
            # JPEG/PNG - use PIL
            if not HAS_PIL:
                logger.error("PIL/Pillow required for JPEG/PNG files")
                return None
            
            img = Image.open(image_path)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            if len(img_array.shape) == 2:
                # Grayscale - cannot compute NDVI
                logger.error("Grayscale image. Cannot compute NDVI without NIR band.")
                return None
            
            # Assume RGB or RGBA
            if img_array.shape[2] >= 3:
                # Use R and G as approximation (not ideal for NDVI)
                logger.warning("RGB image detected. Using R and G bands as approximation.")
                red_band = img_array[:, :, 0].astype(np.float32)
                nir_band = img_array[:, :, 1].astype(np.float32)  # G as NIR approximation
                
                # Save RGB
                rgb_path = output_dir / "rgb.png"
                img.save(rgb_path)
            else:
                logger.error("Insufficient color channels for NDVI computation")
                return None
        
        # Compute NDVI
        # NDVI = (NIR - Red) / (NIR + Red)
        denominator = nir_band + red_band
        # Avoid division by zero
        denominator = np.where(denominator == 0, np.nan, denominator)
        ndvi = (nir_band - red_band) / denominator
        
        # Filter invalid values
        valid_mask = ~(np.isnan(ndvi) | np.isinf(ndvi))
        valid_ndvi = ndvi[valid_mask]
        
        if len(valid_ndvi) == 0:
            logger.error("No valid NDVI values computed")
            return None
        
        # Compute statistics
        ndvi_min = float(np.nanmin(valid_ndvi))
        ndvi_max = float(np.nanmax(valid_ndvi))
        ndvi_mean = float(np.nanmean(valid_ndvi))
        
        # Save NDVI as numpy array
        ndvi_raw_path = output_dir / "ndvi_raw.npy"
        np.save(ndvi_raw_path, ndvi)
        
        # Create NDVI visualization (normalize to 0-255 for display)
        ndvi_normalized = ((ndvi + 1) / 2 * 255).astype(np.uint8)  # Scale from [-1,1] to [0,255]
        ndvi_image = Image.fromarray(ndvi_normalized, mode='L')
        ndvi_path = output_dir / "ndvi.png"
        ndvi_image.save(ndvi_path)
        
        return {
            "min": round(ndvi_min, 4),
            "max": round(ndvi_max, 4),
            "mean": round(ndvi_mean, 4),
            "output_dir": str(output_dir),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}", exc_info=True)
        return None


def run_test(image_path: str) -> bool:
    """
    Run a single NDVI test on an image file.
    
    Args:
        image_path: Path to test image
    
    Returns:
        True if test passes, False otherwise
    """
    image_path = Path(image_path)
    filename = image_path.name
    
    print(f"\n{'='*60}")
    print(f"[TEST] Running NDVI on {filename}")
    print(f"{'='*60}")
    
    try:
        result = process_ndvi_image(str(image_path))
        
        if result is None:
            print(f"[ERROR] NDVI computation failed for {filename}")
            print("[FAIL] Test failed")
            return False
        
        if not result.get("success", False):
            print(f"[ERROR] NDVI computation unsuccessful for {filename}")
            print("[FAIL] Test failed")
            return False
        
        # Print statistics
        print(f"NDVI Stats → min={result['min']}, max={result['max']}, mean={result['mean']}")
        print(f"Output stored in: {result['output_dir']}")
        
        # Verify output files
        output_dir = Path(result['output_dir'])
        required_files = ['ndvi.png', 'rgb.png', 'ndvi_raw.npy']
        missing_files = []
        
        for file in required_files:
            file_path = output_dir / file
            if not file_path.exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"[ERROR] Missing output files: {', '.join(missing_files)}")
            print("[FAIL] Test failed")
            return False
        
        print("[OK] NDVI computation successful")
        print("[PASS] Test passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        print("[FAIL] Test failed")
        return False


def run_all_tests() -> Dict[str, int]:
    """
    Run all NDVI tests.
    
    Returns:
        Dictionary with test counts: total, passed, failed
    """
    print("\n" + "="*60)
    print("NDVI TESTING SUITE")
    print("="*60)
    
    # Ensure input directory exists
    INPUT_DIR.mkdir(exist_ok=True)
    
    # Find all test images
    test_images = []
    for ext in SUPPORTED_FORMATS:
        test_images.extend(INPUT_DIR.glob(f"*{ext}"))
        test_images.extend(INPUT_DIR.glob(f"*{ext.upper()}"))
    
    if not test_images:
        print(f"\n[WARNING] No test images found in {INPUT_DIR}")
        print("Please place test images (.tif, .tiff, .jpeg, .jpg, .png) in the input folder.")
        return {"total": 0, "passed": 0, "failed": 0}
    
    print(f"\nFound {len(test_images)} test image(s)")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}\n")
    
    # Run tests
    results = {"total": len(test_images), "passed": 0, "failed": 0}
    
    for image_path in test_images:
        if run_test(image_path):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print("="*60 + "\n")
    
    return results


def run_error_handling_test():
    """
    Test error handling with intentionally invalid inputs.
    """
    print("\n" + "="*60)
    print("ERROR HANDLING TESTS")
    print("="*60)
    
    # Test 1: Non-existent file
    print("\n[TEST] Non-existent file")
    result = process_ndvi_image("nonexistent_file.tif")
    if result is None:
        print("[OK] Correctly handled missing file")
    else:
        print("[FAIL] Should have returned None for missing file")
    
    # Test 2: Unsupported format
    print("\n[TEST] Unsupported file format")
    test_file = INPUT_DIR / "test.txt"
    if test_file.exists():
        result = process_ndvi_image(str(test_file))
        if result is None:
            print("[OK] Correctly handled unsupported format")
        else:
            print("[FAIL] Should have returned None for unsupported format")
    else:
        print("[SKIP] No .txt file found for testing")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    """
    Main entry point for NDVI testing.
    
    Run with: python ndvi_test.py
    """
    print("\n" + "="*60)
    print("NDVI TESTING MODULE")
    print("="*60)
    print("\nThis module tests NDVI computation on image files.")
    print("It verifies:")
    print("  - NDVI statistics (min, max, mean)")
    print("  - Output file generation (ndvi.png, rgb.png, ndvi_raw.npy)")
    print("  - Error handling")
    print("\n" + "="*60)
    
    # Check dependencies
    if not HAS_RASTERIO and not HAS_PIL:
        print("\n[ERROR] No image processing libraries available!")
        print("Please install: pip install rasterio pillow")
        sys.exit(1)
    
    # Run all tests
    results = run_all_tests()
    
    # Run error handling tests
    run_error_handling_test()
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

