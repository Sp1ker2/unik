# -*- coding: utf-8 -*-
"""
ISO uniqueization: Changes ISO speed ratings in EXIF.

Modifies ISO speed ratings in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class ISOUUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies ISO speed ratings in EXIF.
    
    Changes ISO value in EXIF metadata
    """
    
    # Common ISO values
    ISO_VALUES = [
        50, 64, 80, 100, 125, 160, 200, 250, 320, 400,
        500, 640, 800, 1000, 1250, 1600, 2000, 2500,
        3200, 4000, 5000, 6400, 8000, 10000, 12800,
        16000, 20000, 25600, 32000, 40000, 51200
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying ISO in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified ISO
        """
        img, original_format = load_image(image_bytes)
        
        # Random ISO value
        iso = random.choice(self.ISO_VALUES)
        
        if original_format.upper() == "PNG":
            # PNG doesn't support EXIF directly, but we can add it as metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("ISO", str(iso))
            
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                exif_dict = {
                    "Exif": {
                        piexif.ExifIFD.ISOSpeedRatings: iso,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

