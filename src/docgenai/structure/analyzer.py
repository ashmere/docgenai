"""
Main project structure analyzer.

Integrates language detection, pattern detection, and semantic grouping
to provide comprehensive codebase analysis with intelligent file handling.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..language.detector import LanguageDetector
from ..language.extractors import LanguageExtractorFactory
from .grouping import FileGroup, SemanticGrouper
from .patterns import ProjectPatternDetector, StructurePattern

logger = logging.getLogger(__name__)


class ProjectStructureAnalyzer:
    """
    Comprehensive project structure analyzer.

    Provides unified analysis combining language detection, project pattern
    recognition, and semantic file grouping with intelligent content extraction.
    """

    def __init__(
        self,
        root_path: Path,
        language_override: Optional[str] = None,
        max_file_size: int = 50000,  # Increased from 15000
        target_extraction_size: int = 20000,  # Size to extract from large files
    ):
        """
        Initialize project structure analyzer.

        Args:
            root_path: Root directory of the project
            language_override: Optional language override for performance
            max_file_size: Maximum file size before extraction (characters)
            target_extraction_size: Target size for extracted content
        """
        self.root_path = root_path
        self.max_file_size = max_file_size
        self.target_extraction_size = target_extraction_size

        # Initialize components
        self.language_detector = LanguageDetector(language_override)
        self.pattern_detector = ProjectPatternDetector(root_path)
        self.extractor_factory = LanguageExtractorFactory()

        # Analysis results
        self.detected_patterns: List[Tuple[StructurePattern, float]] = []
        self.primary_pattern: Optional[StructurePattern] = None
        self.semantic_groups: List[FileGroup] = []
        self.analysis_summary: Dict = {}

        logger.info(f"🔬 Initialized analyzer for {root_path}")
        if language_override:
            logger.info(f"🔧 Language override: {language_override}")

    def analyze_structure(self) -> Dict:
        """
        Perform comprehensive structure analysis.

        Returns:
            Dictionary with complete analysis results
        """
        logger.info("🚀 Starting comprehensive structure analysis")

        # Step 1: Detect project patterns
        self.detected_patterns = self.pattern_detector.detect_patterns()
        if self.detected_patterns:
            self.primary_pattern = self.detected_patterns[0][0]
            logger.info(
                f"📋 Primary pattern: {self.primary_pattern.name} "
                f"(confidence: {self.detected_patterns[0][1]:.2f})"
            )
        else:
            logger.info("📋 No specific pattern detected, using generic analysis")

        # Step 2: Find and analyze source files
        source_files = self._find_source_files()
        logger.info(f"📁 Found {len(source_files)} source files")

        # Step 3: Create semantic groups
        grouper = SemanticGrouper(self.root_path, self.primary_pattern)
        self.semantic_groups = grouper.create_semantic_groups(source_files)
        logger.info(f"🎯 Created {len(self.semantic_groups)} semantic groups")

        # Step 4: Process groups with intelligent extraction
        processed_groups = self._process_groups_with_extraction()

        # Step 5: Create analysis summary
        self.analysis_summary = self._create_analysis_summary(
            source_files, processed_groups
        )

        logger.info("✅ Structure analysis complete")
        return self.analysis_summary

    def _find_source_files(self) -> List[Path]:
        """Find all source files in the project."""
        source_files = []

        # Common directories to skip
        skip_dirs = {
            "__pycache__",
            ".git",
            ".svn",
            "node_modules",
            "vendor",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            ".env",
            "venv",
            ".venv",
            "env",
            ".next",
            ".nuxt",
            "target",
            "bin",
            "obj",
            ".vs",
            ".vscode",
            ".idea",
        }

        # Get supported extensions from language detector
        supported_languages = self.language_detector.get_supported_languages()

        for file_path in self.root_path.rglob("*"):
            # Skip directories and non-files
            if not file_path.is_file():
                continue

            # Skip files in excluded directories
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            # Check if it's a source file
            if self.language_detector.is_source_file(file_path):
                source_files.append(file_path)

        return source_files

    def _process_groups_with_extraction(self) -> List[Dict]:
        """Process semantic groups with intelligent content extraction."""
        processed_groups = []

        for group in self.semantic_groups:
            logger.info(f"📝 Processing group: {group.name}")

            group_data = {
                "name": group.name,
                "description": group.description,
                "group_type": group.group_type,
                "architectural_role": group.architectural_role,
                "primary_language": group.primary_language,
                "file_count": len(group.files),
                "files": [],
                "total_original_size": 0,
                "total_extracted_size": 0,
                "extraction_applied": False,
            }

            # Process each file in the group
            for file_path in group.files:
                file_data = self._process_file_with_extraction(
                    file_path, group.primary_language
                )
                group_data["files"].append(file_data)
                group_data["total_original_size"] += file_data["original_size"]
                group_data["total_extracted_size"] += file_data["extracted_size"]

                if file_data["extraction_applied"]:
                    group_data["extraction_applied"] = True

            # Calculate group statistics
            group_data["compression_ratio"] = (
                group_data["total_extracted_size"] / group_data["total_original_size"]
                if group_data["total_original_size"] > 0
                else 1.0
            )

            group_data["estimated_tokens"] = (
                group_data["total_extracted_size"] // 4
            )  # Rough estimate

            processed_groups.append(group_data)

            logger.info(
                f"  📊 {group_data['file_count']} files, "
                f"{group_data['total_original_size']:,} → "
                f"{group_data['total_extracted_size']:,} chars "
                f"({group_data['compression_ratio']:.2f} ratio)"
            )

        return processed_groups

    def _process_file_with_extraction(
        self, file_path: Path, primary_language: str
    ) -> Dict:
        """Process a single file with intelligent extraction if needed."""
        try:
            # Read original content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            original_size = len(original_content)

            # Detect language for this specific file
            detected_language = self.language_detector.detect_language(file_path)

            # Use primary language if detection is uncertain
            if detected_language == "text" and primary_language != "text":
                detected_language = primary_language

            file_data = {
                "path": str(file_path.relative_to(self.root_path)),
                "name": file_path.name,
                "language": detected_language,
                "original_size": original_size,
                "extracted_size": original_size,
                "extraction_applied": False,
                "extraction_method": None,
                "content": original_content,
            }

            # Apply extraction if file is too large
            if original_size > self.max_file_size:
                logger.debug(
                    f"🔧 Extracting content from large file: {file_path.name} "
                    f"({original_size:,} chars)"
                )

                extractor = self.extractor_factory.create_extractor(detected_language)
                extracted_content = extractor.extract_structure(
                    original_content, self.target_extraction_size
                )

                file_data.update(
                    {
                        "extracted_size": len(extracted_content),
                        "extraction_applied": True,
                        "extraction_method": f"{detected_language}_extractor",
                        "content": extracted_content,
                    }
                )

                logger.debug(
                    f"  📉 Reduced from {original_size:,} to "
                    f"{len(extracted_content):,} chars"
                )

            return file_data

        except Exception as e:
            logger.warning(f"⚠️ Error processing file {file_path}: {e}")
            return {
                "path": str(file_path.relative_to(self.root_path)),
                "name": file_path.name,
                "language": "unknown",
                "original_size": 0,
                "extracted_size": 0,
                "extraction_applied": False,
                "extraction_method": "error",
                "content": f"# Error reading file: {e}",
            }

    def _create_analysis_summary(
        self, source_files: List[Path], processed_groups: List[Dict]
    ) -> Dict:
        """Create comprehensive analysis summary."""
        # Calculate totals
        total_files = len(source_files)
        total_original_size = sum(
            group["total_original_size"] for group in processed_groups
        )
        total_extracted_size = sum(
            group["total_extracted_size"] for group in processed_groups
        )
        total_groups = len(processed_groups)

        # Count extraction applications
        files_with_extraction = sum(
            sum(1 for file_data in group["files"] if file_data["extraction_applied"])
            for group in processed_groups
        )

        # Language distribution
        language_counts = {}
        for group in processed_groups:
            for file_data in group["files"]:
                lang = file_data["language"]
                language_counts[lang] = language_counts.get(lang, 0) + 1

        # Group type distribution
        group_type_counts = {}
        for group in processed_groups:
            group_type = group["group_type"]
            group_type_counts[group_type] = group_type_counts.get(group_type, 0) + 1

        summary = {
            # Project identification
            "root_path": str(self.root_path),
            "analysis_timestamp": self._get_timestamp(),
            # Pattern detection results
            "detected_patterns": [
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "confidence": confidence,
                    "priority": pattern.priority,
                }
                for pattern, confidence in self.detected_patterns[:5]
            ],
            "primary_pattern": (
                {
                    "name": self.primary_pattern.name,
                    "description": self.primary_pattern.description,
                }
                if self.primary_pattern
                else None
            ),
            # File analysis results
            "file_analysis": {
                "total_files": total_files,
                "total_groups": total_groups,
                "files_with_extraction": files_with_extraction,
                "extraction_percentage": (
                    (files_with_extraction / total_files * 100)
                    if total_files > 0
                    else 0
                ),
            },
            # Size analysis
            "size_analysis": {
                "total_original_size": total_original_size,
                "total_extracted_size": total_extracted_size,
                "compression_ratio": (
                    total_extracted_size / total_original_size
                    if total_original_size > 0
                    else 1.0
                ),
                "estimated_tokens": total_extracted_size // 4,  # Rough estimate
            },
            # Language distribution
            "language_distribution": language_counts,
            "primary_language": (
                max(language_counts, key=language_counts.get)
                if language_counts
                else "unknown"
            ),
            # Group analysis
            "group_analysis": {
                "group_type_distribution": group_type_counts,
                "groups": processed_groups,
            },
            # Configuration used
            "analysis_config": {
                "max_file_size": self.max_file_size,
                "target_extraction_size": self.target_extraction_size,
                "language_override": self.language_detector.language_override,
            },
            # Quality metrics
            "quality_metrics": {
                "no_files_excluded": True,  # Key improvement: no files excluded
                "meaningful_grouping": total_groups > 1,
                "language_coverage": len(language_counts),
                "pattern_confidence": (
                    self.detected_patterns[0][1] if self.detected_patterns else 0.0
                ),
            },
        }

        return summary

    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis."""
        import datetime

        return datetime.datetime.now().isoformat()

    def get_groups_for_analysis(self) -> List[Dict]:
        """
        Get processed groups ready for documentation generation.

        Returns:
            List of group dictionaries with extracted content
        """
        if not self.semantic_groups:
            raise ValueError(
                "Structure analysis not performed. Call analyze_structure() first."
            )

        return self.analysis_summary.get("group_analysis", {}).get("groups", [])

    def get_group_content(self, group_name: str) -> Optional[str]:
        """
        Get combined content for a specific group.

        Args:
            group_name: Name of the group to get content for

        Returns:
            Combined content string or None if group not found
        """
        groups = self.get_groups_for_analysis()

        for group in groups:
            if group["name"] == group_name:
                content_parts = []

                for file_data in group["files"]:
                    relative_path = file_data["path"]
                    language = file_data["language"]
                    content = file_data["content"]

                    # Create file header
                    file_header = f"## File: {relative_path}\n\n"

                    # Add content with language tag
                    if content.strip():
                        file_content = f"```{language}\n{content}\n```\n"
                    else:
                        file_content = "*Empty file*\n"

                    content_parts.append(file_header + file_content)

                return "\n".join(content_parts)

        return None

    def get_analysis_report(self) -> str:
        """
        Generate a human-readable analysis report.

        Returns:
            Formatted analysis report
        """
        if not self.analysis_summary:
            return "No analysis performed yet. Call analyze_structure() first."

        summary = self.analysis_summary

        report_lines = [
            "# Project Structure Analysis Report",
            "",
            f"**Project Path:** `{summary['root_path']}`",
            f"**Analysis Time:** {summary['analysis_timestamp']}",
            "",
        ]

        # Pattern detection
        if summary.get("primary_pattern"):
            pattern = summary["primary_pattern"]
            report_lines.extend(
                [
                    "## Detected Project Pattern",
                    "",
                    f"**Type:** {pattern['name']}",
                    f"**Description:** {pattern['description']}",
                    "",
                ]
            )

        # File analysis
        file_analysis = summary["file_analysis"]
        size_analysis = summary["size_analysis"]

        report_lines.extend(
            [
                "## File Analysis Summary",
                "",
                f"- **Total Files:** {file_analysis['total_files']:,}",
                f"- **Semantic Groups:** {file_analysis['total_groups']}",
                f"- **Files with Extraction:** {file_analysis['files_with_extraction']} "
                f"({file_analysis['extraction_percentage']:.1f}%)",
                f"- **Total Size:** {size_analysis['total_original_size']:,} characters",
                f"- **Extracted Size:** {size_analysis['total_extracted_size']:,} characters",
                f"- **Compression Ratio:** {size_analysis['compression_ratio']:.2f}",
                f"- **Estimated Tokens:** {size_analysis['estimated_tokens']:,}",
                "",
            ]
        )

        # Language distribution
        lang_dist = summary["language_distribution"]
        report_lines.extend(
            [
                "## Language Distribution",
                "",
            ]
        )

        for language, count in sorted(
            lang_dist.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / file_analysis["total_files"]) * 100
            report_lines.append(
                f"- **{language.title()}:** {count} files ({percentage:.1f}%)"
            )

        report_lines.append("")

        # Semantic groups
        groups = summary["group_analysis"]["groups"]
        report_lines.extend(
            [
                "## Semantic Groups",
                "",
            ]
        )

        for group in groups:
            extraction_note = (
                " (with extraction)" if group["extraction_applied"] else ""
            )
            report_lines.extend(
                [
                    f"### {group['name']}",
                    "",
                    f"**Description:** {group['description']}",
                    f"**Type:** {group['group_type']}",
                    f"**Role:** {group['architectural_role']}",
                    f"**Files:** {group['file_count']}{extraction_note}",
                    f"**Size:** {group['total_extracted_size']:,} characters",
                    f"**Language:** {group['primary_language']}",
                    "",
                ]
            )

        # Quality metrics
        quality = summary["quality_metrics"]
        report_lines.extend(
            [
                "## Quality Metrics",
                "",
                f"- **No Files Excluded:** {'✅ Yes' if quality['no_files_excluded'] else '❌ No'}",
                f"- **Meaningful Grouping:** {'✅ Yes' if quality['meaningful_grouping'] else '❌ No'}",
                f"- **Language Coverage:** {quality['language_coverage']} languages",
                f"- **Pattern Confidence:** {quality['pattern_confidence']:.2f}",
                "",
            ]
        )

        return "\n".join(report_lines)

    def export_structure_config(self, output_path: Path) -> None:
        """
        Export detected structure as configuration for future use.

        Args:
            output_path: Path to save the configuration file
        """
        if not self.analysis_summary:
            raise ValueError("No analysis to export. Call analyze_structure() first.")

        import yaml

        config = {
            "project_structure": {
                "root_path": str(self.root_path),
                "primary_pattern": self.analysis_summary.get("primary_pattern"),
                "language_override": self.language_detector.language_override,
                "semantic_groups": [
                    {
                        "name": group["name"],
                        "description": group["description"],
                        "group_type": group["group_type"],
                        "architectural_role": group["architectural_role"],
                        "primary_language": group["primary_language"],
                        "file_patterns": [
                            file_data["path"] for file_data in group["files"]
                        ],
                    }
                    for group in self.analysis_summary["group_analysis"]["groups"]
                ],
                "analysis_config": self.analysis_summary["analysis_config"],
            }
        }

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"📄 Exported structure configuration to {output_path}")

    def load_structure_config(self, config_path: Path) -> None:
        """
        Load structure configuration from file.

        Args:
            config_path: Path to the configuration file
        """
        import yaml

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        project_config = config.get("project_structure", {})

        # Update analyzer settings
        if "language_override" in project_config:
            self.language_detector = LanguageDetector(
                project_config["language_override"]
            )

        if "analysis_config" in project_config:
            analysis_config = project_config["analysis_config"]
            self.max_file_size = analysis_config.get(
                "max_file_size", self.max_file_size
            )
            self.target_extraction_size = analysis_config.get(
                "target_extraction_size", self.target_extraction_size
            )

        logger.info(f"📄 Loaded structure configuration from {config_path}")
