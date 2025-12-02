"""
EXIF/IPTC/XMP metadata utilities.
"""

import io
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from PIL import Image, PngImagePlugin
import piexif


def random_string(length: int) -> str:
    """Generate random alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def random_datetime() -> datetime:
    """Generate random datetime within last year."""
    days_ago = random.randint(1, 365)
    return datetime.now() - timedelta(days=days_ago)


def remove_metadata(image_bytes: bytes) -> bytes:
    """
    Remove all metadata from image.

    Args:
        image_bytes: Image with metadata

    Returns:
        Image without metadata
    """
    buffer = io.BytesIO(image_bytes)
    img = Image.open(buffer)
    original_format = img.format or "JPEG"

    # Create new image without metadata
    if img.mode in ("RGBA", "P"):
        # For PNG with transparency
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(list(img.getdata()))
    else:
        new_img = Image.new("RGB", img.size)
        if img.mode != "RGB":
            img = img.convert("RGB")
        new_img.putdata(list(img.getdata()))

    output = io.BytesIO()
    if original_format.upper() == "PNG":
        new_img.save(output, format="PNG")
    else:
        new_img.save(output, format="JPEG", quality=95)

    output.seek(0)
    return output.getvalue()


def generate_random_metadata() -> bytes:
    """
    Generate random EXIF metadata with enhanced information.

    Returns:
        EXIF bytes for embedding in JPEG
    """
    # Try to use enhanced metadata first
    try:
        from src.utils.enhanced_metadata import generate_enhanced_metadata
        return generate_enhanced_metadata(include_gps=False, device_type="random")
    except Exception:
        pass
    
    # Fallback to basic metadata
    # Random datetime
    dt = random_datetime()
    dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")

    # Random camera info (expanded list)
    cameras = [
        ("Canon", "EOS 5D Mark IV"),
        ("Canon", "EOS R5"),
        ("Nikon", "D850"),
        ("Nikon", "Z9"),
        ("Sony", "A7 III"),
        ("Sony", "A7R V"),
        ("Fujifilm", "X-T5"),
        ("Fujifilm", "X-T4"),
        ("Panasonic", "GH6"),
        ("Apple", "iPhone 15 Pro"),
        ("Samsung", "Galaxy S23"),
        ("Google", "Pixel 7"),
    ]
    make, model = random.choice(cameras)

    # Random software
    software_list = [
        "Adobe Photoshop CC 2024",
        "Lightroom Classic 13.0",
        "GIMP 2.10.34",
        "Capture One 23",
        "DxO PhotoLab 7",
    ]

    # Expanded ISO values
    iso_values = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 
                  1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 
                  10000, 12800, 16000, 20000, 25600]
    
    # F-number values
    f_numbers = [(14, 10), (18, 10), (20, 10), (28, 10), (40, 10), (56, 10), 
                 (80, 10), (110, 10), (160, 10), (220, 10)]
    
    # Exposure times
    exposure_times = [(1, 30), (1, 60), (1, 125), (1, 250), (1, 500), (1, 1000),
                      (1, 2000), (1, 4000), (1, 8000)]
    
    # Focal lengths
    focal_lengths = [(24, 1), (28, 1), (35, 1), (50, 1), (85, 1), (100, 1),
                     (135, 1), (200, 1), (300, 1), (400, 1)]

    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: make.encode(),
            piexif.ImageIFD.Model: model.encode(),
            piexif.ImageIFD.Software: random.choice(software_list).encode(),
            piexif.ImageIFD.DateTime: dt_str.encode(),
            piexif.ImageIFD.Artist: random_string(12).encode(),
            piexif.ImageIFD.Copyright: "(c) {} {}".format(dt.year, random_string(8)).encode(),
            piexif.ImageIFD.ImageDescription: random_string(20).encode(),
            piexif.ImageIFD.Orientation: random.choice([1, 3, 6, 8]),
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: dt_str.encode(),
            piexif.ExifIFD.DateTimeDigitized: dt_str.encode(),
            piexif.ExifIFD.UserComment: random_string(32).encode(),
            piexif.ExifIFD.ExifVersion: b"0231",
            piexif.ExifIFD.ColorSpace: random.choice([1, 65535]),
            piexif.ExifIFD.ExposureTime: random.choice(exposure_times),
            piexif.ExifIFD.FNumber: random.choice(f_numbers),
            piexif.ExifIFD.ISOSpeedRatings: random.choice(iso_values),
            piexif.ExifIFD.FocalLength: random.choice(focal_lengths),
            piexif.ExifIFD.ExposureMode: random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8]),
            piexif.ExifIFD.MeteringMode: random.choice([1, 2, 3, 4, 5, 6]),
            piexif.ExifIFD.WhiteBalance: random.choice([0, 1]),
            piexif.ExifIFD.Flash: random.choice([0, 1, 5, 7, 9, 13, 15, 16, 24, 25, 29, 31]),
            piexif.ExifIFD.FocalLengthIn35mmFilm: random.choice([24, 28, 35, 50, 85, 135, 200]),
        },
        "1st": {},
        "thumbnail": None,
    }

    try:
        return piexif.dump(exif_dict)
    except Exception:
        # Fallback to minimal EXIF
        minimal_exif = {
            "0th": {
                piexif.ImageIFD.Artist: random_string(8).encode(),
                piexif.ImageIFD.DateTime: dt_str.encode(),
                piexif.ImageIFD.Make: make.encode(),
                piexif.ImageIFD.Model: model.encode(),
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: dt_str.encode(),
                piexif.ExifIFD.UserComment: random_string(24).encode(),
            },
            "1st": {},
            "thumbnail": None,
        }
        return piexif.dump(minimal_exif)


def apply_metadata(image_bytes: bytes, exif_bytes: bytes) -> bytes:
    """
    Apply EXIF metadata to JPEG image.

    Args:
        image_bytes: Image bytes (JPEG)
        exif_bytes: EXIF bytes to apply

    Returns:
        Image with new metadata
    """
    buffer = io.BytesIO(image_bytes)
    img = Image.open(buffer)

    if img.format != "JPEG":
        # PNG doesn't support EXIF in the same way - use PNG metadata instead
        from src.utils.png_metadata import add_png_metadata
        img = add_png_metadata(img)
        output = io.BytesIO()
        if hasattr(img, 'info') and isinstance(img.info, PngImagePlugin.PngInfo):
            img.save(output, format="PNG", pnginfo=img.info, optimize=False)
        else:
            img.save(output, format="PNG", optimize=False)
        output.seek(0)
        return output.getvalue()

    output = io.BytesIO()

    # Ensure RGB mode
    if img.mode != "RGB":
        img = img.convert("RGB")

    img.save(output, format="JPEG", quality=95, exif=exif_bytes)
    output.seek(0)
    return output.getvalue()


def get_metadata_info(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract metadata information from image.

    Args:
        image_bytes: Image bytes

    Returns:
        Dictionary with metadata info
    """
    buffer = io.BytesIO(image_bytes)
    img = Image.open(buffer)

    info = {
        "format": img.format,
        "mode": img.mode,
        "size": img.size,
        "has_exif": False,
        "exif_fields": [],
    }

    if img.format == "JPEG":
        try:
            exif_data = img._getexif()
            if exif_data:
                info["has_exif"] = True
                info["exif_fields"] = list(exif_data.keys())
        except Exception:
            pass

    return info
