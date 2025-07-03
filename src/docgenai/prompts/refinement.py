"""
Documentation Refinement Prompts for DocGenAI

Prompts for refining and improving documentation through iterative processing.
"""

from ..chaining.chain import PromptChain
from ..chaining.step import PromptStep

DOCUMENTATION_REFINEMENT_PROMPTS = {
    "enhance_interfaces": """
Enhance the MAJOR INTERFACES & APIs section of this documentation:

{base_documentation}

Add specific details about:
- API endpoint specifications with request/response examples
- Request/response formats and data models
- Authentication and authorization mechanisms
- Error handling patterns and status codes
- Rate limiting and API versioning
- Integration examples and common usage patterns

Focus on providing practical information that developers need to integrate
with or extend these interfaces.
""",
    "improve_dataflow": """
Enhance the DATA FLOW & PROCESSING section of this documentation:

{enhanced_documentation}

Add detailed information about:
- Step-by-step data processing flows with examples
- Database interaction patterns and query strategies
- Caching strategies and cache invalidation patterns
- Error handling and rollback procedures
- Data validation and sanitization approaches
- Performance optimization techniques

Provide concrete examples of how data moves through the system.
""",
    "add_operational_details": """
Enhance the OPERATIONAL CONSIDERATIONS section:

{enhanced_documentation}

Add comprehensive operational information:
- Deployment strategies and infrastructure requirements
- Monitoring and alerting setup recommendations
- Configuration management and environment variables
- Security considerations and best practices
- Performance tuning and scaling strategies
- Backup and disaster recovery procedures
- Troubleshooting guides for common issues

Focus on practical guidance for operating this system in production.
""",
    "final_polish": """
Polish and finalize this technical documentation:

{enhanced_documentation}

Final improvements:
- Ensure consistency in terminology throughout
- Add practical examples where they would be helpful
- Verify completeness of all major sections
- Optimize for readability and developer experience
- Cross-reference related sections appropriately
- Add any missing critical information
- Ensure the documentation flows logically

The goal is production-ready documentation that serves both systems
engineers and developers effectively.
""",
}


def create_refinement_chain():
    """Create a prompt chain for iterative documentation refinement."""
    return PromptChain(
        [
            PromptStep(
                name="enhance_interfaces",
                prompt=DOCUMENTATION_REFINEMENT_PROMPTS["enhance_interfaces"],
                output_key="enhanced_interfaces",
            ),
            PromptStep(
                name="improve_dataflow",
                prompt=DOCUMENTATION_REFINEMENT_PROMPTS["improve_dataflow"],
                output_key="enhanced_dataflow",
            ),
            PromptStep(
                name="add_operational_details",
                prompt=DOCUMENTATION_REFINEMENT_PROMPTS["add_operational_details"],
                output_key="enhanced_operational",
            ),
            PromptStep(
                name="final_polish",
                prompt=DOCUMENTATION_REFINEMENT_PROMPTS["final_polish"],
                output_key="final_documentation",
            ),
        ]
    )


QUALITY_IMPROVEMENT_PROMPTS = {
    "add_examples": """
Add practical examples to this documentation:

{documentation}

Focus on adding:
- Code examples showing how to use key APIs
- Configuration examples for common scenarios
- Command-line examples for CLI tools
- Integration examples for external systems
- Testing examples and test data
- Deployment examples and scripts

Make the documentation more actionable with concrete examples.
""",
    "improve_clarity": """
Improve the clarity and readability of this documentation:

{documentation}

Focus on:
- Simplifying complex explanations
- Adding clear section headings and organization
- Explaining technical terms and concepts
- Improving flow between sections
- Adding summary points for key concepts
- Making the language more accessible

Maintain technical accuracy while improving readability.
""",
    "add_troubleshooting": """
Add troubleshooting and debugging information:

{documentation}

Include:
- Common error scenarios and solutions
- Debugging techniques and tools
- Performance troubleshooting guides
- Configuration troubleshooting steps
- Dependency and integration issues
- Monitoring and logging guidance

Help developers and operators solve problems quickly.
""",
}
