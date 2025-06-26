# This file will contain the core logic for the documentation generation
# and improvement processes. It will be called by the CLI commands.

from pathlib import Path

from .config import AppConfig, load_config
from .models import AIModel, MMaDAModel
from .templates import TemplateLoader


class CoreProcessor:
    def __init__(self, config_path: Path = None):
        self.config: AppConfig = load_config(config_path)
        self.ai_model: AIModel = self._init_model()
        self.template_loader = TemplateLoader()

    def _init_model(self) -> AIModel:
        model_config = self.config.model
        if model_config.name.lower() == "mmada":
            return MMaDAModel(
                model_name=model_config.name,
                hugging_face_token=model_config.hugging_face_token,
            )
        else:
            raise ValueError(f"Unsupported model: {model_config.name}")

    def process_file(self, file_path: Path) -> str:
        """
        Processes a single source code file to generate documentation.
        """
        # 1. Read file content
        code = file_path.read_text()

        # 2. Analyze with AI model (placeholder)
        analysis_result = self.ai_model.analyze_code(code)

        # 3. Load templates
        doc_template = self.template_loader.load_doc_template()
        style_guide = self.template_loader.load_style_guide()

        # 4. Generate documentation content (placeholder)
        # In the future, this will use a more sophisticated prompt
        prompt = (
            f"{doc_template}\\n\\n"
            f"Style Guide:\\n{style_guide}\\n\\n"
            f"Code:\\n```\\n{code}\\n```\\n\\n"
            f"Analysis:\\n{analysis_result}"
        )
        generated_doc = self.ai_model.generate_documentation(prompt)

        return generated_doc

    def process_directory(self, dir_path: Path) -> str:
        """
        Processes a directory of source code files and generates a combined
        documentation.
        """
        # Placeholder for directory processing logic
        # For now, let's just indicate it's a directory.
        # A real implementation would iterate files, call process_file,
        # and aggregate the results.
        return f"Documentation for directory: {dir_path.name}"

    def process(self, path: Path) -> str:
        """
        Processes a given path, dispatching to file or directory processing.
        """
        if path.is_file():
            return self.process_file(path)
        elif path.is_dir():
            return self.process_directory(path)
        else:
            raise FileNotFoundError(f"Path does not exist: {path}")
