"""
Centralized configuration for secret keys loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load variables from .env (ignored by VCS)
load_dotenv()

# NVIDIA API keys (primary and secondary)
NVIDIA_API_KEY_1 = os.getenv("NVIDIA_API_KEY_1")
NVIDIA_API_KEY_2 = os.getenv("NVIDIA_API_KEY_2")

# Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Scrapfly API key
SCRAPFLY_API_KEY = os.getenv("SCRAPFLY_API_KEY")

