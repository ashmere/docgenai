# Developer Guide: DocGenAI - DeepSeek-V3 Edition

This document contains comprehensive guidelines for developing and maintaining DocGenAI with DeepSeek-V3 integration and platform-specific optimizations.

## 1. Core Architecture Principles

### Platform-First Design

The application is built around platform detection and optimization:

- **Automatic Detection**: System automatically detects macOS vs Linux/Windows
- **Optimized Backends**: MLX for Apple Silicon, Transformers for other platforms
- **Seamless Experience**: Users don't need to know about backend differences
- **Performance Focus**: Each platform uses the most efficient available model

### Model Abstraction Layer

```python
# src/docgenai/models.py - Core abstraction pattern

class AIModel(ABC):
    """Abstract base class ensuring consistent interface across backends."""

    @abstractmethod
    def generate_documentation(self, code: str, file_path: str, **kwargs) -> str:
        """Generate comprehensive documentation."""
        pass

    @abstractmethod
    def generate_architecture_description(self, code: str, file_path: str, **kwargs) -> str:
        """Generate architectural analysis."""
        pass

class DeepSeekV3Model(AIModel):
    """Platform-aware implementation with dual backends."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.platform = platform.system()
        self.is_mac = self.platform == "Darwin"

        if self.is_mac:
            self._initialize_mlx_model()
        else:
            self._initialize_transformers_model()
```

## 2. Platform-Specific Implementation

### macOS (Apple Silicon) - MLX Backend

**Advantages**:

- Native Apple Silicon optimization
- 8-bit quantization for memory efficiency
- Fast model loading and inference
- No Docker dependency required

**Implementation Details**:

```python
def _initialize_mlx_model(self):
    """Initialize MLX model for macOS."""
    from mlx_lm import load, generate

    # Model: mlx-community/DeepSeek-v3-0324-8bit
    self.model, self.tokenizer = load(self.model_path)
    self.mlx_generate = generate
```

**Performance Characteristics**:

- Model loading: 30-60 seconds
- Memory usage: 4-6GB RAM
- Inference speed: 10-30 seconds per file
- Optimal for: Development and single-user scenarios

### Linux/Windows - Transformers Backend

**Advantages**:

- Full precision model access
- CUDA GPU acceleration support
- Flexible quantization options
- Docker containerization support

**Implementation Details**:

```python
def _initialize_transformers_model(self):
    """Initialize transformers model for non-macOS platforms."""
    from transformers import AutoTokenizer, AutoModelForCausalLM

    # Model: deepseek-ai/DeepSeek-V3
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
    self.model = AutoModelForCausalLM.from_pretrained(
        self.model_path,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
```

**Performance Characteristics**:

- Model loading: 60-300 seconds (depending on hardware)
- Memory usage: 6-16GB RAM (depending on quantization)
- Inference speed: 15-90 seconds per file
- Optimal for: Server deployments and batch processing

## 3. Development Workflow

### Local Development Setup

#### macOS Development (Recommended)

```bash
# 1. Install dependencies
poetry install

# 2. MLX will be automatically installed on macOS
# 3. Run directly - no Docker needed
poetry run docgenai generate myfile.py

# 4. Test model initialization
poetry run docgenai info

# 5. Quick test
poetry run docgenai test simple_file.py
```

#### Linux/Windows Development

```bash
# Option 1: Native development
poetry install
poetry run docgenai generate myfile.py

# Option 2: Docker development (recommended for consistency)
docker build -f docker/Dockerfile -t docgenai .
docker run --rm -v $(pwd):/workspace docgenai generate workspace/myfile.py
```

### Testing Strategy

#### Unit Testing

```python
# tests/test_models.py
def test_model_creation():
    """Test model factory creates appropriate model for platform."""
    model = create_model()

    if platform.system() == "Darwin":
        assert model.backend == "mlx"
        assert "mlx-community" in model.model_path
    else:
        assert model.backend == "transformers"
        assert "deepseek-ai" in model.model_path

def test_documentation_generation():
    """Test documentation generation across platforms."""
    model = create_model()
    code = "def hello(): return 'world'"

    doc = model.generate_documentation(code, "test.py")
    assert len(doc) > 100  # Reasonable documentation length
    assert "hello" in doc.lower()
```

#### Integration Testing

```bash
# Test end-to-end workflow
poetry run docgenai test tests/sample_files/simple.py
poetry run docgenai generate tests/sample_files/ --output-dir test_output

# Verify outputs
ls test_output/
cat test_output/*_documentation.md
```

