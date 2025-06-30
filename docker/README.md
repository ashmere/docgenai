# DocGenAI Docker Guide

Run DocGenAI using Docker for consistent, cross-platform documentation generation with **DeepSeek-Coder-V2-Lite** models.

## Why Docker?

- ✅ **Consistent environment**: Same behavior across all platforms
- ✅ **Proper quantization**: Full Linux quantization support (4-bit/8-bit)
- ✅ **No dependency conflicts**: Isolated Python environment
- ✅ **Easy deployment**: Container-ready for CI/CD and production
- ✅ **Resource management**: Controlled memory and CPU allocation

## Quick Start

### 1. Build the Docker Image

```bash
# Build from project root
docker build -f docker/Dockerfile -t docgenai .

# Or use the helper script
./docker/run.sh --build help
```

### 2. Generate Documentation

```bash
# Generate docs for a single file
./docker/run.sh generate src/models.py

# Generate docs for entire directory
./docker/run.sh generate src/ --output-dir docs/

# Test on a single file first
./docker/run.sh test src/models.py
```

### 3. Cache Management

```bash
# Show cache statistics
./docker/run.sh cache

# Clear output cache only
./docker/run.sh cache --clear-output-cache

# Clear model cache (forces re-download)
./docker/run.sh cache --clear-model-cache
```

## Installation & Setup

### Prerequisites

- **Docker**: 20.10+ with BuildKit support
- **Memory**: 12GB+ available to Docker (16GB recommended)
- **Storage**: 10GB+ free space for models and cache
- **CPU**: 4+ cores recommended

### Docker Desktop Configuration

**macOS/Windows**: Increase Docker resources:

1. Open Docker Desktop → Settings → Resources
2. **Memory**: Set to 12GB minimum (16GB recommended)
3. **CPUs**: Set to 4 minimum (8 recommended)
4. **Disk**: Ensure 10GB+ available
5. Apply & Restart

## Model Information

### DeepSeek-Coder-V2-Lite in Docker

- **Model**: `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`
- **Platform**: Linux (Transformers library)
- **Quantization**: 4-bit default (configurable)
- **Memory**: 6-16GB depending on quantization
- **Download Size**: ~4-8GB (first run only)

### Performance Expectations

| Quantization | Model Loading | Per File | Memory Usage |
|--------------|---------------|----------|--------------|
| 4-bit | 60-120s | 15-30s | 6-8GB |
| 8-bit | 90-180s | 20-45s | 8-12GB |
| 16-bit | 120-300s | 30-90s | 12-16GB |

*Note: First run includes model download time*

## Usage Examples

### Basic Commands

```bash
# Show help
./docker/run.sh help

# Show model info
./docker/run.sh info

# Create config file
./docker/run.sh init

# Interactive shell
./docker/run.sh shell
```

### Documentation Generation

```bash
# Single file with verbose output
./docker/run.sh --verbose generate src/models.py

# Directory with custom output
./docker/run.sh generate src/ --output-dir documentation/

# Skip cache for fresh generation
./docker/run.sh generate src/models.py --no-output-cache

# Generate with specific style
./docker/run.sh generate src/ --style comprehensive
```

### Advanced Options

```bash
# Custom memory allocation
./docker/run.sh --memory 16g generate large_project/

# More CPU cores
./docker/run.sh --cpus 8 generate src/

# Verbose logging with custom resources
./docker/run.sh --verbose --memory 16g --cpus 8 generate src/
```

## Cache Management

### Cache Types

DocGenAI uses two cache types:

1. **Model Cache** (`~/.cache/models/`): Downloaded model files
2. **Output Cache** (`./.docgenai_cache/`): Generated documentation

### Cache Commands

```bash
# Show detailed cache statistics
./docker/run.sh cache

# Clear only generated documentation
./docker/run.sh cache --clear-output-cache

# Clear only model files (forces re-download)
./docker/run.sh cache --clear-model-cache

# Clear everything
./docker/run.sh cache --clear
```

### Cache Persistence

Cache directories are mounted from host:

- Model cache: `~/.cache/models` → `/app/.cache/models`
- Output cache: `./.docgenai_cache` → `/app/.docgenai_cache`

This ensures models persist between container runs.

## Configuration

### Environment Variables

```bash
# Set quantization level
export DOCGENAI_DEFAULT_QUANTIZATION=8bit
./docker/run.sh generate src/

# Custom cache location
export DOCGENAI_CACHE_DIR=/custom/cache
./docker/run.sh generate src/
```

### Configuration File

Create `config.yaml` in your project:

```yaml
model:
  name: "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
  quantization: "4bit"
  max_length: 8192

cache:
  enabled: true
  generation_cache: true
  ttl_hours: 168  # 1 week

output:
  style: "comprehensive"
  include_examples: true
```

