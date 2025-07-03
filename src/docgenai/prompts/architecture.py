"""
Architecture Analysis Prompts for DocGenAI

High-quality prompts designed to generate excellent technical documentation
for systems engineers and developers who need to understand codebases.
"""

from .base_prompts import BasePromptBuilder


class ArchitecturePromptBuilder(BasePromptBuilder):
    """Builder for architecture analysis prompts."""

    def build_architecture_analysis_prompt(self, file_contents: str) -> str:
        """Build the main architecture analysis prompt."""
        return ARCHITECTURE_ANALYSIS_PROMPT.format(file_contents=file_contents)

    def build_systems_engineer_prompt(self, file_contents: str) -> str:
        """Build the systems engineer focused prompt."""
        return SYSTEMS_ENGINEER_PROMPT.format(file_contents=file_contents)

    def build_junior_developer_prompt(self, file_contents: str) -> str:
        """Build the junior developer focused prompt."""
        return JUNIOR_DEVELOPER_PROMPT.format(file_contents=file_contents)


# Create a builder instance to get the formatting rules
_builder = ArchitecturePromptBuilder()

ARCHITECTURE_ANALYSIS_PROMPT = f"""
You are analyzing a codebase to create comprehensive technical documentation
for systems engineers and developers. Your goal is to help them understand
the architecture, interfaces, and design patterns effectively.

{_builder.MARKDOWN_FORMATTING_RULES}

CODEBASE CONTENT:
{{file_contents}}

Generate well-formatted markdown documentation with these sections:

## SYSTEM OVERVIEW
- What does this application/system do? (core purpose and value)
- What problem does it solve and for whom?
- What type of system is it? (web app, API, CLI tool, library, etc.)
- Key business capabilities and use cases

## ARCHITECTURE & DESIGN
- Overall architecture pattern (MVC, microservices, layered,
  event-driven, etc.)
- Key architectural decisions and trade-offs made
- Major components and their responsibilities
- How components interact and communicate
- Design patterns used (Factory, Observer, Strategy, etc.)
- Scalability and performance considerations

## MAJOR INTERFACES & APIs
- External APIs exposed (REST endpoints, GraphQL, gRPC, etc.)
- Request/response formats and data models
- Authentication and authorization mechanisms
- Internal interfaces between components
- Database schemas and data contracts
- Integration points with other systems
- Error handling and response patterns

## DATA FLOW & PROCESSING
- How data enters the system (inputs, events, requests)
- Key data transformations and processing steps
- Data storage patterns and persistence layer
- Caching strategies and performance optimizations
- Event flows and message passing (if applicable)
- Data validation and sanitization approaches

## KEY FILES & COMPONENTS
For each major component, provide:
- **Purpose**: What this component does and why it exists
- **Key classes/functions**: Most important code elements
- **Dependencies**: What it depends on and what depends on it
- **Configuration**: How it's configured and customized
- **Entry points**: How to interact with or extend it

## TECHNOLOGY STACK
- Programming languages and versions
- Frameworks and libraries used
- Database technologies and data stores
- Infrastructure and deployment technologies
- Build tools and development workflow
- Testing frameworks and strategies

## DEVELOPER ONBOARDING
- **Setup instructions**: How to get the system running locally
- **Key patterns**: Important coding patterns and conventions to follow
- **Extension points**: Where and how to add new features
- **Common workflows**: Typical development and deployment processes
- **Debugging tips**: How to troubleshoot common issues
- **Testing approach**: How to write and run tests

## OPERATIONAL CONSIDERATIONS
- Deployment and scaling characteristics
- Monitoring and observability features
- Configuration management approach
- Security considerations and best practices
- Performance characteristics and bottlenecks
- Maintenance and operational procedures

---

**CONTENT GUIDELINES:**
- Be specific about file names, class names, and code structure
- Focus on practical insights that help developers work effectively
- Explain the "why" behind architectural decisions, not just the "what"
- Use clear, professional language accessible to both senior and
  junior developers
- Include concrete examples from the actual codebase
- Highlight any unique or non-standard approaches used
- Point out potential areas for improvement or technical debt
"""

