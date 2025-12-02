# Quickstart: Уникализация изображений

**Feature**: 001-improve-uniqueization
**Date**: 2025-11-28

## Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)

## Installation

```bash
# Clone repository
cd bot_random

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create `.env` file or set environment variable:

```bash
export BOT_TOKEN="your-telegram-bot-token"
```

Or update `src/config.py`:

```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "your-token-here")
```

## Running

### Development

```bash
python -m src.bot
```

### Production (Docker)

```bash
docker build -t uniqueizer-bot .
docker run -e BOT_TOKEN="your-token" uniqueizer-bot
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_metadata.py -v
```

## Usage

1. Start chat with your bot in Telegram
2. Send `/start` to see instructions
3. Send an image (photo or document)
4. Select uniqueization method from buttons:
   - **Только метаданные** — fastest, changes only EXIF/IPTC/XMP
   - **Микро-изменения** — subtle pixel adjustments
   - **LSB-модификация** — changes least significant bits
   - **Комбинированный** — all methods combined (recommended)
5. Receive uniqueized image as document

## Project Structure

```
bot_random/
├── src/
│   ├── bot.py           # Main bot entry point
│   ├── config.py        # Configuration
│   ├── handlers/        # Telegram handlers
│   │   ├── photo.py     # Photo/document handling
│   │   └── callbacks.py # Inline button callbacks
│   ├── uniqueizers/     # Uniqueization algorithms
│   │   ├── base.py      # Base class
│   │   ├── metadata.py  # EXIF/IPTC/XMP
│   │   ├── micro.py     # Micro adjustments
│   │   ├── lsb.py       # LSB modification
│   │   └── combined.py  # All methods
│   └── utils/           # Utilities
│       ├── image.py     # Image processing
│       └── metadata.py  # Metadata utilities
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── Dockerfile          # Container config
```

## API Reference

### Uniqueizers

```python
from src.uniqueizers import MetadataUniqueizer, MicroUniqueizer, LSBUniqueizer, CombinedUniqueizer

# Create uniqueizer
uniqueizer = CombinedUniqueizer()

# Process image
result = uniqueizer.process(image_bytes)
# Returns: UniqueizationResult(image_bytes, filename, ssim, ...)
```

### Quality Verification

```python
from skimage.metrics import structural_similarity as ssim
import numpy as np
from PIL import Image

# Load images
original = np.array(Image.open("original.jpg"))
processed = np.array(Image.open("processed.jpg"))

# Calculate SSIM
score = ssim(original, processed, channel_axis=2)
assert score >= 0.99, f"Quality too low: {score}"
```

## Troubleshooting

### Bot doesn't respond

1. Check BOT_TOKEN is correct
2. Verify bot is running (`python -m src.bot`)
3. Check Telegram API access (no firewall blocking)

### Image processing fails

1. Check image format (JPEG/PNG only)
2. Verify file size (<= 20 MB)
3. Check for corrupted files

### Low quality result

1. Verify SSIM >= 0.99 in tests
2. Check LSB intensity parameter (default 0.1)
3. Review micro-adjustment parameters
