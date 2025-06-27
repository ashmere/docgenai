# Developer Guide: DocGenAI

This document contains notes and guidelines for the AI assistant developing this project.

## 1. Core Principles

- **Modularity**: Keep components decoupled. The model layer, CLI, and core logic should be separate.
- **Configurability**: Prioritize making key aspects like models, prompts, and templates configurable by the user.
- **Extensibility**: The architecture should make it easy to add new models or new commands in the future.

## 2. Code Quality and Linting Standards

### Markdown Linting Rules

To maintain consistent documentation quality, follow these markdownlint rules:

- **MD022**: Headings must be surrounded by blank lines (one line above and below)
- **MD031**: Fenced code blocks must be surrounded by blank lines
- **MD032**: Lists must be surrounded by blank lines
- **MD040**: Fenced code blocks must specify a language

**Example of correct formatting:**

- Headings need blank lines above and below
- Lists need blank lines above and below
- Code blocks need blank lines above and below
- Code blocks must specify a language (e.g., `python`, `bash`, `yaml`)

### Pre-commit Hooks

Run `pre-commit run --all-files` before committing to ensure:

- Markdown formatting compliance
- Python code formatting (black, isort)
- Trailing whitespace removal
- End-of-file fixing

## 3. Key Implementation Patterns

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

## 4. Platform Compatibility and Docker Strategy

### M1/M2/M3 Mac Compatibility Issues

**IMPORTANT**: This project has significant compatibility issues on Apple Silicon Macs (M1, M2, M3) due to:

1. **bitsandbytes incompatibility**: The `bitsandbytes` library doesn't support Apple Silicon, causing quantization to fall back to full precision
2. **Model loading performance**: Without quantization, the 8B parameter MMaDA model requires substantial memory and loads very slowly (1+ hours)
3. **PyTorch compilation**: Some PyTorch operations may not be optimized for Apple Silicon
4. **Memory constraints**: Full precision models require more RAM than quantized versions

**Symptoms on M1/M2/M3 Macs**:

```bash
Warning: 8bit quantization requested but bitsandbytes not available. Using full precision.
You are using a model of type llada to instantiate a model of type mmada. This is not supported for all configurations of models and can yield errors.
```

### Docker-First Approach (RECOMMENDED)

**For all development and production use, Docker is the recommended approach** because:

- ✅ **Full aarch64 Linux support**: Docker provides proper Linux environment with full library support
- ✅ **Consistent performance**: Quantization works properly in Docker containers
- ✅ **Reproducible builds**: Same environment across all machines
- ✅ **Faster model loading**: 4-bit/8-bit quantization significantly reduces memory usage and loading time
- ✅ **No platform-specific issues**: Avoids Apple Silicon compatibility problems

### Docker Configuration

#### Dockerfile Optimizations

```dockerfile
# Use official Python image with full library support
FROM python:3.12-slim

# Install system dependencies for model compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up model cache directory
ENV HF_HOME=/app/.cache/huggingface
RUN mkdir -p $HF_HOME

# Install dependencies in order for better caching
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . .

WORKDIR /app
```

#### Volume Mounts for Performance

```bash
# Mount host cache to avoid re-downloading models
docker run -v ~/.cache/huggingface:/app/.cache/huggingface docgenai

# Mount output directory
docker run -v $(pwd)/output:/app/output docgenai

# Full development setup
docker run -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/src:/app/src \
  docgenai bash
```

### Performance Optimizations

#### Quantization Settings

```yaml
# config.yaml - Recommended settings for different scenarios
model:
  quantization: "4bit"  # 4x faster loading, ~90-95% quality
  # quantization: "8bit"  # 2x faster loading, ~98% quality
  # quantization: "none"  # Full precision, slower loading, best quality
```

#### Memory Management

- **4-bit quantization**: ~2GB RAM usage, fastest loading
- **8-bit quantization**: ~4GB RAM usage, good balance
- **Full precision**: ~16GB RAM usage, highest quality

#### Docker Resource Limits

```bash
# Allocate sufficient resources to Docker
docker run --memory=8g --cpus=4 docgenai

# For Apple Silicon Macs, increase memory allocation in Docker Desktop
# Settings > Resources > Memory: 8GB minimum
```

## 5. Development Workflow

### Local Development (Docker)

```bash
# Build the image
docker build -t docgenai .

# Run with development mounts
docker run -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd):/app \
  docgenai bash

# Inside container
poetry run docgenai generate src/ --output-dir output
```

### Native Development (Not Recommended)

If you must develop natively on M1/M2/M3:

1. **Expect slow performance**: Model loading will take 1+ hours
2. **Use small test files**: Don't process large codebases
3. **Monitor memory usage**: Full precision models are memory-intensive
4. **Consider remote development**: Use GitHub Codespaces or similar

### Logging and Debugging

The application now includes comprehensive logging to help debug performance issues:

```python
# Example log output during model loading
🔧 Initializing MMaDA model: Gen-Verse/MMaDA-8B-Base
⚙️  Quantization: 4bit
🔍 Checking quantization support...
✅ bitsandbytes available for quantization
📋 Step 1/4: Configuring quantization...
📊 Using 4-bit quantization
📥 Step 2/4: Loading MMaDA model...
⏳ This may take several minutes on first run...
✅ Model loaded in 45.23 seconds
📥 Step 3/4: Loading tokenizer...
✅ Tokenizer loaded in 2.15 seconds
📝 Step 4/4: Setting up chat template...
🎉 Model initialization complete! Total time: 47.38 seconds
```

### Troubleshooting

#### If model loading hangs:

1. **Check Docker resources**: Ensure sufficient memory allocation
2. **Monitor logs**: Look for progress indicators in the output
3. **Verify quantization**: Ensure bitsandbytes is working in container
4. **Check network**: Model downloads require stable internet

#### If quantization fails:

1. **Use Docker**: Native Mac development has quantization issues
2. **Update dependencies**: Ensure latest bitsandbytes version
3. **Check GPU support**: CUDA availability affects quantization options

#### Performance optimization:

1. **Use 4-bit quantization**: Fastest loading with good quality
2. **Cache models**: Mount HuggingFace cache directory
3. **Limit scope**: Process smaller codebases during development
4. **Monitor resources**: Use `docker stats` to check resource usage

## 6. Dockerization Strategy

- **Model Caching**: The MMaDA model is large. To avoid re-downloading it on every `docker run`, we will mount a host directory to the container's Hugging Face cache directory (`/root/.cache/huggingface`).
- **Base Image**: Use a slim Python image (`python:3.12-slim`).
- **Dependencies**: Install `torch` first, then the rest from `pyproject.toml` (or `requirements.txt`). This can improve layer caching.
- **Resource Allocation**: Ensure Docker has sufficient memory (8GB+) and CPU allocation
- **Quantization Support**: Docker provides full Linux environment with proper bitsandbytes support

## 7. CLI Framework

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
