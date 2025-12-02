"""
Pytest fixtures for Image Uniqueization Bot tests.
"""

import io
import pytest
from PIL import Image


@pytest.fixture
def sample_jpeg_bytes():
    """Create a sample JPEG image as bytes."""
    img = Image.new("RGB", (100, 100), color=(255, 128, 64))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_png_bytes():
    """Create a sample PNG image as bytes."""
    img = Image.new("RGBA", (100, 100), color=(255, 128, 64, 255))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_png_transparent_bytes():
    """Create a sample PNG image with transparency."""
    img = Image.new("RGBA", (100, 100), color=(255, 128, 64, 128))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def large_jpeg_bytes():
    """Create a larger JPEG image for quality testing."""
    img = Image.new("RGB", (1920, 1080), color=(100, 150, 200))
    # Add some variation for realistic testing
    pixels = img.load()
    for x in range(0, 1920, 10):
        for y in range(0, 1080, 10):
            pixels[x, y] = ((x * 3) % 256, (y * 2) % 256, ((x + y) * 5) % 256)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)
    return buffer.getvalue()
