# -*- coding: utf-8 -*-
"""
All Combined: Combines all uniqueization methods
- Metadata replacement
- Micro changes
- LSB modification
- Method1 (simple)
- Method2 (advanced)
- Method3 (combined 1+2)
"""

from .base import BaseUniqueizer
from .metadata import MetadataUniqueizer
from .micro import MicroUniqueizer
from .lsb import LSBUniqueizer
from .combined import CombinedUniqueizer
from .method1 import Method1Uniqueizer
from .method2 import Method2Uniqueizer
from .method3 import Method3Uniqueizer
from .icc_profile import ICCProfileUniqueizer
# New modular uniqueizers
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


class AllCombinedUniqueizer(BaseUniqueizer):
    """
    Combines ALL uniqueization methods for maximum uniqueization.
    
    Applies in sequence:
    1. CombinedUniqueizer (metadata + micro + lsb)
    2. ICC Profile (color space change)
    3. Method1 (simple enhancements)
    4. Method2 advanced processing (one variant)
    5. Method3 final touch
    """

    def __init__(self):
        """Initialize all combined uniqueizer."""
        # Standard methods
        self.combined = CombinedUniqueizer()
        self.icc_profile = ICCProfileUniqueizer()
        self.method1 = Method1Uniqueizer()
        self.method2 = Method2Uniqueizer(variants=1)
        self.method3 = Method3Uniqueizer(variants=1)
        # New modular uniqueizers
        self.bit_depth = BitDepthUniqueizer()
        self.color_type = ColorTypeUniqueizer()
        self.png_filter = PNGFilterUniqueizer()
        self.interlace = InterlaceUniqueizer()
        self.white_balance = WhiteBalanceUniqueizer()
        self.aperture = ApertureUniqueizer()
        self.resolution = ResolutionUniqueizer()
        self.compression = CompressionUniqueizer()
        self.creator_tool = CreatorToolUniqueizer()
        self.rating = RatingUniqueizer()
        self.color_space = ColorSpaceUniqueizer()
        self.exposure_time = ExposureTimeUniqueizer()

    def process(self, image_bytes: bytes) -> bytes:
        """
        Process image with all methods combined.
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Fully uniqueized image
        """
        result = image_bytes
        
        # Step 1: Apply combined (metadata + micro + lsb)
        result = self.combined.process(result)
        
        # Step 2: Apply ICC profile (color space change)
        try:
            result = self.icc_profile.process(result)
        except Exception as e:
            import logging
            logging.warning("ICC profile step failed: {}".format(e))
        
        # Step 3: Apply method1 (simple enhancements)
        result = self.method1.process(result)
        
        # Step 4: Apply method2 (advanced processing)
        # Get first variant from method2
        try:
            method2_variants = self.method2.process_variants(result, count=1)
            if method2_variants and len(method2_variants) > 0:
                result = method2_variants[0]
        except Exception as e:
            import logging
            logging.warning("Method2 step failed: {}".format(e))
        
        # Step 5: Apply method3 (final combined touch)
        try:
            method3_variants = self.method3.process_variants(result, count=1)
            if method3_variants and len(method3_variants) > 0:
                result = method3_variants[0]
        except Exception as e:
            import logging
            logging.warning("Method3 step failed: {}".format(e))
        
        # Step 6: Apply new modular uniqueizers (random order for uniqueness)
        import random
        modular_methods = [
            ("bit_depth", self.bit_depth),
            ("color_type", self.color_type),
            ("png_filter", self.png_filter),
            ("interlace", self.interlace),
            ("white_balance", self.white_balance),
            ("aperture", self.aperture),
            ("resolution", self.resolution),
            ("compression", self.compression),
            ("creator_tool", self.creator_tool),
            ("rating", self.rating),
            ("color_space", self.color_space),
            ("exposure_time", self.exposure_time),
        ]
        
        # Apply random subset of modular methods (4-8 methods)
        num_methods = random.randint(4, 8)
        selected_methods = random.sample(modular_methods, num_methods)
        
        for method_name, method_uniqueizer in selected_methods:
            try:
                result = method_uniqueizer.process(result)
            except Exception as e:
                import logging
                logging.warning("{} step failed: {}".format(method_name, e))
        
        return result

    def process_variants(self, image_bytes: bytes, count: int = None) -> list:
        """
        Generate multiple unique variants by calling process() count times.
        
        Args:
            image_bytes: Original image bytes
            count: Number of variants to generate
            
        Returns:
            List of uniqueized image bytes
        """
        if count is None:
            count = 1
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"=== AllCombinedUniqueizer.process_variants START ===")
        logger.info(f"Requested count: {count}")
        logger.info(f"Will call process() {count} times - each call generates unique result")
        
        variants = []
        
        for i in range(count):
            try:
                logger.info(f"[{i+1}/{count}] Calling process()...")
                variant = self.process(image_bytes)
                variants.append(variant)
                logger.info(f"[{i+1}/{count}] SUCCESS: variant added, total={len(variants)}")
            except Exception as e:
                logger.error(f"[{i+1}/{count}] ERROR: {e}", exc_info=True)
                # Fallback to metadata-only uniqueization
                from .metadata import MetadataUniqueizer
                metadata_uniqueizer = MetadataUniqueizer()
                try:
                    variant = metadata_uniqueizer.process(image_bytes)
                    variants.append(variant)
                    logger.warning(f"[{i+1}/{count}] FALLBACK: metadata used, total={len(variants)}")
                except Exception as e2:
                    variants.append(image_bytes)
                    logger.warning(f"[{i+1}/{count}] LAST RESORT: original image used, total={len(variants)}")
        
        logger.info(f"=== AllCombinedUniqueizer.process_variants END ===")
        logger.info(f"Generated {len(variants)} variants (requested {count})")
        
        if len(variants) < count:
            logger.error(f"CRITICAL: Only generated {len(variants)} variants but {count} were requested!")
            # Fill remaining with metadata uniqueization
            from .metadata import MetadataUniqueizer
            metadata_uniqueizer = MetadataUniqueizer()
            while len(variants) < count:
                try:
                    variant = metadata_uniqueizer.process(image_bytes)
                    variants.append(variant)
                    logger.warning(f"FILLING: Added variant {len(variants)}/{count} using metadata")
                except:
                    variants.append(image_bytes)
                    logger.warning(f"FILLING: Added variant {len(variants)}/{count} using original")
        
        result = variants[:count]
        logger.info(f"RETURNING: {len(result)} variants (requested {count})")
        return result

