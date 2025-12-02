# -*- coding: utf-8 -*-
"""
Enhanced metadata generation with device information, GPS, and detailed camera settings.
"""

import random
import string
from datetime import datetime, timedelta
import piexif


def random_string(length: int) -> str:
    """Generate random alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def random_datetime() -> datetime:
    """Generate random datetime within last year."""
    days_ago = random.randint(1, 365)
    return datetime.now() - timedelta(days=days_ago)


# Расширенный список устройств
SMARTPHONES = [
    ("Apple", "iPhone 15 Pro Max", "iOS 17.1"),
    ("Apple", "iPhone 14 Pro", "iOS 16.6"),
    ("Apple", "iPhone 13", "iOS 15.7"),
    ("Samsung", "Galaxy S23 Ultra", "Android 13"),
    ("Samsung", "Galaxy S22", "Android 12"),
    ("Samsung", "Galaxy Note 20", "Android 11"),
    ("Xiaomi", "Mi 13 Pro", "Android 13"),
    ("Xiaomi", "Redmi Note 12", "Android 12"),
    ("Google", "Pixel 7 Pro", "Android 13"),
    ("Google", "Pixel 6", "Android 12"),
    ("OnePlus", "11 Pro", "Android 13"),
    ("Huawei", "P60 Pro", "HarmonyOS 3.0"),
    ("OPPO", "Find X6 Pro", "Android 13"),
    ("Vivo", "X90 Pro", "Android 13"),
]

TABLETS = [
    ("Apple", "iPad Pro 12.9-inch", "iOS 17.1"),
    ("Apple", "iPad Air", "iOS 16.6"),
    ("Samsung", "Galaxy Tab S9", "Android 13"),
    ("Microsoft", "Surface Pro 9", "Windows 11"),
]

CAMERAS = [
    ("Canon", "EOS R5", "Firmware 1.8.1"),
    ("Canon", "EOS 5D Mark IV", "Firmware 1.3.6"),
    ("Canon", "EOS R6", "Firmware 1.6.2"),
    ("Nikon", "D850", "Firmware C 1.20"),
    ("Nikon", "Z9", "Firmware 4.10"),
    ("Nikon", "Z7 II", "Firmware 1.60"),
    ("Sony", "A7R V", "Firmware 2.00"),
    ("Sony", "A7 III", "Firmware 4.01"),
    ("Sony", "A1", "Firmware 2.00"),
    ("Fujifilm", "X-T5", "Firmware 1.20"),
    ("Fujifilm", "X-T4", "Firmware 1.80"),
    ("Panasonic", "Lumix GH6", "Firmware 2.0"),
    ("Olympus", "OM-1", "Firmware 1.4"),
    ("Leica", "Q2", "Firmware 4.0"),
]


def generate_random_gps() -> dict:
    """Generate random GPS coordinates."""
    # Популярные города с координатами
    cities = [
        {"lat": 55.7558, "lon": 37.6173, "alt": 156},  # Moscow
        {"lat": 40.7128, "lon": -74.0060, "alt": 10},  # New York
        {"lat": 51.5074, "lon": -0.1278, "alt": 35},   # London
        {"lat": 48.8566, "lon": 2.3522, "alt": 35},   # Paris
        {"lat": 52.5200, "lon": 13.4050, "alt": 34},  # Berlin
        {"lat": 35.6762, "lon": 139.6503, "alt": 40}, # Tokyo
        {"lat": 37.7749, "lon": -122.4194, "alt": 16}, # San Francisco
        {"lat": 34.0522, "lon": -118.2437, "alt": 71}, # Los Angeles
        {"lat": 25.2048, "lon": 55.2708, "alt": 5},   # Dubai
        {"lat": -33.8688, "lon": 151.2093, "alt": 19}, # Sydney
    ]
    
    city = random.choice(cities)
    # Добавляем небольшую случайность (±0.01 градуса)
    lat = city["lat"] + random.uniform(-0.01, 0.01)
    lon = city["lon"] + random.uniform(-0.01, 0.01)
    alt = city["alt"] + random.randint(-10, 10)
    
    return {
        piexif.GPSIFD.GPSLatitudeRef: b"N" if lat >= 0 else b"S",
        piexif.GPSIFD.GPSLatitude: _deg_to_dms(abs(lat)),
        piexif.GPSIFD.GPSLongitudeRef: b"E" if lon >= 0 else b"W",
        piexif.GPSIFD.GPSLongitude: _deg_to_dms(abs(lon)),
        piexif.GPSIFD.GPSAltitudeRef: 0 if alt >= 0 else 1,
        piexif.GPSIFD.GPSAltitude: (int(abs(alt) * 100), 100),
    }


def _deg_to_dms(deg: float) -> tuple:
    """Convert degrees to degrees, minutes, seconds tuple."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60 * 100)
    return ((d, 1), (m, 1), (s, 100))


