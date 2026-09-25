"""
LinkedIn specific content generator
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
from content_engine.models.platforms import LinkedInContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class LinkedInGenerator(PlatformGenerator):
    """LinkedIn specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.LINKEDIN)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.LINKEDIN
    
    @property
    def get_platform_name(self) -> str:
        return "LinkedIn"
    
    @property
    def get_max_length(self) -> int:
        return self.settings.platforms.linkedin_post_length
    
    @property
    def get_hashtag_limit(self) -> int:
        return self.settings.platforms.linkedin_hashtag_limit
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate LinkedIn content"""
        request = self._create_request(prompt, **kwargs)
        
        # Ensure content type is social_post for LinkedIn
        if not kwargs.get('content_type'):
            request.content_type = ContentType.SOCIAL_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create LinkedIn-specific response
        linkedin_response = ContentResponse(
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
        
        return linkedin_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate LinkedIn content for multiple prompts"""
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
        """Generate LinkedIn content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="linkedin",
            content_type="social_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_article(
        self,
        title: str,
        outline: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn article"""
        outline_str = '\n'.join([f"- {point}" for point in outline])
        
        prompt = f"""Create a LinkedIn article with this outline:

Title: {title}
Outline:
{outline_str}

Generate:
- Professional introduction
- Well-structured content for each point
- Professional tone
- Insights and expertise
- Call-to-action at the end
- Appropriate length for LinkedIn articles"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_article"] = True
        return response
    
    async def generate_post(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn post"""
        return await self.generate(content, **kwargs)
    
    async def generate_company_update(
        self,
        company_name: str,
        update_type: str,
        details: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn company update"""
        prompt = f"""Create a LinkedIn company update for:

Company: {company_name}
Update Type: {update_type}
Details: {details}

Generate:
- Professional announcement
- Key achievements or news
- Impact on industry/team
- Call-to-action
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_job_posting(
        self,
        position: str,
        company: str,
        description: str,
        requirements: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn job posting"""
        requirements_str = '\n'.join([f"- {req}" for req in requirements])
        
        prompt = f"""Create a LinkedIn job posting for:

Position: {position}
Company: {company}
Description: {description}
Requirements:
{requirements_str}

Generate:
- Engaging job title and introduction
- Company overview
- Position details
- Requirements and qualifications
- Benefits
- Call-to-action to apply
- Professional tone"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_achievement_post(
        self,
        achievement: str,
        impact: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn achievement post"""
        prompt = f"""Create a LinkedIn achievement post for:

Achievement: {achievement}
Impact: {impact}

Generate:
- Humble but proud announcement
- Context and background
- Lessons learned
- Gratitude
- Professional tone
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_industry_insight(
        self,
        topic: str,
        key_points: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a LinkedIn industry insight post"""
        points_str = '\n'.join([f"- {point}" for point in key_points])
        
        prompt = f"""Create a LinkedIn industry insight post about:

Topic: {topic}
Key Points:
{points_str}

Generate:
- Thought leadership content
- Industry trends and analysis
- Data-driven insights
- Actionable advice
- Professional tone
- Hashtags"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format LinkedIn content"""
        formatted = content.strip()
        
        # Add line breaks for better readability
        if len(formatted) > 200 and '\n' not in formatted:
            sentences = re.split(r'(?<=[.!?])\s+', formatted)
            if len(sentences) > 2:
                # Add line breaks after every 2-3 sentences
                chunks = [sentences[i:i+2] for i in range(0, len(sentences), 2)]
                formatted = '\n\n'.join([' '.join(chunk) for chunk in chunks])
        
        # Add hashtags if requested
        if kwargs.get('use_hashtags', True):
            hashtag_count = kwargs.get('hashtag_count', 3)
            formatted = self._add_hashtags(formatted, hashtag_count)
        
        # LinkedIn typically doesn't use as many emojis
        if kwargs.get('use_emojis', False):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate LinkedIn content"""
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
        
        if emoji_count > 3:
            validation["warnings"].append(
                "Too many emojis for professional LinkedIn content"
            )
        
        # Check for professional tone
        casual_words = ['lol', 'omg', 'btw', 'idk', 'smh']
        content_lower = content.lower()
        
        for word in casual_words:
            if word in content_lower:
                validation["warnings"].append(
                    f"Casual language detected: '{word}' may not be appropriate for LinkedIn"
                )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get LinkedIn-specific default parameters"""
        return {
            "content_type": ContentType.SOCIAL_POST,
            "platform": PlatformType.LINKEDIN,
            "max_length": self.get_max_length,
            "hashtag_count": 3,
            "use_emojis": False,
            "use_hashtags": True,
            "tone": ContentTone.PROFESSIONAL,
        }
    
    def _add_hashtags(self, content: str, count: int) -> str:
        """Add hashtags to content"""
        # Extract existing hashtags
        existing = re.findall(r'#\w+', content)
        
        if len(existing) >= count:
            return content
        
        # Generate relevant hashtags
        words = re.findall(r'\b\w{4,}\b', content.lower())
        words = [w.capitalize() for w in words if not w.startswith('http') and not w.startswith('www')]
        
        # Select top words for hashtags
        words = sorted(set(words), key=len, reverse=True)[:count]
        
        # Add hashtags at the end
        hashtags = ' '.join([f'#{w}' for w in words[:count - len(existing)]])
        
        if hashtags:
            return f"{content}\n\n{hashtags}".strip()
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content (sparingly for LinkedIn)"""
        # Professional emojis for LinkedIn
        emoji_map = {
            'success': ['🎉', '🏆'],
            'growth': ['📈', '🚀'],
            'learning': ['📚', '🎓'],
            'innovation': ['💡', '🔬'],
            'team': ['👥', '🤝'],
            'career': ['💼', '👔'],
            'thankful': ['🙏', '❤️'],
        }
        
        success_words = ['success', 'achievement', 'won', 'award']
        growth_words = ['growth', 'increase', 'expand', 'scale']
        learning_words = ['learn', 'education', 'knowledge', 'skill']
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in success_words):
            emoji = '🎉'
        elif any(word in content_lower for word in growth_words):
            emoji = '📈'
        elif any(word in content_lower for word in learning_words):
            emoji = '📚'
        else:
            emoji = ''
        
        if emoji:
            if content.endswith(('?', '!', '.')):
                return f"{content} {emoji}"
            else:
                return f"{emoji} {content}"
        
        return content
    
    async def optimize_for_professionalism(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for professional appearance"""
        prompt = f"""Optimize this LinkedIn content for professionalism:

{content}

Consider:
- Professional tone and language
- Industry-appropriate terminology
- Thought leadership
- Value to the network
- Engagement with professionals
- Hashtag strategy for professionals"""
        
        return await self.generate(prompt, **kwargs)
