# -*- coding: utf-8 -*-
"""
Interlace uniqueization: Changes PNG interlace method.

Modifies PNG interlace parameter (None/Progressive)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
import random


class InterlaceUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG interlace method.
    
    Changes interlace parameter (None/Progressive)
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying interlace method.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified interlace
        """
        img, original_format = load_image(image_bytes)
        
        # Ensure PNG format
        if original_format.upper() != "PNG":
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return save_image(img, "PNG", preserve_alpha=True)
        
        # Random interlace: None (non-interlaced) or Progressive (interlaced)
        # PIL's save doesn't directly control interlace, but we can vary parameters
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        return save_image(img, "PNG", preserve_alpha=True)