def generate_enhanced_metadata(include_gps: bool = True, device_type: str = "random") -> bytes:
    """
    Generate enhanced EXIF metadata with device information.
    
    Args:
        include_gps: Whether to include GPS coordinates
        device_type: "smartphone", "tablet", "camera", or "random"
    
    Returns:
        EXIF bytes for embedding in JPEG
    """
    dt = random_datetime()
    dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
    
    # Выбор устройства
    if device_type == "smartphone":
        make, model, os_version = random.choice(SMARTPHONES)
    elif device_type == "tablet":
        make, model, os_version = random.choice(TABLETS)
    elif device_type == "camera":
        make, model, os_version = random.choice(CAMERAS)
    else:  # random
        all_devices = SMARTPHONES + TABLETS + CAMERAS
        make, model, os_version = random.choice(all_devices)
    
    # Настройки камеры
    iso_values = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 
                  1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 
                  10000, 12800, 16000, 20000, 25600]
    
    f_numbers = [(14, 10), (18, 10), (20, 10), (28, 10), (40, 10), (56, 10), 
                 (80, 10), (110, 10), (160, 10), (220, 10)]
    
    exposure_times = [(1, 30), (1, 60), (1, 125), (1, 250), (1, 500), (1, 1000),
                      (1, 2000), (1, 4000), (1, 8000)]
    
    focal_lengths = [(24, 1), (28, 1), (35, 1), (50, 1), (85, 1), (100, 1),
                     (135, 1), (200, 1), (300, 1), (400, 1)]
    
    # Режимы съемки
    exposure_modes = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # Auto, Manual, etc.
    metering_modes = [1, 2, 3, 4, 5, 6]  # Average, Center, Spot, etc.
    white_balance_modes = [0, 1]  # Auto, Manual
    flash_modes = [0, 1, 5, 7, 9, 13, 15, 16, 24, 25, 29, 31]  # Various flash modes
    
    software_list = [
        "Adobe Photoshop CC 2024",
        "Lightroom Classic 13.0",
        "GIMP 2.10.34",
        "Capture One 23",
        "DxO PhotoLab 7",
        "Affinity Photo 2",
        "Darktable 4.4",
    ]
    
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: make.encode(),
            piexif.ImageIFD.Model: model.encode(),
            piexif.ImageIFD.Software: random.choice(software_list).encode(),
            piexif.ImageIFD.DateTime: dt_str.encode(),
            piexif.ImageIFD.Artist: random_string(8).encode(),
            piexif.ImageIFD.Copyright: "(c) {} {}".format(dt.year, random_string(6)).encode(),
            piexif.ImageIFD.ImageDescription: random_string(16).encode(),
            piexif.ImageIFD.Orientation: random.choice([1, 3, 6, 8]),  # Orientation
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: dt_str.encode(),
            piexif.ExifIFD.DateTimeDigitized: dt_str.encode(),
            piexif.ExifIFD.UserComment: "Device: {} {} ({})".format(make, model, os_version).encode(),
            piexif.ExifIFD.ExifVersion: b"0231",
            piexif.ExifIFD.ColorSpace: random.choice([1, 65535]),  # sRGB or Uncalibrated
            piexif.ExifIFD.ExposureTime: random.choice(exposure_times),
            piexif.ExifIFD.FNumber: random.choice(f_numbers),
            piexif.ExifIFD.ISOSpeedRatings: random.choice(iso_values),
            piexif.ExifIFD.FocalLength: random.choice(focal_lengths),
            piexif.ExifIFD.ExposureMode: random.choice(exposure_modes),
            piexif.ExifIFD.MeteringMode: random.choice(metering_modes),
            piexif.ExifIFD.WhiteBalance: random.choice(white_balance_modes),
            piexif.ExifIFD.Flash: random.choice(flash_modes),
            piexif.ExifIFD.SceneType: random.choice([0, 1]),  # Directly photographed
            piexif.ExifIFD.FocalLengthIn35mmFilm: random.choice([24, 28, 35, 50, 85, 135, 200]),
        },
        "1st": {},
        "thumbnail": None,
    }
    
    # Добавляем GPS если нужно
    if include_gps:
        exif_dict["GPS"] = generate_random_gps()
    
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
            "Exif": {},
            "1st": {},
            "thumbnail": None,
        }
        if include_gps:
            minimal_exif["GPS"] = generate_random_gps()
        return piexif.dump(minimal_exif)

