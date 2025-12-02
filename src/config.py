"""
Bot configuration and constants.
"""

import os

# Telegram Bot Token - use environment variable for security
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Image processing limits
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_BATCH_SIZE = 10
MAX_COPY_COUNT = 100

# Quality thresholds
MIN_SSIM = 0.99
MAX_SIZE_RATIO = 1.2

# Timeouts (seconds)
METHOD_SELECTION_TIMEOUT = 30
COUNT_SELECTION_TIMEOUT = 30
CUSTOM_COUNT_INPUT_TIMEOUT = 60
MEDIA_GROUP_COLLECTION_TIMEOUT = 2
PROCESSING_TIMEOUT_PER_COPY = 60
PROCESSING_TIMEOUT_MAX = 300

# Supported formats
SUPPORTED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg"]
SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Method names for display
METHOD_NAMES = {
    "metadata": "Только метаданные",
    "micro": "Микро-изменения",
    "lsb": "LSB-модификация",
    "method1": "Простая (Метод 1)",
    "method2": "Продвинутая (Метод 2)",
    "method3": "Комбинация 1+2 (Метод 3)",
    "icc_profile": "ICC цветовой профиль",
    "all_combined": "ВСЕ МЕТОДЫ ВМЕСТЕ 🔥",
    "all_combined_with_pixel": "ВСЕ МЕТОДЫ ВМЕСТЕ 🔥 PIXEL",
}

# Default settings
DEFAULT_METHOD = "all_combined"
DEFAULT_COPY_COUNT = 1
