"""
Message processing pipeline
"""

import logging
import os
from typing import Optional
from telethon.tl.types import Message

from bot.filters import MessageFilter
from bot.ai_service import AIService
from bot.utils import truncate_text, MAX_CAPTION_LENGTH

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Handles message processing pipeline
    """
    
    def __init__(
        self,
        message_filter: MessageFilter,
        ai_service: AIService
    ):
        """
        Initialize message processor
        
        Args:
            message_filter: Message filter instance
            ai_service: AI service instance
        """
        self.filter = message_filter
        self.ai = ai_service
        
        logger.info("Message processor initialized")
    
    async def process_message(
        self,
        message: Message,
        source_channel: str
    ) -> Optional[dict]:
        """
        Process a message through the pipeline
        
        Args:
            message: Telegram message object
            source_channel: Source channel name
        
        Returns:
            Processed message data or None if rejected
        """
        # Extract text
        original_text = message.text or message.message or ""
        
        if not original_text:
            logger.debug("Message has no text, skipping")
            return None
        
        # Check if should forward
        should_forward, reason = self.filter.should_forward(original_text)
        
        if not should_forward:
            logger.info(f"Message rejected: {reason}")
            return None
        
        # Clean text
        cleaned_text = self.filter.clean_message_text(original_text)
        
        if not cleaned_text:
            logger.debug("Message text empty after cleaning, skipping")
            return None
        
        # Generate tags
        tags = await self.ai.generate_tags(cleaned_text)
        
        # Combine text and tags
        final_text = f"{cleaned_text}\n\n{tags}"
        
        # Check length and truncate if needed
        if len(final_text) > MAX_CAPTION_LENGTH:
            logger.warning(f"Text too long ({len(final_text)} chars), truncating")
            
            # Calculate available space for text
            available_space = MAX_CAPTION_LENGTH - len(tags) - 10  # 10 for newlines and buffer
            
            if available_space > 100:  # Only truncate if we have reasonable space
                cleaned_text = truncate_text(cleaned_text, available_space)
                final_text = f"{cleaned_text}\n\n{tags}"
            else:
                # Text is too short even after truncation, use without tags
                final_text = truncate_text(cleaned_text, MAX_CAPTION_LENGTH)
                logger.warning("Removed tags due to length constraints")
        
        return {
            'original_text': original_text,
            'cleaned_text': cleaned_text,
            'final_text': final_text,
            'tags': tags,
            'media': message.media,
            'source_channel': source_channel,
            'message_id': message.id,
            'reason': reason
        }
    
    async def download_media(self, message: Message) -> Optional[str]:
        """
        Download media from message
        
        Args:
            message: Telegram message
        
        Returns:
            Path to downloaded file or None
        """
        if not message.media:
            return None
        
        try:
            file_path = await message.download_media()
            return file_path
        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return None
    
    def cleanup_media_file(self, file_path: str) -> None:
        """
        Clean up downloaded media file
        
        Args:
            file_path: Path to file
        """
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug(f"Cleaned up media file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup media file {file_path}: {e}")
