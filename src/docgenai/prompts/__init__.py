"""
Prompt templates for DocGenAI.

This module contains organized prompt templates for different types of
documentation generation.
"""

from .architecture_prompts import ArchitecturePromptBuilder
from .documentation_prompts import DocumentationPromptBuilder
from .prompt_manager import PromptManager

__all__ = ["DocumentationPromptBuilder", "ArchitecturePromptBuilder", "PromptManager"]
