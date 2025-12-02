# -*- coding: utf-8 -*-
"""
Creator Tool uniqueization: Changes CreatorTool metadata.

Modifies CreatorTool/Software field in metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import piexif
import random


class CreatorToolUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies CreatorTool metadata.
    
    Changes CreatorTool/Software field in EXIF/PNG metadata
    """
    
    # List of popular photo editing software
    CREATOR_TOOLS = [
        "Adobe Photoshop CC 2023",
        "Adobe Photoshop CC 2024",
        "Adobe Lightroom Classic 12.0",
        "Adobe Lightroom Classic 13.0",
        "ON1 Photo RAW 2023",
        "ON1 Photo RAW 2024",
        "Capture One 23",
        "Capture One Pro 16",
        "DxO PhotoLab 7",
        "Luminar AI",
        "Luminar Neo",
        "Affinity Photo 2",
        "GIMP 2.10.36",
        "Pixelmator Pro 3.5",
        "Corel PaintShop Pro 2024",
        "ACDSee Photo Studio Ultimate 2024",
        "Skylum Aurora HDR 2023",
        "Topaz Photo AI 2.0",
    ]
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying CreatorTool metadata.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified CreatorTool
        """
        img, original_format = load_image(image_bytes)
        
        # Random creator tool
        creator_tool = random.choice(self.CREATOR_TOOLS)
        
        if original_format.upper() == "PNG":
            # PNG metadata
            pnginfo = PngInfo()
            pnginfo.add_text("Software", creator_tool)
            pnginfo.add_text("CreatorTool", creator_tool)
            
            # Save PNG with metadata
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
                        piexif.ImageIFD.Software: creator_tool.encode('utf-8'),
                    }
                }
                exif_bytes = piexif.dump(exif_dict)
            except Exception:
                from src.utils.metadata import generate_random_metadata
                exif_bytes = generate_random_metadata()
            
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)

