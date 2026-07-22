# Task Ledger

Task Ledger is a small cross-platform task manager and a practical Python reference
architecture. One framework-independent application core is delivered through a Typer
command-line interface, a PySide6 desktop application, and a Textual terminal UI.

The sample is intentionally substantial enough to demonstrate real boundaries—domain
rules, use cases, repository ports, atomic persistence, dependency injection, testing,
and native packaging—without requiring a database or network service.

## Architecture at a glance

```text
Typer CLI ───────┐
PySide6 desktop ─┼──> application services ──> domain
Textual TUI ─────┘              │
                                v
                         repository port
                                │
                                v
                     atomic JSON persistence
```

Dependencies point inward. The domain knows nothing about files, operating systems, or
UI frameworks. Interface code translates user actions into calls to `TaskService`; it
does not implement business rules.

```text
src/task_ledger/
├── domain/          # Entities, value objects, rules, and expected errors
├── application/     # Use cases and persistence protocols
├── infrastructure/  # JSON repository and cross-platform paths
└── interfaces/
    ├── cli/         # Typer adapter
    ├── desktop/     # PySide6 adapter
    └── tui/         # Textual adapter
```

See [docs/architecture.md](docs/architecture.md) for the dependency rules and extension
examples.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/) for the documented development workflow
- Windows, macOS, or Linux

## Quick start

Install all three interfaces and the developer tools:

```shell
uv sync --all-extras --dev
```

Create and inspect a task with the CLI:

```shell
uv run task-ledger add "Prepare presentation" --priority high --tag work
uv run task-ledger list --pending
uv run task-ledger complete TASK_ID
```

Launch either interactive interface:

```shell
uv run task-ledger-tui
uv run task-ledger-desktop
```

Task data is shared by all interfaces. Set `TASK_LEDGER_DATA_FILE` to use a custom JSON
file; otherwise Task Ledger chooses the conventional per-user data directory for the
current operating system. Copy `.env.example` when documenting local overrides, but do
not commit secret or machine-specific `.env` files.

## Install only what you need

The core library has no third-party runtime dependencies. UI frameworks are optional:

```shell
uv sync --extra cli
uv sync --extra desktop
uv sync --extra tui
uv sync --extra interfaces
```

When published, consumers can use equivalent package extras such as
`task-ledger[desktop]`. Keeping these dependencies optional prevents library and CLI
users from downloading Qt unnecessarily.

## CLI reference

```text
task-ledger add TITLE [--description TEXT] [--priority low|medium|high]
                      [--tag TAG]... [--due YYYY-MM-DD]
task-ledger list [--pending | --completed] [--tag TAG]
task-ledger show TASK_ID
task-ledger edit TASK_ID [OPTIONS]
task-ledger complete TASK_ID
task-ledger reopen TASK_ID
task-ledger delete TASK_ID [--force]
```

Run `uv run task-ledger COMMAND --help` for complete option documentation.

## Development

Run all local quality gates:

```shell
uv run python scripts/check.py
```

Or run them individually:

```shell
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pyright
uv run pytest
```

Pre-commit hooks are optional but recommended:

```shell
uv run pre-commit install
uv run pre-commit run --all-files
```

The VS Code settings contain only shared Python tooling choices. The optional dev
container provides Python 3.12 and `uv`; graphical desktop execution is normally easier
on the host because forwarding a GUI from a container is platform-specific.

## Testing strategy

- Unit tests exercise domain rules and application use cases using an in-memory port.
- Integration tests exercise the JSON repository against temporary files.
- Interface code stays thin so most behavior can be verified without starting a GUI.
- GitHub Actions runs tests on Windows, macOS, and Linux with Python 3.12–3.14.
- Ruff, mypy, Pyright, package builds, and coverage reporting run in CI.

No minimum coverage threshold is imposed initially; the report is informational and
can become a gate once the project establishes a meaningful baseline.

## Native desktop builds

The manual/release workflow uses Qt's `pyside6-deploy` on each target operating system.
A Windows build does not produce macOS or Linux binaries, so native builds run as a
three-platform matrix and are uploaded separately.

```shell
uv sync --extra desktop
uv run pyside6-deploy packaging/desktop/main.py --name TaskLedger --force
```

Signing, notarization, installers, and automatic publication are deliberately left for
the adopting project because they require project-specific identities and secrets. See
[packaging/README.md](packaging/README.md).

## Why there is no Dockerfile

Task Ledger is a local library and native application, not a server. Containers do not
replace Windows executables, macOS application bundles, or native Linux packages, and
they make desktop GUI access awkward. Add a Dockerfile when the project gains a server
or container deployment target; add Compose only when local development needs multiple
cooperating services.

## Using this as a template

The concrete Task Ledger behavior makes architectural decisions visible and testable.
To adapt it, replace the domain and use cases first, then update each interface adapter.
Keep infrastructure behind protocols and keep framework types out of the domain.

See [docs/adapting-the-template.md](docs/adapting-the-template.md) for a rename and
replacement checklist.

## Contributing and security

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), follow
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and report vulnerabilities according to
[SECURITY.md](SECURITY.md).

## License

Copyright (c) 2026 Dhia Haddad. Released under the [MIT License](LICENSE).

