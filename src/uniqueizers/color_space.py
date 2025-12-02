# -*- coding: utf-8 -*-
"""
Color Space uniqueization: Changes color space metadata.

Modifies ColorSpace field in metadata (sRGB, Display P3, Adobe RGB, etc.)
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import piexif
import random


class ColorSpaceUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies ColorSpace metadata.
    
    Changes ColorSpace field in metadata
    """
    
    # Common color spaces
    COLOR_SPACES = [
        "sRGB",
        "Display P3",
        "Adobe RGB (1998)",
        "ProPhoto RGB",
        "Rec. 2020",
        "Rec. 709",
        "DCI-P3",
        "NTSC (1953)",
        "PAL/SECAM",
    ]
    
    # Color space IDs for EXIF
    COLOR_SPACE_IDS = {
        "sRGB": 1,
        "Adobe RGB": 2,
        "Uncalibrated": 65535,
    }
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying ColorSpace metadata.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified ColorSpace
        """
        img, original_format = load_image(image_bytes)
        
        # Random color space
        color_space = random.choice(self.COLOR_SPACES)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            pnginfo = PngInfo()
            pnginfo.add_text("ColorSpace", color_space)
            pnginfo.add_text("sRGB", "0" if color_space != "sRGB" else "1")
            
            # Save PNG with metadata
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF - ColorSpace
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                # Try to map color space to EXIF value
                if "sRGB" in color_space:
                    color_space_id = self.COLOR_SPACE_IDS["sRGB"]
                elif "Adobe RGB" in color_space:
                    color_space_id = self.COLOR_SPACE_IDS["Adobe RGB"]
                else:
                    color_space_id = self.COLOR_SPACE_IDS["Uncalibrated"]
                
                exif_dict = {
                    "Exif": {
                        piexif.ExifIFD.ColorSpace: color_space_id,
                    },
                    "0th": {
                        piexif.ImageIFD.ImageDescription: color_space.encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)


