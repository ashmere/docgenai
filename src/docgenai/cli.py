"""
Command-line interface for DocGenAI.

Provides comprehensive CLI commands for code documentation generation
using DeepSeek-Coder models with platform-aware optimization.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional

import click

from .config import create_default_config_file, load_config
from .core import DocumentationGenerator
from .models import create_model


def setup_logging(verbose: bool = False, config: dict = None):
    """Set up logging based on configuration."""
    log_config = config.get("logging", {}) if config else {}

    if verbose:
        level = getattr(logging, log_config.get("verbose_level", "DEBUG"))
        format_str = log_config.get(
            "verbose_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        level = getattr(logging, log_config.get("level", "INFO"))
        format_str = log_config.get("format", "%(message)s")

    logging.basicConfig(
        level=level, format=format_str, handlers=[logging.StreamHandler(sys.stdout)]
    )


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config, verbose):
    """
    DocGenAI: AI-powered code documentation generator.

    Uses DeepSeek-Coder models with platform-specific optimization:
    - macOS: MLX-optimized DeepSeek-Coder-V2-Lite-Instruct-8bit
    - Linux/Windows: DeepSeek-Coder-V2-Lite-Instruct with quantization
    """
    # Load configuration
    try:
        app_config = load_config(config)
    except Exception as e:
        click.echo(f"❌ Failed to load configuration: {e}", err=True)
        sys.exit(1)

    # Set up logging
    setup_logging(verbose, app_config)

    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj["config"] = app_config
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Output directory for generated documentation",
)
@click.option(
    "--include-architecture",
    is_flag=True,
    default=None,
    help="Include architectural analysis",
)
@click.option(
    "--file-pattern", multiple=True, help="File patterns to process (e.g., '*.py')"
)
@click.option(
    "--detail-level",
    type=click.Choice(["brief", "medium", "detailed"]),
    help="Level of detail in documentation",
)
@click.pass_context
def generate(ctx, target, output_dir, include_architecture, file_pattern, detail_level):
    """
    Generate documentation for code files or directories.

    TARGET can be a single file or directory to process.

    Examples:

        # Generate docs for a single file
        docgenai generate src/models.py

        # Generate docs for entire directory
        docgenai generate src/ --output-dir docs/

        # Include architecture analysis
        docgenai generate src/ --include-architecture

        # Process only Python files
        docgenai generate . --file-pattern "*.py"
    """
    config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]

    click.echo("🚀 Starting DocGenAI documentation generation...")

    # Override config with CLI options
    if output_dir:
        config["output"]["dir"] = output_dir
    if include_architecture is not None:
        config["output"]["include_architecture"] = include_architecture
    if file_pattern:
        config["generation"]["file_patterns"] = list(file_pattern)
    if detail_level:
        config["generation"]["detail_level"] = detail_level

    # Show platform and model information
    import platform

    click.echo(f"🖥️  Platform: {platform.system()}")

    try:
        # Create model
        click.echo("🤖 Initializing AI model...")
        model = create_model(config)
        model_info = model.get_model_info()

        click.echo(f"📍 Model: {model_info['model_path']}")
        click.echo(f"⚙️  Backend: {model_info['backend']}")

        if verbose:
            click.echo(f"🔧 Temperature: {model_info['temperature']}")
            click.echo(f"📝 Max tokens: {model_info['max_tokens']}")
            click.echo(f"🗜️  Quantization: {model_info['quantization']}")

        # Create documentation generator
        generator = DocumentationGenerator(model, config)

        # Process target
        target_path = Path(target)

        if target_path.is_file():
            click.echo(f"📄 Processing file: {target}")
            result = generator.process_file(target_path)
            if result:
                click.echo(f"✅ Documentation generated: {result}")
            else:
                click.echo("❌ Failed to generate documentation", err=True)
                sys.exit(1)
        else:
            click.echo(f"📁 Processing directory: {target}")
            results = generator.process_directory(target_path)

            if results:
                click.echo(f"✅ Generated {len(results)} documentation files:")
                for result in results:
                    click.echo(f"   📄 {result}")
            else:
                click.echo("❌ No documentation generated", err=True)
                sys.exit(1)

        click.echo("🎉 Documentation generation complete!")

    except KeyboardInterrupt:
        click.echo("\n⏹️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during generation: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def info(ctx):
    """
    Display information about the current configuration and model.
    """
    config = ctx.obj["config"]

    click.echo("📋 DocGenAI Information")
    click.echo("=" * 50)

    # Platform information
    import platform

    click.echo(f"🖥️  Platform: {platform.system()} {platform.release()}")
    click.echo(f"🐍 Python: {platform.python_version()}")

    # Model information
    try:
        model = create_model(config)
        model_info = model.get_model_info()

        click.echo("\n🤖 Model Configuration:")
        click.echo(f"   📍 Path: {model_info['model_path']}")
        click.echo(f"   ⚙️  Backend: {model_info['backend']}")
        click.echo(f"   🌡️  Temperature: {model_info['temperature']}")
        click.echo(f"   📝 Max tokens: {model_info['max_tokens']}")
        click.echo(f"   🗜️  Quantization: {model_info['quantization']}")
        click.echo(f"   ✅ Available: {model_info['available']}")

    except Exception as e:
        click.echo(f"   ❌ Model initialization failed: {e}")

    # Configuration summary
    click.echo("\n⚙️  Configuration:")
    click.echo(f"   📁 Output dir: {config['output']['dir']}")
    click.echo(f"   🗂️  Cache dir: {config['cache']['cache_dir']}")
    click.echo(f"   🔍 File patterns: {len(config['generation']['file_patterns'])}")
    click.echo(
        f"   🏗️  Include architecture: {config['output']['include_architecture']}"
    )
    click.echo(f"   📊 Include stats: {config['output']['include_code_stats']}")

    # Cache information
    cache_dir = Path(config["cache"]["cache_dir"])
    if cache_dir.exists():
        cache_files = list(cache_dir.rglob("*"))
        cache_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        click.echo(f"   💾 Cache files: {len(cache_files)}")
        click.echo(f"   📦 Cache size: {cache_size / 1024 / 1024:.1f} MB")
    else:
        click.echo("   💾 Cache: Not initialized")


@cli.command()
@click.option("--clear", is_flag=True, help="Clear all cached data")
@click.option("--stats", is_flag=True, help="Show cache statistics")
@click.pass_context
def cache(ctx, clear, stats):
    """
    Manage documentation generation cache.
    """
    config = ctx.obj["config"]
    cache_dir = Path(config["cache"]["cache_dir"])

    if clear:
        if cache_dir.exists():
            import shutil

            shutil.rmtree(cache_dir)
            click.echo("🗑️  Cache cleared successfully")
        else:
            click.echo("💾 Cache directory does not exist")
        return

    if stats or True:  # Default to showing stats
        click.echo("📊 Cache Statistics")
        click.echo("=" * 30)

        if cache_dir.exists():
            cache_files = list(cache_dir.rglob("*"))
            total_files = len([f for f in cache_files if f.is_file()])
            total_size = sum(f.stat().st_size for f in cache_files if f.is_file())

            click.echo(f"📁 Cache directory: {cache_dir}")
            click.echo(f"📄 Total files: {total_files}")
            click.echo(f"📦 Total size: {total_size / 1024 / 1024:.2f} MB")

            # Show breakdown by type
            generation_cache = cache_dir / "generation"
            model_cache = cache_dir / "models"

            if generation_cache.exists():
                gen_files = list(generation_cache.rglob("*"))
                gen_size = sum(f.stat().st_size for f in gen_files if f.is_file())
                click.echo(
                    f"   📝 Generation cache: {len(gen_files)} files, {gen_size / 1024 / 1024:.2f} MB"
                )

            if model_cache.exists():
                model_files = list(model_cache.rglob("*"))
                model_size = sum(f.stat().st_size for f in model_files if f.is_file())
                click.echo(
                    f"   🤖 Model cache: {len(model_files)} files, {model_size / 1024 / 1024:.2f} MB"
                )
        else:
            click.echo("💾 Cache directory does not exist")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def test(ctx, file_path):
    """
    Test documentation generation on a single file.

    This command is useful for testing the model and configuration
    without processing large directories.
    """
    config = ctx.obj["config"]
    verbose = ctx.obj["verbose"]

    click.echo(f"🧪 Testing documentation generation on: {file_path}")

    try:
        # Create model
        start_time = time.time()
        click.echo("🤖 Initializing model...")

        model = create_model(config)

        init_time = time.time() - start_time
        click.echo(f"✅ Model initialized in {init_time:.2f} seconds")

        # Test generation
        file_path_obj = Path(file_path)

        click.echo("📝 Reading file...")
        with open(file_path_obj, "r", encoding="utf-8") as f:
            code_content = f.read()

        click.echo(f"📊 File size: {len(code_content)} characters")

        # Generate documentation
        click.echo("🔄 Generating documentation...")
        gen_start = time.time()

        documentation = model.generate_documentation(code_content, str(file_path_obj))

        gen_time = time.time() - gen_start
        click.echo(f"✅ Documentation generated in {gen_time:.2f} seconds")

        # Show results
        if verbose:
            click.echo("\n📄 Generated Documentation:")
            click.echo("-" * 50)
            click.echo(documentation)
            click.echo("-" * 50)

        click.echo(f"📝 Documentation length: {len(documentation)} characters")
        click.echo("🎉 Test completed successfully!")

    except Exception as e:
        click.echo(f"❌ Test failed: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="config.yaml",
    help="Output path for configuration file",
)
def init(output):
    """
    Create a default configuration file.
    """
    try:
        config_path = create_default_config_file(output)
        click.echo(f"✅ Configuration file created: {config_path}")
        click.echo("🔧 Edit the file to customize your settings")
        click.echo("📖 See documentation for configuration options")
    except Exception as e:
        click.echo(f"❌ Failed to create configuration file: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
