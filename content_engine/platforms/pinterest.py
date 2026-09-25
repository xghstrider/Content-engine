"""
Pinterest specific content generator
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
from content_engine.models.platforms import PinterestContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class PinterestGenerator(PlatformGenerator):
    """Pinterest specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.PINTEREST)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.PINTEREST
    
    @property
    def get_platform_name(self) -> str:
        return "Pinterest"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.pinterest_description_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return 20  # Pinterest doesn't have a strict limit, but 20 is recommended
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate Pinterest content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for Pinterest
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create Pinterest-specific response
        pinterest_response = ContentResponse(
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
        
        return pinterest_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate Pinterest content for multiple prompts"""
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
        """Generate Pinterest content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="pinterest",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_pin_description(
        self,
        image_url: str,
        image_description: str,
        link_url: str = "",
        **kwargs,
    ) -> ContentResponse:
        """Generate a Pinterest pin description"""
        prompt = f"""Create a Pinterest pin description for:

Image URL: {image_url}
Image Description: {image_description}
Link URL: {link_url}

Generate:
- Engaging and descriptive text
- Keywords for searchability
- Call-to-action to click
- Hashtags (2-3 relevant ones)
- Emojis if appropriate"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_pin"] = True
        response.metadata["image_url"] = image_url
        if link_url:
            response.metadata["link_url"] = link_url
        return response
    
    async def generate_board_description(
        self,
        board_name: str,
        board_topic: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a Pinterest board description"""
        prompt = f"""Create a Pinterest board description for:

Board Name: {board_name}
Topic: {board_topic}

Generate:
- Clear description of what the board is about
- Who it's for
- What they can expect to find
- Keywords for searchability
- Engaging and inviting"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_board"] = True
        response.metadata["board_name"] = board_name
        return response
    
    async def generate_seo_description(
        self,
        product_name: str,
        product_features: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate SEO-optimized Pinterest description"""
        features_str = ', '.join(product_features)
        
        prompt = f"""Create an SEO-optimized Pinterest description for:

Product: {product_name}
Features: {features_str}

Generate:
- Keyword-rich description
- Benefits and features
- Call-to-action
- Hashtags with keywords
- Natural language that includes search terms"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_recipe_pin(
        self,
        recipe_name: str,
        ingredients: List[str],
        instructions: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a Pinterest recipe pin"""
        ingredients_str = '\n'.join([f"- {ing}" for ing in ingredients])
        instructions_str = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(instructions)])
        
        prompt = f"""Create a Pinterest recipe pin for:

Recipe: {recipe_name}
Ingredients:
{ingredients_str}
Instructions:
{instructions_str}

Generate:
- Eye-catching description
- Key ingredients highlighted
- Easy to follow
- Cooking time if possible
- Serving size
- Hashtags for food/recipes"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_diy_pin(
        self,
        project_name: str,
        materials: List[str],
        steps: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a Pinterest DIY project pin"""
        materials_str = ', '.join(materials)
        steps_str = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        
        prompt = f"""Create a Pinterest DIY pin for:

Project: {project_name}
Materials: {materials_str}
Steps:
{steps_str}

Generate:
- Creative project description
- Difficulty level
- Time required
- Cost estimate
- Hashtags for DIY/crafts"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format Pinterest content"""
        formatted = content.strip()
        
        # Pinterest descriptions should be concise and scannable
        if len(formatted) > 100 and '\n' not in formatted:
            sentences = re.split(r'(?<=[.!?])\s+', formatted)
            if len(sentences) > 1:
                # Add line break after first sentence
                formatted = sentences[0] + '\n' + ' '.join(sentences[1:])
        
        # Add hashtags if requested
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 3)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        # Add emojis if requested
        if kwargs.get('use_emojis', True):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate Pinterest content"""
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
                f"Hashtag count ({hashtag_count}) may be excessive"
            )
        
        # Check for keywords
        keyword_patterns = [
            r'\b(diy|do it yourself|recipe|tutorial|guide|how to|how-to|tips|ideas|inspiration)\b',
            r'\b(easy|simple|quick|fast|best|top|amazing|beautiful|creative)\b',
        ]
        
        for pattern in keyword_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                validation["has_keywords"] = True
                break
        else:
            validation["warnings"].append(
                "Consider adding more descriptive keywords for searchability"
            )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get Pinterest-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.PINTEREST,
            "max_length": self.get_max_length,
            "hashtag_count": 3,
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
        
        # Add hashtags at the end
        hashtags = ' '.join([f'#{w}' for w in words[:count - len(existing)]])
        
        if hashtags:
            return f"{content} {hashtags}".strip()
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content"""
        # Common emojis for Pinterest
        emoji_map = {
            'recipe': ['🍴', '🍽️', '👩🍳', '👨🍳'],
            'food': ['🍕', '🍰', '🍩', '🍪'],
            'diy': ['🛠️', '🔨', '✂️'],
            'craft': ['🎨', '✏️', '🧵'],
            'fashion': ['👗', '👔', '👠', '👒'],
            'beauty': ['💄', '💅', '💇'],
            'home': ['🏠', '🛋️', '🪑'],
            'garden': ['🌺', '🌿', '🌱'],
            'travel': ['✈️', '🌍', '🏝️'],
            'wedding': ['💍', '👰', '🤵'],
            'love': ['❤️', '💖'],
            'new': ['🆕', '📌'],
        }
        
        recipe_words = ['recipe', 'food', 'meal', 'cook', 'bake']
        diy_words = ['diy', 'craft', 'project', 'make', 'create']
        fashion_words = ['fashion', 'style', 'clothes', 'outfit']
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in recipe_words):
            emoji = '🍴'
        elif any(word in content_lower for word in diy_words):
            emoji = '🛠️'
        elif any(word in content_lower for word in fashion_words):
            emoji = '👗'
        elif '!' in content:
            emoji = '✨'
        else:
            emoji = '📌'
        
        if emoji:
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def optimize_for_search(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for Pinterest search"""
        prompt = f"""Optimize this Pinterest content for search:

{content}

Consider:
- Keyword density and placement
- Descriptive language
- Search terms users might use
- Hashtag strategy with keywords
- Natural language that ranks well
- Trending topics in the niche"""
        
        return await self.generate(prompt, **kwargs)
