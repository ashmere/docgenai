"""
Multi-Chunk Synthesis Prompts for DocGenAI

Prompts for synthesizing documentation from multiple chunks of a codebase.
"""

MULTI_CHUNK_SYNTHESIS_PROMPT = """
You are synthesizing comprehensive documentation from multiple chunks of a
large codebase. Each chunk has been analyzed separately, and now you need
to create a unified, coherent documentation that brings together all the
insights.

CHUNK ANALYSES:
{chunk_analyses}

Your task is to create a comprehensive technical documentation that:

## SYNTHESIS APPROACH
1. **Identify Common Themes**: Look for patterns and themes across chunks
2. **Resolve Conflicts**: Where chunks provide different perspectives,
   synthesize them into a coherent view
3. **Fill Gaps**: Identify missing connections between chunks and infer
   likely relationships
4. **Prioritize Information**: Focus on the most important architectural
   and design insights

## UNIFIED DOCUMENTATION STRUCTURE

### SYSTEM OVERVIEW
- Synthesize a clear picture of what the entire system does
- Identify the core problem it solves and its primary use cases
- Determine the overall system type and architectural approach
- Highlight key business capabilities that emerge from the analysis

### ARCHITECTURE & DESIGN
- Create a unified view of the system architecture
- Identify major components and their relationships
- Describe key architectural patterns and design decisions
- Explain how different parts of the system work together
- Note any architectural inconsistencies or evolution over time

### MAJOR INTERFACES & INTEGRATION POINTS
- Catalog all external APIs and interfaces discovered
- Describe internal component interfaces and contracts
- Identify integration patterns with external systems
- Document data flow between major components
- Highlight any API versioning or evolution patterns

### DATA FLOW & PROCESSING
- Trace data flow through the entire system
- Identify key data transformations and processing stages
- Describe data storage and persistence patterns
- Note caching strategies and performance optimizations
- Document event flows and asynchronous processing

### KEY COMPONENTS & MODULES
For each major component identified across chunks:
- **Purpose and Responsibility**: What it does and why
- **Key Implementation Details**: Important classes, functions, patterns
- **Dependencies**: What it depends on and what depends on it
- **Configuration**: How it's configured and customized
- **Integration Points**: How it connects to other components

### TECHNOLOGY STACK & TOOLS
- Comprehensive list of technologies used across the system
- Development and build tools identified
- Testing frameworks and strategies
- Infrastructure and deployment technologies
- Third-party libraries and dependencies

### DEVELOPER GUIDANCE
- Overall development setup and workflow
- Key patterns and conventions to follow
- Common development tasks and how to approach them
- Testing strategies and best practices
- Debugging and troubleshooting guidance

## SYNTHESIS GUIDELINES
- **Be Comprehensive**: Include insights from all chunks
- **Resolve Inconsistencies**: Where chunks conflict, provide your best
  synthesis
- **Maintain Coherence**: Ensure the final documentation reads as a
  unified whole
- **Highlight Gaps**: Note areas where more information would be helpful
- **Focus on Value**: Prioritize information that helps developers
  understand and work with the system
- **Use Concrete Examples**: Include specific file names, class names,
  and code patterns from the chunks

Create documentation that serves as a comprehensive guide for both systems
engineers who need to understand the architecture and developers who need
to work with the code effectively.
"""

CHUNK_INTEGRATION_PROMPT = """
You have analyzed multiple chunks of a codebase. Now integrate these
analyses into a single, coherent understanding of the system.

INDIVIDUAL CHUNK ANALYSES:
{chunk_analyses}

Focus on these integration tasks:

## ARCHITECTURAL SYNTHESIS
- How do the components in different chunks work together?
- What is the overall system architecture that emerges?
- Are there clear architectural patterns or is it more ad-hoc?
- What are the major subsystems and their boundaries?

## INTERFACE MAPPING
- What are the key interfaces between components found in different chunks?
- How does data flow between the different parts of the system?
- Are there clear API boundaries or tight coupling?
- What external dependencies and integrations exist?

## PATTERN RECOGNITION
- What common patterns appear across multiple chunks?
- Are there consistent coding conventions and architectural approaches?
- What design patterns are used throughout the system?
- Are there any anti-patterns or technical debt areas?

## OPERATIONAL UNDERSTANDING
- How would this system be deployed and operated?
- What are the key configuration points and operational concerns?
- How would you monitor and troubleshoot this system?
- What are the scaling and performance characteristics?

Provide a unified view that helps engineers understand how all the pieces
fit together into a working system.
"""
