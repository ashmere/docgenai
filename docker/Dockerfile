# DocGenAI Docker Image - Optimized for DeepSeek-Coder-V2-Lite
# Uses AWQ quantized model for memory efficiency in Docker environments

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables for model caching
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

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy source code and entrypoint
COPY . .
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Build and install the package using Poetry
RUN poetry build && \
    pip install --no-cache-dir dist/*.whl

# Install PyTorch and transformers dependencies
RUN pip install --no-cache-dir \
        torch \
        transformers \
        accelerate \
        bitsandbytes \
        huggingface-hub

# Create output directory
RUN mkdir -p /app/output

# Create non-root user
RUN useradd -m -u 1000 docgenai && \
    chown -R docgenai:docgenai /app

USER docgenai

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
