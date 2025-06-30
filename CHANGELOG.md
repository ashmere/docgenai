# Changelog

All notable changes to DocGenAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-12-30

### Added

- **Offline-friendly configuration**: Default behavior now prioritizes cached models over checking for updates
- **New CLI options**: `--check-updates`, `--force-download`, and `--offline` flags for model management
- **Offline mode settings**: Configuration options for `offline_mode`, `check_for_updates`, `force_download`, and `local_files_only`
- **Enhanced footer system**: Configurable simple and extended footers with `--extended-footer` CLI option
- **Markdown quality improvements**: Automatic post-processing to fix common markdown lint issues
- **Template enhancements**: Improved AI prompts and template formatting for better documentation output
- **Comprehensive test suite**: 70 tests covering all modules with 100% pass rate

### Changed

- **BREAKING**: Default behavior now uses cached models without checking for updates (offline-first approach)
- **Model loading**: Respects offline parameters in both MLX and transformers backends
- **Configuration**: Enhanced config.yaml with detailed offline behavior documentation
- **CLI info command**: Now displays offline mode status and model configuration details
- **Template system**: Footer rendering is now separate and configurable

### Fixed

- **Code style issues**: Fixed line length and formatting issues in config.py
- **Markdown formatting**: Generated documentation now passes markdownlint with 0 errors
- **Template spacing**: Removed extra blank lines and markdown code block wrappers
- **Test compatibility**: Updated tests to handle new footer functionality

### Performance

- **Reduced API calls**: Avoids unnecessary HuggingFace API requests in offline mode
- **Faster startup**: Uses cached models by default, reducing initialization time
- **Bandwidth conservation**: Only downloads models when explicitly requested or not cached

### Documentation

- **Offline behavior**: Comprehensive documentation of offline-first configuration
- **CLI examples**: Added examples for new offline-related command options
- **Configuration guide**: Detailed explanation of all offline mode settings

## [0.2.0] - 2024-12-29

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

## [0.1.0] - 2024-12-28

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
