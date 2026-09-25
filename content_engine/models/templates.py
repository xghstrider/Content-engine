"""
Template data models
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TemplateType(str, Enum):
    """Types of templates"""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PYTHON = "python"


class TemplateCategory(str, Enum):
    """Categories of templates"""
    SOCIAL_MEDIA = "social_media"
    BLOG = "blog"
    EMAIL = "email"
    ADVERTISING = "advertising"
    PRODUCT = "product"
    SEO = "seo"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BUSINESS = "business"
    PERSONAL = "personal"


class TemplateVariable(BaseModel):
    """Variable definition for templates"""
    
    name: str = Field(
        default="",
        description="Variable name"
    )
    
    description: str = Field(
        default="",
        description="Variable description"
    )
    
    default_value: Any = Field(
        default=None,
        description="Default value"
    )
    
    required: bool = Field(
        default=False,
        description="Whether the variable is required"
    )
    
    type: str = Field(
        default="string",
        description="Variable type"
    )
    
    options: List[str] = Field(
        default_factory=list,
        description="Available options for the variable"
    )


class Template(BaseModel):
    """Template definition"""
    
    # Identification
    id: str = Field(
        default="",
        description="Unique template identifier"
    )
    
    name: str = Field(
        default="",
        description="Template name"
    )
    
    description: str = Field(
        default="",
        description="Template description"
    )
    
    # Template content
    template_type: TemplateType = Field(
        default=TemplateType.TEXT,
        description="Type of template"
    )
    
    content: str = Field(
        default="",
        description="Template content"
    )
    
    # Metadata
    category: TemplateCategory = Field(
        default=TemplateCategory.SOCIAL_MEDIA,
        description="Template category"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Template tags"
    )
    
    author: Optional[str] = Field(
        default=None,
        description="Template author"
    )
    
    version: str = Field(
        default="1.0",
        description="Template version"
    )
    
    # Variables
    variables: List[TemplateVariable] = Field(
        default_factory=list,
        description="Template variables"
    )
    
    # Usage
    usage_count: int = Field(
        default=0,
        ge=0,
        description="Number of times used"
    )
    
    popularity_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Popularity score"
    )
    
    # Dates
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    
    # Platform-specific
    platform: Optional[str] = Field(
        default=None,
        description="Target platform"
    )
    
    # Example
    example_output: Optional[str] = Field(
        default=None,
        description="Example output"
    )
    
    # Settings
    is_public: bool = Field(
        default=True,
        description="Whether the template is public"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether the template is active"
    )
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    def render(self, variables: Dict[str, Any]) -> str:
        """Render the template with given variables"""
        rendered = self.content
        
        for var in self.variables:
            if var.name in variables:
                value = variables[var.name]
                placeholder = f"{{{{{var.name}}}}}"
                rendered = rendered.replace(placeholder, str(value))
            elif var.required:
                raise ValueError(f"Required variable '{var.name}' not provided")
        
        return rendered
