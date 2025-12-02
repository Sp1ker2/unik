# -*- coding: utf-8 -*-
"""
Method 2: Advanced uniqueization (from main.py)
- Edge crop (sides: 2-2.5%, top/bottom: 2-2.5%)
- Scale jitter (±3%)
- Gamma and contrast tweaks
- Mirroring (for some variants)
- Rounded corners (for some variants)
- Logo detection and transformation
- 6 variants with different combinations
"""

import random
import string
import io
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFilter
import pytesseract

from .base import BaseUniqueizer
from src.utils.image import load_image, save_image, get_icc_profile, apply_icc_profile

# Parameters
# Edge crop: sides 2-2.5%, top/bottom 2-2.5%
EDGE_CROP_SIDE_MIN = 0.02   # 2% for left/right
EDGE_CROP_SIDE_MAX = 0.025  # 2.5% for left/right
EDGE_CROP_TOP_MIN = 0.02    # 2% for top/bottom
EDGE_CROP_TOP_MAX = 0.025  # 2.5% for top/bottom
SCALE_JITTER = 0.03
GAMMA_DELTA = 0.12
CONTRAST_DELTA = 0.05
JPEG_Q_MIN = 84
JPEG_Q_MAX = 94
RADIUS_FRAC = 0.06

ADJ = ["misty", "brave", "silent", "swift", "fuzzy", "vivid", "amber", "frosty",
       "lucky", "cosy", "sunny", "shadow", "velvet", "crimson", "ocean", "sage"]
NOUN = ["lynx", "falcon", "fox", "wolf", "otter", "sparrow", "orca", "panda",
        "tiger", "eagle", "koala", "gecko", "owl", "yak", "marten", "ibis"]

# Setup Tesseract if available
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    pass


def exif_correct(img):
    """Correct EXIF orientation."""
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
        return img


def random_edge_crop_box(w, h):
    """Generate random edge crop box.
    Sides: 2-2.5%, Top/Bottom: 2-2.5%
    """
    # Left/Right: 2-3%
    lm = int(round(random.uniform(EDGE_CROP_SIDE_MIN, EDGE_CROP_SIDE_MAX) * w))
    rm = int(round(random.uniform(EDGE_CROP_SIDE_MIN, EDGE_CROP_SIDE_MAX) * w))
    # Top/Bottom: 3-5%
    tm = int(round(random.uniform(EDGE_CROP_TOP_MIN, EDGE_CROP_TOP_MAX) * h))
    bm = int(round(random.uniform(EDGE_CROP_TOP_MIN, EDGE_CROP_TOP_MAX) * h))
    left = min(max(0, lm), max(0, w - 2))
    top = min(max(0, tm), max(0, h - 2))
    right = max(left + 1, min(w - 1, w - rm))
    bottom = max(top + 1, min(h - 1, h - bm))
    if right - left < 2 or bottom - top < 2:
        # Fallback: use minimum crop values
        dw = int(round(EDGE_CROP_SIDE_MIN * w))
        dh = int(round(EDGE_CROP_TOP_MIN * h))
        left, top, right, bottom = dw, dh, w - dw, h - dh
    return left, top, right, bottom


def apply_gamma(img, gamma):
    """Apply gamma correction."""
    if gamma <= 0:
        return img
    inv = 1.0 / 255.0
    lut = [min(255, max(0, int((i * inv) ** gamma * 255 + 0.5))) for i in range(256)]
    if img.mode != "RGB":
        img = img.convert("RGB")
    r, g, b = img.split()
    r = r.point(lut)
    g = g.point(lut)
    b = b.point(lut)
    return Image.merge("RGB", (r, g, b))


def tweak_shadows_and_contrast(img):
    """Tweak shadows and contrast."""
    gamma = 1.0 + random.uniform(-GAMMA_DELTA, GAMMA_DELTA)
    g_img = apply_gamma(img, gamma)
    img = Image.blend(img.convert("RGB"), g_img.convert("RGB"), 0.7)
    c_factor = 1.0 + random.uniform(-CONTRAST_DELTA, CONTRAST_DELTA)
    img = ImageEnhance.Contrast(img).enhance(c_factor)
    return img


def slight_scale(img):
    """Apply slight scale jitter."""
    w, h = img.size
    factor = 1.0 + random.uniform(-SCALE_JITTER, SCALE_JITTER)
    nw = max(1, int(round(w * factor)))
    nh = max(1, int(round(h * factor)))
    scaled = img.resize((nw, nh), Image.Resampling.LANCZOS)
    return scaled.resize((w, h), Image.Resampling.LANCZOS)


