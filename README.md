# DocGenAI

AI-powered documentation and diagramming tool using the MMaDA multimodal model.

## Overview

DocGenAI is a Python CLI tool that uses the MMaDA (Multimodal Assistant for Data Analysis) model to automatically generate comprehensive technical documentation and architecture diagrams for your codebases. It can analyze code structure, understand functionality, and create visual representations to help developers understand complex systems.

## 🚀 Quick Start (Docker - Recommended)

**For best performance and compatibility (especially on M1/M2/M3 Macs), use Docker:**

```bash
# 1. Build the Docker image
docker build -f docker/Dockerfile -t docgenai .

# 2. Generate documentation for a file
./docker/run.sh generate src/docgenai/models.py

# 3. Generate a diagram
./docker/run.sh diagram src/docgenai/models.py

# 4. Process entire directory
./docker/run.sh generate src/
```

## Features

- 📝 **Code Analysis**: Deep understanding of code structure and functionality
- 🎨 **Architecture Diagrams**: Automatic generation of Mermaid.js system diagrams
- 📚 **Documentation Generation**: Comprehensive technical documentation
- 🔄 **Documentation Improvement**: Enhance existing documentation
- 📋 **Template-driven Output**: Customizable formats and styles
- 💾 **Intelligent Caching**: Avoid re-processing unchanged files
- 🎯 **Multiple Formats**: Support for Python, with more languages planned

## Why Docker?

- ✅ **M1/M2/M3 Mac Compatible**: Avoids Apple Silicon compatibility issues
- ✅ **Faster Model Loading**: Proper quantization support (4-bit/8-bit)
- ✅ **Consistent Performance**: Same behavior across all platforms
- ✅ **No Setup Hassles**: All dependencies included

## Installation & Setup

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd docgenai

# Make runner script executable
chmod +x docker/run.sh

# Build and run
./docker/run.sh --build generate src/
```

### Option 2: Native Installation (Advanced Users)

⚠️ **Warning**: Native installation on M1/M2/M3 Macs may experience slow performance (1+ hours for model loading) due to quantization compatibility issues.

```bash
# Install dependencies
poetry install

# Run (may be very slow on Apple Silicon)
poetry run docgenai generate src/
```

## Usage Examples

### Basic Documentation Generation

```bash
# Generate docs for a single file
./docker/run.sh generate src/models.py

# Generate docs for entire project
./docker/run.sh generate src/ --verbose

# Generate with custom output directory
./docker/run.sh generate src/ --output-dir docs/
```

### Diagram Generation

```bash
# Create architecture diagram for a file
./docker/run.sh diagram src/core.py

# Generate with verbose logging
./docker/run.sh --verbose diagram src/models.py
```

### Interactive Development

```bash
# Start interactive shell for development
./docker/run.sh shell

# Inside container:
poetry run docgenai generate src/models.py
poetry run docgenai --help
```

## Configuration

Create a `config.yaml` file to customize behavior:

```yaml
model:
  name: "Gen-Verse/MMaDA-8B-Base"
  quantization: "4bit"  # Options: 4bit, 8bit, none
  session_cache: true

cache:
  enabled: true
  generation_cache: true
  max_cache_size_mb: 1000

output:
  dir: "output"
  format: "markdown"
```

## Performance Expectations

| Platform | Quantization | First Load | Subsequent | Memory |
|----------|-------------|------------|------------|--------|
| Docker (All) | 4-bit | 2-5 min | 30-60 sec | ~2GB |
| Docker (All) | 8-bit | 3-8 min | 60-120 sec | ~4GB |
| M1/M2/M3 Native | none | 10-30 min | 5-15 min | ~16GB |

## Troubleshooting

### Model Loading Issues

- **Use Docker**: Resolves most compatibility issues
- **Check memory**: Ensure Docker has 8GB+ allocated
- **Verify network**: Model downloads require stable internet
- **Use 4-bit quantization**: Fastest loading option

### Common Issues

- **Slow performance on Mac**: Use Docker instead of native installation
- **Out of memory**: Increase Docker memory limit or use 4-bit quantization
- **Model download hangs**: Check internet connection and Docker resources

## Development

See [docs/developer.md](docs/developer.md) for detailed development guidelines, including:

- Platform compatibility information
- Docker development workflow
- Performance optimization tips
- Troubleshooting guide

## Project Structure

```text
docgenai/
├── src/docgenai/          # Main application code
│   ├── models.py          # AI model abstractions
│   ├── core.py           # Core processing logic
│   ├── cli.py            # Command-line interface
│   └── templates/        # Documentation templates
├── docker/               # Docker configuration
│   ├── Dockerfile        # Container definition
│   ├── run.sh           # Convenient runner script
│   └── README.md        # Docker usage guide
├── docs/                # Documentation
└── tests/               # Test suite
```

## Contributing

1. Use Docker for development to ensure consistent environment
2. Follow the coding standards in [docs/developer.md](docs/developer.md)
3. Add tests for new functionality
4. Update documentation for any changes

## License

See [LICENSE](LICENSE) file for details.
