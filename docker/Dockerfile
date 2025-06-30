# DocGenAI Docker Image for DeepSeek-Coder-V2-Lite
# Optimized for Linux with quantization support

FROM python:3.12-slim

# Install system dependencies for model compilation and quantization
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables for DeepSeek models
ENV HF_HOME=/app/.cache/models
ENV TRANSFORMERS_CACHE=/app/.cache/models
ENV HF_DATASETS_CACHE=/app/.cache/models
ENV TORCH_HOME=/app/.cache/torch
ENV DOCGENAI_CACHE_DIR=/app/.docgenai_cache

# Create cache directories with proper structure
RUN mkdir -p $HF_HOME $TORCH_HOME $DOCGENAI_CACHE_DIR

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install Poetry and use it to build the package
RUN pip install --no-cache-dir poetry

# Copy application code and entrypoint
COPY . .
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Build and install the package using Poetry
RUN poetry build && \
    pip install --no-cache-dir dist/*.whl && \
    pip install --no-cache-dir \
        torch \
        transformers \
        accelerate \
        bitsandbytes \
        huggingface-hub

# Create output directory
RUN mkdir -p /app/output

# Set environment variables for optimal performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TOKENIZERS_PARALLELISM=false

# Set default quantization for Docker (4-bit for memory efficiency)
ENV DOCGENAI_DEFAULT_QUANTIZATION=4bit

# Create non-root user for security and set ownership
RUN useradd -m -u 1000 docgenai && \
    chown -R docgenai:docgenai /app
USER docgenai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD docgenai info || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