#### Platform Testing

```bash
# macOS testing
poetry run python -c "
import platform
from src.docgenai.models import create_model
print(f'Platform: {platform.system()}')
model = create_model()
print(f'Backend: {model.backend}')
print(f'Available: {model.is_available()}')
"

# Cross-platform testing via Docker
docker run --rm docgenai python -c "
import platform
from docgenai.models import create_model
print(f'Platform: {platform.system()}')
model = create_model()
print(f'Backend: {model.backend}')
"
```

## 4. Code Quality Standards

### Markdown Linting Rules

Follow these markdownlint rules for documentation:

- **MD022**: Headings must be surrounded by blank lines
- **MD031**: Fenced code blocks must be surrounded by blank lines
- **MD032**: Lists must be surrounded by blank lines
- **MD040**: Fenced code blocks must specify a language

### Python Code Standards

```python
# Use type hints consistently
def generate_documentation(self, code: str, file_path: str, **kwargs) -> str:
    """Generate documentation with proper typing."""
    pass

# Use descriptive logging with emojis for UX
logger.info("🤖 Initializing DeepSeek-V3 model...")
logger.info("✅ Model loaded successfully")
logger.error("❌ Model initialization failed")

# Handle platform differences gracefully
if self.is_mac:
    return self._generate_with_mlx(prompt, max_tokens)
else:
    return self._generate_with_transformers(prompt, max_tokens)
```

### Pre-commit Hooks

Run before every commit:

```bash
pre-commit run --all-files
```

This ensures:

- Markdown formatting compliance
- Python code formatting (black, isort)
- Trailing whitespace removal
- YAML/JSON validation

## 5. Performance Optimization

### Model Loading Optimization

```python
# Lazy loading pattern
class DeepSeekV3Model:
    def __init__(self, config=None):
        self.model = None  # Don't load immediately
        self.config = config

    def _initialize_model(self):
        """Load model only when needed."""
        if self.model is None:
            # Platform-specific loading logic
            pass
```

### Caching Strategy

```python
# Cache at multiple levels
class CacheManager:
    def get_cache_key(self, file_path: str, include_architecture: bool) -> str:
        """Generate cache key from file content hash and options."""
        with open(file_path, 'rb') as f:
            content_hash = hashlib.md5(f.read()).hexdigest()
        return f"{content_hash}_{include_architecture}"

    def cache_result(self, key: str, result: Dict[str, Any]):
        """Cache generation result with metadata."""
        pass
```

### Memory Management

```python
# Monitor memory usage
def _generate_text(self, prompt: str, max_tokens: int = 2048) -> str:
    """Generate text with memory monitoring."""
    import psutil

    start_memory = psutil.virtual_memory().used
    result = self._actual_generation(prompt, max_tokens)
    end_memory = psutil.virtual_memory().used

    logger.info(f"Memory used: {(end_memory - start_memory) / 1024**2:.1f} MB")
    return result
```

## 6. Configuration Management

### Configuration Hierarchy

1. **Default config**: Built into the application
2. **User config**: `config.yaml` in project root
3. **CLI arguments**: Override config file settings
4. **Environment variables**: For sensitive settings

```python
# src/docgenai/config.py
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration with hierarchy."""
    # Start with defaults
    config = get_default_config()

    # Override with file config
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            user_config = yaml.safe_load(f)
        config = merge_configs(config, user_config)

    # Override with environment variables
    config = apply_env_overrides(config)

    return config
```

### Platform-Specific Defaults

```yaml
# Default configuration with platform awareness
model:
  # Platform detection is automatic
  # macOS: mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit
  # Other: deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct
  temperature: 0.7
  max_tokens: 2048
  top_p: 0.8

cache:
  enabled: true
  generation_cache: true
  model_cache: true
  cache_dir: ".cache/docgenai"
  model_cache_dir: ".cache/models"
  max_cache_size_mb: 2000
  max_generation_cache_mb: 500
  max_model_cache_mb: 1500
  generation_ttl_hours: 24
  model_ttl_hours: 168

output:
  directory: "output"
  template: "default"
  include_architecture: true
  include_code_stats: true
```

### Cache Management

The system uses multiple cache types for optimal performance:

#### Output Cache (Generation Cache)

- **Purpose**: Stores generated documentation results to avoid re-processing unchanged files
- **Location**: `.cache/docgenai/` or configured `cache_dir`
- **Content**: JSON files containing documentation text, metadata, and generation timestamps
- **TTL**: 24 hours by default (configurable via `generation_ttl_hours`)
- **Size Limit**: 500MB by default (configurable via `max_generation_cache_mb`)

