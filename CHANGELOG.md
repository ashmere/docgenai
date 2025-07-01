# Changelog

All notable changes to DocGenAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-07-01

### Added

- **Prompt Chaining System**: Comprehensive multi-step AI generation framework
  - `PromptStep` class for individual chain steps with dependencies and transformations
  - `PromptChain` orchestrator with dependency resolution and error handling
  - `ChainContext` for state management between steps
  - `ChainBuilder` with pre-built chain configurations (simple, enhanced, architecture)
  - CLI support with `--chain/--no-chain` and `--chain-strategy` options
  - Configuration support in `config.yaml` with backward compatibility
  - Comprehensive test suite with 33 new tests covering all chaining components
  - Integration with existing `DocumentationGenerator` and `AIModel` classes
  - Support for future enhancements like architecture diagrams and quality workflows
- **Index and Summary Separation**: Distinct functions for navigation and architectural overview
  - `index.md`: Always generated navigational index of all documentation files
  - `summary.md`: Generated only with chaining enabled for comprehensive architectural overview
- **Enhanced Sample Output**: Fresh documentation generated using enhanced chaining strategy

### Changed

- Extended `AIModel` abstract class with `generate_raw_response()` method for chaining support
- Enhanced `DocumentationGenerator` with optional chain execution capabilities
- Updated CLI with chaining options while maintaining backward compatibility
- Separated index generation (navigation) from summary generation (architectural overview)
- Fixed cached result handling to properly regenerate files in target output directory

### Technical Details

- **Backward Compatibility**: Chaining is disabled by default - existing behavior unchanged
- **Test Coverage**: Added 33 comprehensive tests for all chaining components (104 total tests)
- **Architecture**: Clean separation of concerns with modular chain components
- **Error Handling**: Robust error handling with configurable fail-fast behavior
- **Performance**: Efficient dependency resolution and execution ordering
- **Cache Improvements**: Fixed sequencing issue where index.md was generated before individual files

## [0.4.0] - 2025-07-01

### Added (v0.4.0)

- **Fresh sample documentation**: New comprehensive sample output showcasing clean, professional documentation generation
- **Configuration-driven architecture**: Models are now sourced exclusively from configuration files
- **Enhanced prompt system**: Modular prompt architecture with separate files for better maintainability
- **Improved markdown quality**: Advanced post-processing for clean, lint-free documentation output
- **Directory ignore support**: `.docgenai_ignore` file support for excluding files from generation

### Changed (v0.4.0)

- **BREAKING**: Removed all Mermaid diagram functionality for cleaner, more focused documentation
- **BREAKING**: Models must now be specified in configuration - no hardcoded fallbacks in Python code
- **Prompt architecture**: Extracted prompts into dedicated modules (`base_prompts.py`, `documentation_prompts.py`, `architecture_prompts.py`)
- **Default quantization**: All configurations now default to 4-bit models for optimal performance
- **Documentation format**: Cleaner output with improved section structure and formatting

### Fixed (v0.4.0)

- **Empty markdown blocks**: Eliminated spurious empty code blocks in generated documentation
- **Code block formatting**: Proper closure of all code blocks (Python, bash, etc.)
- **Template structure**: Removed redundant sections causing formatting issues
- **Prompt language**: Replaced aggressive "CRITICAL/FORBIDDEN" language with clear, concise instructions optimized for DeepSeek models

### Removed (v0.4.0)

- **Mermaid diagrams**: Complete removal of diagram generation functionality
- **Diagram configuration**: Removed `include_diagrams` options from CLI and config
- **Hardcoded models**: Eliminated hardcoded model paths from Python code
- **Legacy prompt styles**: Removed outdated prompt formatting approaches

### Performance (v0.4.0)

- **Cleaner generation**: Faster processing without diagram generation overhead
- **Better model utilization**: Optimized prompts for DeepSeek-Coder-V2-Lite-Instruct model
- **Reduced complexity**: Simplified codebase with focused functionality

### Documentation (v0.4.0)

- **Sample output**: Fresh examples of generated documentation quality
- **Configuration guide**: Clear documentation of model configuration requirements
- **Prompt architecture**: Documentation of new modular prompt system

## [0.3.0] - 2025-06-30

### Added (v0.3.0)

- **Offline-friendly configuration**: Default behavior now prioritizes cached models over checking for updates
- **New CLI options**: `--check-updates`, `--force-download`, and `--offline` flags for model management
- **Offline mode settings**: Configuration options for `offline_mode`, `check_for_updates`, `force_download`, and `local_files_only`
- **Enhanced footer system**: Configurable simple and extended footers with `--extended-footer` CLI option
- **Markdown quality improvements**: Automatic post-processing to fix common markdown lint issues
- **Template enhancements**: Improved AI prompts and template formatting for better documentation output
- **Comprehensive test suite**: 70 tests covering all modules with 100% pass rate

