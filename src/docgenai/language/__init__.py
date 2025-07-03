"""
Language detection and content extraction module.

Provides universal language support for content extraction with
intelligent size reduction while preserving essential API information.
"""

from .detector import LanguageDetector
from .extractors import (
    CppExtractor,
    GenericExtractor,
    GoExtractor,
    HelmExtractor,
    JavaScriptExtractor,
    LanguageExtractor,
    LanguageExtractorFactory,
    PythonExtractor,
    TerraformExtractor,
    TypeScriptExtractor,
    YamlExtractor,
)

__all__ = [
    "LanguageDetector",
    "LanguageExtractor",
    "LanguageExtractorFactory",
    "PythonExtractor",
    "TypeScriptExtractor",
    "JavaScriptExtractor",
    "GoExtractor",
    "CppExtractor",
    "TerraformExtractor",
    "HelmExtractor",
    "YamlExtractor",
    "GenericExtractor",
]
