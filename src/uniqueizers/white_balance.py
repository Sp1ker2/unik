# -*- coding: utf-8 -*-
"""
White Balance uniqueization: Changes EXIF white balance.

Modifies EXIF white balance parameter
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from src.utils.metadata import generate_random_metadata
import piexif
import random


class WhiteBalanceUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies EXIF white balance.
    
    Changes white balance parameter in EXIF metadata
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying white balance in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified white balance
        """
        img, original_format = load_image(image_bytes)
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Random white balance value (0 = Auto, 1 = Manual, etc.)
        white_balance = random.choice([0, 1])
        
        # Add EXIF with white balance
        try:
            exif_dict = {
                "Exif": {
                    piexif.ExifIFD.WhiteBalance: white_balance,
                }
            }
            exif_bytes = piexif.dump(exif_dict)
        except:
            exif_bytes = generate_random_metadata()
        
        # Save
        if original_format.upper() == "PNG":
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)