def apply_rounded_corners(img, radius_frac, keep_alpha):
    """Apply rounded corners."""
    w, h = img.size
    radius = max(2, int(round(min(w, h) * radius_frac)))
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    if keep_alpha:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.putalpha(mask)
        return img
    else:
        bg = Image.new("RGB", (w, h), (255, 255, 255))
        img_rgb = img.convert("RGB")
        return Image.composite(img_rgb, bg, mask)


def random_slug():
    """Generate random filename slug."""
    a = random.choice(ADJ)
    n = random.choice(NOUN)
    tail = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    return "{}-{}-{}".format(a, n, tail)


def is_logo(img):
    """Detect if image contains text/logo."""
    try:
        text = pytesseract.image_to_string(img)
        return len(text.strip()) > 3
    except:
        return False


def transform_logo(img):
    """Transform logo without losing text readability."""
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.9, 1.1))
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.9, 1.1))
    
    arr = np.array(img)
    noise = np.random.normal(0, 8, arr.shape).astype(np.int16)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    
    if random.random() < 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))
    else:
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    
    if random.random() < 0.5:
        img = _wave_distort(img)
    
    return img


def _wave_distort(img):
    """Apply wave distortion for text."""
    w, h = img.size
    arr = np.array(img)
    result = np.zeros_like(arr)
    for y in range(h):
        shift = int(5.0 * np.sin(2 * np.pi * y / 60.0))
        result[y] = np.roll(arr[y], shift, axis=0)
    return Image.fromarray(result)


class Method2Uniqueizer(BaseUniqueizer):
    """
    Advanced uniqueization method from main.py.
    
    Generates 6 variants with different combinations of:
    - Edge crop
    - Scale jitter
    - Gamma/contrast tweaks
    - Mirroring (2 variants)
    - Rounded corners (2 variants)
    - PNG/JPEG format mix (3 PNG, 3 JPEG)
    """

    def __init__(self, variants=6, mirrored_count=2, rounded_count=2, png_count=3):
        """
        Initialize method 2 uniqueizer.
        
        Args:
            variants: Number of variants to generate
            mirrored_count: Number of mirrored variants
            rounded_count: Number of rounded corner variants
            png_count: Number of PNG variants
        """
        self.variants = variants
        self.mirrored_count = mirrored_count
        self.rounded_count = rounded_count
        self.png_count = png_count

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image - returns first variant.
        For multiple variants, use process_variants().
        """
        return self.process_variants(image_bytes, count=1)[0]

    def process_variants(self, image_bytes: bytes, count: int = None) -> list:
        """
        Process image and return multiple variants.
        
        Args:
            image_bytes: Original image bytes
            count: Number of variants (default: self.variants)
            
        Returns:
            List of processed image bytes
        """
        if count is None:
            count = self.variants
            
        img, original_format = load_image(image_bytes)
        img = exif_correct(img.convert("RGB"))
        icc_profile = get_icc_profile(image_bytes)
        
        w, h = img.size
        
        # Random selection for variants
        mirror_idx = set(random.sample(range(count), min(self.mirrored_count, count)))
        rounded_idx = set(random.sample(range(count), min(self.rounded_count, count)))
        png_idx = set(random.sample(range(count), min(self.png_count, count)))
        
        variants = []
        
        for i in range(count):
            # Create a copy for this variant
            variant_img = img.copy()
            
            # Edge crop
            box = random_edge_crop_box(w, h)
            variant_img = variant_img.crop(box)
            
            # Scale jitter
            variant_img = slight_scale(variant_img)
            
            # Gamma and contrast
            variant_img = tweak_shadows_and_contrast(variant_img)
            
            # Mirroring
            do_mirror = i in mirror_idx
            if do_mirror:
                if is_logo(variant_img):
                    variant_img = transform_logo(variant_img)
                else:
                    variant_img = ImageOps.mirror(variant_img)
            
            # Rounded corners
            do_rounded = i in rounded_idx
            fmt = "png" if i in png_idx else "jpg"
            if do_rounded:
                keep_alpha = (fmt.lower() == "png")
                variant_img = apply_rounded_corners(variant_img, RADIUS_FRAC, keep_alpha)
            
            # Apply ICC profile
            variant_img = apply_icc_profile(variant_img, icc_profile)
            
            # Save
            if fmt.lower() == "png":
                if variant_img.mode not in ("RGB", "RGBA"):
                    variant_img = variant_img.convert("RGBA")
                variant_bytes = save_image(variant_img, "PNG", preserve_alpha=True)
            else:
                if variant_img.mode != "RGB":
                    variant_img = variant_img.convert("RGB")
                q = random.randint(JPEG_Q_MIN, JPEG_Q_MAX)
                variant_bytes = save_image(variant_img, "JPEG", quality=q)
            
            variants.append(variant_bytes)
        
        return variants

