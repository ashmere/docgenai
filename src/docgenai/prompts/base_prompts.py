"""
Base prompt templates and shared formatting rules for DocGenAI.
"""


class BasePromptBuilder:
    """Base class for building prompts with shared formatting rules."""

    # Shared formatting rules that apply to all documentation
    MARKDOWN_FORMATTING_RULES = """
Please write the documentation in clear, professional Markdown format
following these rules:
- Use ## headers (not # headers) for main sections
- Surround all lists with blank lines before and after
- Use only single blank lines between sections
- Specify language for all code blocks (```python, ```bash, etc.)
- Do NOT wrap your entire response in a code block
- Do NOT use duplicate section headings
        - Ensure that code examples are formatted correctly with proper markers
        - Do not use ```text markers anywhere in the output
        - Close all code blocks properly with ```
        - Keep code examples complete and well-formatted
        - Avoid adding text immediately after closing code blocks
"""

    # Common prohibitions for all prompts
    COMMON_PROHIBITIONS = """
- FORBIDDEN: Never use ```text anywhere in the response
- FORBIDDEN: Do not add any text after closing code blocks with ```
"""

    @staticmethod
    def get_language_from_extension(file_extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
        }
        return language_map.get(file_extension.lower(), "text")

    def build_prompt(self, **kwargs) -> str:
        """Build a prompt with the given parameters. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement build_prompt")
