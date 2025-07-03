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
from .core import DocumentationGenerator, generate_documentation
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
    - macOS: MLX-optimized model (configured in config.yaml)
    - Linux/Windows: Transformers model with quantization (configured in config.yaml)
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
    "--output-dir", "-o", default="output", help="Output directory for generated docs"
)
@click.option(
    "--template",
    type=click.Path(exists=True),
    help="Path to template file for documentation generation",
)
@click.option(
    "--style-guide",
    type=click.Path(exists=True),
    help="Path to style guide file for documentation generation",
)
@click.option(
    "--offline",
    is_flag=True,
    help="Force offline mode (use only cached models)",
)
@click.option(
    "--diagrams",
    is_flag=True,
    help="Include diagrams in the generated documentation",
)
@click.option(
    "--no-output-cache",
    is_flag=True,
    help="Disable output cache for this run",
)
@click.option(
    "--cache-clear",
    is_flag=True,
    help="Clear all cached data",
)
@click.option(
    "--chain/--no-chain",
    default=None,
    help="Enable/disable prompt chaining (overrides config)",
)
@click.option(
    "--chain-strategy",
    type=click.Choice(["simple", "enhanced", "architecture", "multi_file", "codebase"]),
    help="Prompt chain strategy to use",
)
@click.option(
    "--max-files-per-group",
    type=int,
    default=8,
    help="Maximum files to analyze together in multi-file mode",
)
@click.option(
    "--doc-type",
    type=click.Choice(["developer", "user", "both"]),
    default="both",
    help="Type of documentation to generate",
)
@click.option(
    "--project-type",
    type=click.Choice(["microservice", "library", "application", "framework", "auto"]),
    default="auto",
    help="Type of project for tailored documentation",
)
@click.option(
    "--detail-level",
    type=click.Choice(["module", "class", "method", "module_plus_strategic_class"]),
    default="module_plus_strategic_class",
    help="Level of detail for file interaction analysis",
)
@click.option(
    "--simplified",
    is_flag=True,
    help="Use simplified architecture with smart file selection and intelligent chunking",
)
@click.pass_context
def generate(
    ctx,
    target,
    output_dir,
    template,
    style_guide,
    offline,
    diagrams,
    no_output_cache,
    cache_clear,
    chain,
    chain_strategy,
    max_files_per_group,
    doc_type,
    project_type,
    detail_level,
    simplified,
):
    """
    Generate documentation for source code files.

    TARGET can be a single file or directory. Multi-file analysis
    is automatically enabled for directories and can be forced for
    single files with --multi-file.
    """
    import logging
    import time
    from pathlib import Path

    from .config import load_config
    from .core import generate_documentation

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    # Load configuration
    config = load_config()

    # Handle offline mode
    if offline:
        config["model"]["offline_mode"] = True
        config["model"]["local_files_only"] = True
        config["model"]["check_for_updates"] = False

    # Handle cache settings
    if no_output_cache:
        config["cache"]["enabled"] = False
    elif cache_clear:
        from .cache import clear_cache

        clear_cache()

    # Convert target to Path for analysis
    target_path = Path(target)

    # Auto-detect multi-file mode based on target type
    is_directory = target_path.is_dir()
    use_multi_file = is_directory

    # Handle multi-file settings
    config["multi_file"] = {
        "enabled": use_multi_file,
        "max_files_per_group": max_files_per_group,
    }

    # Handle documentation configuration
    config["documentation"]["doc_type"] = doc_type
    config["documentation"]["project_type"] = project_type
    config["documentation"]["detail_level"] = detail_level

    # Handle chaining configuration
    if chain is not None:
        # Explicit --chain or --no-chain flag
        config["chaining"] = {"enabled": chain}
    elif chain_strategy:
        # Chain strategy specified, enable chaining
        config["chaining"] = {"enabled": True}
    elif use_multi_file:
        # Multi-file mode always uses chaining
        config["chaining"] = {"enabled": True}
    else:
        # Default: no chaining for single files
        config["chaining"] = {"enabled": False}

    # Determine chain strategy
    if chain_strategy:
        config["chain_strategy"] = chain_strategy
    elif use_multi_file:
        # Auto-select strategy based on input type
        if is_directory:
            # For directories, use codebase analysis
            config["chain_strategy"] = "codebase"
        else:
            config["chain_strategy"] = "multi_file"
    else:
        config["chain_strategy"] = "simple"

    # Validate target
    if not target_path.exists():
        logger.error(f"❌ Target not found: {target}")
        ctx.exit(1)

    # Directory targets always use multi-file mode
    if is_directory and not use_multi_file:
        logger.error("❌ Internal error: directory should auto-enable multi-file")
        ctx.exit(1)

    logger.info(f"🚀 Starting documentation generation for: {target}")
    logger.info(f"📊 Chain strategy: {config.get('chain_strategy', 'simple')}")
    logger.info(f"🔗 Multi-file mode: {use_multi_file}")
    logger.info(f"🎯 Target type: {'directory' if is_directory else 'file'}")

    start_time = time.time()

    try:
        if simplified:
            # Use simplified architecture
            from .simple_core import generate_documentation_simplified

            result = generate_documentation_simplified(
                codebase_path=str(target_path),
                output_dir=output_dir,
                config=config,
            )
        else:
            # Use legacy architecture
            result = generate_documentation(
                target_path,
                output_dir=output_dir,
                template_file=template,
                style_guide_file=style_guide,
                config=config,
                diagrams=diagrams,
            )

        elapsed_time = time.time() - start_time

        if result.get("success", False):
            logger.info(f"✅ Documentation generated successfully!")

            # Handle different result formats
            if simplified:
                logger.info(f"📄 Output: {result.get('output_path', 'Unknown')}")
                logger.info(f"📊 Files analyzed: {result.get('files_analyzed', 0)}")
                logger.info(f"📦 Chunks created: {result.get('chunks_created', 0)}")
            else:
                logger.info(f"📄 Output: {result.get('output_files', [])}")

                # Show multi-file specific stats
                if use_multi_file and "multi_file_stats" in result:
                    stats = result["multi_file_stats"]
                    logger.info(f"📊 Multi-file stats:")
                    logger.info(f"  - Groups analyzed: {stats.get('groups', 0)}")
                    logger.info(f"  - Total files: {stats.get('total_files', 0)}")
                    logger.info(f"  - Synthesis: {stats.get('synthesis_used', False)}")

            logger.info(f"⏱️  Time: {elapsed_time:.2f} seconds")
        else:
            logger.error(f"❌ Documentation generation failed")
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


@cli.command()
def version():
    """Show the current version of DocGenAI."""
    click.echo(f"DocGenAI version {__version__}")


if __name__ == "__main__":
    cli()
