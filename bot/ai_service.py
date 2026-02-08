"""
AI service for hashtag generation using Groq
"""

import logging
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)


class AIService:
    """
    AI-powered hashtag generation service
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI service
        
        Args:
            api_key: Groq API key (optional)
        """
        self.api_key = api_key
        self.client = None
        
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
                logger.info("Groq AI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.info("No Groq API key provided, using fallback tagging")
    
    async def generate_tags(self, text: str) -> str:
        """
        Generate hashtags for message text
        
        Args:
            text: Message text
        
        Returns:
            Generated hashtags as string
        """
        if not text:
            return "#Naujienos"
        
        # Try AI generation first
        if self.client:
            try:
                ai_tags = await self._generate_ai_tags(text)
                if ai_tags and ai_tags.startswith('#'):
                    return ai_tags
            except Exception as e:
                logger.error(f"AI tag generation failed: {e}")
        
        # Fallback to rule-based tagging
        return self._generate_fallback_tags(text)
    
    async def _generate_ai_tags(self, text: str) -> Optional[str]:
        """
        Generate tags using Groq AI
        
        Args:
            text: Message text
        
        Returns:
            AI-generated tags or None
        """
        if not self.client:
            return None
        
        prompt = f"""
        Analyze the text and generate 1-4 SHORT, ACCURATE hashtags in Lithuanian.
        
        Rules:
        1. Use ONLY generic categories: #Karas, #Rusija, #Technologijos, #Kriminalai, #Pasaulis, #Sveikata, #Žaidimai, #Kripto, #AI, #Mokslas, #Politika.
        2. DO NOT mention #Lietuva unless the text specifically mentions Lithuania.
        3. DO NOT invent long tags. Keep them short and generic.
        4. Output ONLY the tags, separated by spaces.
        5. Maximum 4 tags.
        
        Text: {text[:500]}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=50,
                timeout=10.0
            )
            
            tags = completion.choices[0].message.content.strip()
            
            # Validate tags
            if tags and all(tag.startswith('#') for tag in tags.split()):
                return tags
            
            logger.warning(f"Invalid AI tags format: {tags}")
            return None
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    def _generate_fallback_tags(self, text: str) -> str:
        """
        Generate tags using rule-based approach
        
        Args:
            text: Message text
        
        Returns:
            Rule-based tags
        """
        tags = []
        text_lower = text.lower()
        
        # Tag rules
        rules = {
            '#AI': ['ai', 'gpt', 'llm', 'neural', 'нейросеть', 'ии', 'искусственный интеллект'],
            '#Technologijos': ['tech', 'apple', 'google', 'microsoft', 'iphone', 'телефон', 'гаджет', 'технологи'],
            '#Karas': ['war', 'ukraine', 'russia', 'nato', 'война', 'украина', 'всу', 'рф', 'армия'],
            '#Politika': ['biden', 'putin', 'trump', 'zelensky', 'политика', 'закон', 'президент', 'выборы'],
            '#Kripto': ['crypto', 'bitcoin', 'btc', 'eth', 'крипта', 'биткоин', 'майнинг', 'blockchain'],
            '#Mokslas': ['science', 'space', 'nasa', 'mars', 'наука', 'космос', 'ученые', 'исследование'],
            '#Lietuva': ['lietuva', 'vilnius', 'lithuania', 'литва', 'вильнюс', 'каунас'],
            '#Rusija': ['russia', 'moscow', 'kremlin', 'россия', 'москва', 'кремль'],
            '#Sveikata': ['health', 'medicine', 'vaccine', 'здоровье', 'медицина', 'вакцина'],
            '#Kriminalai': ['crime', 'arrest', 'police', 'преступление', 'арест', 'полиция'],
            '#Žaidimai': ['game', 'gaming', 'playstation', 'xbox', 'игра', 'геймин'],
        }
        
        for tag, keywords in rules.items():
            for keyword in keywords:
                if keyword in text_lower:
                    tags.append(tag)
                    break  # Only add tag once
            
            # Limit to 4 tags
            if len(tags) >= 4:
                break
        
        # Default tag if no matches
        if not tags:
            return "#Naujienos"
        
        return ' '.join(tags)
