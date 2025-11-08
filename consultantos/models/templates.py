"""
Template models for ConsultantOS (v0.4.0)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TemplateCategory(str, Enum):
    """Template categories"""
    PORTER = "porter"
    SWOT = "swot"
    PESTEL = "pestel"
    BLUE_OCEAN = "blue_ocean"
    CUSTOM = "custom"
    INDUSTRY_SPECIFIC = "industry_specific"


class TemplateVisibility(str, Enum):
    """Template visibility"""
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"


class FrameworkTemplate(BaseModel):
    """Framework template model"""
    template_id: str
    name: str = Field(..., description="Template name")
    category: TemplateCategory
    description: Optional[str] = None
    framework_type: str = Field(..., description="porter, swot, pestel, blue_ocean")
    
    # Template content
    prompt_template: str = Field(..., description="Prompt template with placeholders")
    structure: Dict[str, Any] = Field(..., description="Expected output structure")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Example outputs")
    
    # Metadata
    created_by: str = Field(..., description="User ID of creator")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    visibility: TemplateVisibility = TemplateVisibility.PRIVATE
    
    # Usage stats
    usage_count: int = 0
    rating: Optional[float] = None  # Average rating 1-5
    tags: List[str] = Field(default_factory=list)
    
    # Industry/context specific
    industry: Optional[str] = None
    region: Optional[str] = None


class TemplateLibrary(BaseModel):
    """Template library response"""
    templates: List[FrameworkTemplate]
    total: int
    page: int = 1
    page_size: int = 20


class CreateTemplateRequest(BaseModel):
    """Request to create a template"""
    name: str
    category: TemplateCategory
    description: Optional[str] = None
    framework_type: str
    prompt_template: str
    structure: Dict[str, Any]
    examples: Optional[List[Dict[str, Any]]] = None
    visibility: TemplateVisibility = TemplateVisibility.PRIVATE
    tags: Optional[List[str]] = None
    industry: Optional[str] = None
    region: Optional[str] = None


class UpdateTemplateRequest(BaseModel):
    """Request to update a template"""
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    visibility: Optional[TemplateVisibility] = None
    tags: Optional[List[str]] = None

