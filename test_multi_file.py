#!/usr/bin/env python3
"""
Test script for multi-file analysis with DocGenAI.

This demonstrates how multi-file analysis can provide better documentation
by analyzing related files together rather than individually.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.multi_file_analyzer import MultiFileAnalyzer


def test_multi_file_grouping():
    """Test file grouping logic."""
    print("🧪 Testing Multi-File Analysis")
    print("=" * 50)

    # Load config
    config = load_config()

    # Initialize analyzer
    analyzer = MultiFileAnalyzer(config)

    # Test with src/docgenai files
    src_dir = Path("src/docgenai")
    if not src_dir.exists():
        print("❌ Source directory not found")
        return

    # Get Python files
    py_files = list(src_dir.glob("*.py"))
    if not py_files:
        print("❌ No Python files found")
        return

    print(f"📁 Found {len(py_files)} Python files:")
    for file in py_files:
        print(f"  - {file}")

    # Test grouping
    groups = analyzer.group_files_for_analysis(py_files)

    print(f"\n🎯 Created {len(groups)} file groups:")
    for i, group in enumerate(groups):
        print(f"\nGroup {i+1} ({len(group)} files):")
        for file in group:
            print(f"  - {file.name}")

    # Test context preparation for first group
    if groups:
        print(f"\n📝 Testing context preparation for Group 1...")
        context = analyzer.prepare_multi_file_context(groups[0])

        print(f"📊 Context statistics:")
        print(f"  - Files: {context['file_count']}")
        print(f"  - Estimated tokens: {context['estimated_tokens']:.0f}")
        print(f"  - Content length: {len(context['files_content'])} chars")

        # Show summary
        print(f"\n📋 Files summary:")
        print(context["files_summary"])

        # Check if it fits in context window (32k tokens for DeepSeek-V2-Lite)
        if context["estimated_tokens"] < 30000:
            print(f"✅ Group fits in context window")
        else:
            print(f"⚠️  Group may exceed context window")

    print("\n" + "=" * 50)
    print("✅ Multi-file analysis test completed")


def test_chaining_files():
    """Test with chaining directory files."""
    print("\n🔗 Testing Chaining Directory Analysis")
    print("=" * 50)

    config = load_config()
    analyzer = MultiFileAnalyzer(config)

    # Test with chaining directory
    chaining_dir = Path("src/docgenai/chaining")
    if not chaining_dir.exists():
        print("❌ Chaining directory not found")
        return

    py_files = list(chaining_dir.glob("*.py"))
    print(f"📁 Found {len(py_files)} files in chaining directory:")
    for file in py_files:
        print(f"  - {file}")

    # Should recommend multi-file analysis for related files
    should_use = analyzer.should_use_multi_file_analysis(py_files)
    print(f"\n🤔 Should use multi-file analysis: {should_use}")

    if should_use:
        groups = analyzer.group_files_for_analysis(py_files)
        print(f"📦 Would create {len(groups)} groups")

        for i, group in enumerate(groups):
            context = analyzer.prepare_multi_file_context(group)
            print(
                f"Group {i+1}: {context['file_count']} files, "
                f"{context['estimated_tokens']:.0f} tokens"
            )


if __name__ == "__main__":
    test_multi_file_grouping()
    test_chaining_files()
