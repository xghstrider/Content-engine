"""
Twitter/X specific content generator
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union

from content_engine.config.settings import get_settings
from content_engine.core.engine import ContentEngine
from content_engine.models.content import (
    ContentRequest,
    ContentResponse,
    ContentTone,
    ContentType,
    PlatformType,
)
from content_engine.models.generation import GenerationConfig
from content_engine.models.platforms import TwitterContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class TwitterGenerator(PlatformGenerator):
    """Twitter/X specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.TWITTER)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.TWITTER
    
    @property
    def get_platform_name(self) -> str:
        return "Twitter/X"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.twitter_max_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return self.settings.platforms.twitter_hashtag_limit
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Twitter/X content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for Twitter
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create Twitter-specific response
        twitter_response = ContentResponse(
            **response.model_dump(),
            content=formatted_content,
            metadata={
                **response.metadata,
                "platform_specific": {
                    "character_count": len(formatted_content),
                    "is_valid": self.validate_content(formatted_content)["is_valid"],
                }
            }
        )
        
        return twitter_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate Twitter content for multiple prompts"""
        responses = []
        
        for prompt in prompts:
            response = await self.generate(prompt, **kwargs)
            responses.append(response)
        
        return responses
    
    async def generate_stream(
        self,
        prompt: str,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Generate Twitter content with streaming"""
        request = self._create_request(prompt, **kwargs)
        request.content_type = ContentType.SOCIAL_POST
        
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="twitter",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_thread(
        self,
        topic: str,
        tweet_count: int = 3,
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate a Twitter thread (multiple connected tweets)"""
        threads = []
        
        for i in range(tweet_count):
            prompt = f"""Create tweet {i+1} of {tweet_count} for a Twitter thread about: {topic}
            
Make each tweet:
- Standalone but connected to the thread
- {self.get_max_length} characters or less
- Engaging and valuable
- Use thread format (1/{tweet_count}, 2/{tweet_count}, etc.)"""
            
            response = await self.generate(
                prompt,
                **kwargs,
            )
            
            # Add thread position
            response.metadata["thread_position"] = i + 1
            response.metadata["total_tweets"] = tweet_count
            
            threads.append(response)
        
        return threads
    
    async def generate_reply(
        self,
        original_tweet: str,
        reply_style: str = "engaging",
        **kwargs,
    ) -> ContentResponse:
        """Generate a reply to a tweet"""
        prompt = f"""Create an engaging reply to this tweet:

{original_tweet}

Reply style: {reply_style}
- Keep it under {self.get_max_length} characters
- Be relevant and add value
- Use appropriate tone"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_quote_tweet(
        self,
        original_tweet: str,
        quote_text: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a quote tweet"""
        prompt = f"""Create a quote tweet for this content:

Original tweet: {original_tweet}
Your quote: {quote_text}

Combine them into a single tweet that:
- Includes both the original and your quote
- Is under {self.get_max_length} characters
- Adds value to the original"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format Twitter content"""
        formatted = content.strip()
        
        # Ensure it fits within Twitter's limit
        if len(formatted) > self.get_max_length:
            formatted = formatted[:self.get_max_length - 3] + "..."
        
        # Add hashtags if requested
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 2)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        # Add emojis if requested
        if kwargs.get('use_emojis', True):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate Twitter content"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "character_count": len(content),
            "max_length": self.get_max_length,
            "within_limit": len(content) <= self.get_max_length,
        }
        
        if len(content) > self.get_max_length:
            validation["is_valid"] = False
            validation["errors"].append(f"Content exceeds {self.get_max_length} character limit")
        
        # Count hashtags
        hashtags = re.findall(r'#\w+', content)
        hashtag_count = len(hashtags)
        validation["hashtag_count"] = hashtag_count
        
        if hashtag_count > self.get_hashtag_limit():
            validation["warnings"].append(
                f"Hashtag count ({hashtag_count}) exceeds recommended limit ({self.get_hashtag_limit()})"
            )
        
        # Check for URLs
        urls = re.findall(r'https?://\S+', content)
        validation["url_count"] = len(urls)
        
        if len(urls) > 1:
            validation["warnings"].append(
                "Multiple URLs in tweet may reduce engagement"
            )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get Twitter-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.TWITTER,
            "max_length": self.get_max_length,
            "hashtag_count": 2,
            "use_emojis": True,
            "use_hashtags": True,
            "tone": ContentTone.CASUAL,
        }
    
    def _add_hashtags(self, content: str, count: int) -> str:
        """Add hashtags to content"""
        # Extract existing hashtags
        existing = re.findall(r'#\w+', content)
        
        if len(existing) >= count:
            return content
        
        # Generate relevant hashtags (simplified - in production would use AI)
        words = re.findall(r'\b\w{4,}\b', content.lower())
        words = [w for w in words if not w.startswith('http') and not w.startswith('www')]
        
        # Select top words for hashtags
        words = sorted(set(words), key=len, reverse=True)[:count]
        
        # Add hashtags at the end
        hashtags = ' '.join([f'#{w}' for w in words[:count - len(existing)]])
        
        if hashtags:
            return f"{content} {hashtags}".strip()
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content"""
        # Common emojis for different sentiments
        emoji_map = {
            'happy': ['😊', '😃', '😄', '😁'],
            'sad': ['😢', '😭', '😞'],
            'excited': ['😍', '🤩', '🥳'],
            'angry': ['😠', '😡'],
            'thoughtful': ['🤔', '🧐'],
            'funny': ['😂', '😆', '🤣'],
            'love': ['❤️', '💖', '💝'],
            'fire': ['🔥', '💥', '✨'],
            'new': ['🆕', '📢'],
            'important': ['⚠️', '📌', '⭐'],
        }
        
        # Simple sentiment detection
        positive_words = ['good', 'great', 'awesome', 'excellent', 'happy', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad']
        question_words = ['what', 'how', 'why', 'when', 'where']
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in positive_words):
            emoji = '😊'
        elif any(word in content_lower for word in negative_words):
            emoji = '😢'
        elif any(word in content_lower for word in question_words):
            emoji = '🤔'
        elif '!' in content:
            emoji = '😍'
        else:
            emoji = ''
        
        if emoji:
            # Add emoji at the beginning or end
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def get_trending_hashtags(self, topic: str, limit: int = 5) -> List[str]:
        """Get trending hashtags for a topic (simplified)"""
        # In production, this would use Twitter API or other sources
        # For now, generate relevant hashtags
        words = topic.lower().split()
        return [f'#{word}' for word in words[:limit]]
    
    async def optimize_for_engagement(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for maximum engagement"""
        prompt = f"""Optimize this Twitter content for maximum engagement:

{content}

Consider:
- Best posting times
- Optimal length ({self.get_max_length} chars max)
- Hashtag strategy
- Emoji usage
- Call-to-action
- Current trends"""
        
        return await self.generate(prompt, **kwargs)
