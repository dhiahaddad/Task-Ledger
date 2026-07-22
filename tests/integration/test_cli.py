from typer.testing import CliRunner

from task_ledger.interfaces.cli.app import app


def test_cli_add_and_list_share_persistence(tmp_path) -> None:  # type: ignore[no-untyped-def]
    runner = CliRunner()
    environment = {"TASK_LEDGER_DATA_FILE": str(tmp_path / "tasks.json")}

    created = runner.invoke(
        app,
        ["add", "Prepare release", "--priority", "high", "--tag", "work", "--due", "2026-08-01"],
        env=environment,
    )
    listed = runner.invoke(app, ["list", "--pending", "--tag", "work"], env=environment)

    assert created.exit_code == 0
    assert "Created" in created.stdout
    assert listed.exit_code == 0
    assert "Prepare release" in listed.stdout
    assert "2026-08-01" in listed.stdout


def test_cli_rejects_invalid_due_date(tmp_path) -> None:  # type: ignore[no-untyped-def]
    result = CliRunner().invoke(
        app,
        ["add", "Invalid date", "--due", "tomorrow"],
        env={"TASK_LEDGER_DATA_FILE": str(tmp_path / "tasks.json")},
    )

    assert result.exit_code == 2
    assert "YYYY-MM-DD" in result.output
