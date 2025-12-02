"""
ZIP archive utilities for multiple image copies.
"""

import io
import zipfile
from typing import List, Tuple


def create_zip_archive(images: List[Tuple[bytes, str]]) -> io.BytesIO:
    """
    Create a ZIP archive containing multiple images.

    Args:
        images: List of tuples (image_bytes, filename)

    Returns:
        BytesIO buffer containing the ZIP archive
    """
    import logging
    logger = logging.getLogger(__name__)
    
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        seen_names = set()
        for image_bytes, filename in images:
            # Ensure unique filename in ZIP (zipfile may rename duplicates)
            original_filename = filename
            counter = 0
            while filename in seen_names:
                name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
                counter += 1
                filename = f"{name}_{counter}.{ext}" if ext else f"{name}_{counter}"
                logger.warning(f"Filename collision in ZIP: {original_filename} -> {filename}")
            
            seen_names.add(filename)
            logger.info(f"Adding to ZIP: {filename} (original: {original_filename})")
            zf.writestr(filename, image_bytes)

    buffer.seek(0)
    logger.info(f"ZIP archive created with {len(images)} files")
    return buffer


def extract_zip_archive(archive_bytes: bytes) -> List[Tuple[bytes, str]]:
    """
    Extract images from a ZIP archive.

    Args:
        archive_bytes: ZIP archive as bytes

    Returns:
        List of tuples (image_bytes, filename)
    """
    buffer = io.BytesIO(archive_bytes)
    images = []

    with zipfile.ZipFile(buffer, "r") as zf:
        for name in zf.namelist():
            # Skip directories and hidden files
            if name.endswith("/") or name.startswith("."):
                continue
            image_bytes = zf.read(name)
            images.append((image_bytes, name))

    return images
