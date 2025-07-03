# Implementation Plan: DocGenAI - Simplified High-Quality Edition

## 🚨 BREAKING CHANGE: Simplified Architecture (2025-07-03)

**Previous Approach**: Complex semantic analysis with language extractors, pattern detection, and multiple analyzer types.

**New Approach**: LLM-first documentation generation with smart file selection and intelligent chunking.

**Rationale**: The LLM is already excellent at understanding code. Our job is to select the right files, chunk them efficiently, and ask the right questions.

## 1. Project Overview

DocGenAI is a Python-based CLI tool designed to generate high-quality technical documentation for any codebase. The tool uses DeepSeek-V3 with platform-specific optimizations and focuses on practical documentation that serves both systems engineers and junior developers.

**Core Philosophy**: Let the LLM understand the code. Focus on smart file selection and excellent prompts.

**Target Audience**:
1. **Systems Engineers**: Need to understand architecture, interfaces, and data flow quickly
2. **Junior Developers**: Need onboarding information to add features effectively

## 2. Core Features

- **Smart File Selection**: Intelligent heuristics to identify the most important files
- **Intelligent Chunking**: Token-aware chunking that respects LLM context limits
- **High-Quality Prompts**: Purpose-specific prompts organized in `prompts/` directory
- **Chain Processing**: Configurable prompt chains for documentation refinement
- **Platform Optimization**: Automatic model selection (MLX on macOS, Transformers elsewhere)
- **Universal Language Support**: Works with any programming language
- **Template-Driven Output**: Customizable documentation templates
- **Simple Caching**: Efficient caching to avoid regeneration

## 3. Simplified Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Smart File     │    │  Intelligent    │    │  Documentation  │
│  Selector       │───▶│  Chunker        │───▶│  Generator      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  File           │    │  Token-Aware    │    │  Prompt Chain   │
│  Heuristics     │    │  Chunking       │    │  Processing     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 4. Project Structure

```text
docgenai/
├── src/docgenai/
│   ├── __init__.py
│   ├── cli.py                    # Click CLI interface
│   ├── models.py                 # DeepSeek-V3 with platform detection
│   ├── core.py                   # Simplified documentation generator
│   ├── file_selector.py          # Smart file selection heuristics
│   ├── chunker.py                # Intelligent token-aware chunking
│   ├── config.py                 # Configuration management
│   ├── cache.py                  # Simple generation caching
│   ├── templates.py              # Template loading and rendering
│   ├── chaining/                 # Prompt chain system (RETAINED)
│   │   ├── __init__.py
│   │   ├── chain.py
│   │   ├── context.py
│   │   └── step.py
│   ├── prompts/                  # Purpose-specific prompts (NEW)
│   │   ├── __init__.py
│   │   ├── architecture.py       # Architecture analysis prompts
│   │   ├── synthesis.py          # Multi-chunk synthesis prompts
│   │   ├── refinement.py         # Documentation refinement prompts
│   │   └── base.py               # Base prompt templates
│   └── templates/
│       ├── default_doc_template.md
│       └── directory_summary_template.md
├── docs/
│   ├── developer.md              # Development guide
│   ├── plan.md                   # This file
│   └── architecture.md           # System architecture (MAINTAINED)
├── tests/                        # Test suite
├── config.yaml                   # Configuration
└── README.md                     # User guide
```

## 5. Implementation Plan

### Phase 1: Core Simplification (Week 1) ✅ COMPLETE

**Goal**: Replace complex analysis with simple, effective components

**Tasks**:
- [x] Implement `SmartFileSelector` with heuristics-based selection
- [x] Create `IntelligentChunker` for token-aware chunking
- [x] Simplify `DocumentationGenerator` to use new components
- [x] Organize prompts into purpose-specific files in `prompts/` directory
- [x] Maintain prompt chain system for refinement workflows

### Phase 2: Prompt Excellence (Week 1-2) ⚡ PRIORITY

**Goal**: Create high-quality prompts that produce excellent documentation

**Tasks**:
- [ ] Design architecture analysis prompt for systems engineers
- [ ] Create developer onboarding prompt for junior developers
- [ ] Implement multi-chunk synthesis for large codebases
- [ ] Build documentation refinement chains
- [ ] Test and iterate on prompt quality

### Phase 3: Testing & Validation (Week 2-3)

**Goal**: Ensure system works reliably across different codebase types and sizes

**Tasks**:
- [ ] Test on small codebases (10-50 files)
- [ ] Test on medium codebases (100-500 files)
- [ ] Test on large codebases (1000+ files)
- [ ] Validate against success criteria
- [ ] Performance optimization

## 6. Smart File Selection Strategy

### Heuristics-Based Selection

