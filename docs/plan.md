# Implementation Plan: AI Code Documentor (DocGenAI)

## 1. Project Overview

This document outlines the plan for creating a Python-based CLI tool, "DocGenAI," designed to automate the generation and improvement of technical documentation. It will use the MMaDA model to analyze code, generate explanations, and create system diagrams. It will be designed for flexibility with swappable AI models and customizable templates, and will be containerized with Docker.

## 2. Core Features

- **Code Analysis**: Parse and understand single script files or entire directories.
- **Documentation Generation**: Create new documentation from scratch based on the code.
- **Documentation Improvement**: Analyze existing documentation alongside the code and suggest improvements.
- **Visual Diagramming**: Generate system architecture diagrams (e.g., flowcharts, component diagrams) as part of the documentation.
- **Template-driven Output**: Use customizable templates for the final documentation format and style.
- **Configurable Model**: Allow the underlying AI model to be switched out.

## 3. Technical Stack

- **Language**: Python 3.9+
- **CLI Framework**: `click` (for a rich and user-friendly command-line interface)
- **AI Model Interaction**: Hugging Face `transformers` library.
- **Templating**: `Jinja2`
- **Containerization**: Docker

## 4. Proposed Project Structure

```bash
code-assistant/
├── docs/
│   ├── developer.md
│   └── plan.md
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
├── output/
│   └── .gitkeep
├── src/
│   ├── docgenai/
│   │   ├── __init__.py
│   │   ├── cli.py          # Click CLI entry point
│   │   ├── config.py       # Configuration handling
│   │   ├── core.py         # Core documentation generation logic
│   │   ├── models.py       # AI model abstraction layer
│   │   ├── templates.py    # Template loading and rendering
│   │   └── templates/
│   │       ├── default_style_guide.md
│   │       └── default_doc_template.md
│   └── __init__.py
├── tests/
│   ├── .gitkeep
├── .dockerignore
├── .gitignore
├── config.yaml             # Default configuration file
├── pyproject.toml          # Project metadata and dependencies (using Poetry or similar)
└── README.md
```

## 5. Implementation Milestones

### Milestone 1: Project Setup and CLI Scaffolding

- Initialize the project structure as defined above.
- Set up `pyproject.toml` with dependencies like `click`, `transformers`, `torch`, and `jinja2`.
- Create the basic CLI entry point in `src/docgenai/cli.py` with `click`.
- Define initial commands: `docgenai generate` and `docgenai improve`.

### Milestone 2: AI Model Abstraction Layer

- In `src/docgenai/models.py`, define a base `AIModel` abstract class with methods like `generate_text`, `generate_image`, and `generate_with_reasoning`.
- Create a concrete `MMaDAModel` class that inherits from `AIModel`.
- This class will implement the logic to load the `Gen-Verse/MMaDA-8B-Base` model from Hugging Face and interact with it, based on the patterns from the research articles.

### Milestone 3: Core Logic - Documentation Generation

- In `src/docgenai/core.py`, implement the main documentation generation workflow.
- This involves:
    1. Reading the content of the target file or codebase path provided via the CLI.
    2. Instantiating the `MMaDAModel`.
    3. Sending a structured prompt to the model to generate an explanation and a diagram.
    4. Saving the generated text and image to the `output/` directory.

### Milestone 4: Templating System

- In `src/docgenai/templates.py`, implement logic to find and load Jinja2 templates from the `src/docgenai/templates` directory.
- Create a default documentation template (`default_doc_template.md`) that structures the output (e.g., Title, Description, Code Snippet, Architecture Diagram, Suggestions).
- Integrate this into the `core.py` workflow to render the final markdown file using the model's output.
- Add a default style guide that can be injected into prompts.

### Milestone 5: Documentation Improvement Feature

- Implement the `docgenai improve` command.
- This logic will:
    1. Read the source code.
    2. Read the existing documentation file.
    3. Construct a prompt that includes both the code and the existing docs, asking the model to critique and improve the documentation.
    4. Render the output using the templating system.

### Milestone 6: Dockerization

- Create a `Dockerfile` in the `docker/` directory.
- The Dockerfile will:
  - Use a Python base image.
  - Copy the `src` directory and `pyproject.toml`.
  - Install all dependencies.
  - **Strategy for Models**: The model weights are large. To avoid baking them into the image, the `transformers` library will cache them on first run. We will mount a volume to the cache directory (`/root/.cache/huggingface/`) to persist it.
- Create an `entrypoint.sh` script to manage the CLI execution within the container.

### Milestone 7: Configuration and Polish

- In `src/docgenai/config.py`, add support for loading settings from a `config.yaml` file.
- Allow users to override settings (like model name, template paths) via CLI options.
- Add robust error handling, progress indicators for model loading, and helpful logging.
