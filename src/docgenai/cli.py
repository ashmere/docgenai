"""
Command-line interface for DocGenAI.

Provides comprehensive CLI commands for code documentation generation
using DeepSeek-Coder models with platform-aware optimization.
"""

import logging
import sys
import time
from pathlib import Path

import click

from . import __version__
from .config import create_default_config_file, load_config
from .core import generate_documentation
from .models import create_model

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False, config: dict = None):
    """Set up logging configuration."""
    # Configure logging level
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Basic logging configuration
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Configure specific loggers
    if config and "logging" in config:
        logging_config = config["logging"]

        # Set levels for specific loggers
        for logger_name, level in logging_config.get("loggers", {}).items():
            logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config, verbose):
    """
    DocGenAI - AI-powered documentation generator for codebases.

    Generate comprehensive documentation for your code using local LLMs.
    """
    # Load configuration
    config_data = load_config(config)

    # Set up logging
    setup_logging(verbose, config_data)

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = config_data
    ctx.obj["debug"] = verbose


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default="output",
    help="Output directory for generated docs",
)
@click.option(
    "--model",
    "-m",
    help="Model to use for generation (overrides config)",
)
@click.option(
    "--offline",
    is_flag=True,
    help="Force offline mode (use only cached models)",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Disable caching for this run",
)
@click.option(
    "--cache-clear",
    is_flag=True,
    help="Clear cache before generation",
)
@click.option(
    "--metadata-mode",
    type=click.Choice(["none", "footer", "file"]),
    help="Metadata generation mode (overrides config)",
)
@click.pass_context
def generate(
    ctx,
    target,
    output_dir,
    model,
    offline,
    no_cache,
    cache_clear,
    metadata_mode,
):
    """
    Generate documentation for a codebase or single file.

    TARGET can be either a file or directory path.
    """
    config = ctx.obj["config"]

    # Handle cache clearing
    if cache_clear:
        from .cache import CacheManager

        cache_manager = CacheManager(config["cache"])
        cache_manager.clear_cache()
        logger.info("🗑️  Cache cleared successfully")
        return

    # Update config with command-line options
    if model:
        import platform

        if platform.system() == "Darwin":
            config["model"]["mlx_model"] = model
        else:
            config["model"]["transformers_model"] = model

    if offline:
        config["model"]["offline_mode"] = True
        config["model"]["local_files_only"] = True
        config["model"]["check_for_updates"] = False

    if no_cache:
        config["cache"]["enabled"] = False

    if metadata_mode:
        if "output" not in config:
            config["output"] = {}
        config["output"]["metadata_mode"] = metadata_mode

    # Log configuration
    logger.info(f"🚀 Starting documentation generation for: {target}")
    logger.info(f"📁 Output directory: {output_dir}")
    logger.info(f"💾 Cache enabled: {config['cache']['enabled']}")
    logger.info(f"📴 Offline mode: {config['model']['offline_mode']}")

    start_time = time.time()

    try:
        # Generate documentation
        result = generate_documentation(
            codebase_path=target,
            output_dir=output_dir,
            config=config,
        )

        elapsed_time = time.time() - start_time

        if result.get("success", False):
            logger.info("✅ Documentation generated successfully!")
            logger.info(f"📄 Output: {result.get('output_path', 'Unknown')}")
            logger.info(f"📊 Files analyzed: {result.get('files_analyzed', 0)}")
            logger.info(f"📦 Chunks created: {result.get('chunks_created', 0)}")
            logger.info(f"⏱️  Time: {elapsed_time:.2f} seconds")
        else:
            logger.error("❌ Documentation generation failed")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            ctx.exit(1)

    except Exception as e:
        logger.error(f"❌ Error during documentation generation: {str(e)}")
        if ctx.obj and ctx.obj.get("debug"):
            import traceback

            traceback.print_exc()
        ctx.exit(1)


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

        # Show offline mode status
        offline_mode = config["model"].get("offline_mode", False)
        check_updates = config["model"].get("check_for_updates", False)
        local_files_only = config["model"].get("local_files_only", False)

        click.echo(f"   📴 Offline mode: {offline_mode}")
        click.echo(f"   🔄 Check updates: {check_updates}")
        click.echo(f"   📂 Local files only: {local_files_only}")

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
@click.option(
    "--clear-output-cache", is_flag=True, help="Clear only output generation cache"
)
@click.option("--clear-model-cache", is_flag=True, help="Clear only model cache")
@click.option("--stats", is_flag=True, help="Show cache statistics")
@click.pass_context
def cache(ctx, clear, clear_output_cache, clear_model_cache, stats):
    """
    Manage documentation generation cache.

    The system uses multiple cache types:
    - Output cache: Stores generated documentation results
    - Model cache: Stores downloaded model files and session data
    """
    config = ctx.obj["config"]

    # Import here to avoid circular imports
    from .cache import CacheManager

    # Initialize cache manager
    cache_manager = CacheManager(config["cache"])

    # Handle cache clearing operations
    if clear:
        cache_manager.clear_cache()
        # Also clear model cache directory if it exists
        model_cache_dir = Path(config["cache"].get("model_cache_dir", ".cache/models"))
        if model_cache_dir.exists():
            import shutil

            shutil.rmtree(model_cache_dir)
            click.echo("🗑️  Model cache cleared")
        click.echo("🗑️  All caches cleared successfully")
        return

    if clear_output_cache:
        cache_manager.clear_cache()
        click.echo("🗑️  Output cache cleared successfully")
        return

    if clear_model_cache:
        model_cache_dir = Path(config["cache"].get("model_cache_dir", ".cache/models"))
        if model_cache_dir.exists():
            import shutil

            shutil.rmtree(model_cache_dir)
            click.echo("🗑️  Model cache cleared successfully")
        else:
            click.echo("💾 Model cache directory does not exist")
        return

    # Default to showing stats if no action specified
    if stats or not any([clear, clear_output_cache, clear_model_cache]):
        click.echo("📊 Cache Statistics")
        click.echo("=" * 40)

        # Output cache stats
        cache_stats = cache_manager.get_stats()
        click.echo("📝 Output Cache:")
        click.echo(f"   📁 Directory: {cache_stats['cache_dir']}")
        click.echo(f"   📄 Entries: {cache_stats['total_entries']}")
        click.echo(f"   📦 Size: {cache_stats['cache_size_mb']} MB")
        click.echo(f"   ⏰ TTL: {cache_stats['ttl_hours']} hours")
        click.echo(f"   ✅ Enabled: {cache_stats['enabled']}")

        # Model cache stats
        model_cache_dir = Path(config["cache"].get("model_cache_dir", ".cache/models"))
        click.echo("\n🤖 Model Cache:")
        click.echo(f"   📁 Directory: {model_cache_dir}")

        if model_cache_dir.exists():
            model_files = list(model_cache_dir.rglob("*"))
            total_model_files = len([f for f in model_files if f.is_file()])
            total_model_size = sum(f.stat().st_size for f in model_files if f.is_file())
            click.echo(f"   📄 Files: {total_model_files}")
            click.echo(f"   📦 Size: {total_model_size / 1024 / 1024:.2f} MB")
        else:
            click.echo("   📄 Files: 0")
            click.echo("   📦 Size: 0.00 MB")

        # Combined stats
        total_cache_size = cache_stats["cache_size_mb"]
        if model_cache_dir.exists():
            model_files = list(model_cache_dir.rglob("*"))
            total_model_size = (
                sum(f.stat().st_size for f in model_files if f.is_file()) / 1024 / 1024
            )
            total_cache_size += total_model_size

        click.echo(f"\n📊 Total Cache Size: {total_cache_size:.2f} MB")


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
    debug = ctx.obj.get("debug", False)

    click.echo(f"🧪 Testing documentation generation on: {file_path}")

    try:
        # Test using the same architecture as generate command
        start_time = time.time()

        result = generate_documentation(
            codebase_path=file_path,
            output_dir="test_output",
            config=config,
        )

        elapsed_time = time.time() - start_time

        if result.get("success", False):
            click.echo("✅ Documentation generated successfully!")
            click.echo(f"📄 Output: {result.get('output_path', 'Unknown')}")
            click.echo(f"📊 Files analyzed: {result.get('files_analyzed', 0)}")
            click.echo(f"📦 Chunks created: {result.get('chunks_created', 0)}")
            click.echo(f"⏱️  Time: {elapsed_time:.2f} seconds")

            # Show documentation if debug mode
            if debug and result.get("documentation"):
                click.echo("\n📄 Generated Documentation:")
                click.echo("-" * 50)
                click.echo(result["documentation"])
                click.echo("-" * 50)

        else:
            click.echo("❌ Documentation generation failed")
            click.echo(f"Error: {result.get('error', 'Unknown error')}")
            ctx.exit(1)

    except Exception as e:
        click.echo(f"❌ Test failed: {e}", err=True)
        if debug:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        ctx.exit(1)


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


@cli.command()
def version():
    """Show the current version of DocGenAI."""
    click.echo(f"DocGenAI version {__version__}")


if __name__ == "__main__":
    cli()
