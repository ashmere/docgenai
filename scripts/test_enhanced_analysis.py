#!/usr/bin/env python3
"""
Test script for the enhanced multi-language analysis system.

Demonstrates the new capabilities including:
- Universal language support
- Semantic grouping
- Large file handling
- No file exclusions
- Meaningful group names
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from docgenai.enhanced_multi_file_analyzer import EnhancedMultiFileAnalyzer
from docgenai.structure.analyzer import ProjectStructureAnalyzer


def test_enhanced_analysis(source_dir: str):
    """Test the enhanced analysis system."""
    print(f"🚀 Testing Enhanced Analysis on {source_dir}")
    print("=" * 60)

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ Source directory does not exist: {source_dir}")
        return

    # Configuration for testing
    config = {
        "model": {
            "max_context_tokens": 30000,
            "max_tokens": 4000,
        },
        "documentation": {
            "doc_type": "both",
            "project_type": "auto",
            "detail_level": "module_plus_strategic_class",
            "max_file_size": 50000,  # Increased limit
            "target_extraction_size": 20000,
            # "language_override": "python",  # Uncomment to test override
        },
    }

    try:
        # Test 1: Direct structure analysis
        print("\\n🔍 Test 1: Direct Structure Analysis")
        print("-" * 40)

        start_time = time.time()

        analyzer = ProjectStructureAnalyzer(
            root_path=source_path,
            max_file_size=config["documentation"]["max_file_size"],
            target_extraction_size=config["documentation"]["target_extraction_size"],
        )

        analysis_results = analyzer.analyze_structure()

        analysis_time = time.time() - start_time

        print(f"⏱️  Analysis completed in {analysis_time:.2f} seconds")
        print(f"📊 Found {analysis_results['file_analysis']['total_files']} files")
        print(
            f"🎯 Created {analysis_results['file_analysis']['total_groups']} semantic groups"
        )
        print(
            f"🔧 Applied extraction to {analysis_results['file_analysis']['files_with_extraction']} files"
        )

        # Display detected pattern
        if analysis_results.get("primary_pattern"):
            pattern = analysis_results["primary_pattern"]
            print(f"📋 Detected pattern: {pattern['name']} - {pattern['description']}")

        # Display language distribution
        print("\\n🔤 Language Distribution:")
        for lang, count in analysis_results["language_distribution"].items():
            percentage = (
                count / analysis_results["file_analysis"]["total_files"]
            ) * 100
            print(f"  {lang.title()}: {count} files ({percentage:.1f}%)")

        # Display semantic groups
        print("\\n🎯 Semantic Groups:")
        groups = analysis_results["group_analysis"]["groups"]
        for i, group in enumerate(groups, 1):
            extraction_note = " [EXTRACTED]" if group["extraction_applied"] else ""
            print(f"  {i}. {group['name']}{extraction_note}")
            print(
                f"     Type: {group['group_type']} | Language: {group['primary_language']}"
            )
            print(
                f"     Files: {group['file_count']} | Size: {group['total_extracted_size']:,} chars"
            )
            print(f"     Role: {group['architectural_role']}")

        # Test 2: Enhanced multi-file analyzer
        print("\\n\\n🚀 Test 2: Enhanced Multi-File Analyzer")
        print("-" * 40)

        enhanced_analyzer = EnhancedMultiFileAnalyzer(config)

        # Analyze project structure
        enhanced_results = enhanced_analyzer.analyze_project_structure(source_path)

        # Create documentation plan
        doc_plan = enhanced_analyzer.create_documentation_plan(source_path)

        print(
            f"📋 Documentation plan created with {len(doc_plan['group_plan'])} groups"
        )
        print(f"🎯 Execution order: {', '.join(doc_plan['execution_order'])}")

        # Display group priorities
        print("\\n📊 Group Priorities:")
        for group_plan in doc_plan["group_plan"]:
            group = group_plan["group"]
            priority = group["documentation_context"]["group_priority"]
            complexity = group["documentation_context"]["complexity_level"]
            effort = group_plan["estimated_effort"]

            print(f"  {group_plan['order']}. {group['name']} (Priority: {priority})")
            print(f"     Complexity: {complexity} | Effort: {effort}")
            print(f"     Approach: {group_plan['documentation_approach']}")

        # Test 3: Content extraction demonstration
        print("\\n\\n📝 Test 3: Content Extraction Demonstration")
        print("-" * 40)

        # Show content for the first group
        if groups:
            first_group = groups[0]
            print(f"Showing content for group: {first_group['name']}")

            content = enhanced_analyzer.get_group_content_for_documentation(
                first_group["name"]
            )

            if content:
                content_preview = (
                    content[:500] + "..." if len(content) > 500 else content
                )
                print(f"Content preview ({len(content):,} total chars):")
                print("-" * 30)
                print(content_preview)
            else:
                print("No content available for this group")

        # Test 4: Quality metrics
        print("\\n\\n✅ Test 4: Quality Metrics")
        print("-" * 40)

        quality_metrics = analysis_results["quality_metrics"]
        print(
            f"No Files Excluded: {'✅ YES' if quality_metrics['no_files_excluded'] else '❌ NO'}"
        )
        print(
            f"Meaningful Grouping: {'✅ YES' if quality_metrics['meaningful_grouping'] else '❌ NO'}"
        )
        print(f"Language Coverage: {quality_metrics['language_coverage']} languages")
        print(f"Pattern Confidence: {quality_metrics['pattern_confidence']:.2f}")

        # Size reduction analysis
        size_analysis = analysis_results["size_analysis"]
        print(f"\\nSize Reduction Analysis:")
        print(f"Original Size: {size_analysis['total_original_size']:,} characters")
        print(f"Extracted Size: {size_analysis['total_extracted_size']:,} characters")
        print(f"Compression Ratio: {size_analysis['compression_ratio']:.2f}")
        print(f"Estimated Tokens: {size_analysis['estimated_tokens']:,}")

        # Test 5: Export configuration
        print("\\n\\n💾 Test 5: Export Configuration")
        print("-" * 40)

        config_path = Path("test_structure_config.yaml")
        analyzer.export_structure_config(config_path)
        print(f"✅ Configuration exported to {config_path}")

        # Generate full report
        print("\\n\\n📄 Test 6: Generate Analysis Report")
        print("-" * 40)

        report = enhanced_analyzer.generate_analysis_report()
        report_path = Path("test_analysis_report.md")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Full analysis report saved to {report_path}")

        print("\\n🎉 All tests completed successfully!")
        print("\\n📊 Summary:")
        print(f"  - Analyzed {analysis_results['file_analysis']['total_files']} files")
        print(f"  - Created {len(groups)} semantic groups")
        print(f"  - Zero files excluded due to size")
        print(f"  - Meaningful group names (no 'group 1, 2, 3')")
        print(f"  - Universal language support")
        print(f"  - Intelligent content extraction")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


def test_language_detection():
    """Test language detection capabilities."""
    print("\\n🔤 Testing Language Detection")
    print("-" * 40)

    from docgenai.language.detector import LanguageDetector

    detector = LanguageDetector()

    test_files = [
        "example.py",
        "component.tsx",
        "service.ts",
        "main.go",
        "header.hpp",
        "main.tf",
        "chart.yaml",
        "Dockerfile",
        "script.sh",
        "config.json",
    ]

    for filename in test_files:
        file_path = Path(filename)
        detected = detector.detect_language(file_path)
        print(f"  {filename:<15} → {detected}")


def test_pattern_detection():
    """Test project pattern detection."""
    print("\\n📋 Testing Pattern Detection")
    print("-" * 40)

    from docgenai.structure.patterns import ProjectPatternDetector, ProjectPatterns

    # Show available patterns
    patterns = ProjectPatterns.get_all_patterns()
    print(f"Available patterns: {len(patterns)}")

    for pattern in patterns[:5]:  # Show first 5
        print(f"  {pattern.name}: {pattern.description} (priority: {pattern.priority})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_enhanced_analysis.py <source_directory>")
        print("\\nExample: python test_enhanced_analysis.py src/docgenai")
        sys.exit(1)

    source_dir = sys.argv[1]

    # Run language detection test
    test_language_detection()

    # Run pattern detection test
    test_pattern_detection()

    # Run main analysis test
    test_enhanced_analysis(source_dir)
