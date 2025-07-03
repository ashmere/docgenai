"""
Universal language content extractors for intelligent large file handling.

Provides language-specific content extraction with dynamic size reduction
while preserving essential API information and structure.
"""

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LanguageExtractor(ABC):
    """
    Abstract base class for language-specific content extractors.

    Extracts essential structural elements while reducing file size
    for large file analysis within token limits.
    """

    def __init__(self, language: str):
        """
        Initialize extractor for specific language.

        Args:
            language: Language identifier
        """
        self.language = language
        self.preserve_signatures = True
        self.preserve_types = True
        self.preserve_docs = True
        self.max_function_body_lines = 5
        self.max_class_body_lines = 10

    @abstractmethod
    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """
        Extract structural elements from source code.

        Args:
            content: Source code content
            target_size: Target size in characters (None for no limit)

        Returns:
            Extracted structural content
        """
        pass

    def _truncate_to_target(self, content: str, target_size: int) -> str:
        """
        Intelligently truncate content to target size.

        Args:
            content: Content to truncate
            target_size: Target size in characters

        Returns:
            Truncated content with preservation note
        """
        if len(content) <= target_size:
            return content

        # Try to truncate at natural boundaries
        lines = content.split("\n")
        truncated_lines = []
        current_size = 0

        for line in lines:
            if current_size + len(line) + 1 > target_size * 0.9:  # Leave 10% buffer
                break
            truncated_lines.append(line)
            current_size += len(line) + 1

        truncated = "\n".join(truncated_lines)

        # Add truncation notice
        remaining_lines = len(lines) - len(truncated_lines)
        if remaining_lines > 0:
            truncated += (
                f"\n\n// ... {remaining_lines} more lines truncated for analysis ..."
            )

        return truncated

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements (language-specific implementation)."""
        return []

    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract function signatures (language-specific implementation)."""
        return []

    def _extract_class_definitions(self, content: str) -> List[str]:
        """Extract class definitions (language-specific implementation)."""
        return []

    def _extract_type_definitions(self, content: str) -> List[str]:
        """Extract type definitions (language-specific implementation)."""
        return []

    def _extract_constants(self, content: str) -> List[str]:
        """Extract constants and global variables."""
        return []

    def _extract_comments_and_docs(self, content: str) -> List[str]:
        """Extract documentation comments."""
        return []


