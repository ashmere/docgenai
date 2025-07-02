# DocGenAI

AI-powered documentation generator using DeepSeek-Coder-V2-Lite models with platform-optimized performance.

## Overview

DocGenAI is a Python CLI tool that automatically generates comprehensive technical documentation for your codebases using state-of-the-art AI models. It features platform-aware optimization, intelligent caching, and supports multiple programming languages.

**Key Features:**

- 🤖 **Platform-Optimized AI**: MLX for Apple Silicon, Transformers for others
- 📝 **Comprehensive Documentation**: Code analysis, architecture descriptions, usage examples
- 🚀 **High Performance**: Intelligent caching and platform-specific optimizations
- 🎯 **Multi-Language Support**: Python, JavaScript, TypeScript, C++, and more
- 💾 **Smart Caching**: Separate output and model caches for optimal performance
- 🔧 **Flexible Configuration**: YAML-based configuration with CLI overrides

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd docgenai

# Install dependencies
poetry install

# Quick test
poetry run docgenai test simple_test.py
```

### Basic Usage

```bash
# Generate documentation for a single file
poetry run docgenai generate myfile.py

# Process entire directory
poetry run docgenai generate src/ --output-dir docs

# Multi-file analysis for better cross-file understanding
poetry run docgenai generate src/ --multi-file --output-dir docs

# Force fresh generation (bypass cache)
poetry run docgenai generate src/models.py --no-output-cache

# View system information
poetry run docgenai info
```

## 🔗 Multi-File Analysis

DocGenAI supports intelligent multi-file analysis that understands relationships between files and generates better documentation by analyzing related code together.

### How Multi-File Analysis Works

Instead of analyzing files in isolation, multi-file analysis:

1. **Groups Related Files**: Automatically groups files by directory and relationships
2. **Cross-File Understanding**: Analyzes how modules interact and depend on each other
3. **Architectural Insights**: Identifies service boundaries, design patterns, and system architecture
4. **Synthesis**: For large codebases, synthesizes insights across multiple file groups

### Multi-File vs Single-File Comparison

| Aspect | Single-File Analysis | Multi-File Analysis |
|--------|---------------------|---------------------|
| **Scope** | Individual file only | Related files together |
| **Dependencies** | Limited to imports | Full dependency analysis |
| **Architecture** | File-level patterns | System-level architecture |
| **Context** | Isolated understanding | Cross-file relationships |
| **Quality** | Good for individual files | Better for system understanding |
| **Speed** | Faster per file | Slower but more comprehensive |

### Multi-File Usage Examples

#### Basic Multi-File Analysis

```bash
# Analyze a module directory with related files
poetry run docgenai generate src/models/ --multi-file --output-dir docs/models

# Analyze entire codebase with intelligent grouping
poetry run docgenai generate src/ --multi-file --output-dir docs/codebase

# Multi-file analysis with enhanced chaining for highest quality
poetry run docgenai generate src/core/ --multi-file --chain --chain-strategy enhanced
```

#### Project Type Optimization

```bash
# Microservice-focused documentation
poetry run docgenai generate src/ --multi-file --project-type microservice --output-dir docs/microservice

# Library documentation with API focus
poetry run docgenai generate src/ --multi-file --project-type library --output-dir docs/library

# Application documentation with user focus
poetry run docgenai generate src/ --multi-file --project-type application --output-dir docs/application

# Framework documentation with extension points
poetry run docgenai generate src/ --multi-file --project-type framework --output-dir docs/framework
```

#### Advanced Multi-File Options

```bash
# Control file grouping size
poetry run docgenai generate src/ --multi-file --max-files-per-group 5 --output-dir docs

# Multi-file with specific project type and chaining
poetry run docgenai generate src/ --multi-file --project-type microservice --chain --chain-strategy enhanced

