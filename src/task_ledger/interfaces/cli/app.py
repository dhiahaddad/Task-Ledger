"""Command-line interface powered by Typer."""

from datetime import date
from typing import Annotated, Never

import typer

from task_ledger.application.services import TaskService
from task_ledger.domain.errors import TaskLedgerError
from task_ledger.domain.models import Priority, Task
from task_ledger.infrastructure.logging import configure_logging
from task_ledger.interfaces.common import create_service, format_due_date, format_tags, task_status

app = typer.Typer(
    name="task-ledger",
    help="Manage the same task ledger used by the desktop and terminal interfaces.",
    no_args_is_help=True,
)


def _service() -> TaskService:
    return create_service()


def _abort(error: TaskLedgerError) -> Never:
    typer.secho(str(error), fg=typer.colors.RED, err=True)
    raise typer.Exit(code=2)


def _show_task(task: Task) -> None:
    marker = "✓" if task.completed else "·"
    typer.echo(
        f"{marker} {task.id:<8} {task.priority.value:<6} {task.title} "
        f"[due: {format_due_date(task.due_date)}; tags: {format_tags(task)}]"
    )


def _parse_due(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise typer.BadParameter("Dates must use the YYYY-MM-DD format.") from error


@app.command("add")
def add_task(
    title: Annotated[str, typer.Argument(help="Short task title.")],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    priority: Annotated[Priority, typer.Option("--priority", "-p")] = Priority.MEDIUM,
    tag: Annotated[list[str] | None, typer.Option("--tag", "-t")] = None,
    due: Annotated[str | None, typer.Option("--due", help="Due date as YYYY-MM-DD.")] = None,
) -> None:
    """Create a task."""
    try:
        task = _service().create_task(
            title,
            description=description,
            priority=priority,
            tags=tuple(tag or ()),
            due_date=_parse_due(due),
        )
    except TaskLedgerError as error:
        _abort(error)
    typer.echo(f"Created {task.id}: {task.title}")


@app.command("list")
def list_tasks(
    pending: Annotated[bool, typer.Option("--pending", help="Show only open tasks.")] = False,
    completed: Annotated[
        bool, typer.Option("--completed", help="Show only completed tasks.")
    ] = False,
    tag: Annotated[str | None, typer.Option("--tag", "-t")] = None,
) -> None:
    """List tasks, ordered by status and due date."""
    if pending and completed:
        typer.secho(
            "Choose either --pending or --completed, not both.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=2)
    status = False if pending else (True if completed else None)
    tasks = _service().list_tasks(completed=status, tag=tag)
    if not tasks:
        typer.echo("No matching tasks.")
        return
    for task in tasks:
        _show_task(task)


@app.command("show")
def show_task(task_id: Annotated[str, typer.Argument(help="Task identifier.")]) -> None:
    """Show all details for one task."""
    try:
        task = _service().get_task(task_id)
    except TaskLedgerError as error:
        _abort(error)
    _show_task(task)
    typer.echo(f"status: {task_status(task)}")
    typer.echo(f"description: {task.description or '—'}")
    typer.echo(f"created: {task.created_at.isoformat()}")


@app.command("edit")
def edit_task(
    task_id: Annotated[str, typer.Argument(help="Task identifier.")],
    title: Annotated[str | None, typer.Option("--title")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d")] = None,
    priority: Annotated[Priority | None, typer.Option("--priority", "-p")] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", "-t")] = None,
    due: Annotated[str | None, typer.Option("--due", help="Due date as YYYY-MM-DD.")] = None,
    clear_due: Annotated[bool, typer.Option("--clear-due")] = False,
) -> None:
    """Edit fields on an existing task."""
    try:
        task = _service().edit_task(
            task_id,
            title=title,
            description=description,
            priority=priority,
            tags=None if tag is None else tuple(tag),
            due_date=_parse_due(due),
            clear_due_date=clear_due,
        )
    except TaskLedgerError as error:
        _abort(error)
    typer.echo(f"Updated {task.id}: {task.title}")


@app.command("complete")
def complete_task(task_id: Annotated[str, typer.Argument(help="Task identifier.")]) -> None:
    """Mark a task complete."""
    try:
        task = _service().complete_task(task_id)
    except TaskLedgerError as error:
        _abort(error)
    typer.echo(f"Completed {task.id}: {task.title}")


@app.command("reopen")
def reopen_task(task_id: Annotated[str, typer.Argument(help="Task identifier.")]) -> None:
    """Return a completed task to the open list."""
    try:
        task = _service().reopen_task(task_id)
    except TaskLedgerError as error:
        _abort(error)
    typer.echo(f"Reopened {task.id}: {task.title}")


@app.command("delete")
def delete_task(
    task_id: Annotated[str, typer.Argument(help="Task identifier.")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation.")] = False,
) -> None:
    """Permanently remove a task."""
    if not force and not typer.confirm(f"Delete task {task_id}?"):
        raise typer.Abort()
    try:
        _service().delete_task(task_id)
    except TaskLedgerError as error:
        _abort(error)
    typer.echo(f"Deleted {task_id}.")


def main() -> None:
    configure_logging()
    app()


if __name__ == "__main__":
    main()
