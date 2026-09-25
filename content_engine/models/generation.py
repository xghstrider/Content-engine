"""
Generation data models
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GenerationStatus(str, Enum):
    """Status of content generation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationConfig(BaseModel):
    """Configuration for content generation"""
    
    # AI settings
    provider: str = Field(
        default="openai",
        description="AI provider to use"
    )
    
    model: str = Field(
        default="gpt-4-turbo-preview",
        description="Model to use"
    )
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Creativity temperature"
    )
    
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Top-p sampling"
    )
    
    max_tokens: int = Field(
        default=4096,
        ge=1,
        description="Maximum tokens to generate"
    )
    
    frequency_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Frequency penalty"
    )
    
    presence_penalty: float = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="Presence penalty"
    )
    
    # Generation settings
    num_generations: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of generations to create"
    )
    
    use_streaming: bool = Field(
        default=False,
        description="Whether to use streaming generation"
    )
    
    # Caching
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results"
    )
    
    cache_ttl: int = Field(
        default=3600,
        ge=0,
        description="Cache TTL in seconds"
    )
    
    # Retry settings
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )
    
    retry_delay: float = Field(
        default=1.0,
        ge=0.0,
        description="Delay between retries in seconds"
    )
    
    # Custom settings
    custom_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom provider-specific parameters"
    )


class GenerationResult(BaseModel):
    """Result of content generation"""
    
    # Identification
    generation_id: str = Field(
        default="",
        description="Unique generation identifier"
    )
    
    request_id: str = Field(
        default="",
        description="Request identifier"
    )
    
    # Status
    status: GenerationStatus = Field(
        default=GenerationStatus.PENDING,
        description="Generation status"
    )
    
    # Content
    generated_content: List[str] = Field(
        default_factory=list,
        description="List of generated content"
    )
    
    # Progress
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Progress percentage"
    )
    
    current_step: str = Field(
        default="",
        description="Current step in generation"
    )
    
    total_steps: int = Field(
        default=0,
        ge=0,
        description="Total steps in generation"
    )
    
    # Timing
    start_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="Start time of generation"
    )
    
    end_time: Optional[datetime] = Field(
        default=None,
        description="End time of generation"
    )
    
    duration: Optional[float] = Field(
        default=None,
        description="Duration in seconds"
    )
    
    # Metrics
    tokens_used: int = Field(
        default=0,
        ge=0,
        description="Tokens used in generation"
    )
    
    tokens_generated: int = Field(
        default=0,
        ge=0,
        description="Tokens generated"
    )
    
    # Cost
    cost: float = Field(
        default=0.0,
        ge=0.0,
        description="Cost of generation"
    )
    
    # Errors
    errors: List[str] = Field(
        default_factory=list,
        description="List of errors during generation"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
