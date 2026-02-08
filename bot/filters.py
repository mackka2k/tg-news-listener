"""
Message filtering logic
"""

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)


class MessageFilter:
    """
    Handles message filtering based on keywords and spam detection
    """
    
    def __init__(
        self,
        keywords: List[str],
        spam_keywords: List[str],
        filter_patterns: List[str] = None
    ):
        """
        Initialize message filter
        
        Args:
            keywords: List of keywords to match (message must have at least one)
            spam_keywords: List of spam keywords (message rejected if has any)
            filter_patterns: Optional list of patterns to filter from text
        """
        self.keywords = [kw.lower() for kw in keywords]
        self.spam_keywords = [kw.lower() for kw in spam_keywords]
        self.filter_patterns = filter_patterns or [
            't.me/',
            'Подписаться',
            'КиберТопор',
            'ТОПОР',
            'Подпишись',
            'Канал:',
        ]
        
        logger.info(f"Filter initialized: {len(self.keywords)} keywords, {len(self.spam_keywords)} spam keywords")
    
    def should_forward(self, message_text: str) -> Tuple[bool, str]:
        """
        Check if message should be forwarded
        
        Args:
            message_text: Message text to check
        
        Returns:
            Tuple of (should_forward: bool, reason: str)
        """
        if not message_text:
            return False, "Tuščia žinutė"
        
        text_lower = message_text.lower()
        
        # 1. Check spam keywords first
        for spam_word in self.spam_keywords:
            if spam_word in text_lower:
                return False, f"Spam keyword: {spam_word}"
        
        # 2. Check keywords
        # If no keywords configured, forward EVERYTHING (except spam)
        if not self.keywords:
             return True, "✅ No keyword filter (forwarding all)"

        # Check against configured keywords
        has_keyword = False
        matched_keywords = []
        
        for keyword in self.keywords:
            if keyword in text_lower:
                has_keyword = True
                matched_keywords.append(keyword)
        
        if not has_keyword:
            return False, "Nėra keyword'ų" # Message rejected
            
        # All checks passed with keywords
        keywords_str = ', '.join(matched_keywords[:3])
        return True, f"✅ Keyword match: {keywords_str}"
    
    def clean_message_text(self, text: str) -> str:
        """
        Clean message text by removing promotional content
        
        Args:
            text: Original message text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines with filter patterns
            should_skip = False
            for pattern in self.filter_patterns:
                if pattern.lower() in line.lower():
                    should_skip = True
                    break
            
            if not should_skip:
                cleaned_lines.append(line)
        
        cleaned = '\n'.join(cleaned_lines).strip()
        
        # Remove excessive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract matched keywords from text
        
        Args:
            text: Message text
        
        Returns:
            List of matched keywords
        """
        if not text:
            return []
        
        text_lower = text.lower()
        matched = []
        
        for keyword in self.keywords:
            if keyword in text_lower:
                matched.append(keyword)
        
        return matched
    
    def is_spam(self, text: str) -> bool:
        """
        Check if text contains spam keywords
        
        Args:
            text: Message text
        
        Returns:
            True if spam detected
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        for spam_word in self.spam_keywords:
            if spam_word in text_lower:
                return True
        
        return False
