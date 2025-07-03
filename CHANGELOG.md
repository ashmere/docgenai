# Changelog

All notable changes to DocGenAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2025-07-03

### Added

- **Configurable Metadata Generation**: Flexible metadata handling with three modes
  - `none`: Generate clean documentation without metadata
  - `footer`: Include metadata as footer section in documentation file (default)
  - `file`: Save metadata as separate `.metadata.md` file alongside documentation
  - CLI support with `--metadata-mode` option to override configuration
  - Configuration support in `config.yaml` with `output.metadata_mode` setting
  - Comprehensive metadata includes file analysis details, generation timestamps, model info, and platform details
- **Enhanced Markdown Formatting System**: Consolidated formatting rules for consistent output
  - Single source of truth for markdown formatting rules in `BasePromptBuilder`
  - Eliminated duplicate formatting rules across different prompt modules
  - Strengthened formatting instructions to prevent AI model wrapper issues
  - Automatic detection and prevention of ```text code block wrapping
  - Improved prompt engineering with prominent formatting requirements
- **Modular Architecture Prompt System**: Refactored architecture prompts for better maintainability
  - Created `ArchitecturePromptBuilder` class for consistent prompt generation
  - Maintained backward compatibility with existing string template approach
  - Centralized formatting rules reference across all prompt types
  - Enhanced prompt clarity and AI model compliance

### Changed

- **Prompt Engineering**: Significantly improved AI model output quality
  - Moved formatting rules to beginning of prompts for better AI attention
  - Added critical warnings with visual emphasis (⚠️) to prevent common issues
  - Strengthened instructions to prevent entire response wrapping in code blocks
  - Enhanced formatting rule specificity and clarity
- **Code Organization**: Better separation of concerns in prompt system
  - Consolidated formatting rules in `BasePromptBuilder`
  - Removed duplicate code across `ChainBuilder` and other prompt modules
  - Improved maintainability with centralized formatting standards
- **Default Configuration**: Updated default metadata mode to "footer" for backward compatibility

### Fixed

- **Critical Documentation Formatting Bug**: Resolved AI model wrapping entire output in ```text blocks
  - Fixed architecture prompts that were generating improperly formatted documentation
  - Eliminated ```text wrapper issues that made documentation display as code instead of rendered markdown
  - Improved prompt instructions to ensure clean markdown output
- **Function Reference Error**: Fixed `'function' object has no attribute 'format'` error
  - Corrected architecture prompt backward compatibility implementation
  - Maintained proper string template format with `{file_contents}` placeholders
  - Ensured all prompt constants are properly formatted string templates
- **Markdown Quality Issues**: Comprehensive formatting improvements
  - Eliminated spurious empty code blocks in generated documentation
  - Fixed inconsistent formatting across different prompt types
  - Improved overall documentation readability and markdown compliance

### Technical Improvements

- **Comprehensive Testing**: All metadata modes thoroughly tested and validated
  - Verified `none` mode generates clean documentation without metadata
  - Confirmed `footer` mode appends metadata to documentation files
  - Validated `file` mode creates separate `.metadata.md` files
  - Tested CLI override functionality with all three modes
- **Backward Compatibility**: All existing functionality preserved
  - Default "footer" mode maintains existing behavior
  - Configuration-based overrides work seamlessly
  - CLI parameters properly override configuration settings
- **Code Quality**: Enhanced error handling and validation
  - Better error messages for configuration issues
  - Improved validation of metadata mode parameters
  - Robust fallback handling for missing configuration

### Performance

- **Improved Generation Speed**: Eliminated formatting post-processing overhead
  - Better AI model compliance reduces need for output corrections
  - Cleaner prompts result in more consistent first-pass output quality
  - Reduced processing time through better prompt engineering

### Documentation

- **Comprehensive README Updates**: Added detailed metadata configuration documentation
  - Complete usage examples for all three metadata modes
  - Configuration examples and best practices
  - Use case matrix for optimal mode selection
  - Integration examples with other DocGenAI features

### Previous Releases

### Added

- **Comprehensive Chain Strategy Testing**: Extensive validation of all prompt chaining strategies
  - Generated sample documentation using all 5 chain strategies (simple, enhanced, architecture, multi_file, codebase)
  - Tested across all 3 documentation types (user, developer, both) for comprehensive coverage
  - Performance benchmarking and quality analysis across different strategies
  - Created detailed comparison analysis with recommendations for strategy selection
  - Generated 18 sample documentation files showcasing different approaches
- **Multi-File Analysis System**: Intelligent analysis of related files together for better documentation
  - Automatic file grouping by directory and relationships
  - Cross-file dependency analysis and architectural insights
  - Single-group and multi-group analysis with synthesis capabilities
  - Integration with existing chaining system for enhanced quality
  - Support for large codebases with intelligent splitting and synthesis
  - CLI support with `--multi-file` flag and configuration options
- **Project Type Support**: Tailored documentation generation for different project types
  - `microservice`: Focus on service boundaries, API contracts, deployment
  - `library`: Emphasis on public APIs, usage patterns, integration guides
  - `application`: User workflows, configuration, operations manual
  - `framework`: Extension points, patterns, architecture guides
  - CLI support with `--project-type` option
- **Automatic Index Generation**: Always-generated `index.md` files for output directories
  - File listings with links to all generated documentation
  - Statistics and metadata about the documentation set
  - Timestamp and generation information
  - Integrated into both single-file and multi-file workflows
- **Enhanced Markdown Quality**: Comprehensive post-processing for lint-free documentation
  - Automatic fixing of MD012 (multiple blank lines), MD031 (fenced code blocks), MD032 (list spacing)
  - MD047 (single trailing newline) and MD050 (strong style consistency)
  - Intelligent processing order to handle interactions between fixes
  - Backward compatibility with fallback to legacy processing
- **Improved Prompt Engineering**: Fixed AI model wrapping issues in chaining system
  - Added proper formatting instructions to all multi-file analysis prompts
  - Prevents AI from wrapping output in ```markdown code blocks
  - Consistent formatting rules across all prompt types (developer, user, codebase)
  - Enhanced instruction clarity for better AI compliance
