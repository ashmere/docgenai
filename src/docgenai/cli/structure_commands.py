"""
CLI commands for project structure detection and analysis.

Provides commands to detect project structure, generate structure configs,
and analyze codebase organization.
"""

import logging
from pathlib import Path
from typing import Optional

import click

from ..structure.analyzer import ProjectStructureAnalyzer

logger = logging.getLogger(__name__)


@click.group(name="structure")
def structure_commands():
    """Project structure detection and analysis commands."""
    pass


@structure_commands.command()
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--language",
    "-l",
    help="Override language detection (python, typescript, go, cpp, etc.)",
)
@click.option(
    "--max-file-size",
    type=int,
    default=50000,
    help="Maximum file size before extraction (characters)",
)
@click.option(
    "--target-size",
    type=int,
    default=20000,
    help="Target size for extracted content (characters)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output path for structure configuration",
)
@click.option("--report", "-r", is_flag=True, help="Generate detailed analysis report")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def detect(
    source_dir: Path,
    language: Optional[str],
    max_file_size: int,
    target_size: int,
    output: Optional[Path],
    report: bool,
    verbose: bool,
):
    """
    Detect project structure and patterns.

    Analyzes the source directory to identify project patterns,
    create semantic groups, and optionally generate configuration.

    Examples:
        docgenai structure detect ./src
        docgenai structure detect ./src --language python
        docgenai structure detect ./src --output project-structure.yaml
        docgenai structure detect ./src --report --verbose
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    click.echo(f"🔍 Detecting project structure in {source_dir}")

    try:
        # Initialize analyzer
        analyzer = ProjectStructureAnalyzer(
            root_path=source_dir,
            language_override=language,
            max_file_size=max_file_size,
            target_extraction_size=target_size,
        )

        # Perform analysis
        analysis_results = analyzer.analyze_structure()

        # Display summary
        _display_analysis_summary(analysis_results)

        # Generate detailed report if requested
        if report:
            click.echo("\\n" + "=" * 60)
            click.echo("DETAILED ANALYSIS REPORT")
            click.echo("=" * 60)
            report_content = analyzer.get_analysis_report()
            click.echo(report_content)

        # Export configuration if requested
        if output:
            analyzer.export_structure_config(output)
            click.echo(f"\\n📄 Structure configuration exported to {output}")

        # Success message
        click.echo("\\n✅ Structure detection complete!")

        if not output:
            click.echo(
                "\\n💡 Tip: Use --output to save structure "
                "configuration for future use"
            )

    except Exception as e:
        click.echo(f"❌ Error during structure detection: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.ClickException(f"Structure detection failed: {e}")


@structure_commands.command()
@click.argument("config_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--validate",
    "-v",
    is_flag=True,
    help="Validate configuration against current codebase",
)
def load(config_path: Path, validate: bool):
    """
    Load and display project structure configuration.

    Loads a previously saved structure configuration and displays
    the detected patterns and groups.

    Examples:
        docgenai structure load project-structure.yaml
        docgenai structure load project-structure.yaml --validate
    """
    click.echo(f"📄 Loading structure configuration from {config_path}")

    try:
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        project_config = config.get("project_structure", {})

        # Display configuration
        click.echo("\\n" + "=" * 50)
        click.echo("PROJECT STRUCTURE CONFIGURATION")
        click.echo("=" * 50)

        if "primary_pattern" in project_config and project_config["primary_pattern"]:
            pattern = project_config["primary_pattern"]
            click.echo(f"\\n📋 Primary Pattern: {pattern['name']}")
            click.echo(f"   Description: {pattern['description']}")

        if "semantic_groups" in project_config:
            groups = project_config["semantic_groups"]
            click.echo(f"\\n🎯 Semantic Groups ({len(groups)}):")

            for group in groups:
                click.echo(f"\\n  • {group['name']}")
                click.echo(f"    Type: {group['group_type']}")
                click.echo(f"    Language: {group['primary_language']}")
                click.echo(f"    Files: {len(group['file_patterns'])}")
                click.echo(f"    Role: {group['architectural_role']}")

        if "analysis_config" in project_config:
            config_info = project_config["analysis_config"]
            click.echo(f"\\n⚙️ Analysis Configuration:")
            click.echo(
                f"   Max File Size: {config_info.get('max_file_size', 'default'):,} characters"
            )
            click.echo(
                f"   Target Extract Size: {config_info.get('target_extraction_size', 'default'):,} characters"
            )
            if config_info.get("language_override"):
                click.echo(f"   Language Override: {config_info['language_override']}")

        # Validate against current codebase if requested
        if validate:
            click.echo("\\n🔍 Validating configuration against current codebase...")

            root_path = Path(project_config.get("root_path", "."))
            if not root_path.exists():
                click.echo(f"⚠️ Warning: Root path {root_path} does not exist")
                return

            # Re-analyze and compare
            analyzer = ProjectStructureAnalyzer(root_path)
            current_analysis = analyzer.analyze_structure()

            # Compare patterns
            current_pattern = current_analysis.get("primary_pattern")
            saved_pattern = project_config.get("primary_pattern")

            if current_pattern and saved_pattern:
                if current_pattern["name"] == saved_pattern["name"]:
                    click.echo("✅ Pattern validation: MATCH")
                else:
                    click.echo(f"⚠️ Pattern validation: CHANGED")
                    click.echo(f"   Saved: {saved_pattern['name']}")
                    click.echo(f"   Current: {current_pattern['name']}")

            # Compare group counts
            current_groups = len(
                current_analysis.get("group_analysis", {}).get("groups", [])
            )
            saved_groups = len(project_config.get("semantic_groups", []))

            if current_groups == saved_groups:
                click.echo("✅ Group count validation: MATCH")
            else:
                click.echo(f"⚠️ Group count validation: CHANGED")
                click.echo(f"   Saved: {saved_groups} groups")
                click.echo(f"   Current: {current_groups} groups")

        click.echo("\\n✅ Configuration loaded successfully!")

    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)
        raise click.ClickException(f"Failed to load configuration: {e}")


@structure_commands.command()
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--group-name", "-g", help="Analyze specific group only")
@click.option("--language", "-l", help="Override language detection")
@click.option("--show-files", "-f", is_flag=True, help="Show individual file details")
@click.option(
    "--show-content",
    "-c",
    is_flag=True,
    help="Show extracted content (use with caution for large projects)",
)
def analyze(
    source_dir: Path,
    group_name: Optional[str],
    language: Optional[str],
    show_files: bool,
    show_content: bool,
):
    """
    Analyze project structure in detail.

    Provides detailed analysis of semantic groups, file organization,
    and content extraction results.

    Examples:
        docgenai structure analyze ./src
        docgenai structure analyze ./src --group-name "Core Modules"
        docgenai structure analyze ./src --show-files
    """
    click.echo(f"🔬 Analyzing project structure in {source_dir}")

    try:
        # Initialize analyzer
        analyzer = ProjectStructureAnalyzer(
            root_path=source_dir, language_override=language
        )

        # Perform analysis
        analysis_results = analyzer.analyze_structure()
        groups = analyzer.get_groups_for_analysis()

        # Filter to specific group if requested
        if group_name:
            groups = [g for g in groups if g["name"] == group_name]
            if not groups:
                click.echo(f"❌ Group '{group_name}' not found")
                available_groups = [
                    g["name"] for g in analyzer.get_groups_for_analysis()
                ]
                click.echo(f"Available groups: {', '.join(available_groups)}")
                return

        # Display detailed analysis
        for group in groups:
            click.echo(f"\\n" + "=" * 60)
            click.echo(f"GROUP: {group['name']}")
            click.echo("=" * 60)

            click.echo(f"Description: {group['description']}")
            click.echo(f"Type: {group['group_type']}")
            click.echo(f"Architectural Role: {group['architectural_role']}")
            click.echo(f"Primary Language: {group['primary_language']}")
            click.echo(f"File Count: {group['file_count']}")
            click.echo(f"Total Size: {group['total_original_size']:,} characters")
            click.echo(f"Extracted Size: {group['total_extracted_size']:,} characters")
            click.echo(f"Compression Ratio: {group['compression_ratio']:.2f}")
            click.echo(f"Estimated Tokens: {group['estimated_tokens']:,}")

            if group["extraction_applied"]:
                click.echo("🔧 Content extraction applied to large files")

            # Show file details if requested
            if show_files:
                click.echo(f"\\n📁 Files in group:")

                for file_data in group["files"]:
                    extraction_marker = (
                        " [EXTRACTED]" if file_data["extraction_applied"] else ""
                    )
                    click.echo(f"  • {file_data['path']}{extraction_marker}")
                    click.echo(f"    Language: {file_data['language']}")
                    click.echo(
                        f"    Size: {file_data['original_size']:,} → {file_data['extracted_size']:,} chars"
                    )

                    if file_data["extraction_applied"]:
                        click.echo(f"    Method: {file_data['extraction_method']}")

            # Show content if requested (warning for large output)
            if show_content:
                if group["total_extracted_size"] > 10000:
                    if not click.confirm(
                        f"\\n⚠️ Group content is {group['total_extracted_size']:,} characters. Show anyway?"
                    ):
                        continue

                click.echo(f"\\n📝 Content:")
                click.echo("-" * 40)

                group_content = analyzer.get_group_content(group["name"])
                if group_content:
                    click.echo(group_content)
                else:
                    click.echo("No content available")

        click.echo("\\n✅ Analysis complete!")

    except Exception as e:
        click.echo(f"❌ Error during analysis: {e}", err=True)
        raise click.ClickException(f"Analysis failed: {e}")


def _display_analysis_summary(analysis_results: dict):
    """Display a summary of analysis results."""
    click.echo("\\n" + "=" * 50)
    click.echo("STRUCTURE ANALYSIS SUMMARY")
    click.echo("=" * 50)

    # Pattern detection
    if analysis_results.get("primary_pattern"):
        pattern = analysis_results["primary_pattern"]
        click.echo(f"\\n📋 Detected Pattern: {pattern['name']}")
        click.echo(f"   Description: {pattern['description']}")

    # File analysis
    file_analysis = analysis_results["file_analysis"]
    size_analysis = analysis_results["size_analysis"]

    click.echo(f"\\n📊 File Analysis:")
    click.echo(f"   Total Files: {file_analysis['total_files']:,}")
    click.echo(f"   Semantic Groups: {file_analysis['total_groups']}")
    click.echo(
        f"   Files with Extraction: {file_analysis['files_with_extraction']} ({file_analysis['extraction_percentage']:.1f}%)"
    )
    click.echo(
        f"   Size Reduction: {size_analysis['total_original_size']:,} → {size_analysis['total_extracted_size']:,} chars"
    )
    click.echo(f"   Compression Ratio: {size_analysis['compression_ratio']:.2f}")

    # Language distribution
    lang_dist = analysis_results["language_distribution"]
    click.echo(f"\\n🔤 Languages Detected:")
    for language, count in sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]:
        percentage = (count / file_analysis["total_files"]) * 100
        click.echo(f"   {language.title()}: {count} files ({percentage:.1f}%)")

    # Semantic groups
    groups = analysis_results["group_analysis"]["groups"]
    click.echo(f"\\n🎯 Semantic Groups ({len(groups)}):")

    for group in groups:
        extraction_note = " (with extraction)" if group["extraction_applied"] else ""
        click.echo(
            f"   • {group['name']}: {group['file_count']} files{extraction_note}"
        )
        click.echo(
            f"     Type: {group['group_type']} | Language: {group['primary_language']}"
        )

    # Quality metrics
    quality = analysis_results["quality_metrics"]
    click.echo(f"\\n✅ Quality Metrics:")
    click.echo(
        f"   No Files Excluded: {'Yes' if quality['no_files_excluded'] else 'No'}"
    )
    click.echo(
        f"   Meaningful Grouping: {'Yes' if quality['meaningful_grouping'] else 'No'}"
    )
    click.echo(f"   Pattern Confidence: {quality['pattern_confidence']:.2f}")


# Register commands with main CLI
def register_structure_commands(cli_group):
    """Register structure commands with the main CLI group."""
    cli_group.add_command(structure_commands)
