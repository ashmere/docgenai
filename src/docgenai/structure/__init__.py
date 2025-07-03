"""
Project structure analysis module.

Provides intelligent project structure detection and semantic grouping
for universal codebase analysis.
"""

from .analyzer import ProjectStructureAnalyzer
from .grouping import SemanticGrouper
from .patterns import ProjectPatterns, StructurePattern

__all__ = [
    "ProjectStructureAnalyzer",
    "ProjectPatterns",
    "StructurePattern",
    "SemanticGrouper",
]
