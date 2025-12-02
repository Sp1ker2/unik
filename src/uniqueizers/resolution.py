# -*- coding: utf-8 -*-
"""
Resolution uniqueization: Changes image resolution/DPI.

Modifies image resolution in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from src.utils.metadata import generate_random_metadata
import piexif
import random


class ResolutionUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies image resolution/DPI.
    
    Changes resolution parameter in EXIF metadata
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying resolution.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified resolution
        """
        img, original_format = load_image(image_bytes)
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Random resolution values (72, 96, 150, 200, 300 DPI)
        resolutions = [72, 96, 150, 200, 300]
        x_resolution = random.choice(resolutions)
        y_resolution = x_resolution  # Usually same
        
        # Set DPI in image
        img.info['dpi'] = (x_resolution, y_resolution)
        
        # Add EXIF with resolution
        try:
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.XResolution: (x_resolution, 1),
                    piexif.ImageIFD.YResolution: (y_resolution, 1),
                    piexif.ImageIFD.ResolutionUnit: 2,  # Inches
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


