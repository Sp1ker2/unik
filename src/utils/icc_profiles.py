# -*- coding: utf-8 -*-
"""
ICC Profile utilities for image uniqueization.

Uses compact ICC profiles from: https://github.com/saucecontrol/Compact-ICC-Profiles
These profiles are minimal and perfect for embedding in images.
"""

import os
import random
from typing import Optional, List, Dict
from pathlib import Path


# Список доступных ICC профилей из репозитория
# Эти профили можно скачать из: https://github.com/saucecontrol/Compact-ICC-Profiles/tree/master/profiles
ICC_PROFILES = {
    # sRGB профили (самые распространенные)
    "sRGB-v2-nano": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/sRGB-v2-nano.icc",
        "size": 410,
        "description": "sRGB nano (20-point curve)",
    },
    "sRGB-v2-micro": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/sRGB-v2-micro.icc",
        "size": 456,
        "description": "sRGB micro (44-point curve)",
    },
    "sRGB-v2-magic": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/sRGB-v2-magic.icc",
        "size": 790,
        "description": "sRGB magic (209-point curve)",
    },
    "sRGB-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/sRGB-v4.icc",
        "size": 480,
        "description": "sRGB V4 (parametric curve)",
    },
    
    # Adobe совместимые профили
    "AdobeRGB-v2": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/AdobeCompat-v2.icc",
        "size": 374,
        "description": "Adobe RGB (1998) V2",
    },
    "AdobeRGB-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/AdobeCompat-v4.icc",
        "size": 480,
        "description": "Adobe RGB (1998) V4",
    },
    "AppleRGB-v2": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/AppleCompat-v2.icc",
        "size": 374,
        "description": "Apple RGB V2",
    },
    "AppleRGB-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/AppleCompat-v4.icc",
        "size": 480,
        "description": "Apple RGB V4",
    },
    "WideGamut-v2": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/WideGamutCompat-v2.icc",
        "size": 374,
        "description": "Wide Gamut RGB V2",
    },
    "WideGamut-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/WideGamutCompat-v4.icc",
        "size": 480,
        "description": "Wide Gamut RGB V4",
    },
    
    # Rec. 709 профили
    "Rec709-v2-micro": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec709-v2-micro.icc",
        "size": 456,
        "description": "Rec. 709 micro",
    },
    "Rec709-v2-magic": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec709-v2-magic.icc",
        "size": 790,
        "description": "Rec. 709 magic",
    },
    "Rec709-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec709-v4.icc",
        "size": 480,
        "description": "Rec. 709 V4",
    },
    
    # Rec. 2020 профили (HDR)
    "Rec2020-v2-micro": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec2020-v2-micro.icc",
        "size": 460,
        "description": "Rec. 2020 micro",
    },
    "Rec2020-v2-magic": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec2020-v2-magic.icc",
        "size": 790,
        "description": "Rec. 2020 magic",
    },
    "Rec2020-v4": {
        "url": "https://github.com/saucecontrol/Compact-ICC-Profiles/raw/master/profiles/Rec2020-v4.icc",
        "size": 480,
        "description": "Rec. 2020 V4",
    },
}


def get_profiles_dir() -> Path:
    """Get directory for storing ICC profiles."""
    profiles_dir = Path(__file__).parent.parent / "icc_profiles"
    profiles_dir.mkdir(exist_ok=True)
    return profiles_dir


def download_profile(profile_name: str, force: bool = False) -> Optional[bytes]:
    """
    Download ICC profile from GitHub.
    
    Args:
        profile_name: Name of the profile from ICC_PROFILES dict
        force: Force re-download even if file exists
        
    Returns:
        Profile bytes or None if download failed
    """
    if profile_name not in ICC_PROFILES:
        return None
    
    profiles_dir = get_profiles_dir()
    profile_file = profiles_dir / "{}.icc".format(profile_name)
    
    # Check if already downloaded
    if profile_file.exists() and not force:
        try:
            return profile_file.read_bytes()
        except Exception:
            pass
    
    # Download from GitHub
    try:
        import urllib.request
        url = ICC_PROFILES[profile_name]["url"]
        with urllib.request.urlopen(url, timeout=10) as response:
            profile_data = response.read()
            # Validate it's actually an ICC profile (starts with ICC profile header)
            if len(profile_data) > 4 and profile_data[:4] == b"acsp":
                # Save for future use
                try:
                    profile_file.write_bytes(profile_data)
                except Exception:
                    pass
                return profile_data
            else:
                return None
    except Exception:
        # Silent fail - return None
        return None


def get_random_profile() -> Optional[bytes]:
    """
    Get a random ICC profile.
    
    Returns:
        Random ICC profile bytes or None
    """
    profile_name = random.choice(list(ICC_PROFILES.keys()))
    return download_profile(profile_name)


def get_profile_by_type(profile_type: str = "random") -> Optional[bytes]:
    """
    Get ICC profile by type.
    
    Args:
        profile_type: "sRGB", "AdobeRGB", "AppleRGB", "WideGamut", "Rec709", "Rec2020", or "random"
    
    Returns:
        ICC profile bytes or None
    """
    if profile_type == "random":
        return get_random_profile()
    
    # Filter profiles by type
    matching_profiles = [
        name for name in ICC_PROFILES.keys()
        if name.lower().startswith(profile_type.lower())
    ]
    
    if not matching_profiles:
        # Try alternative names
        type_mapping = {
            "adobe": "AdobeRGB",
            "apple": "AppleRGB",
            "wide": "WideGamut",
            "rec709": "Rec709",
            "rec2020": "Rec2020",
            "srgb": "sRGB",
        }
        for key, value in type_mapping.items():
            if key in profile_type.lower():
                matching_profiles = [
                    name for name in ICC_PROFILES.keys()
                    if name.lower().startswith(value.lower())
                ]
                break
    
    if matching_profiles:
        profile_name = random.choice(matching_profiles)
        return download_profile(profile_name)
    
    return get_random_profile()


def apply_icc_profile_to_image(img, profile_bytes: bytes) -> None:
    """
    Apply ICC profile to PIL Image.
    
    Args:
        img: PIL Image
        profile_bytes: ICC profile bytes
    """
    if profile_bytes:
        img.info["icc_profile"] = profile_bytes


def get_all_profile_names() -> List[str]:
    """Get list of all available profile names."""
    return list(ICC_PROFILES.keys())


def get_profile_info(profile_name: str) -> Optional[Dict]:
    """Get information about a profile."""
    if profile_name in ICC_PROFILES:
        return ICC_PROFILES[profile_name].copy()
    return None

