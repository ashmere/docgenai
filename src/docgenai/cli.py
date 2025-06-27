import logging
import sys
from pathlib import Path

import click

from .cache import GenerationCache
from .config import load_config
from .core import CoreProcessor

# Set up logging for CLI


def setup_logging(verbose: bool = False):
    """Setup logging configuration for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """
    DocGenAI: AI-powered documentation and diagramming tool.

    This tool uses the MMaDA model to analyze codebases and generate
    comprehensive documentation with architecture diagrams.

    For best performance, use Docker (see docs/developer.md).
    """
    setup_logging(verbose)

    if verbose:
        click.echo("🔍 Verbose logging enabled")


@cli.command()
@click.argument(
    "path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the configuration file.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Path to the output directory.",
)
@click.option(
    "--token",
    "hugging_face_token",
    help="Hugging Face token for model access (overrides environment variable).",
)
@click.option(
    "--diagram",
    is_flag=True,
    help="Generate a diagram instead of documentation.",
)
def generate(
    path: Path,
    config_path: Path,
    diagram: bool,
    output_dir: Path,
    hugging_face_token: str,
):
    """
    Generates documentation for a given file or directory.

    The Hugging Face token can be provided via:
    1. --token command line option (highest priority)
    2. HUGGING_FACE_TOKEN environment variable
    3. Config file (not recommended for security)

    Examples:
        # Generate docs for a single file
        docgenai generate src/main.py

        # Generate docs for entire directory
        docgenai generate src/ --output-dir docs/

        # Generate diagram for a file
        docgenai generate src/main.py --diagram
    """
    logger = logging.getLogger(__name__)

    try:
        click.echo("🚀 Starting DocGenAI...")
        click.echo(f"📁 Processing: {path}")

        if diagram:
            click.echo("📊 Mode: Diagram generation")
        else:
            click.echo("📝 Mode: Documentation generation")

        # Initialize processor with progress indication
        click.echo("⚙️  Initializing processor...")
        processor = CoreProcessor(
            config_path=config_path,
            output_dir=output_dir,
            hugging_face_token=hugging_face_token,
        )

        click.echo("✅ Processor initialized successfully")

        if diagram:
            if not path.is_file():
                click.echo(
                    "❌ Error: Diagram generation is only supported for single files.",
                    err=True,
                )
                return

            click.echo("🎨 Generating diagram...")
            result = processor.process_file(path, generate_diagram=True)
            click.echo(f"✅ Diagram generated: {result}")
        else:
            click.echo("📝 Generating documentation...")
            results = processor.process(path)

            click.echo(f"✅ Documentation generation complete!")
            for result in results:
                click.echo(f"  📄 Generated: {result}")

    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        click.echo("\n💡 Troubleshooting tips:")
        click.echo("  - Check your internet connection (model downloads required)")
        click.echo("  - Ensure sufficient memory (8GB+ recommended)")
        click.echo("  - Try using Docker for better compatibility")
        click.echo("  - Use --verbose flag for detailed logging")
        sys.exit(1)


@cli.command()
@click.argument("code_path", type=click.Path(exists=True))
@click.argument("doc_path", type=click.Path(exists=True))
def improve(code_path: str, doc_path: str):
    """
    Improve existing documentation based on the source code.
    """
    click.echo(f"Improving docs at {doc_path} for code at {code_path}...")
    # Core logic will be called here


@cli.group()
def cache():
    """Cache management commands."""
    pass


@cache.command()
@click.option(
    "--config", type=click.Path(exists=True, path_type=Path), help="Path to config file"
)
def stats(config):
    """Show cache statistics."""
    app_config = load_config(config)
    if not app_config.cache.enabled:
        click.echo("Cache is disabled in configuration")
        return

    gen_cache = GenerationCache(
        cache_dir=app_config.cache.cache_dir,
        max_size_mb=app_config.cache.max_cache_size_mb,
    )

    stats_data = gen_cache.get_stats()
    click.echo("Cache Statistics:")
    click.echo(f"  Total entries: {stats_data['total_entries']}")
    click.echo(f"  Total size: {stats_data['total_size_mb']} MB")
    click.echo(f"  Max size: {stats_data['max_size_mb']} MB")
    click.echo(f"  Cache directory: {stats_data['cache_dir']}")


@cache.command()
@click.option(
    "--config", type=click.Path(exists=True, path_type=Path), help="Path to config file"
)
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def clear(config):
    """Clear all cached generation results."""
    app_config = load_config(config)
    if not app_config.cache.enabled:
        click.echo("Cache is disabled in configuration")
        return

    gen_cache = GenerationCache(
        cache_dir=app_config.cache.cache_dir,
        max_size_mb=app_config.cache.max_cache_size_mb,
    )

    gen_cache.clear()
    click.echo("Cache cleared successfully")


if __name__ == "__main__":
    cli()
