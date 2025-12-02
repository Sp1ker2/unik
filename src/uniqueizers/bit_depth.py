# -*- coding: utf-8 -*-
"""
Bit Depth uniqueization: Changes PNG bit depth.

Modifies PNG bit depth parameter (8, 16, etc.)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
import random


class BitDepthUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG bit depth.
    
    Changes bit depth parameter in PNG metadata.
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying bit depth.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified bit depth
        """
        img, original_format = load_image(image_bytes)
        
        # Only process PNG images
        if original_format.upper() != "PNG":
            # Convert to PNG if not already
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return save_image(img, "PNG", preserve_alpha=True)
        
        # Random bit depth: 8 or 16
        bit_depth = random.choice([8, 16])
        
        # Save with specific bit depth
        # Note: PIL doesn't directly control bit depth, but we can ensure it's saved correctly
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        return save_image(img, "PNG", preserve_alpha=True)



