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
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--output-dir", "-o", default="output", help="Output directory for generated docs"
)
@click.option(
    "--architecture/--no-architecture",
    default=True,
    help="Include/exclude architecture analysis",
)
@click.option(
    "--no-output-cache",
    is_flag=True,
    help="Disable output cache for this run",
)
@click.option(
    "--extended-footer",
    is_flag=True,
    help="Use extended footer with detailed file and model information",
)
@click.option(
    "--check-updates",
    is_flag=True,
    help="Check for model updates (overrides offline mode)",
)
@click.option(
    "--force-download",
    is_flag=True,
    help="Force re-download of models even if cached",
)
@click.option(
    "--offline",
    is_flag=True,
    help="Force offline mode (use only cached models)",
)
@click.option(
    "--chain/--no-chain",
    default=None,
    help="Enable/disable prompt chaining (overrides config)",
)
@click.option(
    "--chain-strategy",
    type=click.Choice(["simple", "enhanced", "architecture"]),
    help="Prompt chain strategy to use",
)
@click.pass_context
def generate(
    ctx,
    path,
    output_dir,
    architecture,
    no_output_cache,
    extended_footer,
    check_updates,
    force_download,
    offline,
    chain,
    chain_strategy,
):
    """
    Generate comprehensive documentation for code files or directories.

    PATH can be a single file or directory to process.

    \b
    Examples:
        docgenai generate myfile.py
        docgenai generate src/ --output-dir docs
        docgenai generate . --no-architecture
        docgenai generate src/
        docgenai generate src/ --no-output-cache
        docgenai generate src/ --check-updates
        docgenai generate src/ --force-download
        docgenai generate src/ --offline
    """
    config = ctx.obj["config"]
    verbose = ctx.obj.get("verbose", False)

    try:
        click.echo("🚀 Starting DocGenAI documentation generation...")

        # Show platform information
        import platform

        click.echo(f"🖥️  Platform: {platform.system()}")

        # Apply CLI overrides to model configuration
        model_config = config.copy()
        if check_updates:
            model_config["model"]["check_for_updates"] = True
            model_config["model"]["offline_mode"] = False
            model_config["model"]["local_files_only"] = False
            click.echo("🔄 Model update checking enabled")

        if force_download:
            model_config["model"]["force_download"] = True
            model_config["model"]["check_for_updates"] = True
            model_config["model"]["offline_mode"] = False
            model_config["model"]["local_files_only"] = False
            click.echo("⬇️  Force download enabled")

        if offline:
            model_config["model"]["offline_mode"] = True
            model_config["model"]["check_for_updates"] = False
            model_config["model"]["local_files_only"] = True
            click.echo("📴 Offline mode enabled")

        # Show offline/online status
        if model_config["model"]["offline_mode"]:
            click.echo("📴 Mode: Offline (using cached models only)")
        else:
            click.echo("🌐 Mode: Online (may download/update models)")

        # Initialize model
        click.echo("🤖 Initializing AI model...")
        model = create_model(model_config)

        # Show model information
        model_info = model.get_model_info()
        click.echo(f"📍 Model: {model_info['model_path']}")
        click.echo(f"⚙️  Backend: {model_info['backend']}")
        click.echo(f"🔧 Temperature: {model_info['temperature']}")
        click.echo(f"📝 Max tokens: {model_info['max_tokens']}")
        click.echo(f"🗜️  Quantization: {model_info['quantization']}")

        # Initialize generator with cache configuration
        generator_config = model_config.copy()
        if no_output_cache:
            # Disable output cache for this run
            generator_config["cache"]["enabled"] = False
            generator_config["cache"]["generation_cache"] = False

        # Update output directory in config
        generator_config["output"]["dir"] = output_dir
        generator_config["output"]["include_architecture"] = architecture
        generator_config["templates"]["use_extended_footer"] = extended_footer

        # Apply chaining configuration overrides
        if chain is not None:
            generator_config["chaining"]["enabled"] = chain
            if chain:
                click.echo("🔗 Prompt chaining enabled")
            else:
                click.echo("📝 Prompt chaining disabled")

        if chain_strategy:
            generator_config["chaining"]["default_strategy"] = chain_strategy
            click.echo(f"🔗 Chain strategy: {chain_strategy}")

        # Show chaining status
        chaining_enabled = generator_config["chaining"]["enabled"]
        if chaining_enabled:
            strategy = generator_config["chaining"]["default_strategy"]
            click.echo(f"🔗 Chaining: Enabled ({strategy} strategy)")
        else:
            click.echo("📝 Chaining: Disabled")

        generator = DocumentationGenerator(model, generator_config)

        # Process the path
        input_path = Path(path)

        if input_path.is_file():
            click.echo(f"📄 Processing file: {input_path}")
            result = generator.process_file(input_path)
            if result:
                click.echo(f"✅ Documentation generated: {result}")
            else:
                click.echo("❌ Failed to generate documentation")
                sys.exit(1)
        else:
            click.echo(f"📁 Processing directory: {input_path}")
            results = generator.process_directory(input_path)
            if results:
                click.echo(f"✅ Generated {len(results)} documentation files")
                for result in results[:5]:  # Show first 5 results
                    click.echo(f"   📄 {result}")
                if len(results) > 5:
                    click.echo(f"   ... and {len(results) - 5} more")
            else:
                click.echo("❌ No documentation files generated")
                sys.exit(1)

        click.echo("🎉 Documentation generation complete!")

    except KeyboardInterrupt:
        click.echo("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
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


if __name__ == "__main__":
    cli()
