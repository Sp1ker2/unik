# -*- coding: utf-8 -*-
"""
Exposure Mode uniqueization: Changes exposure mode in EXIF.

Modifies ExposureMode field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class ExposureModeUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies exposure mode in EXIF.
    
    Changes ExposureMode field in EXIF metadata
    """
    
    # Exposure mode values (see EXIF spec)
    EXPOSURE_MODES = {
        0: "Auto exposure",
        1: "Manual exposure",
        2: "Auto bracket",
    }
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying exposure mode in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified exposure mode
        """
        img, original_format = load_image(image_bytes)
        
        # Random exposure mode
        exposure_mode = random.choice(list(self.EXPOSURE_MODES.keys()))
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("ExposureMode", str(exposure_mode))
            pnginfo.add_text("ExposureModeDesc", self.EXPOSURE_MODES[exposure_mode])
            
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
                        piexif.ExifIFD.ExposureMode: exposure_mode,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

