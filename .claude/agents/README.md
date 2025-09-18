# Project Agents Configuration

This directory contains agent configurations for the beacon-delivery-compass project, designed for use with **Claude Code**. These configurations are inspired by and use exact definitions from the [Agents Repository](https://github.com/wshobson/agents).

## Claude Code Integration

These agent configurations are specifically set up for use with Claude Code and support multiple model types:

### **Anthropic Models**
- **Claude Sonnet** (sonnet) - Used by python-pro and test-automator agents
- **Claude Opus** (opus) - Used by docs-architect agent for comprehensive documentation

### **Alternative Models**
- **GLM by Zhipu AI** - Can be used as an alternative to Anthropic models
- Other compatible models supported by Claude Code

The agent definitions are model-agnostic and can work with any AI model supported by your Claude Code setup, though performance and capabilities may vary based on the chosen model.

## Our Lean Team Agent Trio

### 1. python-pro.md
- **Purpose**: Master Python 3.12+ with modern features, async programming, performance optimization, and production-ready practices
- **Recommended Model**: Sonnet (or GLM equivalent)
- **Use for**: Python development, optimization, or advanced Python patterns
- **When to use**: PROACTIVELY for any Python development work

### 2. test-automator.md
- **Purpose**: Master AI-powered test automation with modern frameworks, self-healing tests, and comprehensive quality engineering
- **Recommended Model**: Sonnet (or GLM equivalent)
- **Use for**: Testing automation or quality assurance
- **When to use**: PROACTIVELY for testing automation or quality assurance

### 3. docs-architect.md
- **Purpose**: Creates comprehensive technical documentation from existing codebases. Analyzes architecture, design patterns, and implementation details to produce long-form technical manuals and ebooks
- **Recommended Model**: Opus (or GLM equivalent for comprehensive tasks)
- **Use for**: System documentation, architecture guides, or technical deep-dives
- **When to use**: PROACTIVELY for system documentation, architecture guides, or technical deep-dives

## Usage Guidelines

1. **Use agents proactively** - Don't wait for problems, use them preventively
2. **Start with python-pro** for most development tasks
3. **Involve test-automator early** in the development process
4. **Use docs-architect** for architectural decisions and user-facing documentation
5. **Keep the lean approach** - These three agents cover 80% of needs
6. **Model flexibility** - While configured for specific models, agents can adapt to available models in your Claude Code setup

## Agent Selection Matrix

| Task | Primary Agent | Secondary Agent |
|------|---------------|-----------------|
| Code Development | python-pro | test-automator |
| Testing | test-automator | python-pro |
| Documentation | docs-architect | python-pro |
| Architecture | python-pro | docs-architect |
| Performance | python-pro | test-automator |
| Code Review | python-pro | test-automator |

## Credit & Inspiration

These agent definitions are exact 1:1 copies from the [Agents Repository](https://github.com/wshobson/agents) by Will Shobson. The repository provides a comprehensive collection of specialized agents for various development tasks.

We've adopted a lean approach, selecting just three core agents that provide maximum coverage for our Python development project while maintaining focus and efficiency.

## Adding New Agents

Only add additional agents when there's a clear, recurring need that this trio cannot address. Consider:

- performance-engineer (for specific performance bottlenecks)
- backend-security-coder (when exposing APIs)
- data-scientist (for advanced analytics features)

Always maintain the lean approach - prefer depth over breadth in agent coverage.

## File Structure

```
.claude/agents/
├── README.md                    # This file
├── python-pro.md                # Python development expert
├── test-automator.md            # Test automation specialist
└── docs-architect.md            # Technical documentation architect
```

All agent files are maintained as exact 1:1 copies from the original repository to ensure consistency and reliability.
