# -*- coding: utf-8 -*-
"""
Subject Distance uniqueization: Changes subject distance in EXIF.

Modifies SubjectDistance field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random
from fractions import Fraction


class SubjectDistanceUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies subject distance in EXIF.
    
    Changes SubjectDistance field in EXIF metadata (distance to subject in meters)
    """
    
    # Common subject distances (in meters, as fractions for precision)
    SUBJECT_DISTANCES = [
        (1, 100),      # 0.01 m (macro)
        (5, 100),      # 0.05 m
        (10, 100),     # 0.1 m
        (20, 100),     # 0.2 m
        (50, 100),     # 0.5 m
        (1, 1),        # 1 m
        (2, 1),        # 2 m
        (3, 1),        # 3 m
        (5, 1),        # 5 m
        (10, 1),       # 10 m
        (20, 1),       # 20 m
        (50, 1),       # 50 m
        (100, 1),      # 100 m
        (200, 1),      # 200 m
        (500, 1),      # 500 m
        (1000, 1),     # 1000 m (infinity)
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying subject distance in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified subject distance
        """
        img, original_format = load_image(image_bytes)
        
        # Random subject distance
        distance = random.choice(self.SUBJECT_DISTANCES)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            distance_str = f"{distance[0]}/{distance[1]}" if distance[1] != 1 else str(distance[0])
            pnginfo.add_text("SubjectDistance", distance_str)
            
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                # SubjectDistance tag is 37382 (0x9206)
                exif_dict = {
                    "Exif": {
                        37382: distance,  # SubjectDistance
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