SYSTEMS_ENGINEER_PROMPT = f"""
You are creating documentation specifically for systems engineers who need to
understand how this codebase fits into larger infrastructure and operational
contexts.

CODEBASE CONTENT:
{{file_contents}}

Focus on these systems engineering concerns:

## SYSTEM BOUNDARIES & INTERFACES
- What services/systems does this component interact with?
- Network protocols and communication patterns used
- Data formats and serialization approaches
- API contracts and service level agreements
- Dependencies on external services and their failure modes

## DEPLOYMENT & INFRASTRUCTURE
- How is this system deployed and configured?
- Infrastructure requirements (compute, memory, storage, network)
- Scaling characteristics and bottlenecks
- Configuration management and environment variables
- Container/orchestration considerations

## OPERATIONAL CHARACTERISTICS
- Monitoring and alerting capabilities
- Logging and observability features
- Health checks and service discovery
- Backup and disaster recovery considerations
- Security boundaries and access controls

## INTEGRATION PATTERNS
- How does this fit into the overall system architecture?
- Data flow patterns with upstream/downstream systems
- Event processing and message handling
- State management and consistency guarantees
- Error handling and circuit breaker patterns

{_builder.MARKDOWN_FORMATTING_RULES}

Provide specific, actionable insights that help systems engineers operate
and integrate this component effectively.
"""

JUNIOR_DEVELOPER_PROMPT = f"""
You are creating onboarding documentation for junior developers who need to
understand this codebase and start contributing effectively.

CODEBASE CONTENT:
{{file_contents}}

Focus on these onboarding needs:

## GETTING STARTED
- What does this project do? (simple explanation)
- How to set up the development environment
- How to run the application locally
- How to run tests and verify everything works
- Common first tasks for new developers

## CODE ORGANIZATION
- How is the code organized? (directory structure)
- Where to find different types of functionality
- Naming conventions and coding standards
- Key files every developer should know about
- How to navigate the codebase effectively

## DEVELOPMENT WORKFLOW
- How to make changes safely
- Testing approach and best practices
- Code review process and expectations
- How to add new features or fix bugs
- Common development tools and commands

## KEY CONCEPTS & PATTERNS
- Important domain concepts and terminology
- Common patterns used throughout the codebase
- Key abstractions and interfaces
- How different parts of the system work together
- Examples of typical changes and how to implement them

## GETTING HELP
- Where to find more detailed documentation
- How to ask questions and get support
- Common mistakes to avoid
- Resources for learning more about the technologies used

{_builder.MARKDOWN_FORMATTING_RULES}

Use clear, encouraging language that helps junior developers build confidence
and understanding gradually.
"""

