# Contributing to AI Processing API

Thank you for your interest in contributing to the AI Processing API! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** and test them
5. **Submit a pull request**

## Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

3. **Run the development server:**
   ```bash
   python start.py
   ```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Add type hints where appropriate

## Testing

- Run the test suite: `python test_api.py`
- Test both OpenAI and Ollama providers
- Ensure all endpoints work correctly
- Test error handling scenarios

## Pull Request Guidelines

1. **Clear description** of what the PR does
2. **Reference issues** if applicable
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Follow the existing code style**

## Feature Requests

- Use GitHub Issues to request new features
- Provide clear use cases and examples
- Consider the impact on existing functionality

## Bug Reports

- Include steps to reproduce the issue
- Provide error messages and logs
- Specify your environment (OS, Python version, etc.)
- Include expected vs actual behavior

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing! 🚀 