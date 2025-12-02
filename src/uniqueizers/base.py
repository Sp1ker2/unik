"""
Base class for image uniqueization methods.
"""

import io
from abc import ABC, abstractmethod
from typing import Tuple, Optional

from PIL import Image

from src.config import MIN_SSIM, MAX_SIZE_RATIO


class BaseUniqueizer(ABC):
    """Abstract base class for all uniqueization methods."""

    @abstractmethod
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image and return uniqueized version.

        Args:
            image_bytes: Original image as bytes

        Returns:
            Uniqueized image as bytes
        """
        pass

    def validate_quality(
        self, original_bytes: bytes, processed_bytes: bytes
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that processed image meets quality requirements.

        Args:
            original_bytes: Original image bytes
            processed_bytes: Processed image bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        from src.utils.image import calculate_ssim

        # Check SSIM
        ssim_value = calculate_ssim(original_bytes, processed_bytes)
        if ssim_value < MIN_SSIM:
            return False, "SSIM {:.4f} below threshold {}".format(ssim_value, MIN_SSIM)

        # Check size ratio
        size_ratio = len(processed_bytes) / len(original_bytes)
        if size_ratio > MAX_SIZE_RATIO:
            return False, "Size ratio {:.2f} exceeds maximum {}".format(size_ratio, MAX_SIZE_RATIO)

        return True, None

    def _load_image(self, image_bytes: bytes) -> Tuple[Image.Image, str]:
        """
        Load image from bytes and detect format.

        Args:
            image_bytes: Image as bytes

        Returns:
            Tuple of (PIL Image, format string)
        """
        buffer = io.BytesIO(image_bytes)
        img = Image.open(buffer)
        original_format = img.format or "JPEG"
        return img, original_format

    def _save_image(
        self,
        img: Image.Image,
        original_format: str,
        quality: int = 95,
        exif_bytes: Optional[bytes] = None,
    ) -> bytes:
        """
        Save image to bytes preserving format.

        Args:
            img: PIL Image to save
            original_format: Original format (JPEG, PNG)
            quality: JPEG quality (ignored for PNG)
            exif_bytes: Optional EXIF data for JPEG

        Returns:
            Image as bytes
        """
        output = io.BytesIO()

        if original_format.upper() == "PNG":
            img.save(output, format="PNG", optimize=False)
        else:
            save_kwargs = {"format": "JPEG", "quality": quality}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes
            # Ensure RGB mode for JPEG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output, **save_kwargs)

        output.seek(0)
        return output.getvalue()
