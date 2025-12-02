# -*- coding: utf-8 -*-
"""
PNG tIME chunk uniqueization: Changes PNG modification time.

Modifies tIME chunk (modification time) in PNG metadata
"""

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image
from datetime import datetime, timedelta
import random
from PIL.PngImagePlugin import PngInfo


class PNGTimeUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies PNG tIME chunk (modification time).
    
    Changes PNG tIME chunk which stores modification time
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by modifying PNG tIME chunk.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Processed image with modified tIME chunk
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
        
        # PNG tIME format: (year, month, day, hour, minute, second)
        time_tuple = (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second
        )
        
        if original_format.upper() == "PNG":
            # PNG tIME chunk
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            
            # Note: PIL doesn't directly support tIME chunk modification
            # This is handled via PNG metadata text chunks as workaround
            pnginfo = PngInfo()
            pnginfo.add_text("tIME", f"{dt.year}-{dt.month:02d}-{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}")
            pnginfo.add_text("ModificationTime", str(time_tuple))
            
            # Save with metadata
            import io
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="PNG", pnginfo=pnginfo, optimize=False)
            output_buffer.seek(0)
            return output_buffer.getvalue()
        else:
            # Convert to PNG first
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            pnginfo = PngInfo()
            pnginfo.add_text("tIME", f"{dt.year}-{dt.month:02d}-{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}")
            
            import io
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="PNG", pnginfo=pnginfo, optimize=False)
            output_buffer.seek(0)
            return output_buffer.getvalue()

