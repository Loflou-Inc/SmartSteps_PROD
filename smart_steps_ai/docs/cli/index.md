# CLI Reference

This section provides detailed documentation for the Smart Steps AI command-line interface (CLI).

## Overview

The Smart Steps AI CLI provides commands for managing personas, sessions, conversations, analysis, configuration, and performance.

## Command Groups

- [Session Commands](session.md): Create, manage, and analyze client sessions
- [Conversation Commands](conversation.md): Interact with and manage conversations
- [Analysis Commands](analysis.md): Generate insights, reports, and visualizations
- [Config Commands](config.md): Configure the Smart Steps AI module
- [Persona Commands](persona.md): Create and manage professional personas
- [Performance Commands](performance.md): Optimize and monitor system performance

## Getting Started

```bash
# Install the package
pip install smart-steps-ai

# View the main help
smart-steps-ai --help

# View help for a specific command group
smart-steps-ai session --help
```

## Global Options

All commands support the following global options:

- `--help, -h`: Show help message
- `--version`: Show version and exit
- `--config PATH`: Path to the configuration file
- `--verbose`: Enable verbose output
- `--quiet`: Suppress non-error output

## Usage Examples

```bash
# Create a session
smart-steps-ai session create --persona therapist --client "John Doe"

# Start a conversation
smart-steps-ai conversation interactive --session-id <session-id>

# Analyze a session
smart-steps-ai analysis report --session-id <session-id> --format markdown

# Configure the system
smart-steps-ai config set --key cache.memory_size --value 2000

# Create a persona
smart-steps-ai persona create --name "Dr. Smith" --type therapist

# Optimize performance
smart-steps-ai performance optimize
```
