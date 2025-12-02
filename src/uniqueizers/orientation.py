# -*- coding: utf-8 -*-
"""
Orientation uniqueization: Changes image orientation in EXIF.

Modifies Orientation field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class OrientationUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies image orientation in EXIF.
    
    Changes Orientation field in EXIF metadata
    """
    
    # Orientation values (see EXIF spec)
    ORIENTATIONS = {
        1: "Normal (0°)",
        3: "Upside down (180°)",
        6: "Rotated 90° CCW",
        8: "Rotated 90° CW",
    }
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying orientation in EXIF.
        
        Note: This only changes metadata, not the actual image rotation.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified orientation metadata
        """
        img, original_format = load_image(image_bytes)
        
        # Random orientation
        orientation = random.choice(list(self.ORIENTATIONS.keys()))
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("Orientation", str(orientation))
            
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                exif_dict = {
                    "0th": {
                        piexif.ImageIFD.Orientation: orientation,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