### Changed (v0.3.0)

- **BREAKING**: Default behavior now uses cached models without checking for updates (offline-first approach)
- **Model loading**: Respects offline parameters in both MLX and transformers backends
- **Configuration**: Enhanced config.yaml with detailed offline behavior documentation
- **CLI info command**: Now displays offline mode status and model configuration details
- **Template system**: Footer rendering is now separate and configurable

### Fixed (v0.3.0)

- **Code style issues**: Fixed line length and formatting issues in config.py
- **Markdown formatting**: Generated documentation now passes markdownlint with 0 errors
- **Template spacing**: Removed extra blank lines and markdown code block wrappers
- **Test compatibility**: Updated tests to handle new footer functionality

### Performance (v0.3.0)

- **Reduced API calls**: Avoids unnecessary HuggingFace API requests in offline mode
- **Faster startup**: Uses cached models by default, reducing initialization time
- **Bandwidth conservation**: Only downloads models when explicitly requested or not cached

### Documentation (v0.3.0)

- **Offline behavior**: Comprehensive documentation of offline-first configuration
- **CLI examples**: Added examples for new offline-related command options
- **Configuration guide**: Detailed explanation of all offline mode settings

## [0.2.0] - 2025-06-29

### Added (v0.2.0)

- **Complete migration to DeepSeek-Coder-V2-Lite**: Replaced MMaDA with state-of-the-art DeepSeek models
- **Platform-aware optimization**: Automatic detection and optimization for macOS (MLX) and Linux/Windows (Transformers)
- **Intelligent caching system**: Separate output and model caches for optimal performance
- **Multi-language support**: Support for 22+ programming languages including Python, JavaScript, TypeScript, C++, Java, Go, Rust, and more
- **Comprehensive CLI**: Full command-line interface with generate, test, info, and cache commands
- **Template system**: Jinja2-based templating with customizable documentation formats
- **Configuration management**: YAML-based configuration with environment variable overrides

### Changed (v0.2.0)

- **Model backend**: Complete rewrite using DeepSeek-Coder-V2-Lite models
- **Architecture**: Modular design with separate concerns for models, generation, caching, and templates
- **Performance**: Significant performance improvements with platform-specific optimizations
- **Output quality**: Enhanced documentation generation with better structure and formatting

### Performance (v0.2.0)

- **macOS (MLX)**: 6-10s model loading, 17-28s per file generation
- **Linux/Windows**: 60-120s model loading (first run), 30-60s per file generation
- **Memory usage**: 4-6GB on macOS, 6-16GB on other platforms
- **Cache efficiency**: Instant results for unchanged files

## [0.1.0] - 2025-06-26

### Added (v0.1.0)

- **Initial implementation**: Basic documentation generation using MMaDA model
- **Core functionality**: File and directory processing capabilities
- **Basic CLI**: Simple command-line interface for documentation generation

### Features

- MMaDA model integration for code analysis
- Basic template system
- Simple caching mechanism
- Python code analysis

---

## Migration Guide

### From v0.3.0 to v0.4.0

**Configuration Changes:**

- Mermaid diagram functionality has been completely removed. Remove any `include_diagrams` settings from your configuration.
- Models must now be specified in configuration files. The system will error if no model is configured.

**CLI Changes:**

- Removed `--diagrams` and `--no-diagrams` flags
- Removed `--prompt-chaining` functionality
- Cleaner, more focused CLI interface

**Behavior Changes:**

- Documentation generation is now faster and more reliable
- Output format is cleaner with better markdown compliance
- No more diagram-related post-processing overhead

**Migration Steps:**

1. Update configuration files to ensure models are properly specified
2. Remove any diagram-related configuration options
3. Clear cache if experiencing issues: `docgenai cache clear`
4. Regenerate documentation to see improved output quality

### From v0.2.0 to v0.3.0

**Configuration Changes:**

- The application now defaults to offline mode. To enable online model checking, set:

  ```yaml
  model:
    offline_mode: false
    check_for_updates: true
  ```

**CLI Changes:**

- Use `--check-updates` flag to check for model updates
- Use `--force-download` to re-download models
- Use `--offline` to force offline mode
- Use `--extended-footer` for detailed footer information

**Behavior Changes:**

- Models are no longer checked for updates by default
- First-time users will need internet connection to download models
- Subsequent runs work completely offline

### From v0.1.0 to v0.2.0

**Breaking Changes:**

- Complete rewrite of the codebase
- New configuration format (YAML-based)
- Different CLI commands and options
- New model backend (DeepSeek instead of MMaDA)

**Migration Steps:**

1. Update configuration to new YAML format
2. Clear old cache directories
3. Update CLI commands to new format
4. Test with new model backend

---

## Support

For issues and questions:

- Check the [README.md](README.md) for usage examples
- Review [docs/developer.md](docs/developer.md) for development information
- Report bugs via GitHub issues
