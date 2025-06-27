# Use Python 3.12 with full Linux support for proper quantization
FROM python:3.12-slim

# Install system dependencies for model compilation and quantization
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables for model caching and optimization
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HF_DATASETS_CACHE=/app/.cache/huggingface
ENV TORCH_HOME=/app/.cache/torch

# Create cache directories
RUN mkdir -p $HF_HOME $TORCH_HOME

# Set working directory
WORKDIR /app

# Copy only pyproject.toml (no poetry.lock to allow fresh dependency resolution)
COPY pyproject.toml ./

# Install Poetry
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# Copy application code
COPY . .

# Install dependencies and project with fresh Linux-compatible lock file
RUN poetry install --without dev

# Create output directory
RUN mkdir -p /app/output

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose any necessary ports (if adding web interface later)
EXPOSE 8000

# Default command
CMD ["poetry", "run", "docgenai", "--help"]
