# DocGenAI Docker Guide

This guide helps you run DocGenAI using Docker, which is the **recommended approach** for all platforms, especially M1/M2/M3 Macs.

## Why Docker?

- ✅ **Proper quantization support**: Full bitsandbytes support in Linux environment
- ✅ **Fast model loading**: 4-bit/8-bit quantization works correctly
- ✅ **Consistent performance**: Same behavior across all platforms
- ✅ **No compatibility issues**: Avoids Apple Silicon library problems
- ✅ **Reproducible environment**: Same setup for all developers

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image (run from project root)
docker build -f docker/Dockerfile -t docgenai .
```

### 2. Run with Model Caching (Recommended)

```bash
# Create cache directory on host
mkdir -p ~/.cache/huggingface

# Run with model cache mount to avoid re-downloading
docker run --rm -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/docgenai/models.py
```

### 3. Interactive Development

```bash
# Start interactive container for development
docker run --rm -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd):/app \
  docgenai bash

# Inside container, run commands
poetry run docgenai generate src/ --output-dir output
poetry run docgenai generate src/main.py --diagram
```

## Configuration

### Resource Allocation

For optimal performance, allocate sufficient resources to Docker:

```bash
# Run with explicit resource limits
docker run --rm -it \
  --memory=8g \
  --cpus=4 \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/
```

### Docker Desktop Settings (Mac/Windows)

1. Open Docker Desktop Settings
2. Go to Resources > Advanced
3. Set Memory to **8GB minimum** (16GB recommended)
4. Set CPUs to **4 minimum**
5. Click "Apply & Restart"

## Volume Mounts Explained

| Mount | Purpose | Required |
|-------|---------|----------|
| `~/.cache/huggingface:/app/.cache/huggingface` | Model cache (avoids re-download) | **Highly Recommended** |
| `$(pwd)/output:/app/output` | Output directory | **Recommended** |
| `$(pwd):/app` | Development (live code changes) | Development only |

## Example Commands

### Generate Documentation for Single File

```bash
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/models.py
```

### Generate Documentation for Directory

```bash
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/ --output-dir output
```

### Generate Diagram

```bash
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/models.py --diagram
```

### Verbose Logging

```bash
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai --verbose generate src/models.py
```

## Performance Optimization

### First Run (Model Download)

The first run will download the MMaDA model (~15GB). This happens once:

```bash
# First run - downloads model (can take 10-30 minutes depending on connection)
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  docgenai poetry run docgenai generate --help

# Subsequent runs use cached model (much faster)
```

### Expected Performance

| Quantization | First Load | Subsequent Loads | Memory Usage |
|--------------|------------|------------------|--------------|
| 4-bit | 2-5 minutes | 30-60 seconds | ~2GB |
| 8-bit | 3-8 minutes | 60-120 seconds | ~4GB |
| none | 10-30 minutes | 5-15 minutes | ~16GB |

## Troubleshooting

### Model Download Issues

```bash
# Check if model download is progressing
docker run --rm -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  docgenai bash

# Inside container, check cache
ls -la /app/.cache/huggingface/hub/
```

### Memory Issues

```bash
# Check Docker memory allocation
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  docgenai poetry run docgenai --verbose generate src/models.py

# If out of memory, increase Docker resources or use 4-bit quantization
```

### Permission Issues (Linux)

```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/

# Or run with user mapping
docker run --rm \
  --user $(id -u):$(id -g) \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  docgenai poetry run docgenai generate src/
```

## Configuration File

Create a custom config file for Docker use:

```yaml
# docker-config.yaml
model:
  name: "Gen-Verse/MMaDA-8B-Base"
  quantization: "4bit"  # Fastest for Docker
  session_cache: true

cache:
  enabled: true
  generation_cache: true
  cache_dir: "/app/.cache/docgenai"
  max_cache_size_mb: 1000

output:
  dir: "/app/output"
```

Use with:

```bash
docker run --rm \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/docker-config.yaml:/app/config.yaml \
  docgenai poetry run docgenai --config config.yaml generate src/
```

## Development Workflow

### Building and Testing

```bash
# Build image
docker build -f docker/Dockerfile -t docgenai .

# Test basic functionality
docker run --rm docgenai poetry run docgenai --help

# Test with sample file
echo "def hello(): print('world')" > test.py
docker run --rm \
  -v $(pwd):/app/workspace \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  docgenai poetry run docgenai generate workspace/test.py
```

### Live Development

```bash
# Mount source for live changes
docker run --rm -it \
  -v ~/.cache/huggingface:/app/.cache/huggingface \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/output:/app/output \
  docgenai bash

# Inside container, changes to src/ are immediately available
poetry run docgenai generate src/models.py
```

## Production Deployment

For production use, consider:

1. **Multi-stage build** to reduce image size
2. **Model pre-loading** to avoid download delays
3. **Resource monitoring** to ensure adequate performance
4. **Health checks** for container orchestration
5. **Persistent volumes** for model cache

Example production command:

```bash
docker run -d \
  --name docgenai-service \
  --memory=8g \
  --cpus=4 \
  --restart=unless-stopped \
  -v docgenai-cache:/app/.cache/huggingface \
  -v /host/output:/app/output \
  docgenai poetry run docgenai generate /app/workspace
```
