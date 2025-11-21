# Contributing to The Talking Heads

Thank you for your interest in contributing to The Talking Heads! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/The_Talking_Heads.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov flake8 mypy black
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Maximum line length: 127 characters
- Use black for code formatting: `black src/`

## Testing

- Write tests for new features
- Ensure all tests pass: `pytest tests/`
- Maintain or improve test coverage

## Commit Messages

- Use clear, descriptive commit messages
- Reference issue numbers if applicable
- Format: `type: description` (e.g., `feat: Add multi-persona support`)

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Request review from maintainers

## Code Review

- Be open to feedback
- Respond to comments promptly
- Make requested changes

## Questions?

Feel free to open an issue for questions or discussions.