# Large codebase analysis with synthesis
poetry run docgenai generate large_project/ --multi-file --max-files-per-group 3 --output-dir docs/analysis
```

### Multi-File Output Structure

Multi-file analysis generates organized documentation:

```text
docs/
├── index.md                     # Navigation index (always generated)
├── multi_file_documentation.md  # Single group analysis
└── codebase_documentation.md    # Multi-group synthesis (large codebases)
```

For large codebases with multiple groups:

```text
docs/
├── index.md                     # Navigation index
├── codebase_documentation.md    # Comprehensive overview
├── group_1_documentation.md     # Individual group docs
├── group_2_documentation.md
└── group_3_documentation.md
```

### Project Types

DocGenAI supports different project types for tailored documentation:

#### Microservice Projects

- **Focus**: Service boundaries, API contracts, deployment considerations
- **Sections**: Service Architecture, API Documentation, Deployment Guide
- **Best for**: Individual services, API-focused modules

```bash
poetry run docgenai generate src/user-service/ --multi-file --project-type microservice
```

#### Library Projects

- **Focus**: Public APIs, usage patterns, integration guides
- **Sections**: API Reference, Usage Examples, Integration Guide
- **Best for**: Reusable libraries, SDK modules

```bash
poetry run docgenai generate src/sdk/ --multi-file --project-type library
```

#### Application Projects

- **Focus**: User workflows, configuration, operations
- **Sections**: User Guide, Configuration, Operations Manual
- **Best for**: End-user applications, CLI tools

```bash
poetry run docgenai generate src/ --multi-file --project-type application
```

#### Framework Projects

- **Focus**: Extension points, patterns, architecture
- **Sections**: Architecture Guide, Extension Guide, Best Practices
- **Best for**: Frameworks, platforms, extensible systems

```bash
poetry run docgenai generate src/framework/ --multi-file --project-type framework
```

### Configuration-Based Multi-File

Enable multi-file analysis by default in `config.yaml`:

```yaml
multi_file:
  enabled: true
  max_files_per_group: 6
  project_type: "auto"  # or "microservice", "library", "application", "framework"

chaining:
  enabled: true
  default_strategy: "enhanced"
```

Then use normally:

```bash
# Will use multi-file analysis from config
poetry run docgenai generate src/

# Override project type for this run
poetry run docgenai generate src/ --project-type microservice

# Disable multi-file for this run
poetry run docgenai generate src/ --no-multi-file
```

## 🔗 Prompt Chaining Strategies

DocGenAI supports advanced prompt chaining for enhanced documentation quality. Chaining breaks documentation generation into multiple focused steps, allowing the AI to build understanding progressively.

### Available Strategies

#### **Simple** (Default)

- **Steps**: 1 step - Direct documentation generation
- **Behavior**: Identical to current system (backward compatible)
- **Use case**: Quick documentation, existing workflows
- **Performance**: Fastest (~17s per file on Apple Silicon)

#### **Enhanced**

- **Steps**: 3 steps - Analyze → Document → Enhance
- **Process**:
  1. **Analyze**: Code structure and pattern identification
  2. **Document**: Generate comprehensive documentation
  3. **Enhance**: Refine with additional insights and examples
- **Use case**: Higher quality documentation with deeper analysis
- **Performance**: ~3x slower but potentially much better quality

#### **Architecture**

- **Steps**: 4 steps - Analyze → Describe → Diagram → Combine
- **Process**:
  1. **Architectural Analysis**: Deep system architecture analysis
  2. **Text Description**: Detailed architectural descriptions
  3. **Diagram Specification**: Generate Mermaid diagram specs
  4. **Combined Documentation**: Merge text and diagrams
- **Use case**: Complex systems needing architectural docs with diagrams
- **Performance**: Slowest but most comprehensive output

### Usage Examples

#### Basic Chaining Commands

```bash
# Use simple strategy (default - same as current behavior)
poetry run docgenai generate src/models.py

# Enable enhanced strategy for better quality
poetry run docgenai generate src/models.py --chain --chain-strategy enhanced

# Generate architectural documentation with diagrams
poetry run docgenai generate src/core.py --chain --chain-strategy architecture

# Process entire directory with enhanced strategy
poetry run docgenai generate src/ --chain --chain-strategy enhanced --output-dir docs
```

#### Configuration-Based Usage

Enable chaining by default in `config.yaml`:

```yaml
chaining:
  enabled: true
  default_strategy: "enhanced"  # or "simple", "architecture"
  max_steps: 10
  timeout_per_step: 300
  fail_fast: true
```

Then use normally:

```bash
# Will use enhanced strategy from config
poetry run docgenai generate src/models.py

# Override config strategy
poetry run docgenai generate src/models.py --chain-strategy architecture

# Disable chaining for this run
poetry run docgenai generate src/models.py --no-chain
```

#### Advanced Chaining Options

```bash
# Enhanced strategy with custom timeout
poetry run docgenai generate large_file.py --chain --chain-strategy enhanced

