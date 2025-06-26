# This file will contain the core logic for the documentation generation
# and improvement processes. It will be called by the CLI commands.

from pathlib import Path

import click

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

    def process(self, path: Path) -> list[str]:
        """
        Processes a file or directory to generate documentation.
        Returns a list of paths to the generated documentation files.
        """
        if path.is_dir():
            return self.process_directory(path)
        else:
            return [self.process_file(path)]

    def process_file(self, file_path: Path) -> str:
        """
        Processes a single source code file to generate documentation.
        """
        # 1. Read the source code
        code = file_path.read_text()

        # 2. Load templates
        doc_template = self.template_loader.load_documentation()
        style_guide = self.template_loader.load_style_guide()

        # 3. Analyze the code
        analysis_result = self.ai_model.analyze_code(code)

        # 4. Generate documentation content (placeholder)
        # In the future, this will use a more sophisticated prompt
        prompt = (
            f"{doc_template}\\n\\n"
            f"Style Guide:\\n{style_guide}\\n\\n"
            f"Code:\\n```\\n{code}\\n```\\n\\n"
            f"Analysis:\\n{analysis_result}"
        )
        generated_doc = self.ai_model.generate_documentation(prompt)

        output_path = self.config.output.dir / f"{file_path.stem}_doc.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(generated_doc)

        return str(output_path)

    def process_directory(self, dir_path: Path) -> list[str]:
        """
        Processes all supported files in a directory recursively.
        """
        generated_files = []
        supported_extensions = [".py", ".png", ".jpg", ".jpeg"]
        for file_path in dir_path.rglob("*"):
            if file_path.suffix in supported_extensions:
                click.echo(f"Processing {file_path}...")
                if file_path.suffix == ".py":
                    generated_file = self.process_file(file_path)
                else:
                    generated_file = self.process_image(file_path)
                generated_files.append(generated_file)
        return generated_files

    def process_image(self, image_path: Path) -> str:
        """
        Processes an image file to generate documentation.
        """
        # 1. Analyze the image
        analysis_result = self.ai_model.analyze_image(image_path)

        # 2. Load templates
        doc_template = self.template_loader.load_documentation()
        style_guide = self.template_loader.load_style_guide()

        # 3. Generate documentation content
        prompt = (
            f"{doc_template}\\n\\n"
            f"Style Guide:\\n{style_guide}\\n\\n"
            f"Image Analysis:\\n{analysis_result}"
        )
        generated_doc = self.ai_model.generate_documentation(prompt)

        # 4. Save the documentation
        output_path = self.config.output.dir / f"{image_path.stem}_doc.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(generated_doc)

        return str(output_path)
