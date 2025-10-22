# Contributing to BaseModel Agent

Thank you for your interest in contributing! Here's how you can help.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
4. Install in dev mode: `pip install -e ".[dev]"`
5. Install pre-commit hooks (optional): `pre-commit install`

## Project Structure

- `src/agents/` - Agent implementations
- `src/workflows/` - Long-running workflows
- `src/functions/` - Tool functions
- `src/models/` - Data models and contracts
- `tests/` - Test suite
- `examples/` - Usage examples

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests for new functionality
4. Run tests: `pytest tests/`
5. Format code: `black src/ tests/`
6. Commit with clear message: `git commit -m "Add: feature description"`
7. Push and create pull request

## Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small
- Add comments for complex logic

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for >80% coverage
- Use pytest fixtures for setup

## Pull Request Process

1. Update README.md if needed
2. Update CHANGELOG.md
3. Ensure CI passes
4. Request review from maintainers
5. Address feedback

## Questions?

Open an issue or start a discussion!
