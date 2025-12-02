#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки данных изображения.

Использование:
    python check_image_data.py <путь_к_изображению>
"""

import sys
import os
from PIL import Image

try:
    import piexif
    HAS_PIEXIF = True
except ImportError:
    HAS_PIEXIF = False
    print("Warning: piexif not installed. EXIF data will be limited.")


def check_image_data(image_path):
    """Проверить данные изображения."""
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return
    
    print(f"\n{'='*60}")
    print(f"Image: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    
    # Основная информация
    print(f"\n📸 Basic Info:")
    print(f"  Format: {img.format}")
    print(f"  Mode: {img.mode}")
    print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
    print(f"  File size: {os.path.getsize(image_path)} bytes")
    
    # PNG параметры
    if img.format == "PNG":
        print(f"\n🖼️  PNG Info:")
        if 'dpi' in img.info:
            print(f"  DPI: {img.info['dpi']}")
        print(f"  Info keys: {list(img.info.keys())}")
    
    # EXIF данные
    if HAS_PIEXIF:
        try:
            exif_dict = piexif.load(image_path)
            
            print(f"\n📋 EXIF Data:")
            
            # White Balance
            if "Exif" in exif_dict:
                exif = exif_dict["Exif"]
                if piexif.ExifIFD.WhiteBalance in exif:
                    wb = exif[piexif.ExifIFD.WhiteBalance]
                    wb_text = "Auto" if wb == 0 else "Manual" if wb == 1 else str(wb)
                    print(f"  White Balance: {wb_text} ({wb})")
                
                # Aperture
                if piexif.ExifIFD.FNumber in exif:
                    fnum = exif[piexif.ExifIFD.FNumber]
                    if isinstance(fnum, tuple) and len(fnum) == 2:
                        aperture = fnum[0] / fnum[1]
                        print(f"  Aperture: f/{aperture:.1f}")
            
            # Resolution
            if "0th" in exif_dict:
                zeroth = exif_dict["0th"]
                if piexif.ImageIFD.XResolution in zeroth:
                    xres = zeroth[piexif.ImageIFD.XResolution]
                    if isinstance(xres, tuple) and len(xres) == 2:
                        dpi = xres[0] / xres[1]
                        print(f"  Resolution: {dpi:.0f} DPI")
        except Exception as e:
            print(f"  No EXIF data or error reading: {e}")
    else:
        print(f"\n📋 EXIF Data:")
        print(f"  (piexif not installed - install with: pip install piexif)")
    
    # Hash для проверки уникальности
    import hashlib
    with open(image_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    print(f"\n🔐 Hash (MD5):")
    print(f"  {file_hash}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        check_image_data(image_path)
    else:
        print("Usage: python check_image_data.py <image_path>")
        print("\nExample:")
        print("  python check_image_data.py photo_1_of_20.jpg")
        print("\nTo check all files in a directory:")
        print("  for file in *.jpg; do python check_image_data.py \"$file\"; done")



