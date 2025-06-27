# Cursor AI Code Management Rules

This directory contains Cursor AI assistant rules designed for automated code management, quality assurance, and development workflow optimization. These rules are specifically written for AI assistants to execute automatically, providing intelligent code assistance with minimal human intervention.

## Rule Overview

### 📝 Git Commit Standards (`git-commit-standards.mdc`)

**AI Behavior**: Automatically generate and validate conventional commit messages for all version control operations.

**Automated Actions**:

- Generate commit messages following Conventional Commits v1.0.0 specification
- Automatically detect commit type based on file changes and code analysis
- Assign appropriate scopes based on modified file paths
- Validate message format and correct common mistakes
- Detect and properly format breaking changes
- Suggest version bumps based on commit history analysis

**Integration Benefits**:

- Enables automated semantic versioning
- Generates changelogs automatically
- Improves CI/CD pipeline integration
- Provides clear change communication

### 🔧 Code Quality Automation (`code-quality-automation.mdc`)

**AI Behavior**: Automatically detect, configure, and implement code quality tools and pre-commit hooks.

**Automated Actions**:

- Scan repositories for existing quality tools and configurations
- Generate appropriate `.pre-commit-config.yaml` based on detected technologies
- Provide language-specific tool recommendations (Python/Ruff, JavaScript/ESLint, etc.)
- Set up security scanning with tools like Gitleaks
- Configure automated formatting and linting
- Provide troubleshooting commands and solutions

**Integration Benefits**:

- Consistent code style across all projects
- Early detection of bugs and security issues
- Reduced code review time and effort
- Automated quality enforcement

### 📚 Documentation Maintenance (`documentation-maintenance.mdc`)

**AI Behavior**: Actively validate documentation accuracy and suggest updates when discrepancies are found.

**Automated Actions**:

- Automatically assess documentation confidence levels (HIGH/MEDIUM/LOW)
- Cross-reference documentation with actual code implementation
- Validate code examples, links, and configuration samples
- Check version consistency across documentation
- Suggest specific documentation improvements
- Warn users about potentially outdated information

**Integration Benefits**:

- Trustworthy documentation that stays current
- Reduced developer confusion and support requests
- Better onboarding experience for new team members
- Proactive identification of documentation gaps

### 🔍 Codebase Understanding (`codebase-understanding.mdc`)

**AI Behavior**: Systematically analyze and understand codebases through automated exploration and pattern recognition.

**Automated Actions**:

- Execute discovery commands to understand project structure
- Analyze dependencies, configuration, and architectural patterns
- Map data flow and identify integration points
- Assess documentation quality and validate against code
- Build comprehensive mental models of system architecture
- Provide structured explanations of codebase organization

**Integration Benefits**:

- Informed decision-making when suggesting code changes
- Reduced risk of breaking existing functionality
- Better understanding of system constraints and patterns
- Improved code suggestions that align with existing architecture

### 📖 Developer Guide Review (`review_developer_guide.mdc`)

**AI Behavior**: Automatically locate, analyze, and apply MCP project developer documentation before making changes.

**Automated Actions**:

- Search for and prioritize developer documentation sources
- Extract key MCP protocol patterns and requirements
- Validate documentation against actual code implementation
- Ensure all suggestions follow documented patterns
- Check environment variable and configuration requirements
- Report documentation issues and suggest improvements

**Integration Benefits**:

- Consistent adherence to project-specific patterns
- Reduced bugs from misunderstanding requirements
- Better integration with existing MCP tools and protocols
- Proactive identification of documentation problems

## AI Assistant Workflow Integration

### 🤖 Automated Decision Making

These rules enable the AI assistant to:

- **Analyze before acting**: Understand codebase patterns before suggesting changes
- **Validate continuously**: Check documentation accuracy and code consistency
- **Generate intelligently**: Create commit messages, configurations, and code following established patterns
- **Communicate clearly**: Provide structured feedback about confidence levels and potential issues

### 🔄 Continuous Quality Assurance

The rules work together to create a self-reinforcing quality system:

1. **Understanding** → Analyze codebase and documentation
2. **Quality Setup** → Configure appropriate tools and standards
3. **Implementation** → Make changes following established patterns
4. **Documentation** → Update and validate documentation accuracy
5. **Commitment** → Generate proper commit messages for changes

### ⚡ Immediate Feedback Loop

- Real-time validation of code changes against project patterns
- Instant detection of documentation inconsistencies
- Automatic correction of common formatting and style issues
- Proactive suggestions for improvements and optimizations

## Rule Execution Patterns

### 🎯 Always Active Rules (`alwaysApply: true`)

These rules run automatically for every interaction:

- **Git Commit Standards**: Every commit suggestion follows conventional format
- **Code Quality Automation**: Every code change includes quality checks
- **Documentation Maintenance**: Every documentation reference is validated
- **Codebase Understanding**: Every suggestion is informed by codebase analysis
- **Developer Guide Review**: Every MCP project change follows documented patterns

### 🔍 Context-Aware Execution

Rules adapt their behavior based on:

- **Project type**: Different tools for Python vs JavaScript vs Go projects
- **Existing setup**: Work with current tools or suggest improvements
- **Documentation quality**: Adjust confidence levels based on validation results
- **Change scope**: Scale analysis depth based on modification complexity

## Implementation for AI Assistants

### 📋 Execution Checklist

For each user interaction, the AI assistant should:

- [ ] Analyze project structure and existing tools
- [ ] Validate any referenced documentation
- [ ] Apply appropriate quality standards
- [ ] Generate conventional commit messages
- [ ] Provide confidence assessments for suggestions
- [ ] Report any inconsistencies or issues found

### 🛠️ Tool Integration Commands

The rules provide specific commands for:

- Repository analysis and pattern detection
- Quality tool setup and configuration
- Documentation validation and testing
- Commit message generation and validation
- Error detection and resolution

### 📊 Quality Metrics

Track and report on:

- Commit message compliance rates
- Documentation accuracy improvements
- Code quality tool adoption
- Issue detection and resolution rates
- User satisfaction with automated suggestions

## Benefits for Development Teams

### 🚀 Productivity Improvements

- **Reduced Manual Work**: Automated quality checks and commit message generation
- **Faster Onboarding**: Consistent patterns and validated documentation
- **Fewer Bugs**: Early detection through automated analysis
- **Better Collaboration**: Clear commit history and documentation standards

### 🎯 Quality Assurance

- **Consistent Standards**: Automated enforcement across all projects
- **Proactive Issue Detection**: Find problems before they become critical
- **Documentation Accuracy**: Validated and maintained automatically
- **Knowledge Preservation**: Systematic understanding and documentation

### 🔧 Maintenance Reduction

- **Self-Updating Configurations**: Automated tool setup and maintenance
- **Proactive Documentation Updates**: Identify and suggest fixes automatically
- **Reduced Support Requests**: Clear, accurate documentation and examples
- **Automated Quality Enforcement**: Consistent standards without manual oversight

## Customization and Extension

### 🎛️ Rule Configuration

Each rule can be customized by:

- Adjusting `alwaysApply` settings for specific workflows
- Modifying glob patterns for file-specific behavior
- Adding project-specific patterns and requirements
- Configuring tool preferences and validation criteria

### 📈 Continuous Improvement

The rules are designed to:

- Learn from project-specific patterns and preferences
- Adapt to new tools and technologies
- Incorporate feedback from development teams
- Evolve with changing best practices and standards

These AI-focused rules create an intelligent development assistant that proactively maintains code quality, documentation accuracy, and development workflow efficiency while requiring minimal human intervention.
