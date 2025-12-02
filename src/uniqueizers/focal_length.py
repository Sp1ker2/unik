# -*- coding: utf-8 -*-
"""
Focal Length uniqueization: Changes focal length in EXIF.

Modifies FocalLength and FocalLengthIn35mmFilm in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class FocalLengthUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies focal length in EXIF.
    
    Changes FocalLength and FocalLengthIn35mmFilm in EXIF metadata
    """
    
    # Common focal lengths (in mm)
    FOCAL_LENGTHS = [
        14, 16, 18, 20, 24, 28, 35, 40, 50, 55, 60,
        70, 85, 90, 100, 105, 135, 150, 180, 200,
        250, 300, 400, 500, 600, 800
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying focal length in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified focal length
        """
        img, original_format = load_image(image_bytes)
        
        # Random focal length
        focal_length = random.choice(self.FOCAL_LENGTHS)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("FocalLength", str(focal_length))
            pnginfo.add_text("FocalLength35mm", str(focal_length))
            
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
                        piexif.ExifIFD.FocalLength: (focal_length, 1),
                        piexif.ExifIFD.FocalLengthIn35mmFilm: focal_length,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

