"""
Facebook specific content generator
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
from content_engine.models.platforms import FacebookContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class FacebookGenerator(PlatformGenerator):
    """Facebook specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.FACEBOOK)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.FACEBOOK
    
    @property
    def get_platform_name(self) -> str:
        return "Facebook"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.facebook_post_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return self.settings.platforms.facebook_hashtag_limit
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Facebook content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for Facebook
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create Facebook-specific response
        facebook_response = ContentResponse(
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
        
        return facebook_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate Facebook content for multiple prompts"""
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
        """Generate Facebook content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="facebook",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_post(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook post"""
        return await self.generate(content, **kwargs)
    
    async def generate_album_post(
        self,
        images: List[str],
        caption: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook album post"""
        prompt = f"""Create a Facebook album post with these images:

Images: {', '.join(images)}
Caption: {caption}

Generate:
- Engaging album description
- Context for the images
- Call-to-action"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_album"] = True
        response.metadata["image_count"] = len(images)
        return response
    
    async def generate_video_post(
        self,
        video_url: str,
        description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook video post"""
        prompt = f"""Create a Facebook video post for:

Video URL: {video_url}
Description: {description}

Generate:
- Attention-grabbing caption
- Video description
- Call-to-action
- Hashtags"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_video"] = True
        response.metadata["video_url"] = video_url
        return response
    
    async def generate_link_post(
        self,
        link_url: str,
        link_title: str = "",
        link_description: str = "",
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook link post"""
        prompt = f"""Create a Facebook link post for:

URL: {link_url}
Title: {link_title}
Description: {link_description}

Generate:
- Engaging post text
- Context for the link
- Call-to-action
- Hashtags"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_link"] = True
        response.metadata["link_url"] = link_url
        return response
    
    async def generate_live_video_announcement(
        self,
        title: str,
        start_time: str,
        description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook live video announcement"""
        prompt = f"""Create a Facebook live video announcement for:

Title: {title}
Start Time: {start_time}
Description: {description}

Generate:
- Exciting announcement
- Countdown if applicable
- What viewers can expect
- Call-to-action to join"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_event_post(
        self,
        event_name: str,
        event_date: str,
        event_location: str,
        event_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Facebook event post"""
        prompt = f"""Create a Facebook event post for:

Event Name: {event_name}
Date: {event_date}
Location: {event_location}
Description: {event_description}

Generate:
- Event announcement
- Key details
- Call-to-action to attend
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format Facebook content"""
        formatted = content.strip()
        
        # Add line breaks for better readability on Facebook
        if len(formatted) > 200 and '\n' not in formatted:
            sentences = re.split(r'(?<=[.!?])\s+', formatted)
            if len(sentences) > 2:
                # Add line break after first 1-2 sentences
                formatted = ' '.join(sentences[:2]) + '\n\n' + ' '.join(sentences[2:])
        
        # Add hashtags if requested
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 3)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        # Add emojis if requested
        if kwargs.get('use_emojis', True):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate Facebook content"""
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
        
        # Check for line breaks
        line_count = content.count('\n') + 1
        validation["line_count"] = line_count
        
        if line_count > 10:
            validation["warnings"].append(
                "Too many line breaks may affect readability"
            )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get Facebook-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.FACEBOOK,
            "max_length": self.get_max_length,
            "hashtag_count": 3,
            "use_emojis": True,
            "use_hashtags": True,
            "tone": ContentTone.FRIENDLY,
        }
    
    def _add_hashtags(self, content: str, count: int) -> str:
        """Add hashtags to content"""
        # Extract existing hashtags
        existing = re.findall(r'#\w+', content)
        
        if len(existing) >= count:
            return content
        
        # Generate relevant hashtags
        words = re.findall(r'\b\w{4,}\b', content.lower())
        words = [w for w in words if not w.startswith('http') and not w.startswith('www')]
        
        # Select top words for hashtags
        words = sorted(set(words), key=len, reverse=True)[:count]
        
        # Add hashtags at the end
        hashtags = ' '.join([f'#{w}' for w in words[:count - len(existing)]])
        
        if hashtags:
            return f"{content}\n\n{hashtags}".strip()
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content"""
        # Common emojis for Facebook
        emoji_map = {
            'happy': ['😊', '😃', '😄'],
            'love': ['❤️', '💖', '💝'],
            'excited': ['😍', '🤩', '🥳'],
            'funny': ['😂', '😆', '🤣'],
            'important': ['⚠️', '📌', '⭐'],
            'question': ['🤔', '❓'],
            'event': ['🎉', '🎊', '📅'],
            'video': ['🎥', '📹', '🎬'],
            'photo': ['📸', '🖼️'],
        }
        
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
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def optimize_for_reach(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for maximum reach"""
        prompt = f"""Optimize this Facebook content for maximum reach:

{content}

Consider:
- Best posting times for the audience
- Optimal length
- Hashtag strategy
- Emoji usage
- Shareability
- Engagement potential"""
        
        return await self.generate(prompt, **kwargs)
