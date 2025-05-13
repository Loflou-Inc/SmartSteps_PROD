# Smart Steps AI Professional Persona Module

## Overview

The Smart Steps AI Professional Persona module provides AI-powered professional personas for therapeutic and facilitation contexts. The system features a multi-layered cognitive architecture that maintains psychological coherence while evolving through interaction.

## Quick Start

1. **Check system requirements and dependencies**:
   ```
   python check_system.py
   ```

2. **Install missing dependencies**:
   ```
   install_deps.bat
   ```

3. **Run the simplified API server**:
   ```
   run_simplified_api.bat
   ```

4. **Access the API documentation**:
   Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Keys

The system can use the following AI providers:

- **OpenAI** - Set the `OPENAI_API_KEY` environment variable
- **Anthropic** - Set the `ANTHROPIC_API_KEY` environment variable

You can add these to a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Directory Structure

- `src/` - Source code for the Smart Steps AI module
- `config/` - Configuration files
- `logs/` - Log files
- `docs/` - Documentation
- `tests/` - Test suite
- `scripts/` - Utility scripts

## Available Scripts

- `check_system.py` - Check system dependencies and configuration
- `install_deps.bat` - Install required dependencies
- `run_simplified_api.bat` - Run the simplified API server
- `run_api_server.bat` - Run the full API server (requires all dependencies)
- `run_api.py` - Python script to run the API with debug output

## Using the API

Once the API server is running, you can access:

- API Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health
- Personas: http://127.0.0.1:8000/api/v1/personas
- Sessions: http://127.0.0.1:8000/api/v1/sessions

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- Administrator Guide
- Facilitator Guide
- Technical Reference
- Troubleshooting Guide
- What to Expect Guide

## Getting Help

If you encounter any issues:

1. Check the logs in the `logs/` directory
2. Consult the Troubleshooting Guide
3. Run the system check script: `python check_system.py`
4. Try running the simplified API: `run_simplified_api.bat`
