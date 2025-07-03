"""
Project pattern detection and classification.

Defines common project patterns and provides detection logic
for various project types and frameworks.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class StructurePattern:
    """
    Represents a project structure pattern.

    Defines the characteristics that identify a specific
    project type or framework structure.
    """

    name: str
    description: str
    required_files: List[str]
    required_dirs: List[str]
    optional_files: List[str]
    optional_dirs: List[str]
    file_patterns: List[str]
    priority: int = 0
    language_hints: List[str] = None

    def __post_init__(self):
        if self.language_hints is None:
            self.language_hints = []


class ProjectPatterns:
    """
    Collection of project patterns for detection.

    Provides patterns for common project types across
    different languages and frameworks.
    """

    # Web Frontend Patterns
    REACT_APP = StructurePattern(
        name="react_app",
        description="React application",
        required_files=["package.json"],
        required_dirs=["src"],
        optional_files=["tsconfig.json", "webpack.config.js", "vite.config.ts"],
        optional_dirs=["public", "components", "hooks", "pages", "styles"],
        file_patterns=["*.jsx", "*.tsx", "*.js", "*.ts"],
        priority=8,
        language_hints=["javascript", "typescript", "jsx", "tsx"],
    )

    NEXT_APP = StructurePattern(
        name="nextjs_app",
        description="Next.js application",
        required_files=["package.json", "next.config.js"],
        required_dirs=["pages", "src"],
        optional_files=["tsconfig.json"],
        optional_dirs=["public", "components", "styles", "api", "lib"],
        file_patterns=["*.jsx", "*.tsx", "*.js", "*.ts"],
        priority=9,
        language_hints=["javascript", "typescript", "jsx", "tsx"],
    )

    VUE_APP = StructurePattern(
        name="vue_app",
        description="Vue.js application",
        required_files=["package.json", "vue.config.js"],
        required_dirs=["src"],
        optional_files=["tsconfig.json"],
        optional_dirs=["public", "components", "views", "router", "store"],
        file_patterns=["*.vue", "*.js", "*.ts"],
        priority=8,
        language_hints=["javascript", "typescript", "vue"],
    )

    ANGULAR_APP = StructurePattern(
        name="angular_app",
        description="Angular application",
        required_files=["package.json", "angular.json"],
        required_dirs=["src"],
        optional_files=["tsconfig.json"],
        optional_dirs=["app", "assets", "environments"],
        file_patterns=["*.ts", "*.html", "*.scss", "*.css"],
        priority=9,
        language_hints=["typescript", "javascript"],
    )

    # Backend Patterns
    PYTHON_PACKAGE = StructurePattern(
        name="python_package",
        description="Python package/library",
        required_files=["setup.py", "pyproject.toml"],
        required_dirs=["src"],
        optional_files=["requirements.txt", "setup.cfg", "tox.ini"],
        optional_dirs=["tests", "docs"],
        file_patterns=["*.py"],
        priority=7,
        language_hints=["python"],
    )

    PYTHON_APP = StructurePattern(
        name="python_app",
        description="Python application",
        required_files=["main.py", "app.py", "run.py"],
        required_dirs=[],
        optional_files=["requirements.txt", "config.py", "settings.py"],
        optional_dirs=["src", "lib", "utils", "models", "views", "controllers"],
        file_patterns=["*.py"],
        priority=6,
        language_hints=["python"],
    )

    DJANGO_APP = StructurePattern(
        name="django_app",
        description="Django application",
        required_files=["manage.py", "settings.py"],
        required_dirs=["apps", "templates"],
        optional_files=["requirements.txt", "urls.py"],
        optional_dirs=["static", "media", "locale"],
        file_patterns=["*.py"],
        priority=9,
        language_hints=["python"],
    )

    FLASK_APP = StructurePattern(
        name="flask_app",
        description="Flask application",
        required_files=["app.py", "run.py"],
        required_dirs=[],
        optional_files=["requirements.txt", "config.py"],
        optional_dirs=["templates", "static", "models", "views"],
        file_patterns=["*.py"],
        priority=8,
        language_hints=["python"],
    )

    FASTAPI_APP = StructurePattern(
        name="fastapi_app",
        description="FastAPI application",
        required_files=["main.py"],
        required_dirs=["routers", "models"],
        optional_files=["requirements.txt", "config.py"],
        optional_dirs=["schemas", "database", "auth", "utils"],
        file_patterns=["*.py"],
        priority=8,
        language_hints=["python"],
    )

    # Go Patterns
    GO_MODULE = StructurePattern(
        name="go_module",
        description="Go module",
        required_files=["go.mod"],
        required_dirs=[],
        optional_files=["go.sum", "main.go"],
        optional_dirs=["cmd", "internal", "pkg", "api", "web"],
        file_patterns=["*.go"],
        priority=8,
        language_hints=["go"],
    )

    GO_CLI = StructurePattern(
        name="go_cli",
        description="Go CLI application",
        required_files=["go.mod", "main.go"],
        required_dirs=["cmd"],
        optional_files=["go.sum"],
        optional_dirs=["internal", "pkg"],
        file_patterns=["*.go"],
        priority=9,
        language_hints=["go"],
    )

    # C++ Patterns
    CMAKE_PROJECT = StructurePattern(
        name="cmake_project",
        description="CMake C++ project",
        required_files=["CMakeLists.txt"],
        required_dirs=["src"],
        optional_files=["conanfile.txt", "vcpkg.json"],
        optional_dirs=["include", "lib", "test", "docs"],
        file_patterns=["*.cpp", "*.hpp", "*.c", "*.h"],
        priority=8,
        language_hints=["cpp", "c"],
    )

    HEADER_ONLY = StructurePattern(
        name="header_only_lib",
        description="Header-only C++ library",
        required_files=[],
        required_dirs=["include"],
        optional_files=["CMakeLists.txt"],
        optional_dirs=["test", "example", "docs"],
        file_patterns=["*.hpp", "*.h"],
        priority=7,
        language_hints=["cpp", "c"],
    )

    # DevOps Patterns
    TERRAFORM_MODULE = StructurePattern(
        name="terraform_module",
        description="Terraform module",
        required_files=["main.tf", "variables.tf", "outputs.tf"],
        required_dirs=[],
        optional_files=["versions.tf", "terraform.tfvars"],
        optional_dirs=["modules", "examples"],
        file_patterns=["*.tf", "*.tfvars"],
        priority=9,
        language_hints=["terraform"],
    )

    TERRAFORM_PROJECT = StructurePattern(
        name="terraform_project",
        description="Terraform project",
        required_files=["main.tf"],
        required_dirs=[],
        optional_files=["variables.tf", "outputs.tf", "terraform.tfvars"],
        optional_dirs=["modules", "environments"],
        file_patterns=["*.tf", "*.tfvars"],
        priority=7,
        language_hints=["terraform"],
    )

    HELM_CHART = StructurePattern(
        name="helm_chart",
        description="Helm chart",
        required_files=["Chart.yaml"],
        required_dirs=["templates"],
        optional_files=["values.yaml"],
        optional_dirs=["charts", "crds"],
        file_patterns=["*.yaml", "*.yml"],
        priority=9,
        language_hints=["yaml", "helm"],
    )

    KUBERNETES_MANIFESTS = StructurePattern(
        name="k8s_manifests",
        description="Kubernetes manifests",
        required_files=[],
        required_dirs=["manifests", "k8s", "kubernetes"],
        optional_files=["kustomization.yaml"],
        optional_dirs=["base", "overlays"],
        file_patterns=["*.yaml", "*.yml"],
        priority=6,
        language_hints=["yaml"],
    )

    # Microservices Patterns
    MICROSERVICE_MONO = StructurePattern(
        name="microservice_monorepo",
        description="Microservices monorepo",
        required_files=[],
        required_dirs=["services", "shared", "libs"],
        optional_files=["docker-compose.yml"],
        optional_dirs=["infrastructure", "docs", "scripts"],
        file_patterns=["*"],
        priority=8,
        language_hints=[],
    )

    DOCKER_COMPOSE = StructurePattern(
        name="docker_compose",
        description="Docker Compose application",
        required_files=["docker-compose.yml"],
        required_dirs=[],
        optional_files=["Dockerfile", ".env"],
        optional_dirs=["services", "config"],
        file_patterns=["*.yml", "*.yaml"],
        priority=7,
        language_hints=["yaml"],
    )

    # Data Science Patterns
    JUPYTER_PROJECT = StructurePattern(
        name="jupyter_project",
        description="Jupyter notebook project",
        required_files=[],
        required_dirs=["notebooks"],
        optional_files=["requirements.txt", "environment.yml"],
        optional_dirs=["data", "src", "models", "reports"],
        file_patterns=["*.ipynb", "*.py"],
        priority=6,
        language_hints=["python"],
    )

    ML_PROJECT = StructurePattern(
        name="ml_project",
        description="Machine learning project",
        required_files=["requirements.txt"],
        required_dirs=["data", "models", "src"],
        optional_files=["setup.py", "config.yaml"],
        optional_dirs=["notebooks", "experiments", "reports"],
        file_patterns=["*.py", "*.ipynb"],
        priority=7,
        language_hints=["python"],
    )

    # Generic Patterns
    GENERIC_LIBRARY = StructurePattern(
        name="generic_library",
        description="Generic library/package",
        required_files=[],
        required_dirs=["src", "lib"],
        optional_files=["README.md"],
        optional_dirs=["test", "tests", "docs", "examples"],
        file_patterns=["*"],
        priority=3,
        language_hints=[],
    )

    GENERIC_APP = StructurePattern(
        name="generic_app",
        description="Generic application",
        required_files=["main.*", "app.*", "index.*"],
        required_dirs=[],
        optional_files=["config.*", "settings.*"],
        optional_dirs=["src", "lib", "utils"],
        file_patterns=["*"],
        priority=2,
        language_hints=[],
    )

    @classmethod
    def get_all_patterns(cls) -> List[StructurePattern]:
        """Get all defined patterns sorted by priority."""
        patterns = []

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, StructurePattern):
                patterns.append(attr)

        # Sort by priority (highest first)
        patterns.sort(key=lambda p: p.priority, reverse=True)
        return patterns

    @classmethod
    def get_patterns_by_language(cls, language: str) -> List[StructurePattern]:
        """Get patterns that support a specific language."""
        patterns = []

        for pattern in cls.get_all_patterns():
            if not pattern.language_hints or language in pattern.language_hints:
                patterns.append(pattern)

        return patterns

    @classmethod
    def get_pattern_by_name(cls, name: str) -> Optional[StructurePattern]:
        """Get a specific pattern by name."""
        for pattern in cls.get_all_patterns():
            if pattern.name == name:
                return pattern
        return None


class ProjectPatternDetector:
    """
    Detects project patterns based on file system structure.

    Analyzes directory structure and file patterns to identify
    the most likely project type.
    """

    def __init__(self, root_path: Path):
        """
        Initialize detector for a project root.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path
        self.file_cache: Dict[str, Set[str]] = {}
        self.dir_cache: Dict[str, Set[str]] = {}

    def detect_patterns(
        self, max_depth: int = 3
    ) -> List[Tuple[StructurePattern, float]]:
        """
        Detect project patterns with confidence scores.

        Args:
            max_depth: Maximum directory depth to analyze

        Returns:
            List of (pattern, confidence_score) tuples sorted by confidence
        """
        logger.info(f"🔍 Detecting project patterns in {self.root_path}")

        # Scan directory structure
        self._scan_structure(max_depth)

        # Score each pattern
        pattern_scores = []

        for pattern in ProjectPatterns.get_all_patterns():
            score = self._score_pattern(pattern)
            if score > 0:
                pattern_scores.append((pattern, score))

        # Sort by score (highest first)
        pattern_scores.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"📊 Found {len(pattern_scores)} matching patterns")
        for pattern, score in pattern_scores[:3]:  # Log top 3
            logger.info(f"  - {pattern.name}: {score:.2f}")

        return pattern_scores

    def _scan_structure(self, max_depth: int):
        """Scan directory structure and cache results."""
        logger.debug(f"📁 Scanning structure (max depth: {max_depth})")

        # Reset caches
        self.file_cache.clear()
        self.dir_cache.clear()

        # Scan directories
        for depth in range(max_depth + 1):
            depth_key = f"depth_{depth}"
            self.file_cache[depth_key] = set()
            self.dir_cache[depth_key] = set()

            # Find all paths at this depth
            if depth == 0:
                paths = [self.root_path]
            else:
                paths = []
                for path in self.root_path.rglob("*"):
                    if len(path.parts) - len(self.root_path.parts) == depth:
                        paths.append(path)

            # Categorize paths
            for path in paths:
                relative_path = path.relative_to(self.root_path)

                if path.is_file():
                    self.file_cache[depth_key].add(str(relative_path))
                    self.file_cache[depth_key].add(path.name)  # Also add filename
                elif path.is_dir():
                    self.dir_cache[depth_key].add(str(relative_path))
                    self.dir_cache[depth_key].add(path.name)  # Also add dirname

        # Create combined caches
        self.file_cache["all"] = set()
        self.dir_cache["all"] = set()

        for depth_key in self.file_cache:
            if depth_key != "all":
                self.file_cache["all"].update(self.file_cache[depth_key])

        for depth_key in self.dir_cache:
            if depth_key != "all":
                self.dir_cache["all"].update(self.dir_cache[depth_key])

    def _score_pattern(self, pattern: StructurePattern) -> float:
        """
        Score how well a pattern matches the project structure.

        Args:
            pattern: Pattern to score

        Returns:
            Confidence score (0.0 to 1.0)
        """
        score = 0.0
        max_score = 0.0

        # Required files (high weight)
        if pattern.required_files:
            max_score += 30
            required_found = 0

            for req_file in pattern.required_files:
                if self._file_exists(req_file):
                    required_found += 1

            if required_found == len(pattern.required_files):
                score += 30  # Full points if all required files found
            elif required_found > 0:
                score += 15  # Partial points if some found
            else:
                return 0.0  # No match if required files missing

        # Required directories (high weight)
        if pattern.required_dirs:
            max_score += 25
            required_found = 0

            for req_dir in pattern.required_dirs:
                if self._dir_exists(req_dir):
                    required_found += 1

            if required_found == len(pattern.required_dirs):
                score += 25
            elif required_found > 0:
                score += 12
            else:
                return 0.0  # No match if required directories missing

        # Optional files (medium weight)
        if pattern.optional_files:
            max_score += 20
            optional_found = 0

            for opt_file in pattern.optional_files:
                if self._file_exists(opt_file):
                    optional_found += 1

            if optional_found > 0:
                score += (optional_found / len(pattern.optional_files)) * 20

        # Optional directories (medium weight)
        if pattern.optional_dirs:
            max_score += 15
            optional_found = 0

            for opt_dir in pattern.optional_dirs:
                if self._dir_exists(opt_dir):
                    optional_found += 1

            if optional_found > 0:
                score += (optional_found / len(pattern.optional_dirs)) * 15

        # File patterns (low weight)
        if pattern.file_patterns:
            max_score += 10
            pattern_matches = 0

            for file_pattern in pattern.file_patterns:
                if self._pattern_matches(file_pattern):
                    pattern_matches += 1

            if pattern_matches > 0:
                score += (pattern_matches / len(pattern.file_patterns)) * 10

        # Normalize score
        if max_score > 0:
            normalized_score = score / max_score

            # Apply priority boost
            priority_boost = pattern.priority / 10.0
            final_score = min(1.0, normalized_score + priority_boost)

            return final_score

        return 0.0

    def _file_exists(self, filename: str) -> bool:
        """Check if a file exists in the project."""
        return filename in self.file_cache["all"]

    def _dir_exists(self, dirname: str) -> bool:
        """Check if a directory exists in the project."""
        return dirname in self.dir_cache["all"]

    def _pattern_matches(self, pattern: str) -> bool:
        """Check if any files match the pattern."""
        if pattern == "*":
            return True

        # Simple pattern matching for now
        if pattern.startswith("*."):
            extension = pattern[2:]
            for filename in self.file_cache["all"]:
                if filename.endswith(f".{extension}"):
                    return True

        return False

    def get_primary_language(self) -> Optional[str]:
        """
        Determine the primary language based on file extensions.

        Returns:
            Primary language identifier or None
        """
        extension_counts = {}

        for filename in self.file_cache["all"]:
            if "." in filename:
                extension = filename.split(".")[-1].lower()
                extension_counts[extension] = extension_counts.get(extension, 0) + 1

        if not extension_counts:
            return None

        # Map extensions to languages
        extension_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "jsx": "javascript",
            "tsx": "typescript",
            "go": "go",
            "cpp": "cpp",
            "cc": "cpp",
            "cxx": "cpp",
            "c": "c",
            "h": "c",
            "hpp": "cpp",
            "tf": "terraform",
            "yaml": "yaml",
            "yml": "yaml",
            "java": "java",
            "rs": "rust",
            "rb": "ruby",
            "php": "php",
            "cs": "csharp",
            "swift": "swift",
            "kt": "kotlin",
            "scala": "scala",
        }

        # Find most common extension
        most_common_ext = max(extension_counts, key=extension_counts.get)
        return extension_map.get(most_common_ext, "unknown")

    def get_structure_summary(self) -> Dict[str, any]:
        """
        Get a summary of the project structure.

        Returns:
            Dictionary with structure information
        """
        return {
            "root_path": str(self.root_path),
            "total_files": len(self.file_cache.get("all", set())),
            "total_dirs": len(self.dir_cache.get("all", set())),
            "primary_language": self.get_primary_language(),
            "detected_patterns": [
                {"name": pattern.name, "confidence": score}
                for pattern, score in self.detect_patterns()[:5]
            ],
            "file_types": self._get_file_type_distribution(),
            "directory_structure": self._get_directory_structure(),
        }

    def _get_file_type_distribution(self) -> Dict[str, int]:
        """Get distribution of file types."""
        extension_counts = {}

        for filename in self.file_cache.get("all", set()):
            if "." in filename:
                extension = filename.split(".")[-1].lower()
                extension_counts[extension] = extension_counts.get(extension, 0) + 1

        return extension_counts

    def _get_directory_structure(self) -> List[str]:
        """Get list of main directories."""
        main_dirs = []

        for dirname in self.dir_cache.get("depth_1", set()):
            if "/" not in dirname:  # Only top-level directories
                main_dirs.append(dirname)

        return sorted(main_dirs)
