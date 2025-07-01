"""
Documentation generation prompt templates.
"""

from pathlib import Path

from .base_prompts import BasePromptBuilder


class DocumentationPromptBuilder(BasePromptBuilder):
    """Builder for documentation generation prompts."""

    # Core documentation sections that should be included
    DOCUMENTATION_SECTIONS = """
1. **Overview**: Brief description of what the code does
2. **Key Components**: Main classes, functions, and their purposes
3. **Architecture**: How the components work together
4. **Usage Examples**: Practical examples of how to use the code
5. **Dependencies**: Any external libraries or modules used
6. **Configuration**: Any configuration options or environment variables
7. **Error Handling**: How errors are handled and common issues
8. **Performance Considerations**: Any performance notes or optimizations
"""

    # Additional formatting rules specific to main documentation
    DOCUMENTATION_FORMATTING_RULES = """
- Focus on clear text explanations rather than diagrams
- Keep the documentation readable and accessible
"""

    def build_prompt(
        self,
        code: str,
        file_path: str,
        language: str = None,
    ) -> str:
        """
        Build documentation generation prompt.

        Args:
            code: Source code to document
            file_path: Path to the source file
            language: Programming language (auto-detected if None)

        Returns:
            Complete documentation prompt
        """
        if language is None:
            file_extension = Path(file_path).suffix.lower()
            language = self.get_language_from_extension(file_extension)

        prompt = f"""You are an expert software developer and technical writer.
Generate comprehensive, clear, and well-structured documentation for the
following {language} code.

The documentation should include:

{self.DOCUMENTATION_SECTIONS}
{self.MARKDOWN_FORMATTING_RULES}
{self.DOCUMENTATION_FORMATTING_RULES}

**File Path**: `{file_path}`

**Code**:
```{language}
{code}
```

Provide the documentation:"""

        return prompt
