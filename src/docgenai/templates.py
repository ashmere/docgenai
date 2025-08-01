"""
Template management for DocGenAI.

Handles loading and rendering of Jinja2 templates for documentation generation.
Provides both default templates and support for custom template directories.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


class TemplateManager:
    """
    Manages Jinja2 templates for documentation generation.

    Provides methods to load and render templates with context data,
    supporting both built-in and custom template directories.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize template manager with configuration.

        Args:
            config: Template configuration dictionary
        """
        self.template_dir = Path(config.get("directory", "src/docgenai/templates"))
        self.doc_template_name = config.get("doc_template", "default_doc_template.md")
        self.summary_template_name = config.get(
            "directory_summary_template", "directory_summary_template.md"
        )
        self.footer_template_name = config.get("footer_template", "default_footer.md")
        self.extended_footer_template_name = config.get(
            "extended_footer_template", "default_extended_footer.md"
        )
        self.use_extended_footer = config.get("use_extended_footer", False)

        # Ensure template directory exists
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["format_size"] = self._format_size
        self.env.filters["format_duration"] = self._format_duration

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def render_documentation(self, context: Dict[str, Any]) -> str:
        """
        Render documentation template with context.

        Args:
            context: Template context dictionary

        Returns:
            Rendered documentation string
        """
        try:
            template = self.env.get_template(self.doc_template_name)
            doc_content = template.render(**context)
        except TemplateNotFound:
            # Fall back to default template
            doc_content = self._render_default_documentation(context)

        # Add footer
        footer_content = self.render_footer(context)
        full_content = doc_content + "\n\n" + footer_content

        # Clean up markdown formatting
        return self._clean_markdown(full_content)

    def render_directory_summary(self, context: Dict[str, Any]) -> str:
        """
        Render directory summary template with context.

        Args:
            context: Template context dictionary

        Returns:
            Rendered directory summary string
        """
        try:
            template = self.env.get_template(self.summary_template_name)
            return template.render(**context)
        except TemplateNotFound:
            # Fall back to default template
            return self._render_default_directory_summary(context)

    def render_footer(self, context: Dict[str, Any]) -> str:
        """
        Render footer template with context.

        Args:
            context: Template context dictionary

        Returns:
            Rendered footer string
        """
        footer_template_name = (
            self.extended_footer_template_name
            if self.use_extended_footer
            else self.footer_template_name
        )

        try:
            template = self.env.get_template(footer_template_name)
            return template.render(**context)
        except TemplateNotFound:
            # Fall back to default footer
            return self._render_default_footer(context)

    def _render_default_documentation(self, context: Dict[str, Any]) -> str:
        """
        Render using built-in default documentation template.

        Args:
            context: Template context dictionary

        Returns:
            Rendered documentation string
        """
        template_content = """# Documentation: {{ file_name }}

**File**: `{{ file_path }}`
**Language**: {{ language }}
**Generated**: {{ generation_time }}
**Model**: {{ model_info.name }} ({{ model_info.backend }})

{% if code_stats %}
## File Statistics

- **Lines of code**: {{ code_stats.lines }}
- **Characters**: {{ code_stats.characters }}
- **File size**: {{ code_stats.size_kb }} KB
{% endif %}

## Documentation

{{ documentation }}

{% if architecture_description and include_architecture %}
## Architecture Analysis

{{ architecture_description }}
{% endif %}

---
*Generated by DocGenAI using {{ model_info.name }} on {{ model_info.platform }}*
"""

        template = Template(template_content)
        return template.render(**context)

    def _render_default_directory_summary(self, context: Dict[str, Any]) -> str:
        """
        Render using built-in default directory summary template.

        Args:
            context: Template context dictionary

        Returns:
            Rendered directory summary string
        """
        template_content = """# Directory Documentation Summary

**Directory**: `{{ directory_path }}`
**Generated**: {{ generation_time }}
**Total Files**: {{ total_files }}
**Successful**: {{ successful_files }}
**Failed**: {{ failed_files }}

