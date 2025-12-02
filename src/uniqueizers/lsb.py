"""
LSB (Least Significant Bit) uniqueization method.

Modifies the least significant bits of pixel values.
Changes are mathematically guaranteed but visually imperceptible.
"""

import random
import io

from PIL import Image
import numpy as np

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image, get_icc_profile, apply_icc_profile
from src.utils.metadata import generate_random_metadata


class LSBUniqueizer(BaseUniqueizer):
    """
    Uniqueizer that modifies least significant bits of pixels.

    This method:
    - Modifies LSB of random pixels (configurable percentage)
    - Changes are ±1 in pixel value (invisible to human eye)
    - Guarantees different binary hash
    - Maintains visual quality (SSIM typically >= 0.999)

    Best for: Maximum hash change with minimal visual impact.
    """

    def __init__(self, modification_percent: float = 5.0, bits_to_modify: int = 1):
        """
        Initialize LSB uniqueizer.

        Args:
            modification_percent: Percentage of pixels to modify (0.1-100)
            bits_to_modify: Number of LSB bits to modify (1-2)
        """
        self.modification_percent = max(0.1, min(100, modification_percent))
        self.bits_to_modify = max(1, min(2, bits_to_modify))

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image with LSB modifications.

        Args:
            image_bytes: Original image as bytes

        Returns:
            Image with LSB modifications
        """
        img, original_format = load_image(image_bytes)
        icc_profile = get_icc_profile(image_bytes)

        # Handle different modes
        has_alpha = img.mode == "RGBA"
        original_mode = img.mode

        # Convert to numpy array
        img_array = np.array(img)

        # Calculate number of pixels to modify
        if len(img_array.shape) == 3:
            total_pixels = img_array.shape[0] * img_array.shape[1]
            channels = img_array.shape[2]
            # Don't modify alpha channel
            channels_to_modify = min(channels, 3)
        else:
            total_pixels = img_array.shape[0] * img_array.shape[1]
            channels_to_modify = 1

        pixels_to_modify = max(1, int(total_pixels * self.modification_percent / 100))

        # Generate random positions to modify
        y_positions = np.random.randint(0, img_array.shape[0], pixels_to_modify)
        x_positions = np.random.randint(0, img_array.shape[1], pixels_to_modify)

        # Generate random modifications (+1 or -1 for LSB)
        for i in range(pixels_to_modify):
            y, x = y_positions[i], x_positions[i]

            if len(img_array.shape) == 3:
                # Modify each color channel independently
                for c in range(channels_to_modify):
                    current_value = int(img_array[y, x, c])
                    # Flip LSB: if even, add 1; if odd, subtract 1
                    if current_value % 2 == 0:
                        new_value = min(255, current_value + 1)
                    else:
                        new_value = max(0, current_value - 1)

                    # For more modification, also flip second bit sometimes
                    if self.bits_to_modify > 1 and random.random() < 0.3:
                        if (new_value >> 1) % 2 == 0:
                            new_value = min(255, new_value + 2)
                        else:
                            new_value = max(0, new_value - 2)

                    img_array[y, x, c] = new_value
            else:
                # Grayscale image
                current_value = int(img_array[y, x])
                if current_value % 2 == 0:
                    new_value = min(255, current_value + 1)
                else:
                    new_value = max(0, current_value - 1)
                img_array[y, x] = new_value

        # Convert back to PIL Image
        modified_img = Image.fromarray(img_array.astype(np.uint8), mode=original_mode)

        # Apply ICC profile
        modified_img = apply_icc_profile(modified_img, icc_profile)

        # Save with appropriate format
        if original_format.upper() == "PNG":
            return save_image(modified_img, "PNG", preserve_alpha=has_alpha)
        else:
            exif_bytes = generate_random_metadata()
            return save_image(modified_img, "JPEG", quality=95, exif_bytes=exif_bytes)
