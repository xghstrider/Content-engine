"""
Snapchat specific content generator
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
from content_engine.models.platforms import SnapchatContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class SnapchatGenerator(PlatformGenerator):
    """Snapchat specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.SNAPCHAT)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.SNAPCHAT
    
    @property
    def get_platform_name(self) -> str:
        return "Snapchat"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.snapchat_caption_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return 3  # Snapchat captions are very short
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Snapchat content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for Snapchat
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response for Snapchat's short format
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create Snapchat-specific response
        snapchat_response = ContentResponse(
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
        
        return snapchat_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate Snapchat content for multiple prompts"""
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
        """Generate Snapchat content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="snapchat",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_story(
        self,
        image_video_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Snapchat story"""
        prompt = f"""Create a Snapchat story caption for:

Media description: {image_video_description}

Generate:
- Very short caption ({self.get_max_length} chars max)
- Casual and fun tone
- Emojis to complement
- Hashtags (max 3)
- Call-to-action or question"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_story"] = True
        return response
    
    async def generate_spotlight_content(
        self,
        video_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Snapchat Spotlight content"""
        prompt = f"""Create Snapchat Spotlight content for:

Video description: {video_description}

Generate:
- Eye-catching caption
- Descriptive but short
- Emojis
- Hashtags (1-2)
- Encourages viewing"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_spotlight"] = True
        return response
    
    async def generate_filter_content(
        self,
        filter_name: str,
        filter_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate content for a Snapchat filter/lens"""
        prompt = f"""Create content for promoting a Snapchat filter:

Filter Name: {filter_name}
Description: {filter_description}

Generate:
- Fun and engaging caption
- How to use the filter
- What it does
- Emojis
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_geofilter_content(
        self,
        location: str,
        event: str = "",
        **kwargs,
    ) -> ContentResponse:
        """Generate content for a Snapchat geofilter"""
        prompt = f"""Create content for a Snapchat geofilter at:

Location: {location}
Event: {event}

Generate:
- Location-specific caption
- Event details if applicable
- Emojis related to location
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format Snapchat content"""
        formatted = content.strip()
        
        # Snapchat captions must be very short
        if len(formatted) > self.get_max_length:
            formatted = formatted[:self.get_max_length - 3] + "..."
        
        # Add emojis if requested (Snapchat is very emoji-friendly)
        if kwargs.get('use_emojis', True):
            formatted = self._add_emojis(formatted)
        
        # Add hashtags if requested (but very limited)
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 1)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate Snapchat content"""
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
        
        # Count emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', content))
        validation["emoji_count"] = emoji_count
        
        # Check for casual tone
        formal_words = ['therefore', 'however', 'furthermore', 'consequently']
        content_lower = content.lower()
        
        for word in formal_words:
            if word in content_lower:
                validation["warnings"].append(
                    f"Formal language detected: '{word}' may not fit Snapchat's casual tone"
                )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get Snapchat-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.SNAPCHAT,
            "max_length": self.get_max_length,
            "hashtag_count": 1,
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
        
        # Generate relevant hashtags
        words = re.findall(r'\b\w{3,}\b', content.lower())
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
        # Common emojis for Snapchat
        emoji_map = {
            'fun': ['😂', '😆', '🤣', '😜'],
            'cool': ['😎', '🤘', '🆒'],
            'love': ['❤️', '💖', '😍'],
            'fire': ['🔥', '💥'],
            'new': ['🆕', '📢'],
            'photo': ['📸', '📷'],
            'video': ['🎥', '📹'],
            'selfie': ['🤳'],
            'filter': ['🌈', '✨'],
            'snap': ['👻'],
        }
        
        fun_words = ['funny', 'lol', 'haha', 'joke']
        cool_words = ['cool', 'awesome', 'amazing']
        love_words = ['love', 'heart', 'adore']
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in fun_words):
            emoji = '😂'
        elif any(word in content_lower for word in cool_words):
            emoji = '😎'
        elif any(word in content_lower for word in love_words):
            emoji = '❤️'
        elif '!' in content:
            emoji = '🔥'
        else:
            emoji = '👻'  # Default Snapchat ghost
        
        if emoji:
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def optimize_for_engagement(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for Snapchat engagement"""
        prompt = f"""Optimize this Snapchat content for engagement:

{content}

Consider:
- Very short and to the point
- Casual, fun tone
- Emoji usage
- Call-to-action or question
- Encourages interaction
- Fits Snapchat's ephemeral nature"""
        
        return await self.generate(prompt, **kwargs)