## Processing Results

{% if successful_files > 0 %}
### Successfully Processed Files

{% for result in results %}
- **{{ result.input_file }}**
  - Output: `{{ result.output_file }}`
  - Generation time: {{ result.generation_time | format_duration }}
{% endfor %}
{% endif %}

{% if failed_results %}
### Failed Files

{% for result in failed_results %}
- **{{ result.input_file }}**: {{ result.error }}
{% endfor %}
{% endif %}

## Summary

{% if successful_files > 0 %}
✅ Successfully generated documentation for {{ successful_files }} file(s).
{% endif %}
{% if failed_files > 0 %}
❌ Failed to process {{ failed_files }} file(s).
{% endif %}

All generated documentation files are available in the output directory.

---
*Generated by DocGenAI*
"""

        template = Template(template_content)
        return template.render(**context)

    def _render_default_footer(self, context: Dict[str, Any]) -> str:
        """
        Render using built-in default footer template.

        Args:
            context: Template context dictionary

        Returns:
            Rendered footer string
        """
        if self.use_extended_footer:
            template_content = """---

*Generated by DocGenAI using {{ model_info.backend }} backend on {{ model_info.platform }}*

**File**: `{{ file_path }}`
**Language**: {{ language }}
**Generated**: {{ generation_time }}
**Model**: {{ model_info.model_path }} ({{ model_info.backend }})

{% if code_stats and include_code_stats %}
## File Statistics

- **Lines of code**: {{ code_stats.lines }}
- **Characters**: {{ code_stats.characters }}
- **File size**: {{ code_stats.size_kb }} KB
{% endif %}"""
        else:
            template_content = """---

