# -*- coding: utf-8 -*-
"""
Rating uniqueization: Changes image rating metadata.

Modifies Rating field in XMP/EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import piexif
import random


class RatingUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies Rating metadata.
    
    Changes Rating field (0-5 stars) in metadata
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying Rating metadata.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified Rating
        """
        img, original_format = load_image(image_bytes)
        
        # Random rating: 0-5 stars
        rating = random.randint(0, 5)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            pnginfo = PngInfo()
            pnginfo.add_text("Rating", str(rating))
            pnginfo.add_text("XMP:Rating", str(rating))
            
            # Save PNG with metadata
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF - Rating in EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                # Rating is typically stored in UserComment or ImageDescription
                exif_dict = {
                    "0th": {
                        piexif.ImageIFD.ImageDescription: f"Rating: {rating}".encode('utf-8'),
                    },
                    "Exif": {
                        piexif.ExifIFD.UserComment: f"Rating:{rating}".encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

