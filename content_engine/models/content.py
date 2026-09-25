"""
Content data models
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of content that can be generated"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"
    CODE = "code"
    SOCIAL_POST = "social_post"
    BLOG_POST = "blog_post"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    PRODUCT_DESCRIPTION = "product_description"
    SEO_CONTENT = "seo_content"
    SCRIPT = "script"
    POEM = "poem"
    STORY = "story"
    QUOTE = "quote"
    POLL = "poll"
    QUIZ = "quiz"


class PlatformType(str, Enum):
    """Supported social media platforms"""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEB = "web"
    EMAIL = "email"
    BLOG = "blog"
    OTHER = "other"


class ContentQuality(str, Enum):
    """Quality levels for generated content"""
    DRAFT = "draft"
    STANDARD = "standard"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"


class ContentTone(str, Enum):
    """Tone styles for content"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    HUMOROUS = "humorous"
    SARCASTIC = "sarcastic"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    STORYTELLING = "storytelling"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    EMOTIONAL = "emotional"


class ContentStyle(str, Enum):
    """Writing styles for content"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    CONCise = "concise"
    DETAILED = "detailed"
    SIMPLE = "simple"
    COMPLEX = "complex"
    CREATIVE = "creative"
    DIRECT = "direct"
    METAPHORICAL = "metaphorical"


class ContentRequest(BaseModel):
    """Request model for content generation"""
    
    # Content specification
    content_type: ContentType = Field(
        default=ContentType.TEXT,
        description="Type of content to generate"
    )
    
    platform: Optional[PlatformType] = Field(
        default=None,
        description="Target platform for the content"
    )
    
    # Content input
    prompt: str = Field(
        default="",
        description="The main prompt or topic for content generation"
    )
    
    context: Optional[str] = Field(
        default=None,
        description="Additional context or background information"
    )
    
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to include in the content"
    )
    
    # Style and tone
    tone: Optional[ContentTone] = Field(
        default=None,
        description="Desired tone for the content"
    )
    
    style: Optional[ContentStyle] = Field(
        default=None,
        description="Writing style for the content"
    )
    
    quality: ContentQuality = Field(
        default=ContentQuality.STANDARD,
        description="Quality level for the content"
    )
    
    # Length constraints
    min_length: Optional[int] = Field(
        default=None,
        description="Minimum length in characters"
    )
    
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum length in characters"
    )
    
    # Formatting
    use_markdown: bool = Field(
        default=False,
        description="Whether to use markdown formatting"
    )
    
    use_emojis: bool = Field(
        default=True,
        description="Whether to include emojis"
    )
    
    use_hashtags: bool = Field(
        default=True,
        description="Whether to include hashtags"
    )
    
    hashtag_count: Optional[int] = Field(
        default=None,
        description="Number of hashtags to include"
    )
    
    # AI Provider settings
    provider: Optional[str] = Field(
        default=None,
        description="AI provider to use"
    )
    
    model: Optional[str] = Field(
        default=None,
        description="Specific model to use"
    )
    
    temperature: Optional[float] = Field(
        default=None,
        description="Creativity temperature (0-1)"
    )
    
    # Customization
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Custom instructions for content generation"
    )
    
    template_id: Optional[str] = Field(
        default=None,
        description="Template ID to use for generation"
    )
    
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variables to substitute in the template"
    )
    
    # Metadata
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier for tracking"
    )
    
    # Additional options
    include_call_to_action: bool = Field(
        default=False,
        description="Whether to include a call to action"
    )
    
    include_questions: bool = Field(
        default=False,
        description="Whether to include questions"
    )
    
    target_audience: Optional[str] = Field(
        default=None,
        description="Target audience for the content"
    )
    
    language: str = Field(
        default="en",
        description="Language for the content"
    )


class ContentResponse(BaseModel):
    """Response model for generated content"""
    
    # Content
    content: str = Field(
        default="",
        description="Generated content"
    )
    
    content_type: ContentType = Field(
        default=ContentType.TEXT,
        description="Type of generated content"
    )
    
    platform: Optional[PlatformType] = Field(
        default=None,
        description="Target platform"
    )
    
    # Metadata
    request_id: str = Field(
        default="",
        description="Unique request identifier"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier"
    )
    
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )
    
    # Generation info
    provider: str = Field(
        default="",
        description="AI provider used"
    )
    
    model: str = Field(
        default="",
        description="Model used for generation"
    )
    
    generation_time: float = Field(
        default=0.0,
        description="Time taken for generation in seconds"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of generation"
    )
    
    # Quality metrics
    quality_score: Optional[float] = Field(
        default=None,
        description="Quality score (0-1)"
    )
    
    readability_score: Optional[float] = Field(
        default=None,
        description="Readability score"
    )
    
    # Analysis
    sentiment: Optional[str] = Field(
        default=None,
        description="Sentiment analysis result"
    )
    
    tone: Optional[str] = Field(
        default=None,
        description="Detected tone"
    )
    
    keywords_used: List[str] = Field(
        default_factory=list,
        description="Keywords used in the content"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="Hashtags in the content"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    word_count: int = Field(
        default=0,
        description="Word count"
    )
    
    sentence_count: int = Field(
        default=0,
        description="Sentence count"
    )
    
    paragraph_count: int = Field(
        default=0,
        description="Paragraph count"
    )
    
    # Additional data
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Alternatives
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative content variations"
    )
    
    # Warnings and suggestions
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about the generated content"
    )
    
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improvement"
    )
