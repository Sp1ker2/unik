# -*- coding: utf-8 -*-
"""
Flash uniqueization: Changes flash settings in EXIF.

Modifies Flash field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class FlashUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies flash settings in EXIF.
    
    Changes Flash field in EXIF metadata
    """
    
    # Flash values (see EXIF spec)
    FLASH_VALUES = [
        0,      # Flash did not fire
        1,      # Flash fired
        5,      # Flash fired, compulsory flash mode, return light not detected
        7,      # Flash fired, compulsory flash mode, return light detected
        9,      # Flash fired, compulsory flash mode
        13,     # Flash fired, compulsory flash mode, return light not detected, red-eye reduction mode
        15,     # Flash fired, compulsory flash mode, return light detected, red-eye reduction mode
        16,     # No flash function
        24,     # Auto mode
        25,     # Flash fired, auto mode, return light not detected
        29,     # Flash fired, auto mode, return light detected
        31,     # Flash fired, auto mode, return light detected, red-eye reduction mode
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying flash settings in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified flash settings
        """
        img, original_format = load_image(image_bytes)
        
        # Random flash value
        flash = random.choice(self.FLASH_VALUES)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("Flash", str(flash))
            
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
                        piexif.ExifIFD.Flash: flash,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

