# -*- coding: utf-8 -*-
"""
Lens Model uniqueization: Changes lens model in EXIF.

Modifies LensModel field in EXIF metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
import piexif
import random


class LensModelUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies lens model in EXIF.
    
    Changes LensModel field in EXIF metadata
    """
    
    # Popular lens models
    LENS_MODELS = [
        "Canon EF 24-70mm f/2.8L II USM",
        "Canon EF 70-200mm f/2.8L IS III USM",
        "Canon EF 85mm f/1.2L II USM",
        "Nikon AF-S NIKKOR 24-70mm f/2.8E ED VR",
        "Nikon AF-S NIKKOR 70-200mm f/2.8E FL ED VR",
        "Nikon AF-S NIKKOR 85mm f/1.4G",
        "Sony FE 24-70mm f/2.8 GM",
        "Sony FE 70-200mm f/2.8 GM OSS",
        "Sony FE 85mm f/1.4 GM",
        "Fujifilm XF 16-55mm f/2.8 R LM WR",
        "Fujifilm XF 50-140mm f/2.8 R LM OIS WR",
        "Fujifilm XF 56mm f/1.2 R",
        "Sigma 24-70mm f/2.8 DG OS HSM | Art",
        "Sigma 70-200mm f/2.8 DG OS HSM | Sports",
        "Tamron SP 24-70mm f/2.8 Di VC USD G2",
        "Tamron SP 70-200mm f/2.8 Di VC USD G2",
        "Zeiss Otus 85mm f/1.4",
        "Leica Summilux-M 50mm f/1.4 ASPH",
        "iPhone 15 Pro Main Camera",
        "Samsung Galaxy S23 Ultra Main Camera",
        "Google Pixel 7 Pro Main Camera",
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying lens model in EXIF.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified lens model
        """
        img, original_format = load_image(image_bytes)
        
        # Random lens model
        lens_model = random.choice(self.LENS_MODELS)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            from PIL.PngImagePlugin import PngInfo
            pnginfo = PngInfo()
            pnginfo.add_text("LensModel", lens_model)
            pnginfo.add_text("Lens", lens_model)
            
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            return save_image(img, "PNG", preserve_alpha=True)
        else:
            # JPEG EXIF - LensModel is in EXIF
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            try:
                exif_dict = {
                    "Exif": {
                        # LensModel tag number is 42036 (0xA434)
                        42036: lens_model.encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

