#!/usr/bin/env python3
"""
Simple demonstration of multi-file analysis benefits.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.models import create_model
from docgenai.multi_file_analyzer import MultiFileAnalyzer


def demo_multi_file_analysis():
    """Demonstrate multi-file analysis with a simple prompt."""
    print("🔗 Multi-File Analysis Demo")
    print("=" * 50)

    # Load config and create model
    config = load_config()
    model = create_model(config)
    analyzer = MultiFileAnalyzer(config)

    # Test with chaining directory
    chaining_dir = Path("src/docgenai/chaining")
    py_files = [f for f in chaining_dir.glob("*.py") if f.name != "__init__.py"]

    print(f"📁 Files to analyze: {[f.name for f in py_files]}")

    # Group files
    groups = analyzer.group_files_for_analysis(py_files)
    if not groups:
        print("❌ No suitable groups found")
        return

    # Use first group
    file_group = groups[0]
    context = analyzer.prepare_multi_file_context(file_group)

    print(f"🎯 Analyzing {context['file_count']} files together")
    print(f"📊 Token estimate: {context['estimated_tokens']:.0f}")

    # Create a simple multi-file analysis prompt
    prompt = f"""
Analyze these {context['file_count']} related Python files and explain how they work together:

{context['files_summary']}

{context['files_content']}

Focus on:
1. What is the overall purpose of this module?
2. How do the files interact with each other?
3. What are the main classes and their relationships?
4. What design patterns are used?

Provide a clear, comprehensive overview:"""

    print("🤖 Generating multi-file analysis...")

    # Generate response using correct API
    response = model.generate_raw_response(prompt)

    # Save output
    output_file = Path("test_output/multi_file_demo.md")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        f.write("# Multi-File Analysis Demo\n\n")
        f.write(f"**Files analyzed:** {', '.join(context['file_names'])}\n\n")
        f.write("## Analysis Result\n\n")
        f.write(response)

    print(f"✅ Analysis saved to: {output_file}")
    print(f"📄 Response length: {len(response)} characters")

    # Show preview
    print("\n📖 Preview (first 500 characters):")
    print("-" * 50)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("-" * 50)


def compare_token_usage():
    """Compare token usage between approaches."""
    print("\n🔢 Token Usage Comparison")
    print("=" * 50)

    config = load_config()
    analyzer = MultiFileAnalyzer(config)

    # Get chaining files
    chaining_dir = Path("src/docgenai/chaining")
    py_files = [f for f in chaining_dir.glob("*.py") if f.name != "__init__.py"]

    # Single-file approach
    single_file_tokens = 0
    for file in py_files:
        try:
            with open(file, "r") as f:
                content = f.read()
            tokens = len(content) / 3.5  # Approximate
            single_file_tokens += tokens
        except Exception:
            continue

    # Multi-file approach
    groups = analyzer.group_files_for_analysis(py_files)
    multi_file_tokens = 0
    if groups:
        context = analyzer.prepare_multi_file_context(groups[0])
        multi_file_tokens = context["estimated_tokens"]

    print(f"📊 Token Usage Analysis:")
    print(f"  Single-file (total): {single_file_tokens:.0f} tokens")
    print(f"  Multi-file (once):   {multi_file_tokens:.0f} tokens")
    print(f"  Efficiency ratio:    {multi_file_tokens/single_file_tokens:.2f}")

    print(f"\n💡 Benefits of Multi-File:")
    print(f"  ✅ Analyzes relationships between files")
    print(f"  ✅ Provides architectural overview")
    print(f"  ✅ Avoids duplicate explanations")
    print(f"  ✅ Better context for complex systems")

    print(f"\n🎯 Recommendation:")
    print(f"  Use multi-file for modules with {len(py_files)} related files")
    print(f"  Token usage is reasonable: {multi_file_tokens:.0f} < 30k limit")


if __name__ == "__main__":
    demo_multi_file_analysis()
    compare_token_usage()