- **Strategy Analysis Documentation**: Comprehensive analysis and comparison documents
  - `COMPREHENSIVE_ANALYSIS.md`: Detailed performance metrics, quality analysis, and strategy recommendations
  - `GENERATION_SUMMARY.md`: Concise overview of findings and strategic recommendations
  - Performance benchmarks showing Enhanced strategy produces most detailed documentation (12,761 chars)
  - Quality rankings and use case matrix for optimal strategy selection
  - Technical observations on multi-file analysis effectiveness

### Changed

- **Multi-File Integration**: Seamless integration of multi-file analysis with existing systems
  - Enhanced `DocumentationGenerator` with multi-file capabilities
  - Updated CLI with multi-file options while maintaining backward compatibility
  - Configuration support for multi-file analysis parameters
  - Intelligent file grouping with configurable group sizes
- **Chaining System Enhancement**: Improved prompt templates for better output quality
  - Updated all chaining prompts with proper markdown formatting instructions
  - Enhanced codebase analysis chain with multi-step synthesis
  - Better error handling and dependency resolution in multi-file contexts
- **Output Organization**: Better structure for generated documentation
  - Automatic index generation for all output directories
  - Improved file naming and organization for multi-file outputs
  - Enhanced metadata and timestamp tracking

### Fixed

- **Chain Strategy Selection**: Fixed hardcoded strategy override in multi-group analysis
  - Corrected logic that was forcing "codebase" strategy regardless of CLI parameter
  - Now properly respects user-specified chain strategy for all scenarios
  - Maintains appropriate fallbacks for incompatible strategy/scope combinations
- **Markdown Wrapper Issues**: Resolved AI models wrapping content in ```markdown blocks
  - Fixed prompts in `ChainBuilder` multi-file analysis chains
  - Added proper formatting instructions to prevent wrapper generation
  - Consistent behavior across all documentation generation types
- **Post-Processing Quality**: Comprehensive markdown lint issue resolution
  - Fixed MD012 (multiple consecutive blank lines) through intelligent processing
  - Resolved MD031 (fenced code block spacing) and MD032 (list spacing) issues
  - Proper handling of processing order to prevent re-introduction of issues
- **Index Generation**: Reliable index.md creation for all documentation sets
  - Fixed integration with multi-file workflows
  - Proper error handling for index generation failures
  - Consistent format and content across different generation modes

### Technical Improvements

- **Code Quality**: Enhanced prompt engineering and output processing
  - Modular post-processing system with individual fix functions
  - Better separation of concerns in multi-file analysis
  - Improved error handling and logging throughout the system
- **Configuration**: Extended configuration options for new features
  - Multi-file analysis parameters (max files per group, synthesis thresholds)
  - Project type configurations and templates
  - Post-processing options and markdown linting integration
- **Testing**: Comprehensive validation of new features
  - Multi-file analysis workflow testing
  - Prompt formatting verification
  - Post-processing quality assurance

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
