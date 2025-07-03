"""
Base prompt templates and shared formatting rules for DocGenAI.
"""


class BasePromptBuilder:
    """Base class for building prompts with shared formatting rules."""

    # Shared formatting rules that apply to all documentation
    MARKDOWN_FORMATTING_RULES = """
**CRITICAL OUTPUT FORMAT REQUIREMENTS:**

⚠️ NEVER wrap your entire response in a code block (```text or ``` markdown)
⚠️ Write direct markdown content, not code-block-wrapped markdown
⚠️ Start immediately with the first ## header - no preamble or code blocks

**Markdown formatting rules:**
- Use ## headers (not # headers) for main sections
- Use ### headers for subsections
- Surround all lists with blank lines before and after
- Use only single blank lines between sections
- Specify language for code examples (```python, ```bash, etc.)
- Do NOT use duplicate section headings
- Ensure code examples are formatted correctly with proper language markers
- Do NOT use ```text markers anywhere in the output
- Close all code blocks properly with ```
- Keep code examples complete and well-formatted
- Avoid adding text immediately after closing code blocks

**Response format:**
Write the documentation as direct markdown content. Start with:

## SYSTEM OVERVIEW
(your content here)

## ARCHITECTURE & DESIGN
(your content here)

etc.

DO NOT wrap the entire response in ``` markdown blocks."""

    # Common guidelines for all prompts
    COMMON_GUIDELINES = """
- Never use ```text anywhere in the response
- Do not add any text immediately after closing code blocks with ```
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