# Architecture strategy for complex systems
poetry run docgenai generate src/core.py --chain --chain-strategy architecture

# Simple strategy (explicit)
poetry run docgenai generate src/utils.py --chain --chain-strategy simple
```

### When to Use Each Strategy

| Strategy | Best For | Output Quality | Speed | Use Cases |
|----------|----------|----------------|--------|-----------|
| **Simple** | Quick docs, CI/CD, large codebases | Good | Fastest | Existing workflows, bulk processing |
| **Enhanced** | Production documentation | Better | 3x slower | Important modules, public APIs |
| **Architecture** | System documentation | Best | 4x slower | Core systems, complex architectures |

### Strategy Comparison Example

For the same `src/models.py` file:

**Simple Strategy Output:**

- Standard documentation with classes, methods, usage
- ~17 seconds generation time

**Enhanced Strategy Output:**

- All simple content PLUS:
- Deeper analysis of design patterns
- More comprehensive usage examples
- Performance considerations
- Best practices recommendations
- ~50 seconds generation time

**Architecture Strategy Output:**

- All enhanced content PLUS:
- Architectural analysis and diagrams
- System interaction flows
- Component relationship diagrams
- Design decision explanations
- ~70 seconds generation time

### Performance Impact

| Platform | Simple | Enhanced | Architecture |
|----------|--------|----------|--------------|
| **macOS (MLX)** | ~17s | ~50s | ~70s |
| **Linux (Docker)** | ~30s | ~90s | ~120s |

*Times are estimates for typical Python files on tested platforms*

## Platform Optimization

DocGenAI automatically detects your platform and uses the optimal model backend:

### macOS (Apple Silicon)

- **Model**: `mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit`
- **Backend**: MLX with native Apple Silicon optimization
- **Performance**: ~30-60s model loading, ~10-30s per file
- **Memory**: ~4-6GB RAM usage
- **Quantization**: 4-bit (MLX native)

### Linux/Windows

- **Model**: `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ`
- **Backend**: Transformers with optional CUDA acceleration
- **Performance**: ~60-300s model loading, ~15-90s per file
- **Memory**: ~6-16GB RAM (depending on quantization)
- **Quantization**: 4-bit AWQ (pre-quantized)

## Supported Models and Platforms

### ✅ Tested and Supported

| Platform | Environment | Model | Backend | Status | Performance |
|----------|-------------|--------|---------|--------|-------------|
| **macOS (Apple Silicon)** | Native Python | `mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit` | MLX | ✅ **Fully Tested** | 6s load, 17s generation |
| **macOS (Apple Silicon)** | Native Python | `mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit` | MLX | ✅ **Fully Tested** | 8s load, 28s generation |
| **Linux (x86_64)** | Docker | `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | Transformers | 🔄 **Architecture Ready** | Expected: 60-120s load |
| **Linux (ARM64)** | Docker | `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | Transformers | 🔄 **Architecture Ready** | Expected: 60-120s load |

### 🚧 Planned Support

| Platform | Environment | Model | Backend | Status | Notes |
|----------|-------------|--------|---------|--------|-------|
| **Linux (x86_64)** | Native Python | `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | Transformers | 🔄 **Planned** | Requires CUDA/CPU testing |
| **Windows** | Native Python | `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | Transformers | 🔄 **Planned** | Requires Windows testing |
| **Windows** | Docker | `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` | Transformers | 🔄 **Planned** | Docker Desktop support |

### 📋 Model Details

#### MLX Models (macOS Only)

- **4-bit**: `mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit` (~8.8GB download)
- **8-bit**: `mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit` (~8.8GB download)
- **Advantages**: Native Apple Silicon optimization, fast inference
- **Requirements**: macOS with Apple Silicon (M1/M2/M3)

#### AWQ Models (Linux/Windows)

- **4-bit AWQ**: `TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ` (~3GB download)
- **Advantages**: Pre-quantized, smaller download, memory efficient
- **Requirements**: Linux/Windows with sufficient RAM (6GB+)

### 🐳 Docker Support Status

#### Current Docker Implementation

- **Base Image**: `python:3.11-slim` with quantization libraries
- **Supported Platforms**: `linux/amd64`, `linux/arm64`
- **Model**: AWQ 4-bit quantized for memory efficiency
- **Cache Strategy**: Platform-specific cache directories
- **Memory Requirements**: 12GB+ recommended

#### Docker Platform Detection

```bash
# Automatic platform-aware cache directories
~/.cache/models-docker-amd64/    # Intel/AMD x86_64
~/.cache/models-docker-arm64/    # ARM64 (Raspberry Pi, etc.)
```

### 🔧 Platform-Specific Configuration

#### macOS (Native)

```yaml
model:
  mlx_model: "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"
  quantization: "4bit"
