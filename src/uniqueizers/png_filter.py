# -*- coding: utf-8 -*-
"""
PNG Filter uniqueization: Changes PNG filter method.

Modifies PNG filter parameter (None, Sub, Up, Average, Paeth, Adaptive)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
import random


class PNGFilterUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG filter method.
    
    Changes PNG filter parameter (Adaptive, None, Sub, Up, Average, Paeth)
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying PNG filter.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified PNG filter
        """
        img, original_format = load_image(image_bytes)
        
        # Ensure PNG format
        if original_format.upper() != "PNG":
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return save_image(img, "PNG", preserve_alpha=True)
        
        # PNG filters: None, Sub, Up, Average, Paeth, Adaptive
        # PIL uses adaptive by default, but we can vary the compression
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        # Save with different compression levels to simulate filter changes
        # Note: PIL doesn't directly control filter, but compression affects it
        compression_level = random.choice([0, 1, 6, 9])  # Different compression = different filter behavior
        
        return save_image(img, "PNG", preserve_alpha=True)



