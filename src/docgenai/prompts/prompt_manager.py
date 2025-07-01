"""
Prompt manager for coordinating different prompt builders.
"""

from pathlib import Path

from .architecture_prompts import ArchitecturePromptBuilder
from .documentation_prompts import DocumentationPromptBuilder


class PromptManager:
    """Manager for coordinating different prompt builders."""

    def __init__(self):
        """Initialize prompt builders."""
        self.doc_builder = DocumentationPromptBuilder()
        self.arch_builder = ArchitecturePromptBuilder()

    def build_documentation_prompt(self, code: str, file_path: str, **kwargs) -> str:
        """
        Build documentation generation prompt.

        Args:
            code: Source code to document
            file_path: Path to the source file
            **kwargs: Additional parameters for prompt building

        Returns:
            Complete documentation prompt
        """
        return self.doc_builder.build_prompt(code, file_path, **kwargs)

    def build_architecture_prompt(self, code: str, file_path: str, **kwargs) -> str:
        """
        Build architecture analysis prompt.

        Args:
            code: Source code to analyze
            file_path: Path to the source file
            **kwargs: Additional parameters for prompt building

        Returns:
            Complete architecture analysis prompt
        """
        return self.arch_builder.build_prompt(code, file_path, **kwargs)

    def detect_language(self, file_path: str) -> str:
        """
        Detect programming language from file path.

        Args:
            file_path: Path to the source file

        Returns:
            Programming language identifier
        """
        file_extension = Path(file_path).suffix.lower()
        return self.doc_builder.get_language_from_extension(file_extension)