```

#### Linux/Windows (Native or Docker)

```yaml
model:
  transformers_model: "TechxGenus/DeepSeek-Coder-V2-Lite-Instruct-AWQ"
  load_in_4bit: true
```

### 📊 Performance Benchmarks

#### macOS M3 (Tested

- **Model Loading**: 6-10 seconds (cached)
- **Single File**: 17-28 seconds (with architecture analysis)
- **Memory Usage**: 4-6GB peak
- **Cache Performance**: Instant for unchanged files

#### Docker Linux (Expected)

- **Model Loading**: 60-120 seconds (first run)
- **Single File**: 30-60 seconds (estimated)
- **Memory Usage**: 8-12GB peak
- **Download Size**: ~3GB (AWQ model)

## Command Examples

### Documentation Generation

```bash
# Single file with default (simple) strategy
poetry run docgenai generate src/models.py

# Multi-file analysis for better cross-file understanding
poetry run docgenai generate src/models/ --multi-file --output-dir docs/models

# Enhanced documentation with multi-step chaining
poetry run docgenai generate src/models.py --chain --chain-strategy enhanced

# Multi-file analysis with enhanced chaining for highest quality
poetry run docgenai generate src/core/ --multi-file --chain --chain-strategy enhanced

# Project-type specific documentation
poetry run docgenai generate src/ --multi-file --project-type microservice --output-dir docs/microservice

# Architectural documentation with diagrams
poetry run docgenai generate src/core.py --chain --chain-strategy architecture

# Directory processing with enhanced strategy
poetry run docgenai generate src/ --output-dir documentation --chain --chain-strategy enhanced

# Large codebase multi-file analysis with synthesis
poetry run docgenai generate large_project/ --multi-file --max-files-per-group 3 --output-dir docs

# Force regeneration without cache
poetry run docgenai generate src/core.py --no-output-cache

# Combine multi-file, chaining, and project type
poetry run docgenai generate src/ --multi-file --chain --chain-strategy enhanced --project-type application
```

### Cache Management

```bash
# View cache statistics
poetry run docgenai cache

# Clear all caches
poetry run docgenai cache --clear

# Clear only output cache (keep model files)
poetry run docgenai cache --clear-output-cache

# Clear only model cache (keep generation results)
poetry run docgenai cache --clear-model-cache
```

### Testing and Development

```bash
# Quick test without saving files
poetry run docgenai test example.py

# Verbose logging for debugging
poetry run docgenai --verbose generate problematic_file.py

# System information and model status
poetry run docgenai info
```

## Configuration

Create a `config.yaml` file to customize behavior:

```yaml
# AI Model Configuration
model:
  temperature: 0.7          # Creativity level (0.0-2.0)
  max_tokens: 2048          # Maximum output length
  top_p: 0.8               # Nucleus sampling
  quantization: "4bit"     # Options: "none", "8bit", "4bit"

# Cache Configuration
cache:
  enabled: true
  generation_cache: true    # Cache documentation results
  model_cache: true        # Cache downloaded models
  max_cache_size_mb: 2000  # Total cache limit
  generation_ttl_hours: 24 # How long to keep results

# Output Configuration
output:
  dir: "output"
  include_architecture: true
  include_code_stats: true
  markdown_style: "github"
