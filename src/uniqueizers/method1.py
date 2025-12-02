# -*- coding: utf-8 -*-
"""
Method 1: Simple uniqueization (from bot.py)
- Edge crop (0-3 pixels)
- Color enhancement (±2%)
- Brightness enhancement (±2%)
- EXIF metadata replacement
"""

import random
import io
import string
from PIL import Image, ImageEnhance
import piexif

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image, get_icc_profile, apply_icc_profile
from src.utils.metadata import generate_random_metadata


def random_string(length):
    """Generate random string for EXIF."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(length))


class Method1Uniqueizer(BaseUniqueizer):
    """
    Simple uniqueization method from original bot.py.
    
    Applies:
    - Random edge crop (0-3 pixels)
    - Color enhancement (±2%)
    - Brightness enhancement (±2%)
    - EXIF metadata replacement
    """

    def process(self, image_bytes: bytes) -> bytes:
        """Process image with method 1."""
        try:
            input_buffer = io.BytesIO(image_bytes)
            img = Image.open(input_buffer)
            original_format = img.format or "JPEG"
            icc_profile = get_icc_profile(image_bytes)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Random edge crop
            width, height = img.size
            crop_pixels = random.randint(0, 3)
            if crop_pixels > 0 and width > crop_pixels * 2 and height > crop_pixels * 2:
                img = img.crop((
                    crop_pixels,
                    crop_pixels,
                    width - crop_pixels,
                    height - crop_pixels
                ))

            # Color and brightness enhancement
            img = ImageEnhance.Color(img).enhance(random.uniform(0.98, 1.02))
            img = ImageEnhance.Brightness(img).enhance(random.uniform(0.98, 1.02))

            # Apply ICC profile
            img = apply_icc_profile(img, icc_profile)

            # Save with metadata
            if original_format == 'PNG':
                return save_image(img, "PNG", preserve_alpha=False)
            else:
                # Generate EXIF metadata
                try:
                    exif_dict = {
                        "0th": {
                            piexif.ImageIFD.Artist: random_string(8).encode(),
                            piexif.ImageIFD.ImageDescription: random_string(12).encode()
                        },
                        "Exif": {
                            piexif.ExifIFD.UserComment: random_string(16).encode()
                        }
                    }
                    exif_bytes = piexif.dump(exif_dict)
                except:
                    exif_bytes = generate_random_metadata()
                
                return save_image(img, "JPEG", quality=100, exif_bytes=exif_bytes)

        except Exception as e:
            # Fallback: return original with new metadata
            return image_bytes