#### Model Cache

- **Purpose**: Stores downloaded model files and session data
- **Location**: `.cache/models/` or configured `model_cache_dir`
- **Content**: Model weights, tokenizer files, configuration files
- **TTL**: 168 hours (1 week) by default (configurable via `model_ttl_hours`)
- **Size Limit**: 1500MB by default (configurable via `max_model_cache_mb`)

#### Cache Management Commands

```bash
# View cache statistics
docgenai cache
docgenai cache --stats

# Clear all caches
docgenai cache --clear

# Clear only output/generation cache
docgenai cache --clear-output-cache

# Clear only model cache
docgenai cache --clear-model-cache

# Generate without using output cache (force regeneration)
docgenai generate myfile.py --no-output-cache

# Generate with output cache disabled for entire directory
docgenai generate src/ --no-output-cache --output-dir fresh-docs
```

#### Cache Configuration Options

```yaml
cache:
  # Enable/disable caching entirely
  enabled: true

  # Individual cache type controls
  generation_cache: true    # Output cache
  model_cache: true        # Model file cache

  # Cache directories
  cache_dir: ".cache/docgenai"     # Output cache location
  model_cache_dir: ".cache/models" # Model cache location

  # Size limits (MB)
  max_cache_size_mb: 2000         # Total cache limit
  max_generation_cache_mb: 500    # Output cache limit
  max_model_cache_mb: 1500        # Model cache limit

  # Time-to-live (hours)
  generation_ttl_hours: 24        # How long to keep output cache
  model_ttl_hours: 168           # How long to keep model cache

  # Cleanup behavior
  auto_cleanup: true              # Automatically clean old cache
  cleanup_on_startup: false      # Clean cache on application start
```

## 7. Error Handling and Logging

### Comprehensive Error Handling

```python
def _initialize_model(self):
    """Initialize model with comprehensive error handling."""
    try:
        if self.is_mac:
            self._initialize_mlx_model()
        else:
            self._initialize_transformers_model()
    except ImportError as e:
        if self.is_mac:
            raise ImportError(
                "mlx-lm is required for macOS. Install with: pip install mlx-lm"
            ) from e
        else:
            raise ImportError(
                "transformers is required. Install with: pip install transformers torch"
            ) from e
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {str(e)}")
        logger.error("💡 Try: docgenai info --verbose for more details")
        raise
```

### User-Friendly Logging

```python
# Progressive logging with emojis
logger.info("🔧 Initializing DeepSeek-V3 model...")
logger.info("📥 Step 1/3: Loading model and tokenizer...")
logger.info("⚙️  Step 2/3: Configuring generation parameters...")
logger.info("✅ Step 3/3: Model ready for generation")
logger.info("🎉 Model initialization complete!")
```

## 8. Template System

### Template Architecture

```python
# src/docgenai/templates.py
class TemplateManager:
    def render_documentation(self, context: Dict[str, Any]) -> str:
        """Render documentation template with context."""
        template = self.env.get_template('default_doc_template.md')
        return template.render(**context)

    def render_directory_summary(self, context: Dict[str, Any]) -> str:
        """Render directory summary template."""
        template = self.env.get_template('directory_summary_template.md')
        return template.render(**context)
```

### Template Context

```python
# Rich context for templates
context = {
    'file_path': file_path,
    'file_name': Path(file_path).name,
    'language': self._detect_language(Path(file_path).suffix),
    'documentation': documentation,
    'architecture_description': architecture_description,
    'generation_time': time.strftime('%Y-%m-%d %H:%M:%S'),
    'model_info': self.model.get_model_info(),
    'code_stats': {
        'lines': len(code_content.splitlines()),
        'characters': len(code_content),
        'size_kb': round(len(code_content.encode('utf-8')) / 1024, 2)
    }
}
```

## 9. CLI Design Principles

### User Experience Focus

```python
@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='output')
@click.option('--architecture/--no-architecture', default=True)
def generate(path, output_dir, architecture):
    """
    Generate documentation with clear help text.

    Examples:
        docgenai generate myfile.py
        docgenai generate src/ --output-dir docs
    """
    # Show progress and context
    click.echo("🚀 DocGenAI - AI-powered documentation generator")
    click.echo(f"📍 Processing: {path}")
    click.echo(f"📁 Output directory: {output_dir}")
```

### Error Handling in CLI

