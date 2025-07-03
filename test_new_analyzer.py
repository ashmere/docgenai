#!/usr/bin/env python3
"""
Test script for the new enhanced multi-file analyzer.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.enhanced_multi_file_analyzer import EnhancedMultiFileAnalyzer


def test_new_analyzer():
    """Test the new enhanced analyzer."""
    print("🧪 Testing new enhanced analyzer...")

    # Load config
    config = load_config()

    # Create analyzer (only needs config)
    print("🔧 Creating enhanced analyzer...")
    analyzer = EnhancedMultiFileAnalyzer(config)

    # Test on API service
    target_path = Path("/Users/mat.davies/code/skyral-group/acc/services/api")

    print(f"📁 Analyzing: {target_path}")

    # Test structure analysis
    structure_results = analyzer.analyze_project_structure(target_path)
    print(f"🏗️ Primary pattern: {structure_results.get('primary_pattern', 'None')}")
    print(f"🔤 Primary language: {structure_results.get('primary_language', 'None')}")

    # Test semantic groups
    groups = analyzer.get_semantic_groups(target_path)
    print(f"📊 Found {len(groups)} semantic groups:")
    for group in groups:
        print(f"  - {group.name}: {len(group.files)} files " f"({group.group_type})")
        print(f"    Role: {group.architectural_role}")

    # Test documentation plan
    doc_plan = analyzer.create_documentation_plan(target_path)
    print(f"📋 Documentation approach: {doc_plan.get('approach', 'Unknown')}")

    print("✅ Enhanced analyzer test complete!")
    return True


if __name__ == "__main__":
    test_new_analyzer()
