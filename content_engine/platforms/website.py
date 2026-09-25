"""
Website/Blog specific content generator
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
from content_engine.models.platforms import WebsiteContent
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class WebsiteGenerator(PlatformGenerator):
    """Website/Blog specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.WEB)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.WEB
    
    @property
    def get_platform_name(self) -> str:
        return "Website/Blog"
    
    @property
    def get_max_length(self) -> int:
        return 10000  # Websites can have much longer content
    
    @property
    def get_hashtag_limit(self) -> int:
        return 10  # Hashtags are less common on websites
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate website/blog content"""
        request = self._create_request(prompt, **kwargs)
        
        # Default to blog_post for website content
        if not kwargs.get('content_type'):
            request.content_type = ContentType.BLOG_POST
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create website-specific response
        website_response = ContentResponse(
            **response.model_dump(),
            content=formatted_content,
            metadata={
                **response.metadata,
                "platform_specific": {
                    "character_count": len(formatted_content),
                    "word_count": len(formatted_content.split()),
                    "is_valid": self.validate_content(formatted_content)["is_valid"],
                }
            }
        )
        
        return website_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate website content for multiple prompts"""
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
        """Generate website content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="web",
            content_type="blog_post",
            **kwargs,
        ):
            yield chunk
    
    async def generate_blog_post(
        self,
        title: str,
        outline: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a complete blog post"""
        outline_str = '\n'.join([f"- {point}" for point in outline])
        
        prompt = f"""Create a blog post with this outline:

Title: {title}
Outline:
{outline_str}

Generate:
- Engaging introduction
- Well-structured content for each section
- Subheadings (use ## for subheadings)
- Examples and details
- Conclusion
- Call-to-action
- SEO-friendly content
- Use Markdown formatting"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_blog_post"] = True
        response.metadata["title"] = title
        return response
    
    async def generate_website_page(
        self,
        page_title: str,
        sections: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a website page"""
        sections_str = '\n'.join([f"## {section}" for section in sections])
        
        prompt = f"""Create a website page for:

Title: {page_title}
Sections:
{sections_str}

Generate:
- Professional page content
- Clear section headings
- Informative and engaging
- Call-to-action where appropriate
- Use Markdown formatting"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_page"] = True
        response.metadata["page_title"] = page_title
        return response
    
    async def generate_product_description(
        self,
        product_name: str,
        features: List[str],
        benefits: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a product description"""
        features_str = '\n'.join([f"- {feature}" for feature in features])
        benefits_str = '\n'.join([f"- {benefit}" for benefit in benefits])
        
        prompt = f"""Create a product description for:

Product: {product_name}
Features:
{features_str}
Benefits:
{benefits_str}

Generate:
- Compelling product introduction
- Feature descriptions
- Benefit explanations
- Use cases
- Call-to-action
- SEO-friendly"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_product"] = True
        response.metadata["product_name"] = product_name
        return response
    
    async def generate_seo_content(
        self,
        keyword: str,
        related_keywords: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate SEO-optimized content"""
        keywords_str = ', '.join(related_keywords)
        
        prompt = f"""Create SEO-optimized content for keyword: {keyword}

Related keywords: {keywords_str}

Generate:
- Content that naturally incorporates keywords
- Valuable and informative
- Well-structured
- Engaging
- At least 500 words
- Use subheadings (##)
- Include keyword in first paragraph"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_seo"] = True
        response.metadata["primary_keyword"] = keyword
        response.metadata["related_keywords"] = related_keywords
        return response
    
    async def generate_landing_page(
        self,
        product_service: str,
        value_proposition: str,
        features: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a landing page"""
        features_str = '\n'.join([f"- {feature}" for feature in features])
        
        prompt = f"""Create a landing page for:

Product/Service: {product_service}
Value Proposition: {value_proposition}
Features:
{features_str}

Generate:
- Attention-grabbing headline
- Subheadline
- Feature benefits
- Social proof elements
- Strong call-to-action
- Conversion-focused"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_landing_page"] = True
        return response
    
    async def generate_about_page(
        self,
        company_name: str,
        company_description: str,
        team: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate an about page"""
        team_str = '\n'.join([f"- {member}" for member in team])
        
        prompt = f"""Create an about page for:

Company: {company_name}
Description: {company_description}
Team:
{team_str}

Generate:
- Company story
- Mission and vision
- Team bios
- Company values
- Professional but friendly tone"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_about_page"] = True
        return response
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format website content"""
        formatted = content.strip()
        
        # Add proper Markdown formatting if requested
        if kwargs.get('use_markdown', True):
            formatted = self._format_markdown(formatted)
        
        # Add emojis if requested
        if kwargs.get('use_emojis', False):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate website content"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "character_count": len(content),
            "word_count": len(content.split()),
            "max_length": self.get_max_length,
            "within_limit": len(content) <= self.get_max_length,
        }
        
        # Website content can be very long, so we don't enforce a strict limit
        if len(content) > 50000:
            validation["warnings"].append(
                "Content is very long, consider breaking into multiple pages"
            )
        
        # Check for subheadings if it's a long post
        if len(content) > 1000:
            subheading_count = content.count('##')
            if subheading_count < 2:
                validation["warnings"].append(
                    "Consider adding subheadings for better readability"
                )
        
        # Check for Markdown formatting
        if kwargs.get('use_markdown', True):
            if '##' not in content and len(content) > 500:
                validation["warnings"].append(
                    "Consider adding subheadings with ## for better structure"
                )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get website-specific default parameters"""
        return {
            "content_type": ContentType.BLOG_POST,
            "platform": PlatformType.WEB,
            "max_length": self.get_max_length,
            "hashtag_count": 0,
            "use_emojis": False,
            "use_hashtags": False,
            "use_markdown": True,
            "tone": ContentTone.PROFESSIONAL,
        }
    
    def _format_markdown(self, content: str) -> str:
        """Format content with Markdown"""
        # Add line breaks for better readability
        if '\n' not in content and len(content) > 200:
            sentences = re.split(r'(?<=[.!?])\s+', content)
            if len(sentences) > 2:
                # Add line breaks after every 2-3 sentences
                chunks = [sentences[i:i+2] for i in range(0, len(sentences), 2)]
                content = '\n\n'.join([' '.join(chunk) for chunk in chunks])
        
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content (sparingly for websites)"""
        # Professional emojis for websites
        emoji_map = {
            'important': ['⚠️', '📌', '⭐'],
            'new': ['🆕', '📢'],
            'success': ['🎉', '🏆'],
            'tip': ['💡'],
            'question': ['❓'],
            'check': ['✅'],
            'arrow': ['➡️'],
        }
        
        return content  # Websites typically don't use many emojis
    
    async def optimize_for_seo(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize content for SEO"""
        prompt = f"""Optimize this website content for SEO:

{content}

Consider:
- Keyword density and placement
- Meta description
- Header tags (H1, H2, H3)
- Internal linking opportunities
- Readability
- Mobile-friendliness
- Schema markup opportunities
- Image alt text suggestions"""
        
        return await self.generate(prompt, **kwargs)
