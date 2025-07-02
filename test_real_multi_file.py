#!/usr/bin/env python3
"""
Real multi-file documentation generation test.

Demonstrates the difference between single-file and multi-file analysis.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.chaining.builders import ChainBuilder
from docgenai.config import load_config
from docgenai.models import create_model
from docgenai.multi_file_analyzer import MultiFileAnalyzer


def generate_multi_file_docs():
    """Generate documentation using multi-file analysis."""
    print("🚀 Multi-File Documentation Generation Test")
    print("=" * 60)

    # Load config and create model
    config = load_config()
    model = create_model(config)
    analyzer = MultiFileAnalyzer(config)

    # Test with chaining directory (related files)
    chaining_dir = Path("src/docgenai/chaining")
    py_files = [f for f in chaining_dir.glob("*.py") if f.name != "__init__.py"]

    print(f"📁 Analyzing {len(py_files)} chaining files:")
    for file in py_files:
        print(f"  - {file.name}")

    # Group files for analysis
    groups = analyzer.group_files_for_analysis(py_files)

    if not groups:
        print("❌ No suitable file groups found")
        return

    # Use the first group for demonstration
    file_group = groups[0]
    print(f"\n🎯 Using group with {len(file_group)} files")

    # Prepare multi-file context
    context = analyzer.prepare_multi_file_context(file_group)
    print(f"📊 Context: {context['estimated_tokens']:.0f} tokens")

    # Create multi-file analysis chain
    chain = ChainBuilder.multi_file_analysis_chain()

    print(f"\n🔗 Running multi-file analysis chain...")
    print(f"   Steps: {len(chain.steps)}")

    # Execute the chain with multi-file context
    try:
        from docgenai.chaining.context import ChainContext

        # Create chain context with multi-file data
        chain_context = ChainContext()

        # Add all the multi-file context data
        chain_context.set_variable("files_content", context["files_content"])
        chain_context.set_variable("files_summary", context["files_summary"])
        chain_context.set_variable("file_count", context["file_count"])
        chain_context.set_variable("file_names", context["file_names"])

        print("📝 Executing chain steps...")

        # Execute each step
        for i, step in enumerate(chain.steps):
            print(f"  Step {i+1}: {step.name}")

            # Prepare prompt with current context
            prompt = step.format_prompt(chain_context.get_all_variables())

            # Show prompt preview (first 200 chars)
            prompt_preview = prompt[:200].replace("\n", " ")
            print(f"    Prompt: {prompt_preview}...")

            # Generate response
            response = model.generate(prompt)

            # Store result in context
            chain_context.set_variable(step.name, response)

            # Show response preview
            response_preview = response[:150].replace("\n", " ")
            print(f"    Result: {response_preview}...")
            print()

        # Get final documentation
        final_docs = chain_context.get_variable("comprehensive_documentation")

        # Save to file
        output_file = Path("test_output/multi_file_chaining_docs.md")
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, "w") as f:
            f.write("# Multi-File Analysis: Chaining Module\n\n")
            f.write(f"**Files analyzed:** {', '.join(context['file_names'])}\n\n")
            f.write(f"**Analysis approach:** Multi-file with cross-references\n\n")
            f.write("---\n\n")
            f.write(final_docs)

        print(f"✅ Multi-file documentation saved to: {output_file}")
        print(f"📄 Document length: {len(final_docs)} characters")

        # Show some statistics
        overview = chain_context.get_variable("file_group_overview")
        cross_analysis = chain_context.get_variable("cross_file_analysis")

        print(f"\n📊 Analysis Results:")
        print(f"  - Overview length: {len(overview)} chars")
        print(f"  - Cross-analysis length: {len(cross_analysis)} chars")
        print(f"  - Final docs length: {len(final_docs)} chars")

    except Exception as e:
        print(f"❌ Error during chain execution: {e}")
        import traceback

        traceback.print_exc()


def compare_approaches():
    """Compare single-file vs multi-file approach."""
    print("\n" + "=" * 60)
    print("📊 Single-File vs Multi-File Comparison")
    print("=" * 60)

    print("🔍 Single-File Approach:")
    print("  ✅ Fast and simple")
    print("  ❌ Misses cross-file relationships")
    print("  ❌ No architectural context")
    print("  ❌ Duplicated explanations")

    print("\n🔗 Multi-File Approach:")
    print("  ✅ Understands relationships between files")
    print("  ✅ Better architectural documentation")
    print("  ✅ Comprehensive module overview")
    print("  ✅ Avoids duplication")
    print("  ⚠️  Uses more tokens per analysis")
    print("  ⚠️  Slightly more complex")

    print("\n💡 Recommendation:")
    print("  - Use multi-file for related files (same module/package)")
    print("  - Use single-file for standalone utilities")
    print("  - Current DeepSeek-V2-Lite handles 5-8 files easily")


if __name__ == "__main__":
    generate_multi_file_docs()
    compare_approaches()
