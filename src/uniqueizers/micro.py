"""
Micro-changes uniqueization method.

Applies imperceptible pixel modifications:
- Subpixel shift (1-2 pixels)
- Micro brightness adjustment (±0.5%)
- Micro color adjustment (±0.5%)
"""

import random

from PIL import ImageEnhance

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image, get_icc_profile, apply_icc_profile, preserve_transparency
from src.utils.metadata import generate_random_metadata


class MicroUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that applies micro-changes to pixels.

    This method:
    - Applies subpixel shift (0-2 pixels from edges)
    - Adjusts brightness by ±0.5% (imperceptible)
    - Adjusts color saturation by ±0.5% (imperceptible)
    - Generates new metadata

    Best for: Balance between uniqueization and quality.
    SSIM typically >= 0.995
    """

    def __init__(
        self,
        max_shift: int = 2,
        brightness_range: tuple = (0.995, 1.005),
        color_range: tuple = (0.995, 1.005),
    ):
        """
        Initialize micro uniqueizer.

        Args:
            max_shift: Maximum pixel shift from edges (0-3)
            brightness_range: Range for brightness adjustment
            color_range: Range for color saturation adjustment
        """
        self.max_shift = max_shift
        self.brightness_range = brightness_range
        self.color_range = color_range

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image with micro-changes.

        Args:
            image_bytes: Original image as bytes

        Returns:
            Image with micro-modifications
        """
        img, original_format = load_image(image_bytes)
        icc_profile = get_icc_profile(image_bytes)

        # Preserve transparency for PNG
        has_alpha = img.mode == "RGBA"
        alpha_channel = None
        if has_alpha:
            alpha_channel = img.split()[3]
            img = preserve_transparency(img)

        # Apply subpixel shift (random crop from edges)
        width, height = img.size
        shift = random.randint(0, self.max_shift)

        if shift > 0 and width > shift * 2 and height > shift * 2:
            # Random offset for crop position
            x_offset = random.randint(0, shift)
            y_offset = random.randint(0, shift)
            img = img.crop((
                x_offset,
                y_offset,
                width - (shift - x_offset),
                height - (shift - y_offset)
            ))

        # Apply micro brightness adjustment
        if img.mode in ("RGBA", "RGB", "L"):
            # For RGBA, we need to handle alpha separately
            if img.mode == "RGBA":
                rgb_img = img.convert("RGB")
                rgb_img = ImageEnhance.Brightness(rgb_img).enhance(
                    random.uniform(*self.brightness_range)
                )
                rgb_img = ImageEnhance.Color(rgb_img).enhance(
                    random.uniform(*self.color_range)
                )
                # Merge back with alpha
                r, g, b = rgb_img.split()
                if alpha_channel:
                    # Resize alpha to match new size
                    alpha_resized = alpha_channel.resize(img.size)
                    img = Image.merge("RGBA", (r, g, b, alpha_resized))
                else:
                    img = rgb_img.convert("RGBA")
            else:
                img = ImageEnhance.Brightness(img).enhance(
                    random.uniform(*self.brightness_range)
                )
                img = ImageEnhance.Color(img).enhance(
                    random.uniform(*self.color_range)
                )

        # Apply ICC profile
        img = apply_icc_profile(img, icc_profile)

        # Save with appropriate format
        if original_format.upper() == "PNG":
            return save_image(img, "PNG", preserve_alpha=has_alpha)
        else:
            exif_bytes = generate_random_metadata()
            return save_image(img, "JPEG", quality=95, exif_bytes=exif_bytes)


# Import Image at module level for merge operation
from PIL import Image
