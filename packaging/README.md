# Native desktop packaging

Native applications must be built on their target operating system. The
`desktop-build.yml` workflow runs Qt's `pyside6-deploy` independently on Windows,
macOS, and Linux and uploads the results as workflow artifacts.

For a local build:

```shell
uv sync --extra desktop --dev
uv run pyside6-deploy packaging/desktop/main.py --name TaskLedger --force
```

Production releases should add platform-specific icons, installers, code signing,
and macOS notarization. Those operations require identities and secrets and are
therefore intentionally not enabled by this template.