```python
try:
    result = generator.generate_for_file(path, output_dir, architecture)
    click.echo("✅ Documentation generated successfully!")
except FileNotFoundError as e:
    click.echo(f"❌ Error: {e}", err=True)
    sys.exit(1)
except Exception as e:
    click.echo(f"❌ Unexpected error: {e}", err=True)
    if verbose:
        import traceback
        traceback.print_exc()
    sys.exit(1)
```

## 10. Testing and Validation

### Test File Structure

```text
tests/
├── test_models.py          # Model abstraction tests
├── test_core.py            # Core logic tests
├── test_cli.py             # CLI command tests
├── test_config.py          # Configuration tests
├── test_templates.py       # Template rendering tests
├── test_cache.py           # Cache management tests
├── sample_files/           # Test code samples
│   ├── simple.py
│   ├── complex_class.py
│   └── multi_file_project/
└── fixtures/               # Test fixtures and expected outputs
```

### Platform-Specific Testing

```python
# Test platform detection
def test_platform_detection():
    model = create_model()

    if platform.system() == "Darwin":
        assert hasattr(model, 'mlx_generate')
        assert model.backend == "mlx"
    else:
        assert hasattr(model, 'generation_config')
        assert model.backend == "transformers"

# Test model availability
def test_model_availability():
    model = create_model()
    assert model.is_available()

    model_info = model.get_model_info()
    assert model_info['available'] is True
    assert model_info['name'] == "DeepSeek-V3"
```

## 11. Deployment and Distribution

### Package Configuration

```toml
# pyproject.toml - Platform-specific dependencies
[tool.poetry.dependencies]
python = "^3.12"
click = "^8.2.1"
transformers = "4.53.0"
torch = "^2.7.1"
jinja2 = "^3.1.6"
PyYAML = "^6.0.2"
# Platform-specific dependency
mlx-lm = {version = "^0.20.0", markers = "sys_platform == 'darwin'"}

[tool.poetry.scripts]
docgenai = "docgenai.cli:cli"
```

### Docker Support

```dockerfile
# docker/Dockerfile - For non-macOS platforms
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only pyproject.toml first for better caching
COPY pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . .
WORKDIR /app
```

## 12. Performance Monitoring

### Benchmarking Framework

```python
# Performance monitoring
def benchmark_generation(file_path: str, iterations: int = 3) -> Dict[str, float]:
    """Benchmark documentation generation performance."""
    times = []
    memory_usage = []

    for i in range(iterations):
        start_time = time.time()
        start_memory = psutil.virtual_memory().used

        # Generate documentation
        result = generate_documentation(file_path)

        end_time = time.time()
        end_memory = psutil.virtual_memory().used

        times.append(end_time - start_time)
        memory_usage.append(end_memory - start_memory)

    return {
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times),
        'avg_memory_mb': sum(memory_usage) / len(memory_usage) / 1024**2
    }
```

### Performance Targets

| Platform | Model Loading | Single File | Memory Usage |
|----------|---------------|-------------|--------------|
| macOS (MLX) | < 60s | < 30s | < 6GB |
| Linux (CUDA) | < 120s | < 45s | < 12GB |
| Linux (CPU) | < 300s | < 90s | < 10GB |

## 13. Future Development Guidelines

### Extensibility Patterns

```python
# Plugin architecture for future extensions
class DocumentationPlugin(ABC):
    @abstractmethod
    def process_code(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process code and return enhanced context."""
        pass

# Model plugin system
class ModelPlugin(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if plugin model is available."""
        pass

    @abstractmethod
    def generate_documentation(self, code: str, file_path: str) -> str:
        """Generate documentation using plugin model."""
        pass
```

### Interactive Features (Milestone 4)

```python
# Interactive prompt system design
@cli.command()
@click.argument('file_path')
def interactive(file_path):
    """Interactive documentation tuning session."""
    generator = DocumentationGenerator()

    # Initial generation
    result = generator.generate_for_file(file_path)

    while True:
        # Show current documentation
        click.echo(result['documentation'])

        # Get user feedback
        action = click.prompt(
            "Actions: (r)egenerate, (e)dit, (s)ave, (q)uit",
            type=click.Choice(['r', 'e', 's', 'q'])
        )

        if action == 'r':
            # Regenerate with different parameters
            pass
        elif action == 'e':
            # Allow inline editing
            pass
        # ... etc
```

This developer guide provides comprehensive guidance for maintaining and extending DocGenAI with its new DeepSeek-V3 architecture, focusing on platform optimization, code quality, and user experience.
