# -*- coding: utf-8 -*-
"""
All Combined with Pixel Pattern: Combines all uniqueization methods + pixel pattern overlay.

Applies:
1. All standard methods (metadata, micro, lsb, method1, method2, method3, icc)
2. Pixel pattern overlay (alpha 10 variant)

Returns 1 variant with alpha 10.
"""

from .base import BaseUniqueizer
from .all_combined import AllCombinedUniqueizer
from .pixel_pattern import PixelPatternUniqueizer
# New modular uniqueizers (also used in all_combined)
from .bit_depth import BitDepthUniqueizer
from .color_type import ColorTypeUniqueizer
from .png_filter import PNGFilterUniqueizer
from .interlace import InterlaceUniqueizer
from .white_balance import WhiteBalanceUniqueizer
from .aperture import ApertureUniqueizer
from .resolution import ResolutionUniqueizer
from .compression import CompressionUniqueizer
from .creator_tool import CreatorToolUniqueizer
from .rating import RatingUniqueizer
from .color_space import ColorSpaceUniqueizer
from .exposure_time import ExposureTimeUniqueizer
from .iso import ISOUUniqueizer
from .focal_length import FocalLengthUniqueizer
from .flash import FlashUniqueizer
from .lens_model import LensModelUniqueizer
from .metering_mode import MeteringModeUniqueizer
from .exposure_mode import ExposureModeUniqueizer
from .datetime_exif import DateTimeEXIFUniqueizer
from .orientation import OrientationUniqueizer
from .png_time import PNGTimeUniqueizer
from .camera_make_model import CameraMakeModelUniqueizer
from .subject_distance import SubjectDistanceUniqueizer


class AllCombinedWithPixelUniqueizer(BaseUniqueizer):
    """
    Combines ALL uniqueization methods + pixel pattern overlay.
    
    Applies in sequence:
    1. AllCombinedUniqueizer (all standard methods)
    2. Pixel Pattern overlay (alpha 10)
    
    Returns 1 variant with alpha 10.
    """
    
    def __init__(self):
        """Initialize all combined with pixel uniqueizer."""
        self.all_combined = AllCombinedUniqueizer()
        self.pixel_pattern = PixelPatternUniqueizer()
    
    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image with all methods + pixel pattern.
        Returns variant with alpha 10.
        """
        variants = self.process_variants(image_bytes, count=1)
        return variants[0] if variants else image_bytes
    
    def process_variants(self, image_bytes: bytes, count: int = 1) -> list:
        """
        Process image with all methods + pixel pattern.
        Generates multiple unique variants.
        
        Optimized: Process base image once, then apply variations.
        
        Args:
            image_bytes: Original image bytes
            count: Number of variants to generate
            
        Returns:
            List of processed image bytes
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"=== AllCombinedWithPixelUniqueizer.process_variants START ===")
        logger.info(f"Requested count: {count}")
        
        variants = []
        
        # For each variant, process independently to ensure uniqueness
        # This ensures each copy is truly unique
        for i in range(count):
            logger.info(f"[{i+1}/{count}] Processing variant...")
            try:
                # Process base image (each call generates unique result due to randomness in methods)
                logger.info(f"[{i+1}/{count}] Calling all_combined.process()...")
                base_result = self.all_combined.process(image_bytes)
                logger.info(f"[{i+1}/{count}] all_combined.process() complete, size: {len(base_result)} bytes")
                
                # Apply pixel pattern overlay
                try:
                    logger.info(f"[{i+1}/{count}] Calling pixel_pattern.process_variants()...")
                    pixel_variants = self.pixel_pattern.process_variants(base_result, count=1)
                    if pixel_variants and len(pixel_variants) > 0:
                        logger.info(f"[{i+1}/{count}] pixel_pattern returned variant, size: {len(pixel_variants[0])} bytes")
                        variants.append(pixel_variants[0])
                    else:
                        logger.warning(f"[{i+1}/{count}] pixel_pattern returned empty, using base result")
                        # If pixel pattern fails, use base result
                        variants.append(base_result)
                except Exception as e:
                    logger.warning(f"[{i+1}/{count}] Pixel pattern step failed: {e}")
                    # Fallback: use base result
                    variants.append(base_result)
                
                logger.info(f"[{i+1}/{count}] SUCCESS: variant added, total={len(variants)}")
                    
            except Exception as e:
                logger.error(f"[{i+1}/{count}] All combined step failed: {e}", exc_info=True)
                # Last resort: use original image
                variants.append(image_bytes)
                logger.warning(f"[{i+1}/{count}] FALLBACK: original image used, total={len(variants)}")
        
        # Ensure we have exactly count variants
        logger.info(f"=== AllCombinedWithPixelUniqueizer.process_variants END ===")
        logger.info(f"Generated {len(variants)} variants (requested {count})")
        
        if len(variants) < count:
            logger.warning(f"Not enough variants, filling remaining: {count - len(variants)}")
            # Fill remaining with metadata-only variations
            from .metadata import MetadataUniqueizer
            metadata_uniqueizer = MetadataUniqueizer()
            
            base_variant = variants[0] if variants else image_bytes
            for i in range(len(variants), count):
                try:
                    variants.append(metadata_uniqueizer.process(base_variant))
                    logger.info(f"FILLING: Added variant {len(variants)}/{count} using metadata")
                except:
                    variants.append(base_variant)
                    logger.warning(f"FILLING: Added variant {len(variants)}/{count} using base")
        
        # Return exactly count variants
        result = variants[:count]
        logger.info(f"RETURNING: {len(result)} variants (requested {count})")
        return result

