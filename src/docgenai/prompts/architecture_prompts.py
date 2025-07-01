"""
Architecture analysis prompt templates.
"""

from pathlib import Path

from .base_prompts import BasePromptBuilder


class ArchitecturePromptBuilder(BasePromptBuilder):
    """Builder for architecture analysis prompts - text-only analysis."""

    def build_prompt(
        self, code: str, file_path: str, language: str = None, **kwargs
    ) -> str:
        """
        Build architecture analysis prompt (v0.3.0 working version).

        Args:
            code: Source code to analyze
            file_path: Path to the source file
            language: Programming language (auto-detected if None)

        Returns:
            Complete architecture analysis prompt
        """
        if language is None:
            file_extension = Path(file_path).suffix.lower()
            language = self.get_language_from_extension(file_extension)

        prompt = f"""You are a software architect analyzing code structure. Provide a detailed architectural analysis of the following {language} code.

Focus on:

1. **Architectural Patterns**: Design patterns used (MVC, Observer, Factory, etc.)
2. **Code Organization**: How the code is structured and organized
3. **Data Flow**: How data moves through the system
4. **Dependencies**: Internal and external dependencies
5. **Interfaces**: Public APIs and interfaces exposed
6. **Extensibility**: How the code can be extended or modified
7. **Design Principles**: SOLID principles, separation of concerns, etc.
8. **Potential Improvements**: Suggestions for architectural improvements

Follow markdown formatting rules:
- Use ## headers for main sections, ### for subsections
- Surround all lists with blank lines before and after
- Use only single blank lines between sections
- Avoid duplicate section headings

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

Provide the architectural analysis:"""

        return prompt
