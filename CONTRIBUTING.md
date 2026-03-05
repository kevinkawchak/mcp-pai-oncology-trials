# Contributing to TrialMCP Pack

Thank you for your interest in contributing to the TrialMCP Pack project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/mcp-pai-oncology-trials.git`
3. Install dependencies: `pip install pytest jsonschema`
4. Run the test suite: `python -m pytest tests/ -v`

## Development Guidelines

- **Python 3.11+** is required.
- Follow existing code style (Ruff linter configuration in `pyproject.toml`).
- All MCP tool calls must produce audit records via the callback mechanism.
- Use the shared `servers/common/` module for error codes, validation, and health endpoints.
- De-identification must be applied before returning any patient-linked data.

## Pull Request Process

1. Create a feature branch from `main`.
2. Ensure all tests pass: `python -m pytest tests/ -v`
3. Add tests for any new functionality.
4. Update documentation if the public API changes.
5. Submit a pull request with a clear description of the changes.

## Code of Conduct

This project follows standard open-source community guidelines. Be respectful, constructive, and inclusive in all interactions.

## Areas for Contribution

See the peer-review recommendations in `peer-review/` for a prioritized list of improvements, including:

- Server hardening and inter-server contract enforcement
- Deterministic reproducibility artifacts
- Adversarial and compliance edge-case test coverage
- Research packaging for publication

## Contributors

- [@kevinkawchak](https://github.com/kevinkawchak)
- [@claude](https://github.com/claude)
- [@codex](https://github.com/codex)
