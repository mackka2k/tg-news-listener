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
    
    async def analyze_content(self, text: str) -> dict:
        """
        Analyze content for tags, reliability, and summary using Groq AI
        
        Args:
            text: Message text
        
        Returns:
            Dictionary with analysis results
        """
        result = {
            "tags": self._generate_fallback_tags(text),
            "summary": None,
            "reliability": None,
            "clickbait": None,
            "sentiment": None
        }
        
        if not self.client or not text or len(text) < 50:
            return result
        
        try:
            prompt = f"""
            Analyze the following news text and provide a JSON response.
            
            Text: {text[:1000]}
            
            Response Format (strict JSON):
            {{
                "tags": "3-4 concise Lithuanian hashtags (e.g. #Karas #Technologijos)",
                "reliability_score": "Integer 1-10 (10=Highly Reliable, 1=Fake/Propaganda)",
                "sentiment": "Positive/Neutral/Negative",
                "reasoning": "Very short reason for reliability score"
            }}
            
            Rules:
            1. Reliability: Penalize lack of sources, emotional language, propaganda.
            2. Tags: Must be generic categories in Lithuanian.
            """
            
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, # Lower temperature for consistency
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            import json
            content = completion.choices[0].message.content
            data = json.loads(content)
            
            result["tags"] = data.get("tags", result["tags"])
            result["summary"] = data.get("summary")
            result["reliability"] = data.get("reliability_score")
            result["clickbait"] = data.get("clickbait_score")
            result["sentiment"] = data.get("sentiment")
            result["reasoning"] = data.get("reasoning")
            
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return result

    async def generate_tags(self, text: str) -> str:
        """Legacy method for backward compatibility"""
        analysis = await self.analyze_content(text)
        return analysis["tags"]
        
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
