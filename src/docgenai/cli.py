from pathlib import Path

import click

from .core import CoreProcessor


@click.group()
def cli():
    """
    DocGenAI: AI-powered documentation and diagramming tool.
    """
    pass


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
def generate(path: Path, config_path: Path):
    """
    Generates documentation for a given file or directory.
    """
    try:
        processor = CoreProcessor(config_path=config_path)
        result = processor.process(path)
        click.echo(result)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("code_path", type=click.Path(exists=True))
@click.argument("doc_path", type=click.Path(exists=True))
def improve(code_path: str, doc_path: str):
    """
    Improve existing documentation based on the source code.
    """
    click.echo(f"Improving docs at {doc_path} for code at {code_path}...")
    # Core logic will be called here


if __name__ == "__main__":
    cli()
