# -*- coding: utf-8 -*-
"""
DateTime EXIF uniqueization: Changes date/time in EXIF.

Modifies DateTime, DateTimeOriginal, DateTimeDigitized in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from datetime import datetime, timedelta
import piexif
import random


class DateTimeEXIFUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies date/time in EXIF.
    
    Changes DateTime, DateTimeOriginal, DateTimeDigitized fields
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying date/time in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified date/time
        """
        img, original_format = load_image(image_bytes)
        
        # Random datetime within last 2 years
        days_ago = random.randint(1, 730)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        seconds_offset = random.randint(0, 59)
        
        dt = datetime.now() - timedelta(
            days=days_ago,
            hours=hours_offset,
            minutes=minutes_offset,
            seconds=seconds_offset
        )
        dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("DateTime", dt_str)
            pnginfo.add_text("DateTimeOriginal", dt_str)
            pnginfo.add_text("DateTimeDigitized", dt_str)
            
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
                        piexif.ImageIFD.DateTime: dt_str.encode('utf-8'),
                    },
                    "Exif": {
                        piexif.ExifIFD.DateTimeOriginal: dt_str.encode('utf-8'),
                        piexif.ExifIFD.DateTimeDigitized: dt_str.encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

