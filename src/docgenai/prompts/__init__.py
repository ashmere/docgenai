"""
High-Quality Prompts for DocGenAI

This package contains purpose-specific prompts organized for easy editing
and maintenance. Each module focuses on a specific type of documentation.
"""

from .architecture import ARCHITECTURE_ANALYSIS_PROMPT
from .base import BASE_PROMPT_TEMPLATES
from .prompt_manager import PromptManager
from .refinement import DOCUMENTATION_REFINEMENT_PROMPTS
from .synthesis import MULTI_CHUNK_SYNTHESIS_PROMPT

__all__ = [
    "ARCHITECTURE_ANALYSIS_PROMPT",
    "MULTI_CHUNK_SYNTHESIS_PROMPT",
    "DOCUMENTATION_REFINEMENT_PROMPTS",
    "BASE_PROMPT_TEMPLATES",
    "PromptManager",
]
