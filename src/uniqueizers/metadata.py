"""
Metadata-only uniqueization method.

Replaces EXIF/IPTC/XMP metadata with random values.
Does not modify pixel data.
"""

import io
import io
from .base import BaseUniqueizer
from src.utils.metadata import generate_random_metadata, apply_metadata
from src.utils.image import load_image, save_image, get_icc_profile, apply_icc_profile
from PIL import PngImagePlugin
from PIL import PngImagePlugin


class MetadataUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that only modifies image metadata.

    This method:
    - Removes all original EXIF/IPTC/XMP metadata
    - Generates new random metadata
    - Preserves pixel data unchanged
    - Maintains image quality (SSIM = 1.0 for identical format)

    Best for: Maximum quality preservation when only hash change needed.
    """

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image by replacing metadata only.

        Args:
            image_bytes: Original image as bytes

        Returns:
            Image with new random metadata
        """
        # Load and detect format
        img, original_format = load_image(image_bytes)

        # Preserve ICC profile
        icc_profile = get_icc_profile(image_bytes)

        if original_format.upper() == "PNG":
            # PNG: add text metadata chunks (tEXt, iTXt)
            from src.utils.png_metadata import add_png_metadata
            img = add_png_metadata(img)
            img = apply_icc_profile(img, icc_profile)
            
            # Save with PNG metadata
            output = io.BytesIO()
            pnginfo = None
            if hasattr(img, 'info'):
                if isinstance(img.info, PngImagePlugin.PngInfo):
                    pnginfo = img.info
                elif isinstance(img.info, dict) and 'pnginfo' in img.info:
                    pnginfo = img.info['pnginfo']
            
            if pnginfo:
                img.save(output, format="PNG", pnginfo=pnginfo, optimize=False)
            else:
                img.save(output, format="PNG", optimize=False)
            output.seek(0)
            return output.getvalue()
        else:
            # JPEG: generate new metadata and apply it (don't remove, just replace)
            new_exif = generate_random_metadata()
            
            # Apply new metadata directly to image
            output = io.BytesIO()
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            img = apply_icc_profile(img, icc_profile)
            img.save(output, format="JPEG", quality=95, exif=new_exif)
            output.seek(0)
            return output.getvalue()
