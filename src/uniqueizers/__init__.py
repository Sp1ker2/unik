"""
Image uniqueization methods package.
"""

from enum import Enum


class UniqueizationMethod(Enum):
    """Available uniqueization methods."""
    METADATA = "metadata"
    MICRO = "micro"
    LSB = "lsb"
    METHOD1 = "method1"
    METHOD2 = "method2"
    METHOD3 = "method3"
    ICC_PROFILE = "icc_profile"
    ALL_COMBINED = "all_combined"
    ALL_COMBINED_WITH_PIXEL = "all_combined_with_pixel"


from .base import BaseUniqueizer
from .metadata import MetadataUniqueizer
from .micro import MicroUniqueizer
from .lsb import LSBUniqueizer
from .combined import CombinedUniqueizer
from .method1 import Method1Uniqueizer
from .method2 import Method2Uniqueizer
from .method3 import Method3Uniqueizer
from .icc_profile import ICCProfileUniqueizer


def get_uniqueizer(method: UniqueizationMethod) -> BaseUniqueizer:
    """Factory function to get uniqueizer by method type."""
    uniqueizers = {
        UniqueizationMethod.METADATA: MetadataUniqueizer,
        UniqueizationMethod.MICRO: MicroUniqueizer,
        UniqueizationMethod.LSB: LSBUniqueizer,
        UniqueizationMethod.METHOD1: Method1Uniqueizer,
        UniqueizationMethod.METHOD2: Method2Uniqueizer,
        UniqueizationMethod.METHOD3: Method3Uniqueizer,
        UniqueizationMethod.ICC_PROFILE: ICCProfileUniqueizer,
    }
    
    # Handle all_combined separately as it needs special initialization
    if method == UniqueizationMethod.ALL_COMBINED:
        from .all_combined import AllCombinedUniqueizer
        return AllCombinedUniqueizer()
    
    if method == UniqueizationMethod.ALL_COMBINED_WITH_PIXEL:
        from .all_combined_with_pixel import AllCombinedWithPixelUniqueizer
        return AllCombinedWithPixelUniqueizer()
    
    return uniqueizers[method]()


__all__ = [
    "UniqueizationMethod",
    "BaseUniqueizer",
    "MetadataUniqueizer",
    "MicroUniqueizer",
    "LSBUniqueizer",
    "CombinedUniqueizer",
    "Method1Uniqueizer",
    "Method2Uniqueizer",
    "Method3Uniqueizer",
    "ICCProfileUniqueizer",
    "get_uniqueizer",
]