*Generated by DocGenAI using {{ model_info.backend }} backend*"""

        template = Template(template_content)
        return template.render(**context)

    def _clean_markdown(self, content: str) -> str:
        """
        Clean up markdown formatting to avoid lint issues.

        Args:
            content: Raw markdown content

        Returns:
            Cleaned markdown content
        """
        import re

        # Remove multiple consecutive blank lines
        content = re.sub(r"\n\n\n+", "\n\n", content)

        # Ensure lists are surrounded by blank lines
        content = re.sub(r"([^\n])\n([0-9]+\. |\- |\* )", r"\1\n\n\2", content)
        content = re.sub(r"([0-9]+\. .*|\- .*|\* .*)\n([^\n\s])", r"\1\n\n\2", content)

        # Ensure headers are surrounded by blank lines
        content = re.sub(r"([^\n])\n(#{1,6} )", r"\1\n\n\2", content)
        content = re.sub(r"(#{1,6} .*)\n([^\n\s#])", r"\1\n\n\2", content)

        # Ensure fenced code blocks are surrounded by blank lines
        content = re.sub(r"([^\n])\n(```)", r"\1\n\n\2", content)
        content = re.sub(r"(```)\n([^\n\s])", r"\1\n\n\2", content)

        # Add language to fenced code blocks without language
        # (but not after Mermaid diagrams)
        # Use a more sophisticated approach to avoid Mermaid closings
        lines = content.split("\n")
        in_mermaid = False
        for i, line in enumerate(lines):
            if line.strip() == "```mermaid":
                in_mermaid = True
            elif line.strip() == "```" and in_mermaid:
                in_mermaid = False
                # Don't add 'text' to Mermaid closing
                continue
            elif line.strip() == "```" and not in_mermaid:
                # This is a code block without language, add 'text'
                lines[i] = "```text"
        content = "\n".join(lines)

        # Fix duplicate headings by adding numbers
        lines = content.split("\n")
        heading_counts = {}
        for i, line in enumerate(lines):
            if line.startswith("#"):
                heading_text = line.strip("#").strip()
                if heading_text in heading_counts:
                    heading_counts[heading_text] += 1
                    # Add number to duplicate heading
                    level = len(line) - len(line.lstrip("#"))
                    lines[i] = (
                        "#" * level
                        + f" {heading_text} ({heading_counts[heading_text]})"
                    )
                else:
                    heading_counts[heading_text] = 1
        content = "\n".join(lines)

        # Ensure file ends with single newline
        content = content.rstrip() + "\n"

        return content

    def load_template(self, name: str) -> str:
        """
        Load a template file as raw text.

        Args:
            name: Template filename

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.template_dir / name
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{name}' not found in {self.template_dir}"
            )
        return template_path.read_text(encoding="utf-8")

    def save_template(self, name: str, content: str):
        """
        Save a template file.

        Args:
            name: Template filename
            content: Template content
        """
        template_path = self.template_dir / name
        template_path.write_text(content, encoding="utf-8")

    def list_templates(self) -> list[str]:
        """
        List available template files.

        Returns:
            List of template filenames
        """
        if not self.template_dir.exists():
            return []

        return [
            f.name
            for f in self.template_dir.iterdir()
            if f.is_file() and f.suffix in [".md", ".txt", ".html"]
        ]

    def create_default_templates(self):
        """Create default template files if they don't exist."""
        # Create default documentation template
        doc_template_path = self.template_dir / self.doc_template_name
        if not doc_template_path.exists():
            default_doc_content = """# Documentation: {{ file_name }}

**File**: `{{ file_path }}`
**Language**: {{ language }}
**Generated**: {{ generation_time }}
**Model**: {{ model_info.name }} ({{ model_info.backend }})

{% if code_stats %}
## File Statistics

- **Lines of code**: {{ code_stats.lines }}
- **Characters**: {{ code_stats.characters }}
- **File size**: {{ code_stats.size_kb }} KB
{% endif %}

## Documentation

{{ documentation }}

{% if architecture_description and include_architecture %}
## Architecture Analysis

{{ architecture_description }}
{% endif %}

## Usage Examples

*TODO: Add usage examples based on the code analysis*

## Notes

*TODO: Add any additional notes or considerations*

---
*Generated by DocGenAI using {{ model_info.name }} on {{ model_info.platform }}*
"""
            doc_template_path.write_text(default_doc_content, encoding="utf-8")

        # Create default directory summary template
        summary_template_path = self.template_dir / self.summary_template_name
        if not summary_template_path.exists():
            default_summary_content = """# Directory Documentation Summary

**Directory**: `{{ directory_path }}`
**Generated**: {{ generation_time }}
**Total Files**: {{ total_files }}
**Successful**: {{ successful_files }}
**Failed**: {{ failed_files }}

## Processing Results

{% if successful_files > 0 %}
### Successfully Processed Files

{% for result in results %}
- **{{ result.input_file }}**
  - Output: `{{ result.output_file }}`
  - Generation time: {{ result.generation_time | format_duration }}
{% endfor %}
{% endif %}

{% if failed_results %}
### Failed Files

{% for result in failed_results %}
- **{{ result.input_file }}**: {{ result.error }}
{% endfor %}
{% endif %}

## Summary

{% if successful_files > 0 %}
✅ Successfully generated documentation for {{ successful_files }} file(s).
{% endif %}
{% if failed_files > 0 %}
❌ Failed to process {{ failed_files }} file(s).
{% endif %}

All generated documentation files are available in the output directory.

---
*Generated by DocGenAI*
"""
            summary_template_path.write_text(default_summary_content, encoding="utf-8")


# Backward compatibility
class TemplateLoader(TemplateManager):
    """Backward compatibility wrapper for TemplateLoader."""

    def __init__(self, template_dir: Optional[Path] = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        config = {
            "directory": str(template_dir),
            "doc_template": "default_doc_template.md",
            "directory_summary_template": "directory_summary_template.md",
        }
        super().__init__(config)

    def load_style_guide(self, name: str = "default_style_guide.md") -> str:
        """Legacy method for loading style guide."""
        return self.load_template(name)

    def load_documentation(self, name: str = "default_doc_template.md") -> str:
        """Legacy method for loading documentation template."""
        return self.load_template(name)
