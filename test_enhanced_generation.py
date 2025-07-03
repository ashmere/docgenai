#!/usr/bin/env python3
"""
Test script for enhanced documentation generation.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from docgenai.config import load_config
from docgenai.core import DocumentationGenerator
from docgenai.enhanced_multi_file_analyzer import EnhancedMultiFileAnalyzer
from docgenai.models import create_model


def test_enhanced_generation():
    """Test enhanced documentation generation."""
    print("🧪 Testing enhanced documentation generation...")

    start_time = time.time()

    # Load config
    config = load_config()

    # Create model
    print("🏭 Creating model...")
    model = create_model(config)

    # Create enhanced analyzer
    print("🔧 Creating enhanced analyzer...")
    analyzer = EnhancedMultiFileAnalyzer(config)

    # Test on API service
    target_path = Path("/Users/mat.davies/code/skyral-group/acc/services/api")
    output_dir = Path("test_output/new")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Analyzing: {target_path}")
    print(f"📤 Output: {output_dir}")

    # Get semantic groups for documentation
    groups = analyzer.prepare_groups_for_documentation(target_path)
    print(f"📊 Prepared {len(groups)} groups for documentation")

    # Create documentation generator
    doc_gen = DocumentationGenerator(model, config)

    # Generate documentation for each group
    all_docs = []
    for i, group in enumerate(groups, 1):
        print(f"📝 Generating docs for group {i}/{len(groups)}: {group['name']}")

        # Create context for this group
        context = {
            "files": group["files"],
            "group_info": group,
            "project_info": {
                "root_path": target_path,
                "project_type": "microservice",
                "primary_language": "typescript",
            },
        }

        # Generate documentation for this group
        try:
            group_doc = doc_gen.generate_documentation(
                target=target_path,
                output_dir=output_dir,
                context=context,
                doc_type="both",
            )
            all_docs.append({"group": group["name"], "doc": group_doc})
            print(f"✅ Generated docs for {group['name']}")
        except Exception as e:
            print(f"❌ Failed to generate docs for {group['name']}: {e}")

    # Create index
    index_content = create_documentation_index(groups, all_docs)
    index_path = output_dir / "index.md"
    with open(index_path, "w") as f:
        f.write(index_content)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"✅ Enhanced generation complete!")
    print(f"⏱️ Total time: {total_time:.2f} seconds")
    print(f"📄 Generated {len(all_docs)} group documentations")
    print(f"📋 Index: {index_path}")

    return True


def create_documentation_index(groups, docs):
    """Create an index of all generated documentation."""
    content = "# API Service Documentation\n\n"
    content += "Generated using Enhanced Multi-File Analyzer\n\n"
    content += "## Overview\n\n"
    content += f"This documentation covers {len(groups)} semantic groups:\n\n"

    for group in groups:
        content += (
            f"- **{group['name']}**: {group.get('description', 'No description')}\n"
        )
        content += f"  - Type: {group['group_type']}\n"
        content += f"  - Files: {len(group['files'])}\n"
        content += f"  - Role: {group.get('architectural_role', 'Unknown')}\n\n"

    content += "## Documentation Sections\n\n"
    for doc in docs:
        content += f"- [{doc['group']}](#{doc['group'].lower().replace(' ', '-')})\n"

    content += "\n## Detailed Documentation\n\n"
    for doc in docs:
        content += f"### {doc['group']}\n\n"
        if doc["doc"]:
            content += str(doc["doc"]) + "\n\n"
        else:
            content += "Documentation generation failed for this group.\n\n"

    return content


if __name__ == "__main__":
    test_enhanced_generation()