```

## Performance Expectations

| Platform | Model Loading | Single File | Memory Usage |
|----------|---------------|-------------|--------------|
| **macOS (MLX)** | 30-60s | 10-30s | 4-6GB |
| **Linux (CUDA)** | 60-120s | 15-45s | 8-12GB |
| **Linux (CPU)** | 120-300s | 30-90s | 6-10GB |
| **Windows** | 60-300s | 15-90s | 6-16GB |

*First run times include model download. Subsequent runs use cached models.*

## Supported Languages

- **Python** (.py) - Full support with advanced analysis
- **JavaScript/TypeScript** (.js, .ts, .jsx, .tsx)
- **C/C++** (.c, .cpp, .h, .hpp)
- **Java** (.java)
- **Go** (.go)
- **Rust** (.rs)
- **Ruby** (.rb)
- **PHP** (.php)
- **C#** (.cs)
- **Swift** (.swift)
- **Kotlin** (.kt)
- **Scala** (.scala)
- **R** (.r, .R)

## Output Examples

Generated documentation includes:

### File Documentation

- **Overview**: High-level description of file purpose
- **Key Components**: Classes, functions, and important variables
- **Architecture**: Design patterns and code organization
- **Usage Examples**: Practical code examples
- **Dependencies**: Required imports and external dependencies
- **Configuration**: Environment variables and settings
- **Error Handling**: Exception handling patterns
- **Performance**: Optimization notes and considerations

### Architecture Analysis

- **Code Organization**: Module structure and relationships
- **Design Patterns**: Identified architectural patterns
- **Data Flow**: How data moves through the system
- **Dependencies**: Internal and external dependencies
- **Interfaces**: Public APIs and contracts
- **Extensibility**: Points for future enhancement
- **Improvement Suggestions**: Actionable optimization recommendations

## Cache System

DocGenAI uses a sophisticated two-tier caching system:

### Output Cache

- **Purpose**: Stores generated documentation to avoid re-processing unchanged files
- **Location**: `.docgenai_cache/` (configurable)
- **Content**: Documentation text, metadata, timestamps
- **TTL**: 24 hours (configurable)
- **Benefits**: Instant results for unchanged files

### Model Cache

- **Purpose**: Stores downloaded model files and tokenizers
- **Location**: `.cache/models/` (configurable)
- **Content**: Model weights, tokenizer files, configuration
- **TTL**: 1 week (configurable)
- **Benefits**: Faster startup after initial download

## CLI Commands

### Core Commands

```bash
# Generate documentation
docgenai generate <path> [options]

# Test generation without saving
docgenai test <file>

# Show system information
docgenai info

# Manage caches
docgenai cache [options]
```

### Global Options

```bash
# Verbose logging
docgenai --verbose <command>

# Custom configuration
docgenai --config custom.yaml <command>

# Help for any command
docgenai <command> --help
```

## Development

### Project Structure

```text
docgenai/
├── src/docgenai/          # Main application code
│   ├── models.py          # AI model abstractions and platform detection
│   ├── core.py           # Documentation generation pipeline
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── cache.py          # Caching system
│   ├── templates.py      # Template rendering
│   └── templates/        # Documentation templates
├── docs/                 # Documentation
│   ├── developer.md      # Development guide
│   └── plan.md          # Project roadmap
├── tests/               # Test suite
├── docker/              # Docker configuration (optional)
└── config.yaml         # Default configuration
```

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run pre-commit hooks
poetry run pre-commit install
poetry run pre-commit run --all-files

# Run tests
poetry run pytest

# Type checking
poetry run mypy src/
```

### Contributing

1. Follow the coding standards in [docs/developer.md](docs/developer.md)
2. Add tests for new functionality
3. Update documentation for any changes
4. Run pre-commit hooks before committing
5. Use conventional commit messages

## Troubleshooting

### Common Issues

**Slow performance on Apple Silicon:**

- ✅ **Solution**: Use native installation (poetry install) - MLX optimization included

**Out of memory errors:**

- ✅ **Solution**: Use 4-bit quantization in config.yaml
- ✅ **Alternative**: Process files individually instead of entire directories

**Model download issues:**

- ✅ **Solution**: Check internet connection and available disk space
- ✅ **Alternative**: Clear model cache and retry: `docgenai cache --clear-model-cache`

**Cache-related issues:**

- ✅ **Solution**: Clear output cache: `docgenai cache --clear-output-cache`
- ✅ **Alternative**: Use `--no-output-cache` flag for fresh generation

### Getting Help

```bash
# System diagnostics
poetry run docgenai info --verbose

# Cache statistics
poetry run docgenai cache --stats

# Command help
poetry run docgenai <command> --help
```

## License

See [LICENSE](LICENSE) file for details.

For detailed development information, see [docs/developer.md](docs/developer.md).

For version history and changes, see [CHANGELOG.md](CHANGELOG.md).
