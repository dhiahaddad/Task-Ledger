# Contributing

## Setup

1. Install Python 3.12+ and `uv`.
2. Run `uv sync --all-extras --dev`.
3. Run `uv run pre-commit install` if you want local commit hooks.
4. Verify the checkout with `uv run python scripts/check.py`.

## Changes

Keep business rules in `domain`, orchestration in `application`, external I/O in
`infrastructure`, and framework translation in `interfaces`. Add unit tests for domain
or use-case behavior and integration tests for concrete infrastructure.

Create focused commits and pull requests. Describe the outcome, architectural impact,
and verification performed. Do not include generated virtual environments, native
build output, local task data, or secrets.

## Style

Ruff is the formatter and linter. Both mypy and Pyright check types. Public behavior
should have concise documentation, and expected user errors should use domain-specific
exceptions rather than process exits inside the application layer.