```python
class SmartFileSelector:
    def select_important_files(self, codebase_path: Path) -> List[Path]:
        """Select files using intelligent heuristics."""

        important_files = []

        # 1. Entry points (main.py, index.js, app.py, etc.)
        important_files.extend(self._find_entry_points(codebase_path))

        # 2. Configuration files (package.json, requirements.txt, etc.)
        important_files.extend(self._find_config_files(codebase_path))

        # 3. API/Interface files (routes, controllers, services)
        important_files.extend(self._find_api_files(codebase_path))

        # 4. Core business logic (largest/most connected files)
        important_files.extend(self._find_core_files(codebase_path))

        # 5. Documentation files (README, docs)
        important_files.extend(self._find_documentation_files(codebase_path))

        return self._prioritize_and_limit(important_files, max_files=50)
```

### File Priority Patterns

```python
ENTRY_POINT_PATTERNS = [
    "main.py", "app.py", "server.py", "__main__.py",
    "index.js", "server.js", "app.js", "main.js",
    "main.go", "cmd/*/main.go", "src/main/*"
]

API_PATTERNS = [
    "**/routes/**", "**/controllers/**", "**/handlers/**",
    "**/api/**", "**/endpoints/**", "**/services/**"
]

CONFIG_PATTERNS = [
    "package.json", "requirements.txt", "go.mod", "Cargo.toml",
    "pom.xml", "build.gradle", "*.config.*", "docker-compose.*"
]
```

## 7. Intelligent Chunking Strategy

### Token-Aware Chunking

```python
class IntelligentChunker:
    def chunk_for_llm(self, files: List[Path], max_tokens: int) -> List[Dict]:
        """Chunk files intelligently for LLM consumption."""

        chunks = []
        current_chunk = []
        current_tokens = 0
        safety_margin = 0.8  # Use 80% of context

        for file_path in files:
            file_content = self._read_file_smart(file_path)
            file_tokens = self._estimate_tokens(file_content)

            if current_tokens + file_tokens > max_tokens * safety_margin:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk))
                    current_chunk = [file_path]
                    current_tokens = file_tokens
                else:
                    # Single file too large, extract signatures only
                    chunks.extend(self._split_large_file(file_path, max_tokens))
            else:
                current_chunk.append(file_path)
                current_tokens += file_tokens

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk))

        return chunks
```

### Smart File Reading

```python
def _read_file_smart(self, file_path: Path) -> str:
    """Read file, extracting signatures if too large."""
    content = file_path.read_text(encoding='utf-8', errors='ignore')

    if len(content) > 5000:  # Threshold for signature extraction
        return self._extract_signatures(content, file_path.suffix)

    return content

def _extract_signatures(self, content: str, extension: str) -> str:
    """Extract function/class signatures, imports, and structure."""
    lines = content.split('\n')
    important_lines = []

    for line in lines:
        stripped = line.strip()
        # Keep structural elements across languages
        if (stripped.startswith(('import ', 'from ', 'class ', 'def ', 'function ',
                               'interface ', 'type ', 'const ', 'let ', 'var ',
                               'public ', 'private ', 'protected ', '//', '#')) or
            len(stripped) == 0 or  # Empty lines for structure
            '{' in stripped or '}' in stripped):  # Braces for structure
            important_lines.append(line)

    return '\n'.join(important_lines)
```

## 8. High-Quality Prompt System

### Architecture Analysis Prompt

```python
# prompts/architecture.py
ARCHITECTURE_ANALYSIS_PROMPT = """
You are analyzing a codebase to create documentation for systems engineers and developers.

CODEBASE FILES:
{file_contents}

Create comprehensive documentation with these sections:

## SYSTEM OVERVIEW
- What does this application/system do?
- What problem does it solve?
- What type of system is it? (web app, API, CLI tool, library, etc.)

## ARCHITECTURE & DESIGN
- Overall architecture pattern (MVC, microservices, layered, etc.)
- Key architectural decisions and trade-offs
- Main components and their responsibilities

## MAJOR INTERFACES & APIs
- External APIs (REST endpoints, GraphQL, etc.)
- Internal interfaces between components
- Data contracts and schemas
- Integration points with other systems

## DATA FLOW
- How data moves through the system
- Key data transformations
- Database/storage patterns
- Event flows (if applicable)

## KEY FILES & COMPONENTS
For each major component:
- Purpose and responsibility
- Key classes/functions
- Dependencies and relationships
- Configuration and entry points

## DEVELOPER ONBOARDING
- Setup and running instructions
- Key patterns and conventions
- Where to start when adding features
- Common development workflows

Focus on practical insights. Be specific about file names, class names, and code structure.
"""
```

