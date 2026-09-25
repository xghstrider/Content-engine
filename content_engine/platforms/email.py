"""
Email specific content generator
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
from content_engine.platforms.base import PlatformGenerator

logger = logging.getLogger(__name__)


class EmailGenerator(PlatformGenerator):
    """Email specific content generator"""
    
    def __init__(
        self,
        engine: Optional[ContentEngine] = None,
    ):
        super().__init__(engine, PlatformType.EMAIL)
        self.settings = get_settings()
    
    @property
    def get_platform_type(self) -> PlatformType:
        return PlatformType.EMAIL
    
    @property
    def get_platform_name(self) -> str:
        return "Email"
    
    @property
    def get_max_length(self) -> int:
        return 5000  # Email body can be quite long
    
    @property
    def get_hashtag_limit(self) -> int:
        return 0  # Emails typically don't use hashtags
    
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate email content"""
        request = self._create_request(prompt, **kwargs)
        
        # Default to email for email content
        if not kwargs.get('content_type'):
            request.content_type = ContentType.EMAIL
        
        response = await self.engine.generate_advanced(request)
        
        # Format the response
        formatted_content = self.format_content(response.content, **kwargs)
        
        # Create email-specific response
        email_response = ContentResponse(
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
        
        return email_response
    
    async def generate_batch(
        self,
        prompts: List[str],
        **kwargs,
    ) -> List[ContentResponse]:
        """Generate email content for multiple prompts"""
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
        """Generate email content with streaming"""
        async for chunk in self.engine.generate_stream(
            prompt,
            platform="email",
            content_type="email",
            **kwargs,
        ):
            yield chunk
    
    async def generate_email(
        self,
        subject: str,
        body_prompt: str,
        recipient: str = "",
        **kwargs,
    ) -> ContentResponse:
        """Generate a complete email"""
        prompt = f"""Create an email with:

Subject: {subject}
Recipient: {recipient}
Body prompt: {body_prompt}

Generate:
- Engaging subject line
- Professional greeting
- Well-structured body
- Clear call-to-action
- Professional closing
- Appropriate tone for the recipient"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["subject"] = subject
        response.metadata["recipient"] = recipient
        response.metadata["is_complete_email"] = True
        return response
    
    async def generate_subject_line(
        self,
        email_purpose: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate an email subject line"""
        prompt = f"""Create an engaging email subject line for:

Purpose: {email_purpose}

Generate:
- Short and to the point
- Attention-grabbing
- Clear value proposition
- Under 60 characters
- A/B test variations"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_subject"] = True
        
        # Subject lines should be short
        if len(response.content) > 60:
            response.content = response.content[:57] + "..."
        
        return response
    
    async def generate_email_body(
        self,
        purpose: str,
        key_points: List[str],
        call_to_action: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate an email body"""
        points_str = '\n'.join([f"- {point}" for point in key_points])
        
        prompt = f"""Create an email body for:

Purpose: {purpose}
Key Points:
{points_str}
Call-to-action: {call_to_action}

Generate:
- Professional greeting
- Introduction
- Well-structured body covering all points
- Clear call-to-action
- Professional closing
- Appropriate tone"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_newsletter(
        self,
        title: str,
        articles: List[str],
        **kwargs,
    ) -> ContentResponse:
        """Generate a newsletter"""
        articles_str = '\n\n'.join([f"### {article}" for article in articles])
        
        prompt = f"""Create a newsletter with:

Title: {title}
Articles:
{articles_str}

Generate:
- Engaging introduction
- Well-structured newsletter format
- Article summaries
- Links to full articles
- Call-to-action
- Professional but friendly tone
- Use Markdown formatting"""
        
        response = await self.generate(prompt, **kwargs)
        response.metadata["is_newsletter"] = True
        response.metadata["title"] = title
        return response
    
    async def generate_promotional_email(
        self,
        product_service: str,
        offer: str,
        deadline: str = "",
        **kwargs,
    ) -> ContentResponse:
        """Generate a promotional email"""
        prompt = f"""Create a promotional email for:

Product/Service: {product_service}
Offer: {offer}
Deadline: {deadline}

Generate:
- Attention-grabbing subject line
- Engaging introduction
- Offer details
- Benefits
- Urgency (if deadline)
- Clear call-to-action
- Persuasive but not pushy"""
        
        return await self.generate(prompt, **kwargs)
    
    async def generate_follow_up_email(
        self,
        previous_interaction: str,
        purpose: str,
        **kwargs,
    ) -> ContentResponse:
        """Generate a follow-up email"""
        prompt = f"""Create a follow-up email for:

Previous Interaction: {previous_interaction}
Purpose: {purpose}

Generate:
- Reference to previous interaction
- Reason for follow-up
- Clear next steps
- Polite and professional
- Appropriate tone"""
        
        return await self.generate(prompt, **kwargs)
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format email content"""
        formatted = content.strip()
        
        # Add proper email formatting
        if kwargs.get('use_markdown', True):
            formatted = self._format_markdown(formatted)
        
        # Add emojis if requested (sparingly for emails)
        if kwargs.get('use_emojis', False):
            formatted = self._add_emojis(formatted)
        
        return formatted
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate email content"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "character_count": len(content),
            "word_count": len(content.split()),
            "max_length": self.get_max_length,
            "within_limit": len(content) <= self.get_max_length,
        }
        
        # Check for common email issues
        if len(content) > self.get_max_length:
            validation["warnings"].append(
                f"Content is long ({len(content)} chars), consider shortening"
            )
        
        # Check for line length (emails should have shorter lines)
        lines = content.split('\n')
        for line in lines:
            if len(line) > 100:
                validation["warnings"].append(
                    "Some lines are very long, consider adding line breaks"
                )
                break
        
        # Check for greeting
        if not re.match(r'^(hi|hello|hey|dear|greetings)', content.lower()):
            validation["warnings"].append(
                "Consider adding a proper greeting at the beginning"
            )
        
        # Check for closing
        if not re.search(r'(best regards|sincerely|thank you|cheers|regards)$', content.lower()):
            validation["warnings"].append(
                "Consider adding a proper closing at the end"
            )
        
        return validation
    
    def get_platform_specific_params(self) -> Dict[str, Any]:
        """Get email-specific default parameters"""
        return {
            "content_type": ContentType.EMAIL,
            "platform": PlatformType.EMAIL,
            "max_length": self.get_max_length,
            "hashtag_count": 0,
            "use_emojis": False,
            "use_hashtags": False,
            "use_markdown": True,
            "tone": ContentTone.PROFESSIONAL,
        }
    
    def _format_markdown(self, content: str) -> str:
        """Format content with Markdown for emails"""
        # Add line breaks for better readability
        if '\n' not in content and len(content) > 200:
            sentences = re.split(r'(?<=[.!?])\s+', content)
            if len(sentences) > 2:
                # Add line breaks after every 2 sentences
                chunks = [sentences[i:i+2] for i in range(0, len(sentences), 2)]
                content = '\n\n'.join([' '.join(chunk) for chunk in chunks])
        
        # Ensure proper spacing
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _add_emojis(self, content: str) -> str:
        """Add emojis to content (sparingly for emails)"""
        # Professional emojis for emails
        emoji_map = {
            'important': ['⚠️', '📌'],
            'new': ['🆕'],
            'success': ['🎉'],
            'tip': ['💡'],
            'question': ['❓'],
        }
        
        return content  # Emails typically don't use many emojis
    
    async def optimize_for_deliverability(
        self,
        content: str,
        **kwargs,
    ) -> ContentResponse:
        """Optimize email content for deliverability"""
        prompt = f"""Optimize this email content for deliverability:

{content}

Consider:
- Avoiding spam trigger words
- Proper text-to-link ratio
- Mobile-friendly formatting
- Clear subject line
- Professional tone
- Unsubscribe link if promotional
- CAN-SPAM compliance"""
        
        return await self.generate(prompt, **kwargs)
