"""
Instagram specific content generator
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
from content_engine.models.platforms import InstagramContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class InstagramGenerator(PlatformGenerator):
    """Instagram specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.INSTAGRAM)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.INSTAGRAM
    
    @property
    def get_platform_name(self) -> str:
        return "Instagram"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.instagram_caption_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return self.settings.platforms.instagram_hashtag_limit
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Instagram content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for Instagram
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create Instagram-specific response
        instagram_response = ContentResponse(
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
        
        return instagram_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate Instagram content for multiple prompts"""
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
        """Generate Instagram content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="instagram",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_caption(
        self,
        image_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate an Instagram caption"""
        prompt = f"""Create an engaging Instagram caption for:

Image description: {image_description}

Generate:
- Creative and engaging caption
- Emojis to complement the image
- Relevant hashtags
- Call-to-action if appropriate"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_carousel_caption(
        self,
        image_descriptions: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a caption for an Instagram carousel"""
        images_str = '\n'.join([f"{i+1}. {desc}" for i, desc in enumerate(image_descriptions)])
        
        prompt = f"""Create an Instagram carousel caption for these images:

{images_str}

Generate:
- Overarching theme that connects all images
- Engaging caption
- Emojis
- Hashtags
- Encourage swiping through"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_carousel"] = True
        response.metadata["image_count"] = len(image_descriptions)
        return response
    
    async def generate_story_content(
        self,
        image_video_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Instagram story content"""
        prompt = f"""Create Instagram story content for:

Media description: {image_video_description}

Generate:
- Short, engaging text for story
- Emojis
- Stickers/polls suggestions
- Hashtags (limited for stories)
- Call-to-action"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_story"] = True
        
        # Stories have shorter limits
        if len(response.content) > 100:
            response.content = response.content[:97] + "..."
        
        return response
    
    async def generate_reel_description(
        self,
        video_description: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Instagram reel description"""
        prompt = f"""Create an Instagram reel description for:

Video description: {video_description}

Generate:
- Engaging description
- Key moments in the video
- Hashtags (up to 30)
- Emojis
- Call-to-action
- Music suggestions"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_reel"] = True
        return response
    
    async def generate_hashtag_set(
        self,
        topic: str,
        count: int = 15,
        **kwargs,
    ) -> List[str]:
        """Generate a set of Instagram hashtags"""
        prompt = f"""Generate {count} relevant Instagram hashtags for: {topic}

Rules:
- Mix of popular and niche hashtags
- Include topic-specific hashtags
- Vary in popularity (some high, some medium, some low volume)
- All lowercase, no spaces, no special characters except underscores
- No banned hashtags
- Group by relevance"""
        
        response = await self.engine.generate(
            prompt,
            platform="instagram",
            content_type="text",
            **kwargs,
        )
        
        # Extract hashtags from response
        hashtags = re.findall(r'#\w+', response.content)
        return hashtags[:count]
    
    async def generate_alt_text(
        self,
        image_description: str,
        **kwargs,
    ) -> str:
        """Generate alt text for accessibility"""
        prompt = f"""Create alt text for this Instagram image:

Image description: {image_description}

Rules:
- Describe the image in detail for visually impaired users
- Include important elements, colors, actions
- Be concise but descriptive
- No hashtags or emojis
- Maximum 100 characters"""
        
        response = await self.generate(prompt, **kwargs)
        return response.content
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format Instagram content"""
        formatted = content.strip()
        
        # Add line breaks for better readability
        if len(formatted) > 100 and '\n' not in formatted:
            sentences = re.split(r'(?<=[.!?])\s+', formatted)
            if len(sentences) > 1:
                # Add line break after first sentence
                formatted = sentences[0] + '\n\n' + ' '.join(sentences[1:])
        
        # Add hashtags if requested
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 10)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        # Add emojis if requested
        if kwargs.get('use_emojis', True):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate Instagram content"""
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
        
        if emoji_count > 10:
            validation["warnings"].append(
                "Too many emojis may reduce readability"
            )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get Instagram-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.INSTAGRAM,
            "max_length": self.get_max_length,
            "hashtag_count": 10,
            "use_emojis": True,
            "use_hashtags": True,
            "tone": ContentTone.CREATIVE,
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
        
        # Add hashtags at the end, each on a new line for better readability
        hashtags = '\n'.join([f'#{w}' for w in words[:count - len(existing)]])
        
        if hashtags:
            return f"{content}\n\n{hashtags}".strip()
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content"""
        # Common emojis for Instagram
        emoji_map = {
            'photo': ['📸', '🖼️', '📷'],
            'video': ['🎥', '📹', '🎬'],
            'love': ['❤️', '💖', '💝', '😍'],
            'beautiful': ['🌸', '✨', '🌟'],
            'travel': ['✈️', '🌍', '🗺️'],
            'food': ['🍴', '🍽️', '🍕'],
            'fashion': ['👗', '👔', '👠'],
            'fitness': ['💪', '🏋️', '🏃'],
            'nature': ['🌳', '🌿', '🌺'],
            'funny': ['😂', '😆', '🤣'],
            'cool': ['😎', '🤘', '🆒'],
            'new': ['🆕', '📢'],
        }
        
        positive_words = ['beautiful', 'amazing', 'stunning', 'gorgeous', 'love']
        food_words = ['food', 'eat', 'meal', 'restaurant', 'delicious']
        travel_words = ['travel', 'trip', 'vacation', 'adventure']
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in positive_words):
            emoji = '✨'
        elif any(word in content_lower for word in food_words):
            emoji = '🍴'
        elif any(word in content_lower for word in travel_words):
            emoji = '✈️'
        elif '!' in content:
            emoji = '😍'
        else:
            emoji = '📸'  # Default for Instagram
        
        if emoji:
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def optimize_for_algorithm(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for Instagram algorithm"""
        prompt = f"""Optimize this Instagram content for the algorithm:

{content}

Consider:
- Content that encourages saves and shares
- Hashtag strategy (mix of popular and niche)
- Emoji usage
- Call-to-action
- Storytelling elements
- Reels-friendly format
- Engagement hooks"""
        
        return await self.generate(prompt, **kwargs)
