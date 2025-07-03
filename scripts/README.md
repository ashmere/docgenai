# DocGenAI Scripts

This directory contains utility scripts for working with DocGenAI.

## regenerate_all_docs.py

A comprehensive script that generates documentation using all available chain strategies and documentation types for any source directory.

### Features

- **Complete Coverage**: Tests all 5 chain strategies (simple, enhanced, architecture, multi_file, codebase) with all 3 documentation types (user, developer, both)
- **Detailed Timing**: Captures precise timing for each generation with comprehensive performance analysis
- **Verbose Output**: Real-time progress updates with timestamps and detailed logging
- **Automatic File Selection**: Intelligently selects appropriate test files for single-file strategies
- **Output Analysis**: Analyzes generated files including size, line count, and structure
- **JSON Results**: Saves detailed results to JSON for further analysis
- **Error Handling**: Robust error handling with timeout protection (30 minutes per generation)
- **Cache Bypass**: Uses `--no-output-cache` to ensure fresh generation every time
- **Dry Run Mode**: Preview what would be generated without actually running the generations

### Usage

```bash
# Generate docs for src directory using default output location
python scripts/regenerate_all_docs.py src

# Generate docs with custom output directory
python scripts/regenerate_all_docs.py src my_analysis_output

# Generate docs for any project directory
python scripts/regenerate_all_docs.py /path/to/my/project custom_output

# Run in quiet mode (less verbose output)
python scripts/regenerate_all_docs.py src analysis_output --quiet

# Preview what would be generated without actually running (dry-run)
python scripts/regenerate_all_docs.py src --dry-run
```

### What It Does

1. **Analyzes Source Directory**: Scans for Python files and subdirectories
2. **Selects Test Files**: Picks appropriately-sized files for single-file strategy testing
3. **Runs All Combinations**: Executes 15 total combinations (5 strategies × 3 doc types)
4. **Captures Metrics**: Records timing, success/failure, output file details
5. **Generates Summary**: Provides comprehensive performance and output analysis
6. **Saves Results**: Creates JSON file with all detailed results for future reference

### Output Structure

```text
output_directory/
├── simple/
│   ├── user/
│   ├── developer/
│   └── both/
├── enhanced/
│   ├── user/
│   ├── developer/
│   └── both/
├── architecture/
│   ├── user/
│   ├── developer/
│   └── both/
├── multi_file/
│   ├── user/
│   ├── developer/
│   └── both/
├── codebase/
│   ├── user/
│   ├── developer/
│   └── both/
└── generation_results.json
```

### Performance Insights

The script provides detailed performance analysis including:

- Total generation time and success rate
- Average, fastest, and slowest generation times
- Strategy-specific performance breakdown
- Output file statistics (count, size, lines)
- Detailed per-generation results in JSON format

### Example Output

```text
[14:30:15] 🎯 Starting comprehensive documentation generation
[14:30:15] 📁 Source: src
[14:30:15] 📁 Output: sample_output
[14:30:15] 🕐 Started: 2024-01-15 14:30:15
================================================================================

[14:30:16] 🔗 Strategy: Simple - Single-step documentation generation
[14:30:16] 📄 Selected test file for single-file strategies: src/docgenai/core.py
[14:30:16] 📊 Test file size: 15,234 bytes
[14:30:16] 🚀 Starting: simple strategy, user documentation
[14:30:16] 📝 Command: python -m docgenai.cli generate src/docgenai/core.py --output-dir sample_output/simple/user --chain --chain-strategy simple --doc-type user --no-output-cache
[14:31:41] ✅ Completed in 85.13 seconds
[14:31:41] 📊 Generated 1 files, 10,550 bytes, 238 lines
...
```

### Requirements

- Python 3.8+
- DocGenAI package installed and accessible via `python -m docgenai.cli`
- Source directory with Python files for analysis

This script is perfect for:

- **Performance benchmarking** across different strategies
- **Quality comparison** between documentation types
- **Regression testing** to ensure all strategies work correctly
- **Strategy evaluation** for new projects or codebases
