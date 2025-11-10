"""
Storytelling models for AI-generated narratives and persona-based content.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Persona(str, Enum):
    """Target audience personas with specific content preferences."""
    EXECUTIVE = "executive"  # C-suite, board members
    TECHNICAL = "technical"  # Engineers, data scientists
    SALES = "sales"          # Sales teams, account managers
    INVESTOR = "investor"    # VCs, shareholders
    ANALYST = "analyst"      # Business analysts, consultants


class NarrativeType(str, Enum):
    """Types of narratives that can be generated."""
    SUMMARY = "summary"              # Executive summary
    TREND = "trend"                  # Trend analysis
    INSIGHT = "insight"              # Key insight explanation
    RECOMMENDATION = "recommendation"  # Actionable recommendation
    COMPARISON = "comparison"        # Comparative analysis
    FORECAST = "forecast"            # Future prediction


class ChartAnnotation(BaseModel):
    """Annotation for enhancing visualizations."""
    chart_id: str
    annotation_type: str = Field(..., description="Type: callout, arrow, highlight, trend_line")
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    text: str
    color: str = "#FF6B6B"
    importance: int = Field(ge=1, le=5, default=3)


class NarrativeSection(BaseModel):
    """A section within a narrative."""
    heading: str
    content: str
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    visualizations: List[str] = Field(default_factory=list, description="Chart IDs referenced")
    key_points: List[str] = Field(default_factory=list)
    annotations: List[ChartAnnotation] = Field(default_factory=list)


class Narrative(BaseModel):
    """AI-generated narrative content."""
    title: str
    subtitle: Optional[str] = None
    sections: List[NarrativeSection]
    key_insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    tone: str = Field(default="professional", description="professional, casual, technical, persuasive")
    length_words: int = Field(ge=0)
    confidence_score: float = Field(ge=0, le=1, default=0.8)
    generated_for_persona: Persona
    source_data_summary: str = Field(default="")


class Slide(BaseModel):
    """Presentation slide definition."""
    slide_number: int
    layout: str = Field(default="title_content", description="title, title_content, two_column, full_image")
    title: str
    content: List[str] = Field(default_factory=list, description="Bullet points or paragraphs")
    chart_ids: List[str] = Field(default_factory=list)
    speaker_notes: Optional[str] = None
    background_color: str = "#FFFFFF"
    text_color: str = "#000000"


class StorytellingResult(BaseModel):
    """Complete storytelling output."""
    narrative: Narrative
    persona: Persona
    enhanced_visualizations: List[str] = Field(default_factory=list, description="Chart IDs with annotations")
    presentation_slides: List[Slide] = Field(default_factory=list)
    export_formats: List[str] = Field(default_factory=list, description="Available formats: pdf, pptx, docx, json")
    generation_time_seconds: float = Field(ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StorytellingRequest(BaseModel):
    """Request to generate storytelling content."""
    analysis_data: Dict[str, Any] = Field(..., description="Analysis results to create narrative from")
    persona: Persona
    narrative_types: List[NarrativeType] = Field(default_factory=lambda: [NarrativeType.SUMMARY])
    include_visualizations: bool = True
    include_presentation: bool = False
    tone_preference: Optional[str] = None
    max_length_words: int = Field(default=1500, ge=100, le=10000)
    focus_areas: List[str] = Field(default_factory=list, description="Specific topics to emphasize")


class PersonaAdaptationRequest(BaseModel):
    """Request to adapt existing content for different persona."""
    original_narrative: Narrative
    target_persona: Persona
    preserve_data: bool = True
    adjust_tone: bool = True
    adjust_detail_level: bool = True


class VisualizationEnhancementRequest(BaseModel):
    """Request to enhance visualizations with annotations."""
    chart_ids: List[str]
    analysis_data: Dict[str, Any]
    persona: Persona
    annotation_types: List[str] = Field(default_factory=lambda: ["callout", "trend_line", "highlight"])
    max_annotations_per_chart: int = Field(default=5, ge=1, le=10)


class PresentationRequest(BaseModel):
    """Request to generate presentation slides."""
    narrative: Narrative
    max_slides: int = Field(default=10, ge=3, le=50)
    include_charts: bool = True
    template: str = Field(default="professional", description="professional, modern, minimal, corporate")
    brand_colors: Optional[Dict[str, str]] = None