COMPREHENSIVE_ARCHITECTURE_PROMPT = f"""
You are analyzing a codebase to create comprehensive architecture documentation
similar to high-quality system architecture documents. Your goal is to provide
a complete architectural overview that serves both systems engineers and
developers.

{_builder.MARKDOWN_FORMATTING_RULES}

CODEBASE CONTENT:
{{file_contents}}

Generate comprehensive architecture documentation with the following structure:

## System Overview

Provide a high-level description of the system including:
- What the system does (core purpose and business value)
- System type (web application, API, library, CLI tool, microservice, etc.)
- Key business capabilities and target users
- Technology stack overview

## System Architecture

Create a Mermaid diagram showing the main system components and their
relationships:

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Component Names]
    end

    subgraph "Application Layer"
        APP[Core Components]
    end

    subgraph "Data Layer"
        DATA[Data Components]
    end

    UI --> APP
    APP --> DATA
```

Describe the architecture pattern used (MVC, layered, microservices, etc.) and
explain why this pattern was chosen.

## Data Flow Analysis

### Primary Data Flow

Create a Mermaid diagram showing how data flows through the system:

```mermaid
graph TD
    INPUT[Data Input] --> PROCESS[Processing Steps]
    PROCESS --> OUTPUT[Data Output]

    PROCESS --> STORE[Data Storage]
    STORE --> RETRIEVE[Data Retrieval]
```

### Key Processing Flows

For each major workflow, create detailed flow diagrams showing:
- Input sources and validation
- Processing steps and transformations
- Output destinations and formats
- Error handling paths

## Component Details

### Core Components

For each major component identified, provide:

#### Component Name
- **Purpose**: What this component does
- **Key Methods/Functions**: Main interfaces and operations
- **Dependencies**: What this component depends on
- **Data Handled**: Input/output data types and formats
- **Configuration**: How the component is configured
- **Error Handling**: How errors are managed

### Integration Points

Document how components interact:
- API contracts and interfaces
- Data exchange formats
- Communication protocols
- Dependency relationships

## Configuration System

Show the configuration structure with examples:

```yaml
# Example configuration structure
component_name:
  setting1: value1
  setting2: value2
  nested_config:
    option1: true
    option2: "example"
```

Document:
- Configuration file locations
- Environment variable usage
- Default values and overrides
- Validation rules

## Performance Characteristics

Analyze and document:

### Performance Metrics
- Response times for key operations
- Throughput capabilities
- Resource usage (CPU, memory, disk)
- Scalability limits

### Optimization Strategies
- Caching mechanisms used
- Database query optimization
- Asynchronous processing
- Resource pooling

## Error Handling Strategy

Document the error handling approach:

### Error Categories
- Input validation errors
- Processing errors
- External service failures
- Resource exhaustion

### Error Handling Patterns
- How errors are caught and processed
- Error logging and monitoring
- Recovery mechanisms
- User-facing error messages

## Security Architecture

If applicable, document:
- Authentication mechanisms
- Authorization patterns
- Data encryption
- Security boundaries
- Input validation and sanitization

## Deployment Architecture

Describe how the system is deployed:
- Deployment environments
- Infrastructure requirements
- Scaling strategies
- Monitoring and health checks

## Architecture Benefits

Explain why this architecture was chosen:
- **Maintainability**: How the architecture supports maintenance
- **Scalability**: How the system can grow
- **Reliability**: How reliability is ensured
- **Performance**: Performance advantages
- **Developer Experience**: How it helps developers

## Future Architecture Considerations

Discuss potential improvements:
- **Scalability Enhancements**: How to handle growth
- **Performance Optimizations**: Areas for improvement
- **Technology Upgrades**: Potential technology changes
- **Integration Opportunities**: New integration possibilities

---

Focus on providing concrete, actionable insights that help developers
understand not just what the system does, but why it's designed this way and
how to work with it effectively. Include specific examples from the codebase
where possible.
"""


# Module-level convenience functions for backward compatibility
def get_architecture_analysis_prompt(file_contents: str) -> str:
    """Get the main architecture analysis prompt."""
    builder = ArchitecturePromptBuilder()
    return builder.build_architecture_analysis_prompt(file_contents)


def get_systems_engineer_prompt(file_contents: str) -> str:
    """Get the systems engineer focused prompt."""
    builder = ArchitecturePromptBuilder()
    return builder.build_systems_engineer_prompt(file_contents)


def get_junior_developer_prompt(file_contents: str) -> str:
    """Get the junior developer focused prompt."""
    builder = ArchitecturePromptBuilder()
    return builder.build_junior_developer_prompt(file_contents)


def get_comprehensive_architecture_prompt(file_contents: str) -> str:
    """Get the comprehensive architecture analysis prompt with Mermaid
    diagrams."""
    return COMPREHENSIVE_ARCHITECTURE_PROMPT.format(file_contents=file_contents)
