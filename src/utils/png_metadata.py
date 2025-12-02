# -*- coding: utf-8 -*-
"""
PNG metadata utilities.
PNG doesn't support EXIF like JPEG, but we can add text chunks (tEXt, iTXt).
"""

import random
import string
import time
from datetime import datetime, timedelta
from PIL import Image, PngImagePlugin
import io


def random_string(length: int) -> str:
    """Generate random alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def random_datetime() -> datetime:
    """Generate random datetime within last 2 years with random time."""
    days_ago = random.randint(1, 730)  # Last 2 years
    hours_offset = random.randint(0, 23)
    minutes_offset = random.randint(0, 59)
    seconds_offset = random.randint(0, 59)
    dt = datetime.now() - timedelta(days=days_ago, hours=hours_offset, minutes=minutes_offset, seconds=seconds_offset)
    return dt


def add_png_metadata(img: Image.Image) -> Image.Image:
    """
    Add metadata to PNG image using text chunks.
    
    Args:
        img: PIL Image (PNG)
        
    Returns:
        Image with metadata chunks
    """
    dt = random_datetime()
    
    # Generate random metadata with more variety
    cameras = [
        ("Canon", "EOS 5D Mark IV"), ("Canon", "EOS R5"), ("Canon", "EOS R6"), ("Canon", "EOS 90D"),
        ("Nikon", "D850"), ("Nikon", "D780"), ("Nikon", "Z9"), ("Nikon", "Z7 II"),
        ("Sony", "A7 III"), ("Sony", "A7R IV"), ("Sony", "A7S III"), ("Sony", "A1"),
        ("Fujifilm", "X-T4"), ("Fujifilm", "X-T5"), ("Fujifilm", "X-H2"), ("Fujifilm", "GFX 100S"),
        ("Panasonic", "GH5"), ("Panasonic", "GH6"), ("Panasonic", "S1R"), ("Panasonic", "S5 II"),
        ("Apple", "iPhone 15 Pro"), ("Apple", "iPhone 14 Pro"), ("Apple", "iPhone 13 Pro"), ("Apple", "iPhone 12 Pro"),
        ("Samsung", "Galaxy S23"), ("Samsung", "Galaxy S22"), ("Samsung", "Galaxy S21"), ("Samsung", "Galaxy Note 20"),
        ("Google", "Pixel 8 Pro"), ("Google", "Pixel 7 Pro"), ("Google", "Pixel 6 Pro"),
        ("OnePlus", "11 Pro"), ("OnePlus", "10 Pro"), ("OnePlus", "9 Pro"),
        ("Xiaomi", "13 Pro"), ("Xiaomi", "12 Pro"), ("Xiaomi", "11 Ultra"),
        ("Huawei", "P60 Pro"), ("Huawei", "Mate 50 Pro"), ("Huawei", "P50 Pro"),
        ("Olympus", "OM-1"), ("Olympus", "OM-D E-M1 Mark III"), ("Olympus", "PEN-F"),
        ("Leica", "M11"), ("Leica", "Q2"), ("Leica", "SL2-S"),
        ("Pentax", "K-3 III"), ("Pentax", "K-1 Mark II"),
    ]
    make, model = random.choice(cameras)
    
    software_list = [
        "Adobe Photoshop CC 2024", "Adobe Photoshop CC 2023", "Adobe Photoshop 2022",
        "Lightroom Classic 13.0", "Lightroom Classic 12.0", "Lightroom Classic 11.0",
        "GIMP 2.10.34", "GIMP 2.10.32", "GIMP 2.10.30",
        "Capture One 23", "Capture One 22", "Capture One 21",
        "Affinity Photo 2.0", "Affinity Photo 1.10",
        "Corel PaintShop Pro 2023", "Corel PaintShop Pro 2022",
        "DxO PhotoLab 6", "DxO PhotoLab 5",
        "ON1 Photo RAW 2023", "ON1 Photo RAW 2022",
        "Luminar Neo", "Luminar AI",
        "Skylum Aurora HDR", "Topaz Photo AI",
        "Darktable 4.0", "RawTherapee 5.9",
    ]
    
    # Create metadata dictionary for PNG
    metadata = PngImagePlugin.PngInfo()
    
    # Expanded ISO values
    iso_values = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 
                  1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 
                  10000, 12800, 16000, 20000, 25600]
    
    # Add unique identifier for this specific file (includes timestamp for uniqueness)
    timestamp_ms = int(time.time() * 1000000)  # Microseconds
    unique_id = "{}_{}".format(random_string(12), timestamp_ms)
    
    # Add text chunks (tEXt - Latin-1, iTXt - UTF-8)
    metadata.add_text("Author", random_string(12))
    metadata.add_text("Title", random_string(16))
    metadata.add_text("Description", random_string(24))
    metadata.add_text("Software", random.choice(software_list))
    metadata.add_text("Camera", "{} {}".format(make, model))
    metadata.add_text("Make", make)
    metadata.add_text("Model", model)
    metadata.add_text("DateTime", dt.strftime("%Y:%m:%d %H:%M:%S"))
    metadata.add_text("DateTimeOriginal", dt.strftime("%Y:%m:%d %H:%M:%S"))
    metadata.add_text("DateTimeDigitized", dt.strftime("%Y:%m:%d %H:%M:%S"))
    metadata.add_text("ISO", str(random.choice(iso_values)))
    metadata.add_text("FNumber", "f/{}".format(random.choice([1.4, 1.8, 2.0, 2.8, 4.0, 5.6, 8.0, 11, 16, 22])))
    metadata.add_text("ExposureTime", "1/{}".format(random.choice([30, 60, 125, 250, 500, 1000, 2000, 4000, 8000])))
    metadata.add_text("FocalLength", "{}mm".format(random.choice([24, 28, 35, 50, 85, 100, 135, 200, 300, 400])))
    metadata.add_text("Copyright", "(c) {} {}".format(dt.year, random_string(8)))
    metadata.add_text("Comment", random_string(32))
    metadata.add_text("UserComment", random_string(40))
    metadata.add_text("ExposureMode", str(random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8])))
    metadata.add_text("MeteringMode", str(random.choice([1, 2, 3, 4, 5, 6])))
    metadata.add_text("WhiteBalance", str(random.choice([0, 1])))
    metadata.add_text("Flash", str(random.choice([0, 1, 5, 7, 9, 13, 15, 16, 24, 25, 29, 31])))
    # Add unique identifier and additional unique fields
    metadata.add_text("UniqueID", unique_id)
    metadata.add_text("ImageID", random_string(20))
    metadata.add_text("DocumentID", random_string(24))
    metadata.add_text("CreatorTool", random.choice(software_list))
    metadata.add_text("Keywords", random_string(30))
    metadata.add_text("Subject", random_string(28))
    metadata.add_text("Rating", str(random.choice([0, 1, 2, 3, 4, 5])))
    metadata.add_text("ColorSpace", random.choice(["sRGB", "AdobeRGB", "ProPhoto RGB", "Display P3"]))
    metadata.add_text("ColorDepth", str(random.choice([8, 10, 12, 14, 16])))
    
    # Store metadata in image - preserve original info dict
    # Save original info if it's a dict (for ICC profile, etc.)
    original_info = {}
    if hasattr(img, 'info'):
        if isinstance(img.info, dict):
            original_info = img.info.copy()
        elif isinstance(img.info, PngImagePlugin.PngInfo):
            # If already PngInfo, we can't preserve dict info easily
            # Just use new metadata
            img.info = metadata
            return img
    
    # Store PngInfo in 'pnginfo' key, preserve original info
    if not hasattr(img, 'info') or not isinstance(img.info, dict):
        img.info = {}
    img.info['pnginfo'] = metadata
    # Restore original info items (like ICC profile)
    for key, value in original_info.items():
        if key != 'pnginfo':  # Don't overwrite pnginfo
            img.info[key] = value
    
    return img


def save_png_with_metadata(img: Image.Image, output: io.BytesIO) -> None:
    """
    Save PNG with metadata chunks.
    
    Args:
        img: PIL Image
        output: BytesIO output stream
    """
    # Get metadata if present
    pnginfo = None
    if hasattr(img, 'info') and isinstance(img.info, PngImagePlugin.PngInfo):
        pnginfo = img.info
    elif 'pnginfo' in img.info:
        pnginfo = img.info['pnginfo']
    
    # If no metadata, add it
    if not pnginfo:
        img = add_png_metadata(img)
        pnginfo = img.info if isinstance(img.info, PngImagePlugin.PngInfo) else None
    
    # Save with metadata
    if pnginfo:
        img.save(output, format="PNG", pnginfo=pnginfo, optimize=False)
    else:
        img.save(output, format="PNG", optimize=False)

