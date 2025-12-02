# -*- coding: utf-8 -*-
"""
Color Type uniqueization: Changes PNG color type.

Modifies PNG color type (RGB, RGBA, Grayscale, etc.)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
import random


class ColorTypeUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG color type.
    
    Changes color type parameter (RGB, RGBA, Grayscale, etc.)
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying color type.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified color type
        """
        img, original_format = load_image(image_bytes)
        
        # Random color type conversion
        color_types = ["RGB", "RGBA"]
        target_mode = random.choice(color_types)
        
        # Convert to target color type
        if img.mode != target_mode:
            if target_mode == "RGBA":
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
        
        # Save
        if original_format.upper() == "PNG":
            if img.mode == "RGBA":
                return save_image(img, "PNG", preserve_alpha=True)
            else:
                return save_image(img, "PNG", preserve_alpha=False)
        else:
            # Convert to PNG
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            return save_image(img, "PNG", preserve_alpha=True)



