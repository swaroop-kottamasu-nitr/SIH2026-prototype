import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

def is_leaf_image(image: Image.Image) -> bool:
    """
    Validates if an image contains a plant leaf.
    Uses HSV color thresholding and blur detection.
    Raises ValueError with a specific message for blurry/unclear images.
    Returns True if a leaf is detected, False otherwise.
    """
    # 1. Image preparation
    img = image.copy()
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # 2. Resize for fast computation (< 50ms)
    img.thumbnail((128, 128))
    
    # 3. Blur detection (Laplacian variance)
    gray = img.convert("L")
    img_arr = np.array(gray, dtype=np.int32)
    laplacian_var = np.var(
        img_arr[1:-1, 1:-1] * 4 -
        img_arr[:-2, 1:-1] - img_arr[2:, 1:-1] -
        img_arr[1:-1, :-2] - img_arr[1:-1, 2:]
    )
    
    if laplacian_var < 40.0:
        logger.warning(f"Unclear image detected. Variance: {laplacian_var}")
        raise ValueError("Unable to confirm a leaf in the image. Please upload a clear leaf photo.")
        
    # 4. Color thresholding in HSV
    hsv = img.convert("HSV")
    hsv_data = np.array(hsv)
    
    # Extract channels
    h = hsv_data[:,:,0] # 0-255 in PIL
    s = hsv_data[:,:,1]
    v = hsv_data[:,:,2]
    
    # PIL Hue is 0-255 instead of 0-360. 
    # Green is roughly Hue ~40-160 out of 360, so ~28-113 out of 255.
    green_mask = (h >= 25) & (h <= 118) & (s >= 30) & (v >= 30)
    
    green_ratio = np.sum(green_mask) / hsv_data[:,:,0].size
    
    if green_ratio > 0.05:
        logger.info("Leaf validation passed")
        return True
    
    logger.warning("Non-leaf image detected")
    return False

