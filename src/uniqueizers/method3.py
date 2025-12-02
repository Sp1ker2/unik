# -*- coding: utf-8 -*-
"""
Method 3: Combined method1 and method2
- All features from method1 (crop, color, brightness, EXIF)
- All features from method2 (advanced processing, variants)
- Generates 6 variants with combined processing
"""

from .base import BaseUniqueizer
from .method1 import Method1Uniqueizer
from .method2 import Method2Uniqueizer
from src.utils.image import load_image, save_image
from src.utils.metadata import generate_random_metadata
import piexif
import random
import string


def random_string(length):
    """Generate random string for EXIF."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for _ in range(length))


class Method3Uniqueizer(BaseUniqueizer):
    """
    Combined method1 and method2 uniqueization.
    
    Applies method2 processing first, then method1 enhancements.
    Generates 6 variants with all features combined.
    """

    def __init__(self, variants=6, mirrored_count=2, rounded_count=2, png_count=3):
        """Initialize method 3 uniqueizer."""
        self.method2 = Method2Uniqueizer(variants, mirrored_count, rounded_count, png_count)
        self.variants = variants

    def process(self, image_bytes: bytes) -> bytes:
        """Process image - returns first variant."""
        return self.process_variants(image_bytes, count=1)[0]

    def process_variants(self, image_bytes: bytes, count: int = None) -> list:
        """
        Process image with combined methods.
        
        Args:
            image_bytes: Original image bytes
            count: Number of variants (default: self.variants)
            
        Returns:
            List of processed image bytes
        """
        if count is None:
            count = self.variants
        
        # First apply method2 processing (get variants)
        method2_variants = self.method2.process_variants(image_bytes, count)
        
        # Then apply method1 enhancements to each variant
        from PIL import ImageEnhance
        
        combined_variants = []
        for variant_bytes in method2_variants:
            try:
                # Load variant
                img, original_format = load_image(variant_bytes)
                
                # Apply method1 enhancements
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Additional color and brightness (method1)
                img = ImageEnhance.Color(img).enhance(random.uniform(0.98, 1.02))
                img = ImageEnhance.Brightness(img).enhance(random.uniform(0.98, 1.02))
                
                # Save with EXIF (method1)
                if original_format.upper() == "PNG":
                    combined_bytes = save_image(img, "PNG", preserve_alpha=True)
                else:
                    # Add EXIF metadata
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
                    
                    combined_bytes = save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)
                
                combined_variants.append(combined_bytes)
            except Exception:
                # Fallback to original variant
                combined_variants.append(variant_bytes)
        
        return combined_variants

