# This file will handle loading and rendering of Jinja2 templates.

from pathlib import Path


class TemplateLoader:
    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            self.template_dir = Path(__file__).parent / "templates"
        else:
            self.template_dir = template_dir

    def load_template(self, name: str) -> str:
        """Loads a template file from the template directory."""
        template_path = self.template_dir / name
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{name}' not found in {self.template_dir}"
            )
        return template_path.read_text()

    def load_style_guide(self, name: str = "default_style_guide.md") -> str:
        """Loads the style guide."""
        return self.load_template(name)

    def load_documentation(self, name: str = "default_doc_template.md") -> str:
        """Loads the documentation template."""
        return self.load_template(name)
