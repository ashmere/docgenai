"""
Enhanced multi-file analyzer with universal language support and semantic grouping.

Integrates the new structure analysis system to provide intelligent file grouping
and content extraction without arbitrary size limits.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .structure.analyzer import ProjectStructureAnalyzer
from .structure.grouping import FileGroup

logger = logging.getLogger(__name__)


class EnhancedMultiFileAnalyzer:
    """
    Enhanced multi-file analyzer with universal language support.

    Provides intelligent semantic grouping and content extraction
    for any programming language or project type.
    """

    def __init__(self, config: Dict, model=None):
        """Initialize the enhanced multi-file analyzer."""
        self.config = config
        self.model_config = config.get("model", {})
        self.doc_config = config.get("documentation", {})
        self.model = model

        # Automatic token limit detection
        if model is not None:
            # Use model's actual context limit
            self.max_context_tokens = model.get_context_limit()
            logger.info(
                f"🔍 Detected model context limit: {self.max_context_tokens} tokens"
            )
        else:
            # Fallback to config or conservative default
            self.max_context_tokens = self.model_config.get("max_context_tokens", 12000)
            logger.info(
                f"⚠️  Using fallback context limit: {self.max_context_tokens} tokens"
            )

        self.max_output_tokens = self.model_config.get("max_tokens", 4000)
        self.safety_margin = 0.8  # Use 80% of context to be safe

        # Calculate effective limits
        self.effective_context_tokens = int(
            self.max_context_tokens * self.safety_margin
        )

        # Use model's tokenizer for accurate estimation if available
        if model is not None:
            self.chars_per_token = self._calibrate_chars_per_token()
        else:
            self.chars_per_token = 3.0  # Conservative estimate for code

        self.max_content_chars = int(
            self.effective_context_tokens * self.chars_per_token
        )

        # Enhanced configuration
        self.max_file_size = self.doc_config.get(
            "max_file_size", 50000
        )  # Before extraction
        self.target_extraction_size = min(
            self.doc_config.get("target_extraction_size", 20000),
            self.max_content_chars // 4,  # Ensure room for multiple files
        )
        self.language_override = self.doc_config.get("language_override")

        # Documentation configuration
        self.doc_type = self.doc_config.get("doc_type", "both")
        self.project_type = self.doc_config.get("project_type", "auto")
        self.detail_level = self.doc_config.get(
            "detail_level", "module_plus_strategic_class"
        )

        logger.info("🚀 Enhanced multi-file analyzer initialized")
        logger.info(
            f"📊 Max context: {self.max_context_tokens} tokens (effective: {self.effective_context_tokens})"
        )
        logger.info(f"📄 Max content chars: {self.max_content_chars}")
        logger.info(f"🎯 Target extraction size: {self.target_extraction_size} chars")
        logger.info(f"📋 Doc type: {self.doc_type}")
        logger.info(f"🏗️ Project type: {self.project_type}")
        logger.info(f"🔍 Detail level: {self.detail_level}")
        if self.language_override:
            logger.info(f"🔧 Language override: {self.language_override}")

    def _calibrate_chars_per_token(self) -> float:
        """
        Calibrate characters per token ratio using the model's tokenizer.

        Returns:
            Estimated characters per token for code content
        """
        if self.model is None:
            return 3.0

        # Sample code text for calibration
        sample_texts = [
            "def function_name(param1, param2):\n    return param1 + param2",
            "class MyClass:\n    def __init__(self):\n        self.value = 42",
            "import os\nfrom pathlib import Path\n\nif __name__ == '__main__':",
            "const myFunction = (a, b) => {\n    return a + b;\n};",
            "public class Example {\n    private int value;\n    public Example() {}\n}",
        ]

        total_chars = 0
        total_tokens = 0

        for text in sample_texts:
            try:
                tokens = self.model.estimate_tokens(text)
                total_chars += len(text)
                total_tokens += tokens
            except Exception as e:
                logger.warning(f"Token calibration failed for sample: {e}")
                continue

        if total_tokens > 0:
            ratio = total_chars / total_tokens
            logger.info(f"📐 Calibrated chars/token ratio: {ratio:.2f}")
            return ratio
        else:
            logger.warning("Token calibration failed, using fallback ratio")
            return 3.0

    def analyze_project_structure(self, root_path: Path) -> Dict:
        """
        Analyze project structure using the enhanced system.

        Args:
            root_path: Root directory of the project

        Returns:
            Complete structure analysis results
        """
        logger.info(f"🔍 Analyzing project structure: {root_path}")

        # Initialize structure analyzer
        analyzer = ProjectStructureAnalyzer(
            root_path=root_path,
            language_override=self.language_override,
            max_file_size=self.max_file_size,
            target_extraction_size=self.target_extraction_size,
        )

        # Perform comprehensive analysis
        analysis_results = analyzer.analyze_structure()

        # Store analyzer for later use
        self.structure_analyzer = analyzer

        logger.info("✅ Project structure analysis complete")
        return analysis_results

    def get_semantic_groups(self, root_path: Path) -> List[FileGroup]:
        """
        Get semantic file groups for documentation generation.

        Args:
            root_path: Root directory of the project

        Returns:
            List of semantic file groups
        """
        if not hasattr(self, "structure_analyzer"):
            self.analyze_project_structure(root_path)

        return self.structure_analyzer.semantic_groups

    def prepare_groups_for_documentation(self, root_path: Path) -> List[Dict]:
        """
        Prepare semantic groups for documentation generation.

        Args:
            root_path: Root directory of the project

        Returns:
            List of prepared group dictionaries
        """
        if not hasattr(self, "structure_analyzer"):
            self.analyze_project_structure(root_path)

        groups = self.structure_analyzer.get_groups_for_analysis()

        # Enhance groups with documentation-specific information
        enhanced_groups = []

        for group in groups:
            enhanced_group = self._enhance_group_for_documentation(group)
            enhanced_groups.append(enhanced_group)

        return enhanced_groups

    def _enhance_group_for_documentation(self, group: Dict) -> Dict:
        """
        Enhance a group with documentation-specific information.

        Args:
            group: Group dictionary from structure analyzer

        Returns:
            Enhanced group dictionary
        """
        enhanced = group.copy()

        # Add documentation context
        enhanced["documentation_context"] = {
            "doc_type": self.doc_type,
            "detail_level": self.detail_level,
            "project_type": self.project_type,
            "group_priority": self._calculate_group_priority(group),
            "complexity_level": self._assess_group_complexity(group),
        }

        # Add token estimates
        enhanced["token_estimates"] = {
            "content_tokens": group["total_extracted_size"] // 4,
            "context_tokens": self._estimate_context_tokens(group),
            "fits_in_context": self._check_context_fit(group),
        }

        # Add cross-group relationships
        enhanced["relationships"] = self._identify_group_relationships(group)

        return enhanced

    def _calculate_group_priority(self, group: Dict) -> int:
        """
        Calculate documentation priority for a group.

        Higher priority groups should be documented first.

        Args:
            group: Group dictionary

        Returns:
            Priority score (higher = more important)
        """
        priority = 0

        # Core groups are highest priority
        if group["group_type"] == "core":
            priority += 100
        elif group["group_type"] == "feature":
            priority += 80
        elif group["group_type"] == "infrastructure":
            priority += 60
        elif group["group_type"] == "config":
            priority += 40
        elif group["group_type"] == "test":
            priority += 20

        # Boost priority for main application files
        if any(
            keyword in group["name"].lower()
            for keyword in ["main", "app", "core", "entry"]
        ):
            priority += 50

        # Boost priority for API-related groups
        if any(
            keyword in group["name"].lower() for keyword in ["api", "endpoint", "route"]
        ):
            priority += 30

        # Boost priority for larger groups (more comprehensive)
        if group["file_count"] > 5:
            priority += 20
        elif group["file_count"] > 10:
            priority += 30

        return priority

    def _assess_group_complexity(self, group: Dict) -> str:
        """
        Assess the complexity level of a group.

        Args:
            group: Group dictionary

        Returns:
            Complexity level: "simple", "moderate", "complex", "very_complex"
        """
        # Base complexity on file count and size
        file_count = group["file_count"]
        total_size = group["total_extracted_size"]

        if file_count <= 2 and total_size <= 5000:
            return "simple"
        elif file_count <= 5 and total_size <= 15000:
            return "moderate"
        elif file_count <= 10 and total_size <= 30000:
            return "complex"
        else:
            return "very_complex"

    def _estimate_context_tokens(self, group: Dict) -> int:
        """
        Estimate tokens needed for documentation context.

        Args:
            group: Group dictionary

        Returns:
            Estimated context tokens
        """
        # Use accurate token estimation if model is available
        if self.model is not None and hasattr(self, "structure_analyzer"):
            # Get actual content for accurate estimation
            try:
                content = self.structure_analyzer.get_group_content(group["name"])
                if content:
                    content_tokens = self.model.estimate_tokens(content)
                else:
                    content_tokens = group["total_extracted_size"] // int(
                        self.chars_per_token
                    )
            except Exception:
                # Fallback if group content not available
                content_tokens = group["total_extracted_size"] // int(
                    self.chars_per_token
                )
        else:
            # Fallback to character-based estimation
            content_tokens = group["total_extracted_size"] // int(self.chars_per_token)

        # Add tokens for documentation template
        template_tokens = 500  # Approximate

        # Add tokens for cross-references
        reference_tokens = len(group.get("dependencies", [])) * 50

        return content_tokens + template_tokens + reference_tokens

    def _check_context_fit(self, group: Dict) -> bool:
        """
        Check if group fits within context window.

        Args:
            group: Group dictionary

        Returns:
            True if group fits in context window
        """
        estimated_tokens = self._estimate_context_tokens(group)
        return estimated_tokens <= self.effective_context_tokens

    def _identify_group_relationships(self, group: Dict) -> Dict:
        """
        Identify relationships between groups.

        Args:
            group: Group dictionary

        Returns:
            Dictionary of relationships
        """
        relationships = {
            "depends_on": [],
            "depended_by": [],
            "related_to": [],
            "implements": [],
            "extends": [],
        }

        # This would be enhanced with actual dependency analysis
        # For now, return empty relationships
        return relationships

    def create_documentation_plan(self, root_path: Path) -> Dict:
        """
        Create a comprehensive documentation plan.

        Args:
            root_path: Root directory of the project

        Returns:
            Documentation plan with prioritized groups
        """
        logger.info("📋 Creating documentation plan")

        # Get enhanced groups
        groups = self.prepare_groups_for_documentation(root_path)

        # Sort by priority
        groups.sort(
            key=lambda g: g["documentation_context"]["group_priority"], reverse=True
        )

        # Create plan
        plan = {
            "project_overview": {
                "root_path": str(root_path),
                "total_groups": len(groups),
                "analysis_summary": self.structure_analyzer.analysis_summary,
            },
            "documentation_strategy": {
                "doc_type": self.doc_type,
                "detail_level": self.detail_level,
                "project_type": self.project_type,
            },
            "group_plan": [],
            "execution_order": [],
            "quality_metrics": {
                "no_files_excluded": True,
                "meaningful_grouping": len(groups) > 1,
                "total_files": sum(g["file_count"] for g in groups),
                "total_size": sum(g["total_extracted_size"] for g in groups),
            },
        }

        # Plan each group
        for i, group in enumerate(groups):
            group_plan = {
                "order": i + 1,
                "group": group,
                "documentation_approach": self._determine_documentation_approach(group),
                "estimated_effort": self._estimate_documentation_effort(group),
                "dependencies": group.get("relationships", {}).get("depends_on", []),
            }

            plan["group_plan"].append(group_plan)
            plan["execution_order"].append(group["name"])

        logger.info(f"📊 Documentation plan created: {len(groups)} groups")
        return plan

    def _determine_documentation_approach(self, group: Dict) -> str:
        """
        Determine the best documentation approach for a group.

        Args:
            group: Enhanced group dictionary

        Returns:
            Documentation approach strategy
        """
        complexity = group["documentation_context"]["complexity_level"]
        group_type = group["group_type"]

        if group_type == "core":
            return "comprehensive_with_examples"
        elif group_type == "feature":
            return "detailed_with_usage"
        elif group_type == "infrastructure":
            return "technical_reference"
        elif group_type == "config":
            return "configuration_guide"
        elif group_type == "test":
            return "testing_overview"
        else:
            return "standard_documentation"

    def _estimate_documentation_effort(self, group: Dict) -> str:
        """
        Estimate documentation effort for a group.

        Args:
            group: Enhanced group dictionary

        Returns:
            Effort estimate: "low", "medium", "high", "very_high"
        """
        complexity = group["documentation_context"]["complexity_level"]
        file_count = group["file_count"]

        if complexity == "simple" and file_count <= 3:
            return "low"
        elif complexity == "moderate" and file_count <= 6:
            return "medium"
        elif complexity == "complex" or file_count > 6:
            return "high"
        else:
            return "very_high"

    def get_group_content_for_documentation(self, group_name: str) -> Optional[str]:
        """
        Get formatted content for a specific group for documentation.

        Args:
            group_name: Name of the group

        Returns:
            Formatted content string or None
        """
        if not hasattr(self, "structure_analyzer"):
            raise ValueError(
                "Structure analysis not performed. Call analyze_project_structure() first."
            )

        return self.structure_analyzer.get_group_content(group_name)

    def generate_analysis_report(self) -> str:
        """
        Generate a comprehensive analysis report.

        Returns:
            Formatted analysis report
        """
        if not hasattr(self, "structure_analyzer"):
            raise ValueError(
                "Structure analysis not performed. Call analyze_project_structure() first."
            )

        return self.structure_analyzer.get_analysis_report()

    def export_analysis_config(self, output_path: Path) -> None:
        """
        Export the current analysis configuration for reuse.

        Args:
            output_path: Path to save the configuration
        """
        if not hasattr(self, "structure_analyzer"):
            raise ValueError("No analysis has been performed yet")

        self.structure_analyzer.export_configuration(output_path)
        logger.info(f"📤 Analysis configuration exported to {output_path}")

    def analyze_codebase_structure(self, root_path: Path) -> Dict[str, any]:
        """
        Analyze codebase structure for compatibility with old interface.

        This method provides compatibility with the existing core.py interface
        while using the enhanced analysis capabilities.

        Args:
            root_path: Root directory to analyze

        Returns:
            Structure analysis compatible with old interface
        """
        logger.info(
            f"🔍 Analyzing codebase structure (compatibility mode): {root_path}"
        )

        # Perform enhanced analysis
        analysis_results = self.analyze_project_structure(root_path)
        groups = self.get_semantic_groups(root_path)

        # Find all source files for compatibility
        all_files = []
        for group in groups:
            all_files.extend(group.files)

        # Create group details in old format
        group_details = []
        estimated_total_tokens = 0

        for i, group in enumerate(groups):
            # Prepare context to get token estimates
            context = self.prepare_multi_file_context(group.files)
            estimated_tokens = context.get(
                "estimated_tokens", context["total_size"] // 4
            )

            group_info = {
                "group_id": i + 1,
                "files": [f.name for f in group.files],
                "file_count": len(group.files),
                "estimated_tokens": estimated_tokens,
                "primary_directory": str(group.files[0].parent) if group.files else "",
                "group_name": group.name,  # Enhanced: Include semantic name
                "architectural_role": group.architectural_role,  # Enhanced: Include role
            }
            group_details.append(group_info)
            estimated_total_tokens += estimated_tokens

        # Check for large files (in enhanced mode, we handle large files differently)
        large_files = []
        for group in groups:
            for file_path in group.files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if len(content) > self.max_file_size and len(content) > 50000:
                        large_files.append(
                            {
                                "file": str(file_path),
                                "size": len(content),
                                "reason": "Large file handled with extraction",
                            }
                        )
                except Exception:
                    continue

        # Create structure in old format
        structure = {
            "root_path": str(root_path),
            "total_files": len(all_files),
            "suitable_files": len(all_files),  # Enhanced handles all files
            "groups": len(groups),
            "group_details": group_details,
            "large_files": large_files,
            "estimated_total_tokens": estimated_total_tokens,
            "requires_synthesis": len(groups) > 1,
            # Enhanced additions
            "primary_language": analysis_results.get("primary_language", "unknown"),
            "project_pattern": analysis_results.get("primary_pattern", {}),
            "semantic_groups": groups,
            "enhanced_analysis": analysis_results,
        }

        logger.info(f"📊 Compatibility structure analysis complete:")
        logger.info(f"  - Total files: {structure['total_files']}")
        logger.info(f"  - Analysis groups: {structure['groups']}")
        logger.info(f"  - Requires synthesis: {structure['requires_synthesis']}")
        logger.info(f"  - Primary language: {structure['primary_language']}")

        return structure

    def group_files_for_analysis(self, files: List[Path]) -> List[List[Path]]:
        """
        Group files for analysis (compatibility method).

        Args:
            files: List of files to group

        Returns:
            List of file groups (each group is a list of paths)
        """
        if not hasattr(self, "structure_analyzer"):
            # If no analysis has been done, use the files' parent directory
            if files:
                root_path = files[0].parent
                while root_path.parent != root_path:
                    if all(f.is_relative_to(root_path) for f in files):
                        break
                    root_path = root_path.parent
                self.analyze_project_structure(root_path)
            else:
                return []

        # Get semantic groups and convert to old format
        semantic_groups = self.get_semantic_groups(self.structure_analyzer.root_path)

        # Convert FileGroup objects to lists of paths
        file_groups = []
        for group in semantic_groups:
            # Filter to only include files that were requested
            group_files = [f for f in group.files if f in files]
            if group_files:
                file_groups.append(group_files)

        return file_groups

    def prepare_multi_file_context(self, file_group: List[Path]) -> Dict[str, any]:
        """
        Prepare multi-file context for documentation generation.

        Args:
            file_group: List of files to prepare context for

        Returns:
            Context dictionary compatible with old interface
        """
        logger.info(f"📝 Preparing multi-file context for {len(file_group)} files")

        # Read file contents
        files_content = {}
        files_summary = {}
        total_size = 0

        for file_path in file_group:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Apply content extraction if file is large
                if len(content) > self.max_file_size:
                    if hasattr(self, "structure_analyzer"):
                        extracted = self.structure_analyzer.extract_file_content(
                            file_path
                        )
                        if extracted and isinstance(extracted, dict):
                            content = extracted.get(
                                "extracted_content",
                                content[: self.target_extraction_size],
                            )
                        else:
                            content = content[: self.target_extraction_size]
                    else:
                        content = content[: self.target_extraction_size]

                files_content[str(file_path)] = content
                files_summary[str(file_path)] = (
                    f"File: {file_path.name} ({len(content)} chars)"
                )
                total_size += len(content)

            except Exception as e:
                logger.warning(f"⚠️ Could not read {file_path}: {e}")
                files_content[str(file_path)] = f"# Error reading file: {e}"
                files_summary[str(file_path)] = f"File: {file_path.name} (error)"

        # Detect project type
        project_type = "auto"
        if (
            hasattr(self, "structure_analyzer")
            and self.structure_analyzer.analysis_summary
        ):
            try:
                analysis = self.structure_analyzer.analysis_summary
                if analysis and isinstance(analysis, dict):
                    primary_pattern = analysis.get("primary_pattern", {})
                    if primary_pattern and isinstance(primary_pattern, dict):
                        project_type = primary_pattern.get("name", "auto")
                        if project_type and project_type.startswith("angular"):
                            project_type = "application"
                        elif project_type and project_type.startswith("react"):
                            project_type = "application"
                        elif project_type and "microservice" in project_type:
                            project_type = "microservice"
                        else:
                            project_type = "auto"
            except Exception:
                # Fallback to auto if any error occurs
                project_type = "auto"

        context = {
            "files_content": files_content,
            "files_summary": files_summary,
            "file_count": len(file_group),
            "file_names": [f.name for f in file_group],
            "total_size": total_size,
            "project_type": project_type,
            "group_info": {
                "files": file_group,
                "total_size": total_size,
                "enhanced": True,
            },
        }

        logger.info(
            f"📊 Context prepared: {len(file_group)} files, {total_size} chars, type: {project_type}"
        )
        return context

    def _find_source_files(self, root_path: Path) -> List[Path]:
        """
        Find source files for compatibility.

        Args:
            root_path: Root directory to search

        Returns:
            List of source files
        """
        if (
            hasattr(self, "structure_analyzer")
            and self.structure_analyzer.semantic_groups
        ):
            # Get files from semantic groups
            files = []
            for group in self.structure_analyzer.semantic_groups:
                files.extend(group.files)
            return files
        else:
            # Fallback: basic file discovery
            extensions = [
                ".py",
                ".js",
                ".ts",
                ".jsx",
                ".tsx",
                ".go",
                ".cpp",
                ".c",
                ".h",
                ".hpp",
            ]
            files = []
            for ext in extensions:
                files.extend(root_path.rglob(f"*{ext}"))
            return files

    def should_use_enhanced_analysis(self, file_paths: List[Path]) -> bool:
        """
        Determine if enhanced analysis should be used.

        Args:
            file_paths: List of files to analyze

        Returns:
            True if enhanced analysis is recommended
        """
        # Always use enhanced analysis for comprehensive results
        return True

    def get_legacy_groups(self, root_path: Path) -> List[List[Path]]:
        """
        Get groups in legacy format for backward compatibility.

        Args:
            root_path: Root directory of the project

        Returns:
            List of file path groups
        """
        if not hasattr(self, "structure_analyzer"):
            self.analyze_project_structure(root_path)

        legacy_groups = []

        for group in self.structure_analyzer.semantic_groups:
            # Convert FileGroup to list of paths
            file_paths = [
                Path(root_path) / file_data["path"]
                for file_data in self.structure_analyzer.get_groups_for_analysis()
                if file_data["name"] == group.name
                for file_data in file_data["files"]
            ]

            if file_paths:
                legacy_groups.append(file_paths)

        return legacy_groups

    def create_group_summaries(self, groups: List[List[Path]]) -> List[Dict]:
        """
        Create summaries for each file group for cross-group analysis.

        Args:
            groups: List of file groups

        Returns:
            List of group summaries compatible with old interface
        """
        summaries = []

        for i, group in enumerate(groups):
            context = self.prepare_multi_file_context(group)

            # Create a concise summary of the group
            summary = {
                "group_id": i + 1,
                "primary_directory": str(group[0].parent) if group else "",
                "files": context["file_names"],
                "file_count": context["file_count"],
                "summary": context["files_summary"],
                "estimated_tokens": context.get(
                    "estimated_tokens", context["total_size"] // 4
                ),
                "key_components": self._extract_key_components(group),
                "enhanced": True,  # Mark as enhanced
            }

            summaries.append(summary)

        return summaries

    def _extract_key_components(self, file_group: List[Path]) -> List[str]:
        """Extract key components (classes, functions) from a file group."""
        components = []

        for file_path in file_group:
            try:
                # Use language-specific extraction if available
                if hasattr(self, "structure_analyzer"):
                    extractor = self.structure_analyzer.extractor_factory.get_extractor(
                        self.structure_analyzer.language_detector.detect_language(
                            file_path
                        )
                    )

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    extracted = extractor.extract_content(content)

                    # Add classes and functions with file context
                    for item in extracted.get("classes", []):
                        components.append(f"{file_path.name}::{item}")

                    for item in extracted.get("functions", []):
                        if not item.startswith("_"):  # Skip private functions
                            components.append(f"{file_path.name}::{item}")

                else:
                    # Fallback to regex-based extraction
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    import re

                    classes = re.findall(r"^\s*class\s+(\w+)", content, re.MULTILINE)
                    functions = re.findall(
                        r"^\s*(?:def|function)\s+(\w+)", content, re.MULTILINE
                    )

                    for cls in classes:
                        components.append(f"{file_path.name}::{cls}")

                    for func in functions:
                        if not func.startswith("_"):
                            components.append(f"{file_path.name}::{func}")

            except Exception as e:
                logger.warning(f"⚠️ Could not extract components from {file_path}: {e}")
                continue

        return components[:10]  # Limit to most important components

    def estimate_synthesis_complexity(self, codebase_structure: Dict) -> str:
        """
        Estimate the complexity of synthesis needed for the codebase.

        Args:
            codebase_structure: Output from analyze_codebase_structure

        Returns:
            Complexity level: "simple", "moderate", "complex"
        """
        groups = codebase_structure["groups"]
        total_files = codebase_structure["total_files"]
        total_tokens = codebase_structure.get("estimated_total_tokens", 0)

        if groups <= 2 and total_files <= 10:
            return "simple"
        elif groups <= 5 and total_files <= 25 and total_tokens <= 50000:
            return "moderate"
        else:
            return "complex"
