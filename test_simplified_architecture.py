#!/usr/bin/env python3
"""
Test script for the simplified DocGenAI architecture.

This script tests the new simplified approach with smart file selection,
intelligent chunking, and high-quality prompts.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.simple_core import generate_documentation_simplified

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_simplified_architecture():
    """Test the simplified architecture on our own codebase."""
    logger.info("🧪 Testing Simplified DocGenAI Architecture")

    # Test on our own codebase (smaller subset)
    codebase_path = "src/docgenai"
    output_dir = "test_output/simplified"

    logger.info(f"📂 Testing on: {codebase_path}")
    logger.info(f"📁 Output directory: {output_dir}")

    try:
        # Load configuration
        config = load_config()

        # Override some settings for testing
        config["file_selection"] = {
            "max_files": 10,  # Limit files for testing
            "max_file_size": 5000,
            "include_patterns": ["*.py"],
            "exclude_patterns": ["*/__pycache__/*", "*/test_*"],
        }

        config["chunking"] = {
            "max_chunk_tokens": 8000,  # Smaller chunks for testing
            "safety_margin": 0.75,
            "signature_threshold": 3000,
        }

        config["chains"] = {
            "enable_refinement": False,  # Disable for faster testing
            "enable_synthesis": True,
        }

        logger.info("⚙️ Configuration loaded and customized for testing")

        # Generate documentation
        result = generate_documentation_simplified(
            codebase_path=codebase_path, output_dir=output_dir, config=config
        )

        # Check results
        if result["success"]:
            logger.info("✅ Documentation generation successful!")
            logger.info(f"📊 Files analyzed: {result['files_analyzed']}")
            logger.info(f"📦 Chunks created: {result['chunks_created']}")
            logger.info(f"⏱️ Generation time: {result['generation_time']:.2f}s")
            logger.info(f"📄 Output saved to: {result['output_path']}")

            # Check if output file exists and has content
            output_path = Path(result["output_path"])
            if output_path.exists():
                file_size = output_path.stat().st_size
                logger.info(f"📏 Output file size: {file_size:,} bytes")

                if file_size > 1000:  # At least 1KB of content
                    logger.info(
                        "🎉 Test PASSED - Documentation generated successfully!"
                    )
                    return True
                else:
                    logger.error("❌ Test FAILED - Output file too small")
                    return False
            else:
                logger.error("❌ Test FAILED - Output file not created")
                return False
        else:
            logger.error(f"❌ Test FAILED - {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Test FAILED with exception: {e}")
        return False


def test_file_selector():
    """Test the SmartFileSelector component."""
    logger.info("🔍 Testing SmartFileSelector")

    try:
        from docgenai.file_selector import SmartFileSelector

        config = {
            "file_selection": {
                "max_files": 10,
                "include_patterns": ["*.py"],
                "exclude_patterns": ["*/__pycache__/*"],
            }
        }

        selector = SmartFileSelector(config)
        files = selector.select_important_files(Path("src/docgenai"))

        logger.info(f"📁 Selected {len(files)} files")
        for file_path in files[:5]:  # Show first 5
            logger.info(f"  - {file_path.name}")

        if len(files) > 0:
            logger.info("✅ SmartFileSelector test PASSED")
            return True
        else:
            logger.error("❌ SmartFileSelector test FAILED - No files selected")
            return False

    except Exception as e:
        logger.error(f"❌ SmartFileSelector test FAILED: {e}")
        return False


def test_chunker():
    """Test the IntelligentChunker component."""
    logger.info("📦 Testing IntelligentChunker")

    try:
        from docgenai.chunker import IntelligentChunker
        from docgenai.config import load_config
        from docgenai.models import create_model

        config = load_config()
        config["chunking"] = {"max_chunk_tokens": 5000, "safety_margin": 0.75}

        # Create a mock model for testing
        class MockModel:
            def get_context_limit(self):
                return 8000

            def estimate_tokens(self, text):
                return len(text) // 3

        model = MockModel()
        chunker = IntelligentChunker(config, model)

        # Test with a few files
        test_files = list(Path("src/docgenai").glob("*.py"))[:3]
        chunks = chunker.chunk_files(test_files)

        logger.info(f"📦 Created {len(chunks)} chunks from {len(test_files)} files")
        for i, chunk in enumerate(chunks):
            logger.info(
                f"  Chunk {i+1}: {len(chunk.files)} files, "
                f"{chunk.estimated_tokens} tokens"
            )

        if len(chunks) > 0:
            logger.info("✅ IntelligentChunker test PASSED")
            return True
        else:
            logger.error("❌ IntelligentChunker test FAILED - No chunks created")
            return False

    except Exception as e:
        logger.error(f"❌ IntelligentChunker test FAILED: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("🚀 Starting Simplified Architecture Tests")

    tests = [
        ("SmartFileSelector", test_file_selector),
        ("IntelligentChunker", test_chunker),
        ("Full Pipeline", test_simplified_architecture),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*50}")

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        logger.info("🎉 All tests PASSED! Simplified architecture is working!")
        return 0
    else:
        logger.error("❌ Some tests FAILED. Check the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
