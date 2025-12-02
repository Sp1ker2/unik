# -*- coding: utf-8 -*-
"""
Aperture uniqueization: Changes EXIF aperture/F-number.

Modifies EXIF aperture parameter (f/1.8, f/2.8, etc.)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from src.utils.metadata import generate_random_metadata
import piexif
import random


class ApertureUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies EXIF aperture/F-number.
    
    Changes aperture parameter in EXIF metadata
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying aperture in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified aperture
        """
        img, original_format = load_image(image_bytes)
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Random aperture values (f/1.8, f/2.8, f/4.0, f/5.6, f/8.0, etc.)
        # Stored as (numerator, denominator) in EXIF
        apertures = [
            (18, 10),  # f/1.8
            (28, 10),  # f/2.8
            (40, 10),  # f/4.0
            (56, 10),  # f/5.6
            (80, 10),  # f/8.0
            (110, 10), # f/11
            (160, 10), # f/16
        ]
        aperture = random.choice(apertures)
        
        # Add EXIF with aperture
        try:
            exif_dict = {
                "Exif": {
                    piexif.ExifIFD.FNumber: aperture,
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



