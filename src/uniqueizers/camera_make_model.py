# -*- coding: utf-8 -*-
"""
Camera Make/Model uniqueization: Changes camera make and model in EXIF.

Modifies Make and Model fields in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class CameraMakeModelUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies camera make and model in EXIF.
    
    Changes Make and Model fields in EXIF metadata
    """
    
    # Popular camera models
    CAMERAS = [
        ("Canon", "EOS 5D Mark IV"),
        ("Canon", "EOS R5"),
        ("Canon", "EOS R6"),
        ("Canon", "EOS 90D"),
        ("Nikon", "D850"),
        ("Nikon", "Z9"),
        ("Nikon", "Z7 II"),
        ("Nikon", "D780"),
        ("Sony", "A7 III"),
        ("Sony", "A7R V"),
        ("Sony", "A7 IV"),
        ("Sony", "A6600"),
        ("Fujifilm", "X-T5"),
        ("Fujifilm", "X-T4"),
        ("Fujifilm", "X-H2"),
        ("Panasonic", "GH6"),
        ("Panasonic", "S1R"),
        ("Olympus", "OM-D E-M1 Mark III"),
        ("Leica", "Q3"),
        ("Leica", "M11"),
        ("Pentax", "K-3 III"),
        ("Apple", "iPhone 15 Pro"),
        ("Apple", "iPhone 15 Pro Max"),
        ("Apple", "iPhone 14 Pro"),
        ("Samsung", "Galaxy S23 Ultra"),
        ("Samsung", "Galaxy S22 Ultra"),
        ("Google", "Pixel 7 Pro"),
        ("Google", "Pixel 8 Pro"),
        ("OnePlus", "11 Pro"),
        ("Xiaomi", "13 Pro"),
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying camera make and model in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified camera info
        """
        img, original_format = load_image(image_bytes)
        
        # Random camera
        make, model = random.choice(self.CAMERAS)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("Make", make)
            pnginfo.add_text("Model", model)
            pnginfo.add_text("Camera", f"{make} {model}")
            
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
                        piexif.ImageIFD.Make: make.encode('utf-8'),
                        piexif.ImageIFD.Model: model.encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

