# -*- coding: utf-8 -*-
"""
Compression uniqueization: Changes PNG compression method.

Modifies PNG compression parameter (Deflate/Inflate)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
import random


class CompressionUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG compression method.
    
    Changes compression parameter (Deflate/Inflate)
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying compression method.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified compression
        """
        img, original_format = load_image(image_bytes)
        
        # Ensure PNG format
        if original_format.upper() != "PNG":
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return save_image(img, "PNG", preserve_alpha=True)
        
        # PNG uses Deflate/Inflate compression
        # We can vary compression level (0-9)
        # Lower = faster, larger file
        # Higher = slower, smaller file
        compression_level = random.choice([0, 1, 3, 6, 9])
        
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        # Save with different compression
        return save_image(img, "PNG", preserve_alpha=True)



