#!/usr/bin/env python3
"""
DocGenAI Comprehensive Documentation Generation Script

This script generates documentation using all available chain strategies and documentation types
for a given source directory, with detailed timing analysis and verbose output.

Usage:
    python scripts/regenerate_all_docs.py <source_directory> [output_base_directory]

Example:
    python scripts/regenerate_all_docs.py src sample_output
    python scripts/regenerate_all_docs.py /path/to/my/project analysis_output
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration for all test combinations
CHAIN_STRATEGIES = {
    "simple": {
        "name": "Simple",
        "description": "Single-step documentation generation",
        "scope": "single_file",
        "test_file": None,  # Will be set dynamically
    },
    "enhanced": {
        "name": "Enhanced",
        "description": "Multi-step with analysis and enhancement",
        "scope": "single_file",
        "test_file": None,  # Will be set dynamically
    },
    "architecture": {
        "name": "Architecture",
        "description": "Multi-step with architectural focus",
        "scope": "single_file",
        "test_file": None,  # Will be set dynamically
    },
    "multi_file": {
        "name": "Multi-File",
        "description": "Single group multi-file analysis",
        "scope": "directory",
        "test_dir": None,  # Will be set dynamically
    },
    "codebase": {
        "name": "Codebase",
        "description": "Multiple group synthesis",
        "scope": "directory",
        "test_dir": None,  # Will be set dynamically
    },
}

DOC_TYPES = ["user", "developer", "both"]


class DocumentationGenerator:
    """Handles the generation of documentation across all strategies and types."""

    def __init__(self, source_dir: Path, output_base: Path, verbose: bool = True):
        self.source_dir = Path(source_dir)
        self.output_base = Path(output_base)
        self.verbose = verbose
        self.results = []
        self.start_time = datetime.now()

        # Ensure source directory exists
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {self.source_dir}")

        # Create output base directory
        self.output_base.mkdir(parents=True, exist_ok=True)

        # Find test files for single-file strategies
        self._find_test_files()

    def _find_test_files(self):
        """Find suitable test files for single-file strategies."""
        python_files = list(self.source_dir.rglob("*.py"))

        if not python_files:
            self._log("⚠️  No Python files found for single-file testing")
            return

        # Sort by size and pick a medium-sized file for testing
        python_files.sort(key=lambda f: f.stat().st_size)

        # Pick a file that's not too small or too large
        suitable_files = [f for f in python_files if 5000 < f.stat().st_size < 20000]

        if suitable_files:
            test_file = suitable_files[len(suitable_files) // 2]  # Pick middle file
        else:
            test_file = python_files[len(python_files) // 2] if python_files else None
        if test_file:
            self._log(f"📄 Selected test file for single-file strategies: {test_file}")
            self._log(f"📊 Test file size: {test_file.stat().st_size:,} bytes")

            # Update strategy configurations
            for strategy in ["simple", "enhanced", "architecture"]:
                CHAIN_STRATEGIES[strategy]["test_file"] = test_file
        else:
            self._log("⚠️  No suitable test file found for single-file strategies")

        # Set directory paths for multi-file strategies
        CHAIN_STRATEGIES["multi_file"]["test_dir"] = self.source_dir
        CHAIN_STRATEGIES["codebase"]["test_dir"] = self.source_dir

    def _log(self, message: str):
        """Log a message with timestamp if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def _run_command(self, cmd: list, strategy: str, doc_type: str) -> dict:
        """Run a documentation generation command and capture timing/output."""
        self._log(f"🚀 Starting: {strategy} strategy, {doc_type} documentation")
        self._log(f"📝 Command: {' '.join(cmd)}")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800  # 30 minute timeout
            )
            end_time = time.time()
            duration = end_time - start_time

            success = result.returncode == 0

            if success:
                self._log(f"✅ Completed in {duration:.2f} seconds")
            else:
                self._log(f"❌ Failed after {duration:.2f} seconds")
                self._log(f"📄 Error output: {result.stderr[:500]}...")

            return {
                "strategy": strategy,
                "doc_type": doc_type,
                "success": success,
                "duration": duration,
                "command": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            self._log(f"⏰ Timeout after {duration:.2f} seconds")

            return {
                "strategy": strategy,
                "doc_type": doc_type,
                "success": False,
                "duration": duration,
                "command": " ".join(cmd),
                "stdout": "",
                "stderr": "Command timed out after 30 minutes",
                "return_code": -1,
            }

    def _get_output_files(self, output_dir: Path) -> list:
        """Get list of generated output files with their sizes."""
        if not output_dir.exists():
            return []

        files = []
        for md_file in output_dir.rglob("*.md"):
            try:
                size = md_file.stat().st_size
                with open(md_file, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
                files.append(
                    {
                        "path": str(md_file.relative_to(output_dir)),
                        "size_bytes": size,
                        "size_chars": size,  # Approximation
                        "lines": lines,
                    }
                )
            except Exception as e:
                self._log(f"⚠️  Error reading {md_file}: {e}")

        return files

    def generate_single_file_strategy(self, strategy: str, doc_type: str):
        """Generate documentation for single-file strategies."""
        config = CHAIN_STRATEGIES[strategy]
        test_file = config.get("test_file")

        if not test_file:
            self._log(f"⚠️  Skipping {strategy} - no test file available")
            return None

        output_dir = self.output_base / strategy / doc_type
        cmd = [
            "python",
            "-m",
            "docgenai.cli",
            "generate",
            str(test_file),
            "--output-dir",
            str(output_dir),
            "--chain",
            "--chain-strategy",
            strategy,
            "--doc-type",
            doc_type,
            "--no-output-cache",
        ]

        result = self._run_command(cmd, strategy, doc_type)

        # Add file analysis
        if result["success"]:
            result["output_files"] = self._get_output_files(output_dir)
            total_size = sum(f["size_bytes"] for f in result["output_files"])
            total_lines = sum(f["lines"] for f in result["output_files"])
            result["total_output_size"] = total_size
            result["total_output_lines"] = total_lines
            self._log(
                f"📊 Generated {len(result['output_files'])} files, {total_size:,} bytes, {total_lines} lines"
            )

        return result

    def generate_multi_file_strategy(self, strategy: str, doc_type: str):
        """Generate documentation for multi-file strategies."""
        config = CHAIN_STRATEGIES[strategy]
        test_dir = config.get("test_dir")

        if not test_dir:
            self._log(f"⚠️  Skipping {strategy} - no test directory available")
            return None

        output_dir = self.output_base / strategy / doc_type
        # For multi_file strategy, use a subdirectory if available to create single groups
        source_path = test_dir
        if strategy == "multi_file":
            # Try to find a subdirectory for single-group analysis
            subdirs = [
                d
                for d in test_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            if subdirs:
                # Pick the largest subdirectory by file count
                subdir_files = [(d, len(list(d.rglob("*.py")))) for d in subdirs]
                subdir_files.sort(key=lambda x: x[1], reverse=True)
                if subdir_files and subdir_files[0][1] > 0:
                    source_path = subdir_files[0][0]
                    self._log(
                        f"📁 Using subdirectory for multi_file strategy: {source_path}"
                    )

        cmd = [
            "python",
            "-m",
            "docgenai.cli",
            "generate",
            str(source_path),
            "--output-dir",
            str(output_dir),
            "--chain",
            "--chain-strategy",
            strategy,
            "--doc-type",
            doc_type,
            "--no-output-cache",
        ]

        result = self._run_command(cmd, strategy, doc_type)

        # Add file analysis
        if result["success"]:
            result["output_files"] = self._get_output_files(output_dir)
            total_size = sum(f["size_bytes"] for f in result["output_files"])
            total_lines = sum(f["lines"] for f in result["output_files"])
            result["total_output_size"] = total_size
            result["total_output_lines"] = total_lines
            self._log(
                f"📊 Generated {len(result['output_files'])} files, {total_size:,} bytes, {total_lines} lines"
            )

        return result

    def generate_all(self):
        """Generate documentation for all strategy and doc type combinations."""
        self._log("🎯 Starting comprehensive documentation generation")
        self._log(f"📁 Source: {self.source_dir}")
        self._log(f"📁 Output: {self.output_base}")
        self._log(f"🕐 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("=" * 80)

        total_combinations = 0
        successful_combinations = 0

        # Generate for each strategy and doc type combination
        for strategy, config in CHAIN_STRATEGIES.items():
            self._log(f"\n🔗 Strategy: {config['name']} - {config['description']}")

            for doc_type in DOC_TYPES:
                total_combinations += 1

                if config["scope"] == "single_file":
                    result = self.generate_single_file_strategy(strategy, doc_type)
                else:
                    result = self.generate_multi_file_strategy(strategy, doc_type)

                if result:
                    self.results.append(result)
                    if result["success"]:
                        successful_combinations += 1

                # Small delay between generations
                time.sleep(1)

        # Generate summary
        self._generate_summary(total_combinations, successful_combinations)

    def _generate_summary(self, total: int, successful: int):
        """Generate a comprehensive summary of all generation results."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        self._log("\n" + "=" * 80)
        self._log("📊 GENERATION SUMMARY")
        self._log("=" * 80)
        self._log(f"🕐 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"🕐 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(
            f"⏱️  Total Duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)"
        )
        self._log(f"✅ Successful: {successful}/{total} combinations")
        self._log(f"❌ Failed: {total - successful}/{total} combinations")

        # Performance summary
        if self.results:
            successful_results = [r for r in self.results if r["success"]]
            if successful_results:
                durations = [r["duration"] for r in successful_results]
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)

                self._log(f"\n⚡ Performance Summary:")
                self._log(f"   Average: {avg_duration:.2f}s")
                self._log(f"   Fastest: {min_duration:.2f}s")
                self._log(f"   Slowest: {max_duration:.2f}s")
        # Strategy performance breakdown
        self._log(f"\n📈 Strategy Performance:")
        strategy_stats = {}
        for result in self.results:
            if result["success"]:
                strategy = result["strategy"]
                if strategy not in strategy_stats:
                    strategy_stats[strategy] = []
                strategy_stats[strategy].append(result["duration"])

        for strategy, durations in strategy_stats.items():
            avg_duration = sum(durations) / len(durations)
            self._log(
                f"   {strategy:12}: {avg_duration:6.2f}s avg ({len(durations)} runs)"
            )

        # Output file summary
        self._log(f"\n📄 Output Summary:")
        total_files = 0
        total_size = 0
        total_lines = 0

        for result in self.results:
            if result["success"] and "output_files" in result:
                total_files += len(result["output_files"])
                total_size += result.get("total_output_size", 0)
                total_lines += result.get("total_output_lines", 0)

        self._log(f"   Files Generated: {total_files}")
        self._log(f"   Total Size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        self._log(f"   Total Lines: {total_lines:,}")
        # Save detailed results to JSON
        results_file = self.output_base / "generation_results.json"
        summary_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "total_combinations": total,
            "successful_combinations": successful,
            "source_directory": str(self.source_dir),
            "output_directory": str(self.output_base),
            "results": self.results,
        }

        with open(results_file, "w") as f:
            json.dump(summary_data, f, indent=2, default=str)

        self._log(f"\n💾 Detailed results saved to: {results_file}")
        self._log("🎉 Generation complete!")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate documentation using all chain strategies and doc types",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/regenerate_all_docs.py src
  python scripts/regenerate_all_docs.py src analysis_output
  python scripts/regenerate_all_docs.py /path/to/project custom_output --quiet
        """,
    )
    parser.add_argument(
        "source_directory", help="Source directory to generate documentation for"
    )

    parser.add_argument(
        "output_directory",
        nargs="?",
        default="sample_output",
        help="Base output directory (default: sample_output)",
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Reduce verbose output"
    )

    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be generated without actually running",
    )

    args = parser.parse_args()

    try:
        generator = DocumentationGenerator(
            source_dir=args.source_directory,
            output_base=args.output_directory,
            verbose=not args.quiet,
        )

        if args.dry_run:
            generator._log("🔍 DRY RUN MODE - Showing what would be generated:")
            generator._log(f"📁 Source: {generator.source_dir}")
            generator._log(f"📁 Output: {generator.output_base}")
            generator._log("\n📋 Planned generations:")

            count = 0
            for strategy, config in CHAIN_STRATEGIES.items():
                generator._log(f"\n🔗 {config['name']} Strategy ({config['scope']}):")
                if config["scope"] == "single_file":
                    test_file = config.get("test_file")
                    if test_file:
                        generator._log(f"   📄 Test file: {test_file}")
                        generator._log(
                            f"   📊 File size: {test_file.stat().st_size:,} bytes"
                        )
                    else:
                        generator._log(f"   ⚠️  No suitable test file found")
                else:
                    test_dir = config.get("test_dir")
                    if test_dir:
                        py_files = len(list(test_dir.rglob("*.py")))
                        generator._log(f"   📁 Test directory: {test_dir}")
                        generator._log(f"   📊 Python files: {py_files}")

                for doc_type in DOC_TYPES:
                    if (
                        config["scope"] == "single_file" and config.get("test_file")
                    ) or (config["scope"] == "directory" and config.get("test_dir")):
                        count += 1
                        output_dir = generator.output_base / strategy / doc_type
                        generator._log(f"   📝 {doc_type:9} → {output_dir}")

            generator._log(f"\n📊 Total planned generations: {count}")
            generator._log("🎯 Run without --dry-run to execute all generations")
        else:
            generator.generate_all()

    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
