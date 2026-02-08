"""
Telegram News Bot - Production-ready modular architecture
"""

__version__ = "2.0.0"
__author__ = "News Bot Team"

from bot.client import NewsBot
from bot.config import Config

__all__ = ["NewsBot", "Config"]
