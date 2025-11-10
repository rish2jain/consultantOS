"""
Data storytelling module for AI-generated narratives and persona adaptation.
"""
from consultantos.storytelling.personas import PERSONA_TRAITS, get_persona_traits
from consultantos.storytelling.narrative_generator import NarrativeGenerator
from consultantos.storytelling.viz_enhancer import VisualizationEnhancer
from consultantos.storytelling.presentation_generator import PresentationGenerator

__all__ = [
    "PERSONA_TRAITS",
    "get_persona_traits",
    "NarrativeGenerator",
    "VisualizationEnhancer",
    "PresentationGenerator",
]