### Refinement Chain

```python
# prompts/refinement.py
DOCUMENTATION_REFINEMENT_CHAIN = PromptChain([
    PromptStep(
        name="initial_analysis",
        prompt=ARCHITECTURE_ANALYSIS_PROMPT,
        output_key="base_documentation"
    ),
    PromptStep(
        name="enhance_interfaces",
        prompt="""
        Enhance the MAJOR INTERFACES & APIs section:

        {base_documentation}

        Add specific details about:
        - API endpoint specifications
        - Request/response formats
        - Authentication/authorization
        - Error handling patterns
        """,
        output_key="enhanced_interfaces"
    ),
    PromptStep(
        name="add_dataflow",
        prompt="""
        Enhance the DATA FLOW section:

        {enhanced_interfaces}

        Add detailed information about:
        - Step-by-step data processing flows
        - Database interaction patterns
        - Caching strategies
        - Error handling and rollback procedures
        """,
        output_key="enhanced_dataflow"
    ),
    PromptStep(
        name="final_polish",
        prompt="""
        Polish and finalize the documentation:

        {enhanced_dataflow}

        Final improvements:
        - Ensure consistency in terminology
        - Add practical examples where helpful
        - Verify completeness
        - Optimize for readability
        """,
        output_key="final_documentation"
    )
])
```

## 9. Success Criteria

### For Systems Engineers
- [ ] Clear architecture overview in 2-3 paragraphs
- [ ] Major components and relationships identified
- [ ] API interfaces and data contracts documented
- [ ] Data flow through system explained
- [ ] Key design decisions and patterns explained

### For Junior Developers
- [ ] Setup and running instructions
- [ ] Key files and starting points identified
- [ ] Common patterns and conventions explained
- [ ] Guidance on where to add new features
- [ ] Development workflow documented

### Technical Requirements
- [ ] Works on codebases from 10 files to 1000+ files
- [ ] Generates documentation in under 5 minutes
- [ ] Uses available context efficiently
- [ ] Produces consistent, high-quality output
- [ ] Maintains prompt chain capability for refinement

## 10. Removed Complexity (Breaking Changes)

### ❌ Eliminated Components
- **Semantic Grouping**: Complex file organization algorithms
- **Language Extractors**: Regex-based content extraction
- **Pattern Detection**: Project type detection systems
- **Multiple Analyzers**: Enhanced vs legacy analyzer confusion
- **Over-Engineering**: Complex configuration systems

### ✅ Retained Components
- **Prompt Chains**: For documentation refinement workflows
- **Purpose-Specific Prompts**: Organized in `prompts/` directory
- **Model Abstraction**: Platform-aware model selection
- **Template System**: Customizable output formatting
- **Simple Caching**: Efficient caching system
- **CLI Interface**: User-friendly command-line interface

## 11. Configuration (Simplified)

```yaml
# config.yaml
model:
  temperature: 0.1
  max_tokens: 4000
  context_limit: 16384  # Auto-detected

file_selection:
  max_files: 50
  max_file_size: 10000  # chars
  include_patterns: ["*.py", "*.js", "*.ts", "*.go", "*.java"]
  exclude_patterns: ["*/node_modules/*", "*/__pycache__/*"]

chunking:
  max_chunk_tokens: 12000  # 75% of context limit
  overlap_tokens: 500
  prefer_file_boundaries: true

chains:
  default_strategy: "single_pass"  # or "refinement_chain"
  enable_synthesis: true

output:
  template: "default"
  include_file_tree: true
  include_setup_instructions: true

cache:
  enabled: true
  directory: ".docgenai_cache"
  ttl_hours: 24
```

## 12. Implementation Timeline

### Week 1: Core Implementation
- **Day 1-2**: Implement `SmartFileSelector` and `IntelligentChunker`
- **Day 3-4**: Create high-quality prompts in organized structure
- **Day 5-6**: Simplify `DocumentationGenerator` and integrate components
- **Day 7**: Initial testing and refinement

### Week 2: Testing and Validation
- **Day 1-3**: Test on various codebase sizes and types
- **Day 4-5**: Refine prompts based on output quality
- **Day 6-7**: Performance optimization and bug fixes

### Week 3: Polish and Documentation
- **Day 1-2**: Update documentation and architecture diagrams
- **Day 3-4**: CLI improvements and user experience
- **Day 5-7**: Final testing and release preparation

## 13. Architecture Documentation

The system architecture and data flow diagrams are maintained in `docs/architecture.md` and updated with each implementation change to ensure they remain current and accurate.

---

This simplified approach focuses on what matters: selecting the right files, asking the right questions, and letting the LLM do what it does best - understand and explain code.
