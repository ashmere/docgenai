# This file will contain the core logic for the documentation generation
# and improvement processes. It will be called by the CLI commands.

import logging
import time
from pathlib import Path

import click

from .cache import GenerationCache, ModelCache
from .config import AppConfig, load_config
from .models import MMADA_AVAILABLE, AIModel, MMaDANativeModel
from .templates import TemplateLoader

# Set up logging
logger = logging.getLogger(__name__)

# Fallback import for the old MMaDAModel if native is not available
if not MMADA_AVAILABLE:
    from .models import MMaDAModel

# Global model cache for session-level caching
_model_cache = ModelCache()


class CoreProcessor:
    def __init__(
        self,
        config_path: Path = None,
        output_dir: Path = None,
        hugging_face_token: str = None,
    ):
        logger.info("🔧 Initializing CoreProcessor...")
        start_time = time.time()

        self.config: AppConfig = load_config(config_path)
        if output_dir:
            self.config.output.dir = output_dir
        # Override token if provided via CLI
        if hugging_face_token:
            self.config.model.hugging_face_token = hugging_face_token

        logger.info(f"📋 Configuration loaded from: {config_path or 'default'}")
        logger.info(f"📁 Output directory: {self.config.output.dir}")
        logger.info(f"🤖 Model: {self.config.model.name}")
        logger.info(f"⚙️  Quantization: {self.config.model.quantization}")

        # Initialize caches
        self.generation_cache = None
        if self.config.cache.enabled and self.config.cache.generation_cache:
            logger.info("💾 Initializing generation cache...")
            self.generation_cache = GenerationCache(
                cache_dir=self.config.cache.cache_dir,
                max_size_mb=self.config.cache.max_cache_size_mb,
            )
            stats = self.generation_cache.get_stats()
            logger.info(f"✅ Generation cache enabled: {stats}")

        logger.info("🤖 Initializing AI model...")
        self.ai_model: AIModel = self._init_model()

        logger.info("📝 Initializing template loader...")
        self.template_loader = TemplateLoader()

        init_time = time.time() - start_time
        logger.info(f"✅ CoreProcessor initialized in {init_time:.2f} seconds")

    def _init_model(self) -> AIModel:
        model_config = self.config.model

        # Create a cache key based on model configuration
        cache_key = (
            model_config.name,
            model_config.quantization,
            model_config.hugging_face_token,
        )

        # Try to get cached model if session caching is enabled
        if model_config.session_cache:
            cached_model = _model_cache.get_model(model_config.name, cache_key)
            if cached_model is not None:
                print("Using cached model from session")
                # Update the generation cache reference
                if hasattr(cached_model, "generation_cache"):
                    cached_model.generation_cache = self.generation_cache
                return cached_model

        # Create new model instance
        if MMADA_AVAILABLE:
            model = MMaDANativeModel(
                model_name=model_config.name,
                hugging_face_token=model_config.hugging_face_token,
                quantization=model_config.quantization,
                generation_cache=self.generation_cache,
            )
        else:
            # Fallback to the old MMaDAModel implementation
            model = MMaDAModel(
                model_name=model_config.name,
                hugging_face_token=model_config.hugging_face_token,
            )
            # Add generation cache to fallback model if it supports it
            if hasattr(model, "generation_cache"):
                model.generation_cache = self.generation_cache

        # Cache the model if session caching is enabled
        if model_config.session_cache:
            _model_cache.set_model(model_config.name, model, cache_key)
            print("Model cached for session")

        return model

    def process(self, path: Path) -> list[str]:
        """
        Processes a file or directory to generate documentation.
        Returns a list of paths to the generated documentation files.
        """
        if path.is_dir():
            return self.process_directory(path)
        else:
            return [self.process_file(path)]

    def process_file(self, file_path: Path, generate_diagram: bool = False) -> str:
        """
        Processes a single source code file to generate documentation or a
        diagram.
        """
        if generate_diagram:
            return self.process_for_diagram(file_path)

        # 1. Read the source code
        code = file_path.read_text()

        # 2. Load templates
        doc_template = self.template_loader.load_documentation()
        style_guide = self.template_loader.load_style_guide()

        # 3. Analyze the code
        analysis_result = self.ai_model.analyze_code(code)

        # 4. Generate documentation content (placeholder)
        # In the future, this will use a more sophisticated prompt
        prompt = f"""{doc_template}

Style Guide:
{style_guide}

Code:
```
{code}
```

Analysis:
{analysis_result}
"""
        generated_doc = self.ai_model.generate_text(prompt)

        # 5. Save the documentation
        output_path = self.config.output.dir / f"{file_path.stem}_doc.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(generated_doc)

        return str(output_path)

    def process_for_diagram(self, file_path: Path) -> str:
        """
        Processes a single source code file to generate a diagram.
        """
        # 1. Read the source code
        code = file_path.read_text()

        # 2. Generate the diagram
        diagram = self.ai_model.generate_diagram(code)

        # 3. Save the diagram
        output_path = self.config.output.dir / f"{file_path.stem}_diagram.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"```mermaid\n{diagram}\n```")

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
        prompt = f"""{doc_template}

Style Guide:
{style_guide}

Image Analysis:
{analysis_result}
"""
        generated_doc = self.ai_model.generate_text(prompt)

        # 4. Save the documentation
        output_path = self.config.output.dir / f"{image_path.stem}_doc.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(generated_doc)

        return str(output_path)
