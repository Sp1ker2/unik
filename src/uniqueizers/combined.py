"""
Combined uniqueization method.

Applies all uniqueization methods in sequence for maximum hash change:
1. Metadata replacement
2. Micro-changes (subpixel shift, brightness/color)
3. LSB modification
"""

from .base import BaseUniqueizer
from .metadata import MetadataUniqueizer
from .micro import MicroUniqueizer
from .lsb import LSBUniqueizer


class CombinedUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that combines all methods for maximum uniqueization.

    This method applies in sequence:
    1. Micro-changes (subpixel shift, brightness/color adjustment)
    2. LSB modification (least significant bit changes)
    3. Metadata replacement (new random EXIF data)

    Best for: Maximum uniqueization when hash must be completely different.
    SSIM typically >= 0.99 (meets quality threshold)
    """

    def __init__(self):
        """Initialize combined uniqueizer with all sub-methods."""
        # Use conservative settings for each method to ensure quality
        self.micro = MicroUniqueizer(
            max_shift=1,  # Minimal shift
            brightness_range=(0.997, 1.003),  # ±0.3%
            color_range=(0.997, 1.003),  # ±0.3%
        )
        self.lsb = LSBUniqueizer(
            modification_percent=3.0,  # Only 3% of pixels
            bits_to_modify=1,  # Only 1 bit
        )
        self.metadata = MetadataUniqueizer()

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image with all uniqueization methods.

        Args:
            image_bytes: Original image as bytes

        Returns:
            Fully uniqueized image
        """
        # Step 1: Apply micro-changes (shift, brightness, color)
        result = self.micro.process(image_bytes)

        # Step 2: Apply LSB modifications
        result = self.lsb.process(result)

        # Step 3: Apply metadata changes (also re-saves, ensuring final hash uniqueness)
        result = self.metadata.process(result)

        return result
