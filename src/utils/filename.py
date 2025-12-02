"""
Filename generation utilities for random file names.
"""

import os
import random
import string
from typing import Optional


def generate_random_filename(original_filename: Optional[str] = None, prefix: str = "photo") -> str:
    """
    Generate random filename starting with prefix.
    
    Args:
        original_filename: Original filename (optional, for extension extraction)
        prefix: Prefix for filename (default: "photo")
    
    Returns:
        Random filename with descriptive text (e.g., "photo_unique_a3f9b2c8x7y2.jpg" or "photo_processed_m5n8p2q4k9j3.png")
    
    Examples:
        >>> generate_random_filename("image.jpg")
        'photo_unique_a3f9b2c8x7y2.jpg'
        >>> generate_random_filename("test.png", prefix="image")
        'image_processed_x7y2z9w1m5n8.png'
    """
    import time
    
    # Descriptive words for filenames
    descriptive_words = [
        "unique", "processed", "enhanced", "modified", "optimized",
        "refined", "updated", "edited", "transformed", "customized",
        "improved", "adjusted", "refined", "polished", "finalized"
    ]
    
    # Extract extension from original filename or use default
    if original_filename:
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = ".jpg"
    else:
        ext = ".jpg"
    
    # Choose random descriptive word
    descriptive_word = random.choice(descriptive_words)
    
    # Generate random suffix (12-16 characters for maximum uniqueness)
    random_length = random.randint(12, 16)
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random_length))
    
    # Add microsecond component for extra uniqueness
    time_component = str(int(time.time() * 1000000) % 1000000)  # Last 6 digits of microseconds
    
    # Build filename: prefix_descriptiveword_randomsuffix_time.ext
    filename = f"{prefix}_{descriptive_word}_{random_suffix}_{time_component}{ext}"
    
    return filename


def generate_numbered_filename(
    base_filename: str,
    index: int,
    total: Optional[int] = None,
    prefix: str = "photo"
) -> str:
    """
    Generate numbered filename with random suffix.
    
    Args:
        base_filename: Base filename (for extension)
        index: Current index (1-based)
        total: Total number of files (optional, for zero-padding)
        prefix: Prefix for filename (default: "photo")
    
    Returns:
        Numbered filename (e.g., "photo_1_a3f9.jpg" or "photo_01_b2c8.jpg")
    
    Examples:
        >>> generate_numbered_filename("image.jpg", 1)
        'photo_1_a3f9.jpg'
        >>> generate_numbered_filename("test.png", 5, total=20)
        'photo_05_b2c8.png'
    """
    # Extract extension
    _, ext = os.path.splitext(base_filename)
    if not ext:
        ext = ".jpg"
    
    # Generate random suffix
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    
    # Format number with zero-padding if total is provided and > 9
    if total and total > 9:
        number_str = f"{index:02d}"
    else:
        number_str = str(index)
    
    # Build filename: prefix_number_random.ext
    filename = f"{prefix}_{number_str}_{random_suffix}{ext}"
    
    return filename


def normalize_to_photo(filename: str) -> str:
    """
    Normalize filename to start with "photo" prefix.
    
    If filename already starts with "photo", keeps it.
    Otherwise, replaces the base name with "photo".
    
    Args:
        filename: Original filename
    
    Returns:
        Normalized filename starting with "photo"
    
    Examples:
        >>> normalize_to_photo("image.jpg")
        'photo.jpg'
        >>> normalize_to_photo("my_file.png")
        'photo.png'
        >>> normalize_to_photo("photo_001.jpg")
        'photo_001.jpg'
    """
    name, ext = os.path.splitext(filename)
    
    if not ext:
        ext = ".jpg"
    
    # If already starts with "photo", keep it
    if name.lower().startswith("photo"):
        return filename
    
    # Otherwise, replace with "photo"
    return f"photo{ext}"