Use with Docker:

```bash
./docker/run.sh --verbose generate src/ --config config.yaml
```

## Development Workflow

### Interactive Development

```bash
# Start shell with mounted source
./docker/run.sh shell

# Inside container:
poetry run docgenai generate /app/workspace/src/
poetry run docgenai cache
poetry run docgenai info
```

### Live Code Changes

```bash
# Mount current directory for development
docker run --rm -it \
  -v ~/.cache/models:/app/.cache/models \
  -v $(pwd)/.docgenai_cache:/app/.docgenai_cache \
  -v $(pwd):/app/workspace \
  docgenai bash

# Changes to local files are immediately available
```

### Testing Changes

```bash
# Rebuild image after code changes
./docker/run.sh --build test src/models.py

# Test with different configurations
./docker/run.sh --memory 8g test src/models.py
./docker/run.sh --verbose test src/models.py
```

## Troubleshooting

### Common Issues

**Out of Memory**:

```bash
# Increase Docker memory allocation
./docker/run.sh --memory 16g generate src/

# Or use more aggressive quantization
export DOCGENAI_DEFAULT_QUANTIZATION=4bit
./docker/run.sh generate src/
```

**Slow Performance**:

```bash
# Check if model is cached
./docker/run.sh cache

# Allocate more CPUs
./docker/run.sh --cpus 8 generate src/

# Use output cache for repeated runs
./docker/run.sh generate src/  # Subsequent runs use cache
```

**Permission Issues** (Linux):

```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/
sudo chown -R $USER:$USER .docgenai_cache/

# Or run with user mapping
docker run --rm --user $(id -u):$(id -g) \
  -v ~/.cache/models:/app/.cache/models \
  -v $(pwd)/.docgenai_cache:/app/.docgenai_cache \
  docgenai generate src/
```

**Model Download Failures**:

```bash
# Clear model cache and retry
./docker/run.sh cache --clear-model-cache
./docker/run.sh generate src/

# Check network connectivity
./docker/run.sh shell
# Inside: curl -I https://huggingface.co
```

### Debug Commands

```bash
# Check container environment
./docker/run.sh shell
# Inside container:
env | grep -E "(HF_|TRANSFORMERS_|DOCGENAI_)"
df -h
free -h
poetry run docgenai info

# Check cache contents
ls -la ~/.cache/models/
ls -la .docgenai_cache/

# Verbose logging
./docker/run.sh --verbose info
./docker/run.sh --verbose cache
```

## Production Deployment

### CI/CD Integration

```yaml
# GitHub Actions example
name: Generate Documentation
on: [push]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build DocGenAI
        run: docker build -f docker/Dockerfile -t docgenai .
      - name: Generate Documentation
        run: |
          docker run --rm \
            -v ${{ github.workspace }}:/app/workspace \
            -v ~/.cache/models:/app/.cache/models \
            docgenai generate /app/workspace/src --output-dir /app/workspace/docs
      - name: Upload Documentation
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: docs/
```

### Multi-stage Build (Optional)

For production, create optimized image:

```dockerfile
# Dockerfile.prod
FROM docgenai as builder
RUN poetry run docgenai cache --clear-output-cache

FROM python:3.12-slim as runtime
COPY --from=builder /app/.cache/models /app/.cache/models
COPY --from=builder /app /app
WORKDIR /app
RUN pip install poetry && poetry install --without dev
ENTRYPOINT ["/entrypoint.sh"]
```

### Resource Planning

For production workloads:

- **Memory**: 16GB+ for concurrent processing
- **CPU**: 8+ cores for faster generation
- **Storage**: 20GB+ for models and cache
- **Network**: Stable connection for initial model download

## Performance Optimization

### Best Practices

1. **Use appropriate quantization**:
   - 4-bit: Fastest, lowest memory
   - 8-bit: Balanced performance/quality
   - 16-bit: Highest quality, most memory

2. **Leverage caching**:
   - Keep model cache persistent
   - Use output cache for repeated runs
   - Clear output cache only when needed

3. **Resource allocation**:
   - Start with 12GB memory, increase if needed
   - Use 4+ CPU cores
   - Monitor resource usage with `docker stats`

4. **Batch processing**:
   - Process multiple files in single run
   - Use directory-level generation
   - Leverage parallel processing

## Support

For issues specific to Docker deployment:

1. Check [troubleshooting section](#troubleshooting)
2. Verify Docker resource allocation
3. Test with minimal example
4. Check container logs: `docker logs <container_id>`
5. Use verbose logging: `./docker/run.sh --verbose`

For general DocGenAI issues, see the main project documentation.
