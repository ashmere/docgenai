#!/usr/bin/env python3
"""
Comprehensive test for integrated multi-file analysis in DocGenAI.

This script demonstrates the complete multi-file workflow including:
- Single group analysis
- Multiple group analysis with synthesis
- Large codebase handling
- Intelligent file grouping and splitting
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.core import generate_documentation
from docgenai.multi_file_analyzer import MultiFileAnalyzer


def setup_logging():
    """Configure logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("test_integrated_multi_file.log"),
        ],
    )


def test_single_group_analysis():
    """Test multi-file analysis on a single group (chaining module)."""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing single group multi-file analysis...")

    try:
        # Target the chaining module (small, well-defined group)
        target_path = Path("src/docgenai/chaining")
        output_dir = "test_output/single_group"

        # Load config and enable multi-file mode
        config = load_config()
        config["multi_file"] = {
            "enabled": True,
            "max_files_per_group": 6,
        }
        config["chain_strategy"] = "multi_file"

        logger.info(f"📁 Target: {target_path}")
        logger.info(f"💾 Output: {output_dir}")

        # Generate documentation
        result = generate_documentation(
            target_path=target_path,
            output_dir=output_dir,
            config=config,
        )

        # Check results
        if result["success"]:
            logger.info("✅ Single group analysis successful!")
            logger.info(f"📄 Files generated: {len(result['output_files'])}")
            for file in result["output_files"]:
                logger.info(f"  - {file}")

            if "multi_file_stats" in result:
                stats = result["multi_file_stats"]
                logger.info(
                    f"📊 Stats: {stats['total_files']} files, "
                    f"{stats['groups']} groups, "
                    f"synthesis: {stats['synthesis_used']}"
                )
        else:
            logger.error("❌ Single group analysis failed!")
            logger.error(f"Error: {result.get('error', 'Unknown')}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Single group test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_multiple_group_analysis():
    """Test multi-file analysis on entire codebase (multiple groups)."""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing multiple group codebase analysis...")

    try:
        # Target the entire src directory
        target_path = Path("src/docgenai")
        output_dir = "test_output/codebase_analysis"

        # Load config and enable multi-file mode with synthesis
        config = load_config()
        config["multi_file"] = {
            "enabled": True,
            "max_files_per_group": 4,  # Force multiple groups
        }
        config["chain_strategy"] = "codebase"

        logger.info(f"📁 Target: {target_path}")
        logger.info(f"💾 Output: {output_dir}")

        # First, analyze the codebase structure
        analyzer = MultiFileAnalyzer(config)
        structure = analyzer.analyze_codebase_structure(target_path)

        logger.info(f"📊 Codebase structure preview:")
        logger.info(f"  - Total files: {structure['total_files']}")
        logger.info(f"  - Analysis groups: {structure['groups']}")
        logger.info(f"  - Estimated tokens: {structure['estimated_total_tokens']:.0f}")
        logger.info(f"  - Requires synthesis: {structure['requires_synthesis']}")

        # Generate documentation
        result = generate_documentation(
            target_path=target_path,
            output_dir=output_dir,
            config=config,
        )

        # Check results
        if result["success"]:
            logger.info("✅ Multiple group analysis successful!")
            logger.info(f"📄 Files generated: {len(result['output_files'])}")

            # Show main files
            main_files = [
                f for f in result["output_files"] if "codebase_documentation" in f
            ]
            group_files = [f for f in result["output_files"] if "group_" in f]

            logger.info(f"📋 Main documentation: {len(main_files)} files")
            for file in main_files:
                logger.info(f"  - {Path(file).name}")

            logger.info(f"📦 Group documentation: {len(group_files)} files")
            for file in group_files:
                logger.info(f"  - {Path(file).name}")

            if "multi_file_stats" in result:
                stats = result["multi_file_stats"]
                logger.info(
                    f"📊 Stats: {stats['total_files']} files, "
                    f"{stats['groups']} groups, "
                    f"synthesis: {stats['synthesis_used']}"
                )
        else:
            logger.error("❌ Multiple group analysis failed!")
            logger.error(f"Error: {result.get('error', 'Unknown')}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Multiple group test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_large_file_handling():
    """Test handling of large files and edge cases."""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing large file handling...")

    try:
        # Test with very restrictive file size limits
        target_path = Path("src/docgenai")
        output_dir = "test_output/large_file_test"

        # Load config with small file size limits
        config = load_config()
        config["multi_file"] = {
            "enabled": True,
            "max_files_per_group": 3,
        }
        config["chain_strategy"] = "codebase"

        # Create analyzer with small limits to test edge cases
        analyzer = MultiFileAnalyzer(config)
        analyzer.max_file_size_chars = 5000  # Very small limit

        # Analyze structure
        structure = analyzer.analyze_codebase_structure(target_path)

        logger.info(f"📊 Large file test structure:")
        logger.info(f"  - Total files: {structure['total_files']}")
        logger.info(f"  - Suitable files: {structure['suitable_files']}")
        logger.info(f"  - Large files skipped: {len(structure['large_files'])}")
        logger.info(f"  - Groups: {structure['groups']}")

        # Show some large files that were skipped
        if structure["large_files"]:
            logger.info("📄 Large files skipped:")
            for lf in structure["large_files"][:3]:
                logger.info(f"  - {Path(lf['file']).name}: {lf['size']} chars")

        # Test complexity estimation
        complexity = analyzer.estimate_synthesis_complexity(structure)
        logger.info(f"🔬 Estimated complexity: {complexity}")

        logger.info("✅ Large file handling test completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Large file test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_file_grouping_strategies():
    """Test different file grouping strategies."""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing file grouping strategies...")

    try:
        target_path = Path("src/docgenai")

        # Test with different max_files_per_group settings
        test_configs = [
            {"max_files": 2, "description": "Very small groups"},
            {"max_files": 5, "description": "Medium groups"},
            {"max_files": 10, "description": "Large groups"},
        ]

        for test_config in test_configs:
            logger.info(f"🔧 Testing: {test_config['description']}")

            config = load_config()
            config["multi_file"] = {
                "enabled": True,
                "max_files_per_group": test_config["max_files"],
            }

            analyzer = MultiFileAnalyzer(config)
            structure = analyzer.analyze_codebase_structure(target_path)

            logger.info(f"  - Groups: {structure['groups']}")
            logger.info(
                f"  - Avg files per group: "
                f"{structure['suitable_files'] / max(structure['groups'], 1):.1f}"
            )

            # Show group details
            for group_detail in structure["group_details"][:3]:
                logger.info(
                    f"  - Group {group_detail['group_id']}: "
                    f"{group_detail['file_count']} files, "
                    f"{group_detail['estimated_tokens']:.0f} tokens"
                )

        logger.info("✅ File grouping strategies test completed!")
        return True

    except Exception as e:
        logger.error(f"❌ File grouping test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting DocGenAI Multi-File Integration Tests")
    logger.info("=" * 60)

    # Create output directory
    Path("test_output").mkdir(exist_ok=True)

    test_results = []

    # Run tests
    tests = [
        ("Single Group Analysis", test_single_group_analysis),
        ("Multiple Group Analysis", test_multiple_group_analysis),
        ("Large File Handling", test_large_file_handling),
        ("File Grouping Strategies", test_file_grouping_strategies),
    ]

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        logger.info("-" * 40)

        try:
            result = test_func()
            test_results.append((test_name, result))

            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")

        except Exception as e:
            logger.error(f"💥 {test_name}: CRASHED - {e}")
            test_results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Multi-file integration is working!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
