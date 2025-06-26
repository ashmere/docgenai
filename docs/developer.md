# Developer Guide: DocGenAI

This document contains notes and guidelines for the AI assistant developing this project.

## 1. Core Principles

- **Modularity**: Keep components decoupled. The model layer, CLI, and core logic should be separate.
- **Configurability**: Prioritize making key aspects like models, prompts, and templates configurable by the user.
- **Extensibility**: The architecture should make it easy to add new models or new commands in the future.

## 2. Key Implementation Patterns

### AI Model Abstraction

We will use an abstract base class to define the interface for any AI model. This makes the models swappable.

```python
# src/docgenai/models.py

from abc import ABC, abstractmethod

class AIModel(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    def generate_image(self, prompt: str) -> bytes:
        pass

    @abstractmethod
    def generate_with_reasoning(self, prompt: str) -> dict:
        pass

# Concrete implementation for MMaDA
class MMaDAModel(AIModel):
    def __init__(self, model_name: str = "Gen-Verse/MMaDA-8B-Base"):
        # Load model using transformers pipeline
        self.text_pipeline = ...
        self.image_pipeline = ...
        # etc.

    # ... implement methods
```

### Prompt Engineering

Based on the research articles, prompts for MMaDA should be direct and specific.

- **For documentation generation**:
  `"Create comprehensive documentation for this code including a visual diagram: {code_snippet}"`
- **For explanation**:
  `"Explain this code in detail, including its purpose and how it works: {code}"`
- **For diagram generation**:
  `"Create a flowchart or system architecture diagram showing how this code works: {code}"`
- **For improvement**:
  `"Based on this code and its visual representation, suggest improvements: {code}. Visual shows: {analysis}"`

### Templating with Jinja2

Use Jinja2 to render the final markdown. The context passed to the template should be a dictionary containing the model's output.

```python
# Example context for the template
context = {
    'file_path': 'src/example.py',
    'explanation': 'This function does X, Y, and Z...',
    'diagram_path': 'output/diagram.png',
    'suggestions': 'Consider refactoring this into smaller functions.'
}
```

## 3. Dockerization Strategy

- **Model Caching**: The MMaDA model is large. To avoid re-downloading it on every `docker run`, we will mount a host directory to the container's Hugging Face cache directory (`/root/.cache/huggingface`).
- **Base Image**: Use a slim Python image (`python:3.10-slim`).
- **Dependencies**: Install `torch` first, then the rest from `pyproject.toml` (or `requirements.txt`). This can improve layer caching.

## 4. CLI Framework

We will use `click` for its simplicity and power in creating nested commands and handling options.

```python
# src/docgenai/cli.py
import click

@click.group()
def cli():
    """AI-powered documentation and diagramming tool."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def generate(path):
    """Generate new documentation for a file or directory."""
    click.echo(f"Generating docs for {path}")
    # ... call core logic

# ... and so on
```
