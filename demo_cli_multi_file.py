#!/usr/bin/env python3
"""
Demo script showing how to use DocGenAI's new multi-file analysis feature.

This demonstrates the CLI integration and shows different usage patterns.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show the output."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"💻 Command: {cmd}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("\n📋 Output:")
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print("\n❌ Error:")
                print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("⏱️  Command timed out!")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False


def main():
    """Run CLI demo."""
    print("🚀 DocGenAI Multi-File Analysis CLI Demo")
    print("This demo shows the new multi-file analysis capabilities")

    # Ensure we're in the right directory
    if not Path("src/docgenai").exists():
        print("❌ Error: Please run this from the project root directory")
        sys.exit(1)

    demos = [
        {
            "cmd": "python -m docgenai.cli generate src/docgenai/chaining --multi-file --output-dir demo_output/chaining",
            "description": "Single group multi-file analysis (chaining module)",
        },
        {
            "cmd": "python -m docgenai.cli generate src/docgenai/prompts --multi-file --output-dir demo_output/prompts",
            "description": "Small module analysis (prompts)",
        },
        {
            "cmd": "python -m docgenai.cli generate src/docgenai --multi-file --max-files-per-group 3 --output-dir demo_output/codebase",
            "description": "Full codebase analysis with synthesis (small groups)",
        },
    ]

    # Create output directory
    Path("demo_output").mkdir(exist_ok=True)

    success_count = 0

    for i, demo in enumerate(demos, 1):
        print(f"\n\n🎯 Demo {i}/{len(demos)}")
        success = run_command(demo["cmd"], demo["description"])
        if success:
            success_count += 1

    # Summary
    print(f"\n\n{'='*60}")
    print("📊 DEMO SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {success_count}/{len(demos)}")

    if success_count == len(demos):
        print("🎉 All demos completed successfully!")
        print("\n📁 Check the demo_output/ directory for generated documentation")
        print("\n💡 Try these commands yourself:")
        print("   # Single file with multi-file context")
        print("   python -m docgenai.cli generate src/docgenai/core.py --multi-file")
        print("\n   # Directory analysis")
        print("   python -m docgenai.cli generate src/docgenai --multi-file")
        print("\n   # Custom grouping")
        print(
            "   python -m docgenai.cli generate . --multi-file --max-files-per-group 5"
        )
    else:
        print(f"⚠️  {len(demos) - success_count} demos failed")
        print("Check the error messages above for details")

    return 0 if success_count == len(demos) else 1


if __name__ == "__main__":
    sys.exit(main())
