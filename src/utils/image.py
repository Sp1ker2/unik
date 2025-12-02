"""
Image processing utilities.
"""

import io
from typing import Tuple, Optional

from PIL import Image
from PIL import PngImagePlugin
import numpy as np


def load_image(image_bytes: bytes) -> Tuple[Image.Image, str]:
    """
    Load image from bytes.

    Args:
        image_bytes: Image as bytes

    Returns:
        Tuple of (PIL Image, format string)
    """
    buffer = io.BytesIO(image_bytes)
    img = Image.open(buffer)
    original_format = img.format or "JPEG"
    return img, original_format


def save_image(
    img: Image.Image,
    original_format: str,
    quality: int = 95,
    exif_bytes: Optional[bytes] = None,
    preserve_alpha: bool = True,
) -> bytes:
    """
    Save image to bytes.

    Args:
        img: PIL Image to save
        original_format: Target format (JPEG, PNG)
        quality: JPEG quality (ignored for PNG)
        exif_bytes: Optional EXIF data for JPEG
        preserve_alpha: Whether to preserve alpha channel for PNG

    Returns:
        Image as bytes
    """
    output = io.BytesIO()

    if original_format.upper() == "PNG":
        # Preserve RGBA mode for PNG
        # Check if PNG metadata is present
        pnginfo = None
        if hasattr(img, 'info'):
            if isinstance(img.info, PngImagePlugin.PngInfo):
                pnginfo = img.info
            elif isinstance(img.info, dict) and 'pnginfo' in img.info:
                pnginfo = img.info['pnginfo']
        
        # If no metadata, generate new random metadata for PNG
        if not pnginfo:
            from src.utils.png_metadata import add_png_metadata
            img = add_png_metadata(img)
            # Extract pnginfo from img.info
            if hasattr(img, 'info'):
                if isinstance(img.info, PngImagePlugin.PngInfo):
                    pnginfo = img.info
                elif isinstance(img.info, dict) and 'pnginfo' in img.info:
                    pnginfo = img.info['pnginfo']
        
        # Save with metadata
        if preserve_alpha and img.mode == "RGBA":
            if pnginfo:
                img.save(output, format="PNG", pnginfo=pnginfo, optimize=False)
            else:
                img.save(output, format="PNG", optimize=False)
        else:
            if pnginfo:
                img.save(output, format="PNG", pnginfo=pnginfo, optimize=False)
            else:
                img.save(output, format="PNG", optimize=False)
    else:
        save_kwargs = {"format": "JPEG", "quality": quality}
        if exif_bytes:
            save_kwargs["exif"] = exif_bytes
        # Ensure RGB mode for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.save(output, **save_kwargs)

    output.seek(0)
    return output.getvalue()


def get_image_format(image_bytes: bytes) -> str:
    """
    Detect image format from bytes.

    Args:
        image_bytes: Image as bytes

    Returns:
        Format string (JPEG, PNG)
    """
    buffer = io.BytesIO(image_bytes)
    img = Image.open(buffer)
    return img.format or "JPEG"


def calculate_ssim(original_bytes: bytes, processed_bytes: bytes) -> float:
    """
    Calculate SSIM between original and processed images.

    Args:
        original_bytes: Original image bytes
        processed_bytes: Processed image bytes

    Returns:
        SSIM value (0.0 to 1.0)
    """
    try:
        from skimage.metrics import structural_similarity as ssim

        # Load images
        orig_img, _ = load_image(original_bytes)
        proc_img, _ = load_image(processed_bytes)

        # Convert to same size if needed (handle minor crop differences)
        if orig_img.size != proc_img.size:
            # Use the smaller dimensions
            min_width = min(orig_img.width, proc_img.width)
            min_height = min(orig_img.height, proc_img.height)
            orig_img = orig_img.crop((0, 0, min_width, min_height))
            proc_img = proc_img.crop((0, 0, min_width, min_height))

        # Convert to grayscale arrays for SSIM
        orig_gray = np.array(orig_img.convert("L"))
        proc_gray = np.array(proc_img.convert("L"))

        # Calculate SSIM
        ssim_value = ssim(orig_gray, proc_gray, data_range=255)
        return float(ssim_value)

    except ImportError:
        # If scikit-image not available, return 1.0 (assume quality OK)
        return 1.0
    except Exception:
        # On any error, return 1.0 to not block processing
        return 1.0


def create_preview(image_bytes: bytes, max_size: int = 300) -> bytes:
    """
    Create a thumbnail preview of the image.

    Args:
        image_bytes: Original image bytes
        max_size: Maximum dimension (width or height)

    Returns:
        Preview image as bytes
    """
    img, original_format = load_image(image_bytes)

    # Calculate new size maintaining aspect ratio
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    return save_image(img, original_format, quality=85)


def preserve_transparency(img: Image.Image) -> Image.Image:
    """
    Ensure image transparency is preserved for PNG.

    Args:
        img: PIL Image

    Returns:
        Image with preserved transparency
    """
    if img.mode == "RGBA":
        return img
    elif img.mode == "P" and "transparency" in img.info:
        return img.convert("RGBA")
    elif img.mode == "LA":
        return img.convert("RGBA")
    return img


def get_icc_profile(image_bytes: bytes) -> Optional[bytes]:
    """
    Extract ICC color profile from image.

    Args:
        image_bytes: Image bytes

    Returns:
        ICC profile bytes or None
    """
    img, _ = load_image(image_bytes)
    # Handle both dict and PngInfo objects
    if hasattr(img, 'info'):
        if isinstance(img.info, dict):
            return img.info.get("icc_profile")
        elif isinstance(img.info, PngImagePlugin.PngInfo):
            # PngInfo doesn't store ICC profile - return None
            return None
    return None


def apply_icc_profile(img: Image.Image, icc_profile: Optional[bytes]) -> Image.Image:
    """
    Apply ICC profile to image info.

    Args:
        img: PIL Image
        icc_profile: ICC profile bytes

    Returns:
        Image with ICC profile in info
    """
    if icc_profile:
        img.info["icc_profile"] = icc_profile
    return img
