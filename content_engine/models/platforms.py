"""
Platform-specific content models
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from content_engine.models.content import ContentQuality, ContentTone, ContentType


class PlatformContent(BaseModel):
    """Base class for platform-specific content"""
    
    content: str = Field(
        default="",
        description="The generated content"
    )
    
    content_type: ContentType = Field(
        default=ContentType.TEXT,
        description="Type of content"
    )
    
    tone: Optional[ContentTone] = Field(
        default=None,
        description="Tone of the content"
    )
    
    quality: ContentQuality = Field(
        default=ContentQuality.STANDARD,
        description="Quality level"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class TwitterContent(PlatformContent):
    """Twitter/X specific content"""
    
    # Twitter-specific fields
    tweet_text: str = Field(
        default="",
        description="The tweet text (280 characters max)"
    )
    
    is_thread: bool = Field(
        default=False,
        description="Whether this is part of a thread"
    )
    
    thread_position: Optional[int] = Field(
        default=None,
        description="Position in thread (1-based)"
    )
    
    reply_to_tweet_id: Optional[str] = Field(
        default=None,
        description="ID of tweet being replied to"
    )
    
    quote_tweet_id: Optional[str] = Field(
        default=None,
        description="ID of tweet being quoted"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags"
    )
    
    mentions: List[str] = Field(
        default_factory=list,
        description="List of @mentions"
    )
    
    urls: List[str] = Field(
        default_factory=list,
        description="List of URLs"
    )
    
    media_urls: List[str] = Field(
        default_factory=list,
        description="List of media URLs"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    # Engagement predictions
    predicted_likes: Optional[int] = Field(
        default=None,
        description="Predicted number of likes"
    )
    
    predicted_retweets: Optional[int] = Field(
        default=None,
        description="Predicted number of retweets"
    )
    
    predicted_replies: Optional[int] = Field(
        default=None,
        description="Predicted number of replies"
    )
    
    # Best time to post (optional)
    optimal_post_time: Optional[datetime] = Field(
        default=None,
        description="Optimal time to post"
    )


class FacebookContent(PlatformContent):
    """Facebook specific content"""
    
    post_text: str = Field(
        default="",
        description="The post text"
    )
    
    caption: Optional[str] = Field(
        default=None,
        description="Caption for media"
    )
    
    is_album: bool = Field(
        default=False,
        description="Whether this is an album post"
    )
    
    media_urls: List[str] = Field(
        default_factory=list,
        description="List of media URLs"
    )
    
    video_url: Optional[str] = Field(
        default=None,
        description="Video URL"
    )
    
    link_url: Optional[str] = Field(
        default=None,
        description="Link URL"
    )
    
    link_title: Optional[str] = Field(
        default=None,
        description="Link title"
    )
    
    link_description: Optional[str] = Field(
        default=None,
        description="Link description"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags"
    )
    
    tagged_users: List[str] = Field(
        default_factory=list,
        description="List of tagged users"
    )
    
    location: Optional[str] = Field(
        default=None,
        description="Location tag"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    # Targeting
    target_audience: Optional[str] = Field(
        default=None,
        description="Target audience"
    )


class InstagramContent(PlatformContent):
    """Instagram specific content"""
    
    caption: str = Field(
        default="",
        description="The caption text"
    )
    
    alt_text: Optional[str] = Field(
        default=None,
        description="Alt text for accessibility"
    )
    
    is_carousel: bool = Field(
        default=False,
        description="Whether this is a carousel post"
    )
    
    media_urls: List[str] = Field(
        default_factory=list,
        description="List of image/video URLs"
    )
    
    story_media_url: Optional[str] = Field(
        default=None,
        description="Media URL for story"
    )
    
    reel_video_url: Optional[str] = Field(
        default=None,
        description="Video URL for reel"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags"
    )
    
    mentions: List[str] = Field(
        default_factory=list,
        description="List of @mentions"
    )
    
    location: Optional[str] = Field(
        default=None,
        description="Location tag"
    )
    
    # Story features
    use_poll: bool = Field(
        default=False,
        description="Whether to include a poll"
    )
    
    poll_question: Optional[str] = Field(
        default=None,
        description="Poll question"
    )
    
    poll_options: List[str] = Field(
        default_factory=list,
        description="Poll options"
    )
    
    use_question_sticker: bool = Field(
        default=False,
        description="Whether to use question sticker"
    )
    
    question_text: Optional[str] = Field(
        default=None,
        description="Question text for sticker"
    )
    
    # Reel features
    use_music: bool = Field(
        default=False,
        description="Whether to use music"
    )
    
    music_track: Optional[str] = Field(
        default=None,
        description="Music track name"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    hashtag_count: int = Field(
        default=0,
        description="Number of hashtags"
    )


class LinkedInContent(PlatformContent):
    """LinkedIn specific content"""
    
    post_text: str = Field(
        default="",
        description="The post text"
    )
    
    article_title: Optional[str] = Field(
        default=None,
        description="Article title"
    )
    
    article_content: Optional[str] = Field(
        default=None,
        description="Article content (markdown)"
    )
    
    is_article: bool = Field(
        default=False,
        description="Whether this is an article"
    )
    
    media_urls: List[str] = Field(
        default_factory=list,
        description="List of media URLs"
    )
    
    document_url: Optional[str] = Field(
        default=None,
        description="Document URL"
    )
    
    video_url: Optional[str] = Field(
        default=None,
        description="Video URL"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags"
    )
    
    mentioned_companies: List[str] = Field(
        default_factory=list,
        description="List of mentioned companies"
    )
    
    mentioned_people: List[str] = Field(
        default_factory=list,
        description="List of mentioned people"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    # Professional targeting
    industry_tags: List[str] = Field(
        default_factory=list,
        description="Industry tags"
    )
    
    skill_tags: List[str] = Field(
        default_factory=list,
        description="Skill tags"
    )


class PinterestContent(PlatformContent):
    """Pinterest specific content"""
    
    pin_title: str = Field(
        default="",
        description="Pin title"
    )
    
    pin_description: str = Field(
        default="",
        description="Pin description"
    )
    
    image_url: str = Field(
        default="",
        description="Image URL"
    )
    
    link_url: Optional[str] = Field(
        default=None,
        description="Link URL"
    )
    
    board_name: Optional[str] = Field(
        default=None,
        description="Board name"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="List of hashtags"
    )
    
    # SEO
    seo_keywords: List[str] = Field(
        default_factory=list,
        description="SEO keywords"
    )
    
    seo_title: Optional[str] = Field(
        default=None,
        description="SEO optimized title"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    # Categories
    categories: List[str] = Field(
        default_factory=list,
        description="Categories"
    )


class SnapchatContent(PlatformContent):
    """Snapchat specific content"""
    
    caption: str = Field(
        default="",
        description="Caption text"
    )
    
    image_url: Optional[str] = Field(
        default=None,
        description="Image URL"
    )
    
    video_url: Optional[str] = Field(
        default=None,
        description="Video URL"
    )
    
    is_story: bool = Field(
        default=True,
        description="Whether this is a story"
    )
    
    is_spotlight: bool = Field(
        default=False,
        description="Whether this is for Spotlight"
    )
    
    # Interactive elements
    use_filter: bool = Field(
        default=False,
        description="Whether to use a filter"
    )
    
    filter_name: Optional[str] = Field(
        default=None,
        description="Filter name"
    )
    
    use_lens: bool = Field(
        default=False,
        description="Whether to use a lens"
    )
    
    lens_name: Optional[str] = Field(
        default=None,
        description="Lens name"
    )
    
    # Statistics
    character_count: int = Field(
        default=0,
        description="Character count"
    )
    
    # Duration
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Duration in seconds"
    )


class WebsiteContent(PlatformContent):
    """Website/Blog specific content"""
    
    title: str = Field(
        default="",
        description="Content title"
    )
    
    subtitle: Optional[str] = Field(
        default=None,
        description="Subtitle"
    )
    
    content: str = Field(
        default="",
        description="Main content (HTML or Markdown)"
    )
    
    meta_description: Optional[str] = Field(
        default=None,
        description="Meta description"
    )
    
    meta_keywords: List[str] = Field(
        default_factory=list,
        description="Meta keywords"
    )
    
    slug: Optional[str] = Field(
        default=None,
        description="URL slug"
    )
    
    featured_image_url: Optional[str] = Field(
        default=None,
        description="Featured image URL"
    )
    
    categories: List[str] = Field(
        default_factory=list,
        description="Categories"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags"
    )
    
    author: Optional[str] = Field(
        default=None,
        description="Author name"
    )
    
    published_date: Optional[datetime] = Field(
        default=None,
        description="Published date"
    )
    
    # SEO
    seo_title: Optional[str] = Field(
        default=None,
        description="SEO optimized title"
    )
    
    seo_description: Optional[str] = Field(
        default=None,
        description="SEO optimized description"
    )
    
    seo_keywords: List[str] = Field(
        default_factory=list,
        description="SEO keywords"
    )
    
    # Statistics
    word_count: int = Field(
        default=0,
        description="Word count"
    )
    
    reading_time_minutes: Optional[int] = Field(
        default=None,
        description="Estimated reading time in minutes"
    )
    
    # Content type
    is_blog_post: bool = Field(
        default=True,
        description="Whether this is a blog post"
    )
    
    is_page: bool = Field(
        default=False,
        description="Whether this is a page"
    )
    
    is_product: bool = Field(
        default=False,
        description="Whether this is a product description"
    )
