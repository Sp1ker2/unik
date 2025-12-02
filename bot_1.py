"""
Image Uniqueization Bot - Entry Point

This file serves as backwards compatibility entry point.
The main implementation is in src/bot.py
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env from: {env_path}")
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
    # Try to load .env manually if dotenv is not available
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"Manually loaded .env from: {env_path}")

from src.bot import main

if __name__ == "__main__":
    main()
