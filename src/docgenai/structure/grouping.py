"""
Semantic grouping system for meaningful file organization.

Provides intelligent file grouping based on project structure patterns,
language semantics, and architectural boundaries.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .patterns import ProjectPatternDetector, StructurePattern

logger = logging.getLogger(__name__)


@dataclass
class FileGroup:
    """
    Represents a semantically meaningful group of files.

    Groups files based on their architectural role and relationships
    rather than arbitrary size limits.
    """

    name: str
    description: str
    files: List[Path]
    primary_language: str
    group_type: str  # 'core', 'feature', 'infrastructure', 'config', 'test'
    architectural_role: str
    estimated_tokens: int = 0
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class SemanticGrouper:
    """
    Groups files based on semantic meaning and architectural boundaries.

    Creates meaningful groups that reflect the actual structure and
    organization of the codebase rather than arbitrary file size limits.
    """

    def __init__(
        self, root_path: Path, project_pattern: Optional[StructurePattern] = None
    ):
        """
        Initialize semantic grouper.

        Args:
            root_path: Root directory of the project
            project_pattern: Detected project pattern (optional)
        """
        self.root_path = root_path
        self.project_pattern = project_pattern
        self.language_groups = {
            "web_frontend": ["javascript", "typescript", "jsx", "tsx", "vue"],
            "web_backend": ["python", "java", "go", "csharp", "php", "ruby", "node"],
            "systems": ["cpp", "c", "rust", "go", "zig"],
            "mobile": ["swift", "kotlin", "java", "dart"],
            "devops": ["terraform", "yaml", "dockerfile", "shell", "helm"],
            "data": ["python", "r", "sql", "scala", "jupyter"],
            "config": ["json", "yaml", "toml", "ini", "xml", "env"],
        }

        # Auto-detect pattern if not provided
        if not self.project_pattern:
            detector = ProjectPatternDetector(root_path)
            patterns = detector.detect_patterns()
            if patterns:
                self.project_pattern = patterns[0][0]  # Use highest confidence pattern

    def create_semantic_groups(self, files: List[Path]) -> List[FileGroup]:
        """
        Create semantic groups from a list of files.

        Args:
            files: List of files to group

        Returns:
            List of semantic file groups
        """
        logger.info(f"🎯 Creating semantic groups for {len(files)} files")

        if self.project_pattern:
            logger.info(f"📋 Using pattern: {self.project_pattern.name}")
            return self._group_by_pattern(files)
        else:
            logger.info("📋 Using generic grouping strategy")
            return self._group_generically(files)

    def _group_by_pattern(self, files: List[Path]) -> List[FileGroup]:
        """Group files based on detected project pattern."""
        pattern_name = self.project_pattern.name

        # Use pattern-specific grouping strategies
        if pattern_name.startswith("react") or pattern_name.startswith("nextjs"):
            return self._group_react_app(files)
        elif pattern_name.startswith("vue"):
            return self._group_vue_app(files)
        elif pattern_name.startswith("angular"):
            return self._group_angular_app(files)
        elif pattern_name.startswith("python"):
            return self._group_python_project(files)
        elif pattern_name.startswith("django"):
            return self._group_django_app(files)
        elif pattern_name.startswith("flask") or pattern_name.startswith("fastapi"):
            return self._group_python_web_app(files)
        elif pattern_name.startswith("go"):
            return self._group_go_project(files)
        elif pattern_name.startswith("cmake") or pattern_name.startswith("header_only"):
            return self._group_cpp_project(files)
        elif pattern_name.startswith("terraform"):
            return self._group_terraform_project(files)
        elif pattern_name.startswith("helm"):
            return self._group_helm_chart(files)
        elif pattern_name.startswith("microservice"):
            return self._group_microservices(files)
        else:
            return self._group_generically(files)

    def _group_react_app(self, files: List[Path]) -> List[FileGroup]:
        """Group React application files."""
        groups = []

        # Core application files
        core_files = []
        component_files = []
        hook_files = []
        utility_files = []
        config_files = []
        test_files = []

        for file_path in files:
            path_str = str(file_path).lower()
            file_name = file_path.name.lower()

            # Categorize files
            if any(test in path_str for test in ["test", "spec", "__tests__"]):
                test_files.append(file_path)
            elif (
                "component" in path_str
                or file_name.endswith((".jsx", ".tsx"))
                and "component" in file_name
            ):
                component_files.append(file_path)
            elif "hook" in path_str or file_name.startswith("use"):
                hook_files.append(file_path)
            elif any(util in path_str for util in ["util", "helper", "lib", "service"]):
                utility_files.append(file_path)
            elif any(
                config in file_name for config in ["config", "env", ".json", "package"]
            ):
                config_files.append(file_path)
            elif file_name in [
                "app.tsx",
                "app.jsx",
                "index.tsx",
                "index.jsx",
                "main.tsx",
                "main.jsx",
            ]:
                core_files.append(file_path)
            else:
                # Determine by directory structure
                if "src" in path_str:
                    if "component" in path_str:
                        component_files.append(file_path)
                    else:
                        core_files.append(file_path)
                else:
                    config_files.append(file_path)

        # Create groups
        if core_files:
            groups.append(
                FileGroup(
                    name="Application Core",
                    description="Main application entry points and core logic",
                    files=core_files,
                    primary_language="typescript",
                    group_type="core",
                    architectural_role="Application bootstrap and main logic",
                )
            )

        if component_files:
            groups.append(
                FileGroup(
                    name="React Components",
                    description="React components and UI elements",
                    files=component_files,
                    primary_language="typescript",
                    group_type="feature",
                    architectural_role="User interface components and presentation logic",
                )
            )

        if hook_files:
            groups.append(
                FileGroup(
                    name="React Hooks",
                    description="Custom React hooks and state management",
                    files=hook_files,
                    primary_language="typescript",
                    group_type="feature",
                    architectural_role="State management and side effect handling",
                )
            )

        if utility_files:
            groups.append(
                FileGroup(
                    name="Utilities & Services",
                    description="Utility functions, services, and helpers",
                    files=utility_files,
                    primary_language="typescript",
                    group_type="infrastructure",
                    architectural_role="Business logic and utility functions",
                )
            )

        if config_files:
            groups.append(
                FileGroup(
                    name="Configuration",
                    description="Configuration files and environment setup",
                    files=config_files,
                    primary_language="json",
                    group_type="config",
                    architectural_role="Application configuration and build setup",
                )
            )

        if test_files:
            groups.append(
                FileGroup(
                    name="Tests",
                    description="Test files and test utilities",
                    files=test_files,
                    primary_language="typescript",
                    group_type="test",
                    architectural_role="Test coverage and quality assurance",
                )
            )

        return groups

    def _group_vue_app(self, files: List[Path]) -> List[FileGroup]:
        """Group Vue.js application files."""
        groups = []

        core_files = []
        component_files = []
        view_files = []
        store_files = []
        router_files = []
        config_files = []
        test_files = []

        for file_path in files:
            path_str = str(file_path).lower()
            file_name = file_path.name.lower()

            if any(test in path_str for test in ["test", "spec"]):
                test_files.append(file_path)
            elif "component" in path_str or file_name.endswith(".vue"):
                if "view" in path_str or "page" in path_str:
                    view_files.append(file_path)
                else:
                    component_files.append(file_path)
            elif "store" in path_str or "vuex" in path_str:
                store_files.append(file_path)
            elif "router" in path_str:
                router_files.append(file_path)
            elif any(
                config in file_name for config in ["config", "env", ".json", "package"]
            ):
                config_files.append(file_path)
            elif file_name in ["main.js", "main.ts", "app.vue"]:
                core_files.append(file_path)
            else:
                core_files.append(file_path)

        # Create groups
        if core_files:
            groups.append(
                FileGroup(
                    name="Application Core",
                    description="Main application setup and core logic",
                    files=core_files,
                    primary_language="javascript",
                    group_type="core",
                    architectural_role="Application initialization and core configuration",
                )
            )

        if view_files:
            groups.append(
                FileGroup(
                    name="Views & Pages",
                    description="Vue.js views and page components",
                    files=view_files,
                    primary_language="vue",
                    group_type="feature",
                    architectural_role="Page-level components and routing targets",
                )
            )

        if component_files:
            groups.append(
                FileGroup(
                    name="Vue Components",
                    description="Reusable Vue.js components",
                    files=component_files,
                    primary_language="vue",
                    group_type="feature",
                    architectural_role="Reusable UI components and widgets",
                )
            )

        if store_files:
            groups.append(
                FileGroup(
                    name="State Management",
                    description="Vuex store and state management",
                    files=store_files,
                    primary_language="javascript",
                    group_type="infrastructure",
                    architectural_role="Application state management and data flow",
                )
            )

        if router_files:
            groups.append(
                FileGroup(
                    name="Routing",
                    description="Vue Router configuration and navigation",
                    files=router_files,
                    primary_language="javascript",
                    group_type="infrastructure",
                    architectural_role="Application routing and navigation logic",
                )
            )

        if config_files:
            groups.append(
                FileGroup(
                    name="Configuration",
                    description="Build and environment configuration",
                    files=config_files,
                    primary_language="json",
                    group_type="config",
                    architectural_role="Build tools and environment configuration",
                )
            )

        if test_files:
            groups.append(
                FileGroup(
                    name="Tests",
                    description="Test suites and testing utilities",
                    files=test_files,
                    primary_language="javascript",
                    group_type="test",
                    architectural_role="Test coverage and quality validation",
                )
            )

        return groups

    def _group_python_project(self, files: List[Path]) -> List[FileGroup]:
        """Group Python project files."""
        groups = []

        core_modules = []
        model_files = []
        utility_files = []
        config_files = []
        test_files = []
        cli_files = []

        for file_path in files:
            path_str = str(file_path).lower()
            file_name = file_path.name.lower()

            if any(test in path_str for test in ["test", "tests"]):
                test_files.append(file_path)
            elif any(model in path_str for model in ["model", "schema", "entity"]):
                model_files.append(file_path)
            elif any(util in path_str for util in ["util", "helper", "lib", "common"]):
                utility_files.append(file_path)
            elif any(cli in file_name for cli in ["cli", "main", "app", "run"]):
                cli_files.append(file_path)
            elif any(config in file_name for config in ["config", "settings", "setup"]):
                config_files.append(file_path)
            elif file_name.endswith(".py"):
                core_modules.append(file_path)
            else:
                config_files.append(file_path)

        # Create groups
        if cli_files:
            groups.append(
                FileGroup(
                    name="Application Entry Points",
                    description="Main application and CLI entry points",
                    files=cli_files,
                    primary_language="python",
                    group_type="core",
                    architectural_role="Application initialization and command-line interface",
                )
            )

        if core_modules:
            groups.append(
                FileGroup(
                    name="Core Modules",
                    description="Core business logic and main modules",
                    files=core_modules,
                    primary_language="python",
                    group_type="core",
                    architectural_role="Primary business logic and core functionality",
                )
            )

        if model_files:
            groups.append(
                FileGroup(
                    name="Data Models",
                    description="Data models, schemas, and entities",
                    files=model_files,
                    primary_language="python",
                    group_type="feature",
                    architectural_role="Data structures and domain models",
                )
            )

        if utility_files:
            groups.append(
                FileGroup(
                    name="Utilities & Helpers",
                    description="Utility functions and helper modules",
                    files=utility_files,
                    primary_language="python",
                    group_type="infrastructure",
                    architectural_role="Supporting utilities and common functionality",
                )
            )

        if config_files:
            groups.append(
                FileGroup(
                    name="Configuration",
                    description="Configuration and setup files",
                    files=config_files,
                    primary_language="python",
                    group_type="config",
                    architectural_role="Project configuration and environment setup",
                )
            )

        if test_files:
            groups.append(
                FileGroup(
                    name="Tests",
                    description="Test modules and testing utilities",
                    files=test_files,
                    primary_language="python",
                    group_type="test",
                    architectural_role="Test coverage and quality assurance",
                )
            )

        return groups

    def _group_go_project(self, files: List[Path]) -> List[FileGroup]:
        """Group Go project files."""
        groups = []

        main_files = []
        cmd_files = []
        internal_files = []
        pkg_files = []
        api_files = []
        config_files = []
        test_files = []

        for file_path in files:
            path_str = str(file_path).lower()
            file_name = file_path.name.lower()

            if file_name.endswith("_test.go"):
                test_files.append(file_path)
            elif "cmd/" in path_str:
                cmd_files.append(file_path)
            elif "internal/" in path_str:
                internal_files.append(file_path)
            elif "pkg/" in path_str:
                pkg_files.append(file_path)
            elif "api/" in path_str:
                api_files.append(file_path)
            elif file_name == "main.go":
                main_files.append(file_path)
            elif file_name in ["go.mod", "go.sum"]:
                config_files.append(file_path)
            else:
                # Categorize by content or location
                if "api" in path_str or "handler" in path_str:
                    api_files.append(file_path)
                else:
                    pkg_files.append(file_path)

        # Create groups
        if main_files:
            groups.append(
                FileGroup(
                    name="Application Entry Point",
                    description="Main application entry point",
                    files=main_files,
                    primary_language="go",
                    group_type="core",
                    architectural_role="Application bootstrap and initialization",
                )
            )

        if cmd_files:
            groups.append(
                FileGroup(
                    name="Command Line Interface",
                    description="CLI commands and application commands",
                    files=cmd_files,
                    primary_language="go",
                    group_type="core",
                    architectural_role="Command-line interface and application commands",
                )
            )

        if api_files:
            groups.append(
                FileGroup(
                    name="API Layer",
                    description="HTTP handlers and API endpoints",
                    files=api_files,
                    primary_language="go",
                    group_type="feature",
                    architectural_role="HTTP API and request handling",
                )
            )

        if internal_files:
            groups.append(
                FileGroup(
                    name="Internal Packages",
                    description="Internal application packages",
                    files=internal_files,
                    primary_language="go",
                    group_type="core",
                    architectural_role="Internal business logic and implementation details",
                )
            )

        if pkg_files:
            groups.append(
                FileGroup(
                    name="Public Packages",
                    description="Public packages and libraries",
                    files=pkg_files,
                    primary_language="go",
                    group_type="infrastructure",
                    architectural_role="Reusable packages and public APIs",
                )
            )

        if config_files:
            groups.append(
                FileGroup(
                    name="Module Configuration",
                    description="Go module and dependency configuration",
                    files=config_files,
                    primary_language="go",
                    group_type="config",
                    architectural_role="Module definition and dependency management",
                )
            )

        if test_files:
            groups.append(
                FileGroup(
                    name="Tests",
                    description="Test files and benchmarks",
                    files=test_files,
                    primary_language="go",
                    group_type="test",
                    architectural_role="Test coverage and performance benchmarks",
                )
            )

        return groups

    def _group_terraform_project(self, files: List[Path]) -> List[FileGroup]:
        """Group Terraform project files."""
        groups = []

        main_files = []
        variable_files = []
        output_files = []
        module_files = []
        data_files = []
        config_files = []

        for file_path in files:
            file_name = file_path.name.lower()
            path_str = str(file_path).lower()

            if file_name == "main.tf":
                main_files.append(file_path)
            elif "variable" in file_name:
                variable_files.append(file_path)
            elif "output" in file_name:
                output_files.append(file_path)
            elif "data" in file_name:
                data_files.append(file_path)
            elif "module" in path_str:
                module_files.append(file_path)
            elif file_name.endswith((".tfvars", ".tf")):
                main_files.append(file_path)
            else:
                config_files.append(file_path)

        # Create groups
        if main_files:
            groups.append(
                FileGroup(
                    name="Infrastructure Definition",
                    description="Main Terraform configuration and resources",
                    files=main_files,
                    primary_language="terraform",
                    group_type="core",
                    architectural_role="Primary infrastructure resource definitions",
                )
            )

        if variable_files:
            groups.append(
                FileGroup(
                    name="Variables",
                    description="Input variables and configuration parameters",
                    files=variable_files,
                    primary_language="terraform",
                    group_type="config",
                    architectural_role="Parameterization and configuration inputs",
                )
            )

        if output_files:
            groups.append(
                FileGroup(
                    name="Outputs",
                    description="Output values and exported data",
                    files=output_files,
                    primary_language="terraform",
                    group_type="config",
                    architectural_role="Exported values and integration points",
                )
            )

        if data_files:
            groups.append(
                FileGroup(
                    name="Data Sources",
                    description="External data sources and lookups",
                    files=data_files,
                    primary_language="terraform",
                    group_type="infrastructure",
                    architectural_role="External data integration and lookups",
                )
            )

        if module_files:
            groups.append(
                FileGroup(
                    name="Modules",
                    description="Reusable Terraform modules",
                    files=module_files,
                    primary_language="terraform",
                    group_type="infrastructure",
                    architectural_role="Modular and reusable infrastructure components",
                )
            )

        if config_files:
            groups.append(
                FileGroup(
                    name="Configuration",
                    description="Terraform configuration and environment files",
                    files=config_files,
                    primary_language="terraform",
                    group_type="config",
                    architectural_role="Terraform and provider configuration",
                )
            )

        return groups

    def _group_generically(self, files: List[Path]) -> List[FileGroup]:
        """Generic grouping strategy based on directory structure and file types."""
        groups = []

        # Group by directory first
        directory_groups = {}
        root_files = []

        for file_path in files:
            try:
                relative_path = file_path.relative_to(self.root_path)
                if len(relative_path.parts) == 1:
                    # Root-level file
                    root_files.append(file_path)
                else:
                    # File in subdirectory
                    top_dir = relative_path.parts[0]
                    if top_dir not in directory_groups:
                        directory_groups[top_dir] = []
                    directory_groups[top_dir].append(file_path)
            except ValueError:
                # File not under root path
                root_files.append(file_path)

        # Create groups from directories
        for dir_name, dir_files in directory_groups.items():
            group_type, architectural_role = self._classify_directory(dir_name)
            primary_language = self._detect_primary_language(dir_files)

            groups.append(
                FileGroup(
                    name=f"{dir_name.title()} Module",
                    description=f"Files in the {dir_name} directory",
                    files=dir_files,
                    primary_language=primary_language,
                    group_type=group_type,
                    architectural_role=architectural_role,
                )
            )

        # Handle root files
        if root_files:
            config_files = []
            core_files = []

            for file_path in root_files:
                file_name = file_path.name.lower()
                if any(
                    config in file_name
                    for config in [
                        "config",
                        "setup",
                        "package",
                        "requirements",
                        "makefile",
                    ]
                ):
                    config_files.append(file_path)
                else:
                    core_files.append(file_path)

            if config_files:
                groups.append(
                    FileGroup(
                        name="Project Configuration",
                        description="Root-level configuration and setup files",
                        files=config_files,
                        primary_language=self._detect_primary_language(config_files),
                        group_type="config",
                        architectural_role="Project configuration and build setup",
                    )
                )

            if core_files:
                groups.append(
                    FileGroup(
                        name="Core Files",
                        description="Root-level core application files",
                        files=core_files,
                        primary_language=self._detect_primary_language(core_files),
                        group_type="core",
                        architectural_role="Main application logic and entry points",
                    )
                )

        return groups

    def _classify_directory(self, dir_name: str) -> Tuple[str, str]:
        """Classify directory type and architectural role."""
        dir_lower = dir_name.lower()

        # Test directories
        if any(test in dir_lower for test in ["test", "tests", "spec", "__tests__"]):
            return "test", "Test coverage and quality assurance"

        # Configuration directories
        if any(config in dir_lower for config in ["config", "conf", "settings", "env"]):
            return "config", "Configuration and environment setup"

        # Documentation directories
        if any(doc in dir_lower for doc in ["doc", "docs", "documentation"]):
            return "config", "Project documentation and guides"

        # Source code directories
        if any(src in dir_lower for src in ["src", "source", "lib", "app"]):
            return "core", "Core application source code"

        # Component/feature directories
        if any(
            comp in dir_lower for comp in ["component", "feature", "module", "service"]
        ):
            return "feature", "Feature implementation and business logic"

        # Utility directories
        if any(
            util in dir_lower
            for util in ["util", "utils", "helper", "common", "shared"]
        ):
            return "infrastructure", "Utility functions and shared code"

        # API directories
        if any(api in dir_lower for api in ["api", "handler", "controller", "route"]):
            return "feature", "API endpoints and request handling"

        # Model/data directories
        if any(
            data in dir_lower for data in ["model", "schema", "entity", "data", "db"]
        ):
            return "feature", "Data models and persistence layer"

        # Infrastructure directories
        if any(
            infra in dir_lower
            for infra in ["infra", "deploy", "docker", "k8s", "terraform"]
        ):
            return "infrastructure", "Infrastructure and deployment configuration"

        # Default classification
        return "feature", f"Functionality in the {dir_name} module"

    def _detect_primary_language(self, files: List[Path]) -> str:
        """Detect the primary language of a group of files."""
        extension_counts = {}

        for file_path in files:
            extension = file_path.suffix.lower()
            if extension:
                extension_counts[extension] = extension_counts.get(extension, 0) + 1

        if not extension_counts:
            return "text"

        # Find most common extension
        most_common_ext = max(extension_counts, key=extension_counts.get)

        # Map to language
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".tf": "terraform",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".md": "markdown",
            ".rs": "rust",
            ".java": "java",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        return extension_map.get(most_common_ext, "text")

    # Additional pattern-specific grouping methods for other frameworks...
    def _group_angular_app(self, files: List[Path]) -> List[FileGroup]:
        """Group Angular application files."""
        # Implementation similar to React but with Angular-specific patterns
        return self._group_generically(files)  # Placeholder

    def _group_django_app(self, files: List[Path]) -> List[FileGroup]:
        """Group Django application files."""
        # Implementation with Django-specific patterns (apps, models, views, etc.)
        return self._group_python_project(files)  # Use Python grouping as base

    def _group_python_web_app(self, files: List[Path]) -> List[FileGroup]:
        """Group Flask/FastAPI application files."""
        # Implementation with web framework patterns
        return self._group_python_project(files)  # Use Python grouping as base

    def _group_cpp_project(self, files: List[Path]) -> List[FileGroup]:
        """Group C++ project files."""
        # Implementation with C++ patterns (headers, source, tests, etc.)
        return self._group_generically(files)  # Placeholder

    def _group_helm_chart(self, files: List[Path]) -> List[FileGroup]:
        """Group Helm chart files."""
        # Implementation with Helm patterns (templates, values, charts, etc.)
        return self._group_generically(files)  # Placeholder

    def _group_microservices(self, files: List[Path]) -> List[FileGroup]:
        """Group microservices monorepo files."""
        # Implementation with microservices patterns (services, shared, etc.)
        return self._group_generically(files)  # Placeholder
