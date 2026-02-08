"""
Smart deduplication logic using fuzzy string matching
"""

import logging
from typing import List, Tuple
from thefuzz import fuzz

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Handles message deduplication using fuzzy matching
    """
    
    def __init__(self, threshold: int = 85):
        """
        Initialize deduplicator
        
        Args:
            threshold: Similarity threshold (0-100). Higher means stricter matching.
        """
        self.threshold = threshold
    
    def is_duplicate(self, text: str, recent_messages: List[str]) -> Tuple[bool, float, str]:
        """
        Check if text is a duplicate of any recent message
        
        Args:
            text: New message text
            recent_messages: List of recent message texts
        
        Returns:
            Tuple (is_duplicate, similarity_score, matching_text)
        """
        if not text or not recent_messages:
            return False, 0.0, ""
        
        best_score = 0
        best_match = ""
        
        # Clean text for better comparison (optional)
        # text = text.lower().strip()
        
        for msg in recent_messages:
            # Skip empty messages
            if not msg:
                continue
            
            # fast calculation first
            ratio = fuzz.ratio(text, msg)
            
            # If not even close, skip expensive partial_ratio
            if ratio < 50:
                continue
                
            # Use token_sort_ratio for better accuracy with shuffled words
            score = fuzz.token_sort_ratio(text, msg)
            
            if score > best_score:
                best_score = score
                best_match = msg
                
            if best_score >= self.threshold:
                return True, best_score, best_match
        
        return False, best_score, best_match
