# -*- coding: utf-8 -*-
"""
Metering Mode uniqueization: Changes metering mode in EXIF.

Modifies MeteringMode field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class MeteringModeUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies metering mode in EXIF.
    
    Changes MeteringMode field in EXIF metadata
    """
    
    # Metering mode values (see EXIF spec)
    METERING_MODES = {
        0: "Unknown",
        1: "Average",
        2: "Center-weighted average",
        3: "Spot",
        4: "Multi-spot",
        5: "Multi-segment",
        6: "Partial",
        255: "Other",
    }
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying metering mode in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified metering mode
        """
        img, original_format = load_image(image_bytes)
        
        # Random metering mode
        metering_mode = random.choice(list(self.METERING_MODES.keys()))
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("MeteringMode", str(metering_mode))
            pnginfo.add_text("MeteringModeDesc", self.METERING_MODES[metering_mode])
            
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
                        piexif.ExifIFD.MeteringMode: metering_mode,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

