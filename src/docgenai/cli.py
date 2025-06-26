import click


@click.group()
def cli():
    """
    DocGenAI: AI-powered documentation and diagramming tool.
    """
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def generate(path: str):
    """
    Generate new documentation for a file or directory.
    """
    click.echo(f"Generating docs for {path}...")
    # Core logic will be called here


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
