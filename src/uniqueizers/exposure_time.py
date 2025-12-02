# -*- coding: utf-8 -*-
"""
Exposure Time uniqueization: Changes EXIF exposure time.

Modifies ExposureTime (shutter speed) field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random
from fractions import Fraction


class ExposureTimeUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies EXIF exposure time (shutter speed).
    
    Changes ExposureTime field in EXIF metadata
    """
    
    # Common exposure times (as fractions for precision)
    EXPOSURE_TIMES = [
        (1, 8000),   # 1/8000
        (1, 4000),   # 1/4000
        (1, 2000),   # 1/2000
        (1, 1000),   # 1/1000
        (1, 500),    # 1/500
        (1, 250),    # 1/250
        (1, 125),    # 1/125
        (1, 60),     # 1/60
        (1, 30),     # 1/30
        (1, 15),     # 1/15
        (1, 8),      # 1/8
        (1, 4),      # 1/4
        (1, 2),      # 1/2
        (1, 1),      # 1 sec
        (2, 1),      # 2 sec
        (4, 1),      # 4 sec
        (8, 1),      # 8 sec
        (15, 1),     # 15 sec
        (30, 1),     # 30 sec
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying ExposureTime in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified ExposureTime
        """
        img, original_format = load_image(image_bytes)
        
        # Convert to RGB if needed
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        
        # Random exposure time
        exposure_time = random.choice(self.EXPOSURE_TIMES)
        
        # Add EXIF with exposure time
        try:
            exif_dict = {
                "Exif": {
                    piexif.ExifIFD.ExposureTime: exposure_time,
                    # Also add as decimal for compatibility
                    piexif.ExifIFD.ShutterSpeedValue: (
                        int(exposure_time[1] * 100),
                        int(exposure_time[0] * 100)
                    ),
                }
            }
            exif_bytes = piexif.dump(exif_dict)
        except Exception as e:
            # Fallback: try simplified version
            try:
                exif_dict = {
                    "Exif": {
                        piexif.ExifIFD.ExposureTime: exposure_time,
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
        
        # Save
        if original_format.upper() == "PNG":
            # PNG doesn't directly support EXIF, but we can still modify it
            if img.mode == "RGBA":
                return save_image(img, "PNG", preserve_alpha=True)
            else:
                return save_image(img, "PNG", preserve_alpha=False)
        else:
            # JPEG with EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)


