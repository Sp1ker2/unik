# -*- coding: utf-8 -*-
"""
Pixel Pattern Uniqueization: Creates invisible/visible text pattern overlay.

Based on pixel_bot.py functionality:
- Converts image to pixel array
- Creates pattern of random symbols (letters, digits, special chars)
- Overlays pattern with different alpha values (10 and 255)
- Applies sharpness filters
"""

import random
import copy
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image


def image_to_pixel_array(img):
    """Convert image to pixel array (colors)."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    width, height = img.size
    pixels = []
    pixel_data = img.load()
    
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixel_data[x, y]
            row.append([r, g, b])
        pixels.append(row)
    
    return pixels, width, height


def pixel_array_to_image(pixels, width, height):
    """Convert pixel array back to image."""
    img = Image.new("RGB", (width, height))
    pixel_data = img.load()
    
    for y in range(height):
        for x in range(width):
            if y < len(pixels) and x < len(pixels[y]):
                r, g, b = pixels[y][x]
                pixel_data[x, y] = (int(r), int(g), int(b))
    
    return img


def create_colored_letter_pattern_on_pixels(pixels, width, height, letter_size=8, alpha=255):
    """Create pattern of random symbols colored to match pixel colors."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load small font
    try:
        font = ImageFont.truetype("arial.ttf", letter_size)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", letter_size)
        except:
            font = ImageFont.load_default()
            letter_size = 8
    
    # All symbols
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
    all_symbols = alphabet + digits + special_chars
    
    # Get symbol size
    bbox = draw.textbbox((0, 0), "a", font=font)
    letter_w = bbox[2] - bbox[0]
    letter_h = bbox[3] - bbox[1]
    
    spacing_x = letter_w + 2
    spacing_y = letter_h + 2
    
    for y in range(0, height, spacing_y):
        for x in range(0, width, spacing_x):
            pixel_y = min(y + letter_h // 2, height - 1)
            pixel_x = min(x + letter_w // 2, width - 1)
            
            r, g, b = pixels[pixel_y][pixel_x]
            random_symbol = random.choice(all_symbols)
            
            draw.text((x, y), random_symbol, font=font, fill=(r, g, b, alpha))
    
    return img


def blend_pattern_on_pixels(pixels, width, height, pattern_img):
    """Blend pattern overlay on pixel array."""
    if pattern_img.mode != "RGBA":
        pattern_img = pattern_img.convert("RGBA")
    
    pattern_w, pattern_h = pattern_img.size
    pattern_data = pattern_img.load()
    
    for py in range(min(pattern_h, height)):
        for px in range(min(pattern_w, width)):
            pattern_r, pattern_g, pattern_b, pattern_a = pattern_data[px, py]
            
            if pattern_a > 0:
                bg_r, bg_g, bg_b = pixels[py][px]
                
                alpha = pattern_a / 255.0
                inv_alpha = 1.0 - alpha
                
                new_r = int(pattern_r * alpha + bg_r * inv_alpha)
                new_g = int(pattern_g * alpha + bg_g * inv_alpha)
                new_b = int(pattern_b * alpha + bg_b * inv_alpha)
                
                pixels[py][px] = [new_r, new_g, new_b]
    
    return pixels


class PixelPatternUniqueizer(BaseUniqueizer):
    """
    Pixel Pattern uniqueization method.
    
    Creates text pattern overlay with random symbols:
    - Alpha 10: barely visible symbols
    
    Returns 1 variant with alpha 10.
    """
    
    def process(self, image_bytes: bytes) -> bytes:
        """Process image - returns alpha 10 version."""
        variants = self.process_variants(image_bytes, count=1)
        return variants[0] if variants else image_bytes
    
    def process_variants(self, image_bytes: bytes, count: int = 1) -> list:
        """
        Process image and return variant with alpha 10.
        
        Args:
            image_bytes: Original image bytes
            count: Number of variants (always returns 1 with alpha 10)
            
        Returns:
            List with single processed image bytes (alpha 10)
        """
        img, original_format = load_image(image_bytes)
        
        # Convert to pixel array
        pixels, width, height = image_to_pixel_array(img)
        
        # Calculate letter size
        letter_size = max(6, int(min(width, height) / 50))
        
        # Always use alpha 10
        alpha = 10
        
        # Create pattern with alpha 10
        pattern_img = create_colored_letter_pattern_on_pixels(
            pixels, width, height, letter_size, alpha=alpha
        )
        
        # Blend pattern on pixels
        pixels_blended = blend_pattern_on_pixels(
            copy.deepcopy(pixels), width, height, pattern_img
        )
        
        # Convert back to image
        result_img = pixel_array_to_image(pixels_blended, width, height)
        
        # Apply sharpness filters
        enhancer = ImageEnhance.Sharpness(result_img)
        result_img = enhancer.enhance(1.5)
        result_img = result_img.filter(ImageFilter.SHARPEN)
        
        # Save
        if original_format.upper() == "PNG":
            variant_bytes = save_image(result_img, "PNG", preserve_alpha=True)
        else:
            variant_bytes = save_image(result_img, "JPEG", quality=95)
        
        return [variant_bytes]