class PythonExtractor(LanguageExtractor):
    """Python-specific content extractor."""

    def __init__(self):
        super().__init__("python")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract Python structural elements."""
        extracted_parts = []

        # Extract imports
        imports = self._extract_imports(content)
        if imports:
            extracted_parts.extend(imports)
            extracted_parts.append("")  # Blank line

        # Extract class definitions with minimal bodies
        classes = self._extract_class_definitions(content)
        if classes:
            extracted_parts.extend(classes)
            extracted_parts.append("")

        # Extract function signatures
        functions = self._extract_function_signatures(content)
        if functions:
            extracted_parts.extend(functions)
            extracted_parts.append("")

        # Extract constants
        constants = self._extract_constants(content)
        if constants:
            extracted_parts.extend(constants)
            extracted_parts.append("")

        # Extract module-level docstring
        module_doc = self._extract_module_docstring(content)
        if module_doc:
            extracted_parts.insert(0, module_doc)
            extracted_parts.insert(1, "")

        result = "\n".join(extracted_parts).strip()

        if target_size and len(result) > target_size:
            result = self._truncate_to_target(result, target_size)

        return result

    def _extract_imports(self, content: str) -> List[str]:
        """Extract Python import statements."""
        imports = []

        # Standard imports
        import_patterns = [
            r"^import\s+[\w\.,\s]+",
            r"^from\s+[\w\.]+\s+import\s+[\w\.,\s\*\(\)]+",
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)

        return imports

    def _extract_class_definitions(self, content: str) -> List[str]:
        """Extract Python class definitions with minimal bodies."""
        classes = []

        # Find class definitions
        class_pattern = (
            r'^(class\s+\w+(?:\([^)]*\))?:\s*(?:\n\s*"""[^"]*""")?)(?:\n(.*))?'
        )
        matches = re.finditer(class_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            class_header = match.group(1)
            class_body = match.group(2) if match.group(2) else ""

            # Extract method signatures from class body
            if class_body:
                method_sigs = self._extract_method_signatures(class_body)
                if method_sigs:
                    class_def = (
                        class_header
                        + "\n"
                        + "\n".join(f"    {sig}" for sig in method_sigs[:5])
                    )
                    if len(method_sigs) > 5:
                        class_def += (
                            f"\n    # ... {len(method_sigs) - 5} more methods ..."
                        )
                else:
                    class_def = class_header + "\n    pass"
            else:
                class_def = class_header + "\n    pass"

            classes.append(class_def)

        return classes

    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract Python function signatures."""
        functions = []

        # Find function definitions at module level (not indented)
        func_pattern = (
            r'^(def\s+\w+\s*\([^)]*\)(?:\s*->\s*[^:]+)?:\s*(?:\n\s*"""[^"]*""")?)'
        )
        matches = re.findall(func_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            # Clean up the signature
            sig = match.strip()
            if not sig.endswith(":"):
                sig += ":"

            # Add minimal body
            if '"""' in sig:
                sig += "\n    pass"
            else:
                sig += "\n    pass"

            functions.append(sig)

        return functions

    def _extract_method_signatures(self, class_body: str) -> List[str]:
        """Extract method signatures from class body."""
        methods = []

        method_pattern = r"^\s*(def\s+\w+\s*\([^)]*\)(?:\s*->\s*[^:]+)?:)"
        matches = re.findall(method_pattern, class_body, re.MULTILINE)

        for match in matches:
            methods.append(match.strip() + " ...")

        return methods

    def _extract_constants(self, content: str) -> List[str]:
        """Extract Python constants and module-level variables."""
        constants = []

        # Find module-level assignments (not indented)
        const_pattern = r"^([A-Z_][A-Z0-9_]*\s*=\s*[^\n]+)"
        matches = re.findall(const_pattern, content, re.MULTILINE)
        constants.extend(matches)

        # Find type annotations
        type_pattern = r"^(\w+:\s*\w+(?:\[[^\]]+\])?\s*(?:=\s*[^\n]+)?)"
        matches = re.findall(type_pattern, content, re.MULTILINE)
        constants.extend(matches)

        return constants

    def _extract_module_docstring(self, content: str) -> Optional[str]:
        """Extract module-level docstring."""
        # Look for docstring at the beginning of file (after imports)
        lines = content.split("\n")
        in_docstring = False
        docstring_lines = []
        quote_type = None

        for line in lines:
            stripped = line.strip()

            # Skip empty lines and imports at the beginning
            if not stripped or stripped.startswith(("import ", "from ")):
                continue

            # Check for docstring start
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote_type = stripped[:3]
                    in_docstring = True
                    docstring_lines.append(line)

                    # Check if docstring ends on same line
                    if stripped.count(quote_type) >= 2:
                        break
                else:
                    # No module docstring found
                    break
            else:
                docstring_lines.append(line)
                if quote_type in stripped:
                    break

        if docstring_lines:
            return "\n".join(docstring_lines)

        return None


class TypeScriptExtractor(LanguageExtractor):
    """TypeScript and React-specific content extractor."""

    def __init__(self):
        super().__init__("typescript")
        self.preserve_react_components = True
        self.preserve_props_interfaces = True
        self.preserve_hooks = True

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract TypeScript/React structural elements."""
        extracted_parts = []

        # Extract imports
        imports = self._extract_imports(content)
        if imports:
            extracted_parts.extend(imports)
            extracted_parts.append("")

        # Extract type definitions
        types = self._extract_type_definitions(content)
        if types:
            extracted_parts.extend(types)
            extracted_parts.append("")

        # Extract interfaces
        interfaces = self._extract_interfaces(content)
        if interfaces:
            extracted_parts.extend(interfaces)
            extracted_parts.append("")

        # Extract React components
        components = self._extract_react_components(content)
        if components:
            extracted_parts.extend(components)
            extracted_parts.append("")

        # Extract function signatures
        functions = self._extract_function_signatures(content)
        if functions:
            extracted_parts.extend(functions)
            extracted_parts.append("")

        # Extract constants and exports
        constants = self._extract_constants(content)
        if constants:
            extracted_parts.extend(constants)

        result = "\n".join(extracted_parts).strip()

        if target_size and len(result) > target_size:
            result = self._truncate_to_target(result, target_size)

        return result

    def _extract_imports(self, content: str) -> List[str]:
        """Extract TypeScript import statements."""
        imports = []

        import_patterns = [
            r"^import\s+[^;]+;",
            r"^import\s+type\s+[^;]+;",
            r"^export\s+\*\s+from\s+[^;]+;",
            r"^export\s+\{[^}]+\}\s+from\s+[^;]+;",
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)

        return imports

    def _extract_interfaces(self, content: str) -> List[str]:
        """Extract TypeScript interface definitions."""
        interfaces = []

        interface_pattern = r"^(export\s+)?interface\s+\w+[^{]*\{[^}]*\}"
        matches = re.findall(interface_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            # Clean up the interface
            interface_def = match[1] if isinstance(match, tuple) else match
            interface_def = re.sub(r"\s+", " ", interface_def.strip())
            interfaces.append(interface_def)

        return interfaces

    def _extract_type_definitions(self, content: str) -> List[str]:
        """Extract TypeScript type definitions."""
        types = []

        type_patterns = [
            r"^(export\s+)?type\s+\w+\s*=\s*[^;]+;",
            r"^(export\s+)?enum\s+\w+\s*\{[^}]*\}",
        ]

        for pattern in type_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                type_def = match[1] if isinstance(match, tuple) else match
                types.append(type_def.strip())

        return types

    def _extract_react_components(self, content: str) -> List[str]:
        """Extract React component definitions."""
        components = []

        # Function components
        func_component_patterns = [
            r"^(export\s+)?(const|function)\s+(\w+):\s*React\.FC<[^>]*>\s*=\s*\([^)]*\)\s*=>\s*\{",
            r"^(export\s+)?(const|function)\s+(\w+)\s*=\s*\([^)]*\):\s*JSX\.Element\s*=>\s*\{",
            r"^(export\s+)?function\s+(\w+)\s*\([^)]*\):\s*JSX\.Element\s*\{",
        ]

        for pattern in func_component_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                component_name = match.group(3) if match.group(3) else match.group(2)

                # Extract props interface if present
                props_pattern = rf"interface\s+{component_name}Props\s*\{{[^}}]*\}}"
                props_match = re.search(props_pattern, content, re.DOTALL)

                if props_match:
                    components.append(props_match.group(0))

                # Add simplified component signature
                components.append(
                    f"const {component_name}: React.FC = (props) => {{ /* Component implementation */ }};"
                )

        return components

    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract TypeScript function signatures."""
        functions = []

        func_patterns = [
            r"^(export\s+)?(async\s+)?function\s+(\w+)\s*(\([^)]*\))(\s*:\s*[^{]+)?\s*\{",
            r"^(export\s+)?(const|let)\s+(\w+)\s*:\s*\([^)]*\)\s*=>\s*[^=]+\s*=\s*\([^)]*\)\s*=>\s*\{",
        ]

        for pattern in func_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                func_name = match.group(3)
                params = match.group(4) if len(match.groups()) >= 4 else ""
                return_type = (
                    match.group(5)
                    if len(match.groups()) >= 5 and match.group(5)
                    else ""
                )

                signature = f"function {func_name}{params}{return_type} {{ /* implementation */ }}"
                functions.append(signature)

        return functions

    def _extract_constants(self, content: str) -> List[str]:
        """Extract TypeScript constants and exports."""
        constants = []

        const_patterns = [
            r"^(export\s+)?(const|let)\s+[A-Z_][A-Z0-9_]*\s*[=:][^;]+;",
            r"^export\s+\{[^}]+\};",
            r"^export\s+default\s+[^;]+;",
        ]

        for pattern in const_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                const_def = match[1] if isinstance(match, tuple) else match
                constants.append(const_def.strip())

        return constants


class JavaScriptExtractor(TypeScriptExtractor):
    """JavaScript and React-specific content extractor."""

    def __init__(self):
        super().__init__()
        self.language = "javascript"

    def _extract_interfaces(self, content: str) -> List[str]:
        """JavaScript doesn't have interfaces, return empty list."""
        return []

    def _extract_type_definitions(self, content: str) -> List[str]:
        """JavaScript doesn't have explicit types, extract JSDoc types."""
        types = []

        # Extract JSDoc type definitions
        jsdoc_pattern = r"/\*\*[^*]*\*+(?:[^/*][^*]*\*+)*/\s*(?:function|const|let|var)"
        matches = re.findall(jsdoc_pattern, content, re.DOTALL)
        types.extend(matches)

        return types


class GoExtractor(LanguageExtractor):
    """Go-specific content extractor."""

    def __init__(self):
        super().__init__("go")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract Go structural elements."""
        extracted_parts = []

        # Extract package declaration
        package_decl = self._extract_package_declaration(content)
        if package_decl:
            extracted_parts.append(package_decl)
            extracted_parts.append("")

        # Extract imports
        imports = self._extract_imports(content)
        if imports:
            extracted_parts.extend(imports)
            extracted_parts.append("")

        # Extract type definitions
        types = self._extract_type_definitions(content)
        if types:
            extracted_parts.extend(types)
            extracted_parts.append("")

        # Extract function signatures
        functions = self._extract_function_signatures(content)
        if functions:
            extracted_parts.extend(functions)
            extracted_parts.append("")

        # Extract constants
        constants = self._extract_constants(content)
        if constants:
            extracted_parts.extend(constants)

        result = "\n".join(extracted_parts).strip()

        if target_size and len(result) > target_size:
            result = self._truncate_to_target(result, target_size)

        return result

    def _extract_package_declaration(self, content: str) -> Optional[str]:
        """Extract Go package declaration."""
        match = re.search(r"^package\s+\w+", content, re.MULTILINE)
        return match.group(0) if match else None

    def _extract_imports(self, content: str) -> List[str]:
        """Extract Go import statements."""
        imports = []

        # Single import
        single_imports = re.findall(r'^import\s+"[^"]+"', content, re.MULTILINE)
        imports.extend(single_imports)

        # Multi-line import block
        import_block_pattern = r"import\s*\(\s*([^)]+)\s*\)"
        import_blocks = re.findall(import_block_pattern, content, re.DOTALL)
        for block in import_blocks:
            imports.append(f"import (\n{block.strip()}\n)")

        return imports

    def _extract_type_definitions(self, content: str) -> List[str]:
        """Extract Go type definitions."""
        types = []

        type_patterns = [
            r"^type\s+\w+\s+struct\s*\{[^}]*\}",
            r"^type\s+\w+\s+interface\s*\{[^}]*\}",
            r"^type\s+\w+\s+[^{}\n]+",
        ]

        for pattern in type_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            types.extend(matches)

        return types

    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract Go function signatures."""
        functions = []

        func_pattern = r"^func\s+(?:\([^)]*\)\s+)?(\w+)\s*\([^)]*\)(?:\s*[^{]+)?\s*\{"
        matches = re.finditer(func_pattern, content, re.MULTILINE)

        for match in matches:
            # Extract just the signature without body
            func_start = match.start()
            func_line = content[
                func_start : match.end() - 1
            ]  # Remove the opening brace
            functions.append(func_line + " { /* implementation */ }")

        return functions

    def _extract_constants(self, content: str) -> List[str]:
        """Extract Go constants and variables."""
        constants = []

        const_patterns = [
            r"^const\s+\w+\s*=\s*[^\n]+",
            r"^var\s+\w+\s+\w+(?:\s*=\s*[^\n]+)?",
            r"^const\s*\([^)]+\)",
            r"^var\s*\([^)]+\)",
        ]

        for pattern in const_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            constants.extend(matches)

        return constants


class CppExtractor(LanguageExtractor):
    """C++ specific content extractor."""

    def __init__(self):
        super().__init__("cpp")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract C++ structural elements."""
        extracted_parts = []

        # Extract includes
        includes = self._extract_includes(content)
        if includes:
            extracted_parts.extend(includes)
            extracted_parts.append("")

        # Extract namespace declarations
        namespaces = self._extract_namespaces(content)
        if namespaces:
            extracted_parts.extend(namespaces)
            extracted_parts.append("")

        # Extract class definitions
        classes = self._extract_class_definitions(content)
        if classes:
            extracted_parts.extend(classes)
            extracted_parts.append("")

        # Extract function declarations
        functions = self._extract_function_signatures(content)
        if functions:
            extracted_parts.extend(functions)

        result = "\n".join(extracted_parts).strip()

        if target_size and len(result) > target_size:
            result = self._truncate_to_target(result, target_size)

        return result

    def _extract_includes(self, content: str) -> List[str]:
        """Extract C++ include statements."""
        includes = re.findall(r'^#include\s*[<"][^>"]+[>"]', content, re.MULTILINE)
        return includes

    def _extract_namespaces(self, content: str) -> List[str]:
        """Extract C++ namespace declarations."""
        namespaces = re.findall(r"^namespace\s+\w+\s*\{", content, re.MULTILINE)
        return namespaces

    def _extract_class_definitions(self, content: str) -> List[str]:
        """Extract C++ class definitions."""
        classes = []

        class_pattern = (
            r"^(template\s*<[^>]*>\s*)?(class|struct)\s+(\w+)(?:\s*:\s*[^{]+)?\s*\{"
        )
        matches = re.finditer(class_pattern, content, re.MULTILINE)

        for match in matches:
            class_name = match.group(3)
            template = match.group(1) if match.group(1) else ""
            class_type = match.group(2)

            # Extract public members only
            class_start = match.end()
            brace_count = 1
            class_end = class_start

            for i, char in enumerate(content[class_start:], class_start):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        class_end = i
                        break

            class_body = content[class_start:class_end]

            # Extract public section
            public_section = self._extract_public_section(class_body)

            class_def = f"{template}{class_type} {class_name} {{\npublic:\n{public_section}\n}};"
            classes.append(class_def)

        return classes

    def _extract_public_section(self, class_body: str) -> str:
        """Extract public section from class body."""
        # Find public: section
        public_match = re.search(
            r"public:\s*([^}]*?)(?:private:|protected:|$)", class_body, re.DOTALL
        )
        if public_match:
            public_content = public_match.group(1)

            # Extract method declarations
            methods = re.findall(
                r"^\s*[^/\n]*\([^)]*\)[^{;]*;", public_content, re.MULTILINE
            )
            return "\n".join(f"    {method.strip()}" for method in methods[:5])

        return "    // Public members..."

    def _extract_function_signatures(self, content: str) -> List[str]:
        """Extract C++ function declarations."""
        functions = []

        # Function declarations (not definitions)
        func_pattern = r"^[^/\n]*\w+\s*\([^)]*\)[^{;]*;"
        matches = re.findall(func_pattern, content, re.MULTILINE)

        for match in matches:
            if not any(
                keyword in match for keyword in ["class", "struct", "enum", "#"]
            ):
                functions.append(match.strip())

        return functions


class TerraformExtractor(LanguageExtractor):
    """Terraform-specific content extractor."""

    def __init__(self):
        super().__init__("terraform")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract Terraform structural elements."""
        extracted_parts = []

        # Extract terraform block
        terraform_block = self._extract_terraform_block(content)
        if terraform_block:
            extracted_parts.append(terraform_block)
            extracted_parts.append("")

        # Extract provider blocks
        providers = self._extract_providers(content)
        if providers:
            extracted_parts.extend(providers)
            extracted_parts.append("")

        # Extract variable definitions
        variables = self._extract_variables(content)
        if variables:
            extracted_parts.extend(variables)
            extracted_parts.append("")

        # Extract resource definitions (simplified)
        resources = self._extract_resources(content)
        if resources:
            extracted_parts.extend(resources)
            extracted_parts.append("")

        # Extract outputs
        outputs = self._extract_outputs(content)
        if outputs:
            extracted_parts.extend(outputs)

        result = "\n".join(extracted_parts).strip()

        if target_size and len(result) > target_size:
            result = self._truncate_to_target(result, target_size)

        return result

    def _extract_terraform_block(self, content: str) -> Optional[str]:
        """Extract terraform configuration block."""
        terraform_pattern = r"terraform\s*\{[^}]*\}"
        match = re.search(terraform_pattern, content, re.DOTALL)
        return match.group(0) if match else None

    def _extract_providers(self, content: str) -> List[str]:
        """Extract provider blocks."""
        provider_pattern = r'provider\s+"[^"]+"\s*\{[^}]*\}'
        providers = re.findall(provider_pattern, content, re.DOTALL)
        return providers

    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable definitions."""
        var_pattern = r'variable\s+"[^"]+"\s*\{[^}]*\}'
        variables = re.findall(var_pattern, content, re.DOTALL)
        return variables

    def _extract_resources(self, content: str) -> List[str]:
        """Extract resource definitions (simplified)."""
        resources = []

        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
        matches = re.finditer(resource_pattern, content)

        for match in matches:
            resource_type = match.group(1)
            resource_name = match.group(2)

            # Create simplified resource definition
            simplified = f'resource "{resource_type}" "{resource_name}" {{\n  # Configuration...\n}}'
            resources.append(simplified)

        return resources

    def _extract_outputs(self, content: str) -> List[str]:
        """Extract output definitions."""
        output_pattern = r'output\s+"[^"]+"\s*\{[^}]*\}'
        outputs = re.findall(output_pattern, content, re.DOTALL)
        return outputs


class HelmExtractor(LanguageExtractor):
    """Helm chart template extractor."""

    def __init__(self):
        super().__init__("helm")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract Helm template structural elements."""
        # For Helm templates, preserve the template structure but simplify values
        if target_size and len(content) > target_size:
            return self._truncate_to_target(content, target_size)

        return content


class YamlExtractor(LanguageExtractor):
    """YAML configuration extractor."""

    def __init__(self):
        super().__init__("yaml")

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Extract YAML structural elements."""
        # For YAML, preserve structure but may truncate large values
        if target_size and len(content) > target_size:
            return self._truncate_to_target(content, target_size)

        return content


class GenericExtractor(LanguageExtractor):
    """Generic content extractor for unknown languages."""

    def __init__(self, language: str = "text"):
        super().__init__(language)

    def extract_structure(self, content: str, target_size: Optional[int] = None) -> str:
        """Generic extraction with intelligent truncation."""
        if target_size and len(content) > target_size:
            return self._truncate_to_target(content, target_size)

        return content


class LanguageExtractorFactory:
    """Factory for creating language-specific extractors."""

    EXTRACTORS = {
        "python": PythonExtractor,
        "typescript": TypeScriptExtractor,
        "javascript": JavaScriptExtractor,
        "jsx": JavaScriptExtractor,
        "tsx": TypeScriptExtractor,
        "go": GoExtractor,
        "cpp": CppExtractor,
        "c": CppExtractor,
        "terraform": TerraformExtractor,
        "helm": HelmExtractor,
        "yaml": YamlExtractor,
        "yml": YamlExtractor,
    }

    @classmethod
    def create_extractor(cls, language: str) -> LanguageExtractor:
        """
        Create appropriate extractor for language.

        Args:
            language: Language identifier

        Returns:
            Language-specific extractor instance
        """
        extractor_class = cls.EXTRACTORS.get(language, GenericExtractor)

        if extractor_class == GenericExtractor:
            return extractor_class(language)
        else:
            return extractor_class()

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of languages with specific extractors."""
        return list(cls.EXTRACTORS.keys())

    @classmethod
    def register_extractor(cls, language: str, extractor_class: type):
        """
        Register a custom extractor for a language.

        Args:
            language: Language identifier
            extractor_class: Extractor class
        """
        cls.EXTRACTORS[language] = extractor_class
        logger.info(f"🔧 Registered custom extractor for {language}")
