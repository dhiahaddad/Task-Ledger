"""Interactive terminal interface powered by Textual."""

from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from task_ledger.application.services import TaskService
from task_ledger.domain.errors import TaskLedgerError
from task_ledger.domain.models import Priority
from task_ledger.infrastructure.logging import configure_logging
from task_ledger.interfaces.common import create_service, format_due_date, format_tags


class TaskLedgerApp(App[None]):
    """A keyboard-friendly adapter over the same application service."""

    CSS = """
    #controls { height: auto; padding: 1; }
    #title { width: 1fr; }
    #priority { width: 16; }
    #message { height: 2; padding: 0 1; color: $warning; }
    DataTable { height: 1fr; }
    """
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("r", "refresh_tasks", "Refresh"),
    ]

    def __init__(self, service: TaskService) -> None:
        super().__init__()
        self._service = service

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="controls"):
            yield Input(placeholder="What needs doing?", id="title")
            yield Select(
                [(priority.value.title(), priority) for priority in Priority],
                value=Priority.MEDIUM,
                id="priority",
                allow_blank=False,
            )
            yield Button("Add", id="add", variant="primary")
            yield Button("Toggle", id="toggle")
            yield Button("Delete", id="delete", variant="error")
        yield Static("", id="message")
        yield DataTable(cursor_type="row", zebra_stripes=True, id="tasks")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tasks", DataTable)
        table.add_columns("ID", "Status", "Priority", "Title", "Due", "Tags")
        self.action_refresh_tasks()

    def _selected_task_id(self) -> str | None:
        table = self.query_one("#tasks", DataTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return str(row_key.value)

    def _message(self, message: str) -> None:
        self.query_one("#message", Static).update(message)

    def action_refresh_tasks(self) -> None:
        table = self.query_one("#tasks", DataTable)
        table.clear()
        for task in self._service.list_tasks():
            table.add_row(
                task.id,
                "Done" if task.completed else "Open",
                task.priority.value,
                task.title,
                format_due_date(task.due_date),
                format_tags(task),
                key=task.id,
            )

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self._add_task()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            self._add_task()
        elif event.button.id == "toggle":
            self._toggle_task()
        elif event.button.id == "delete":
            self._delete_task()

    def _add_task(self) -> None:
        title = self.query_one("#title", Input)
        priority = self.query_one("#priority", Select).value
        try:
            self._service.create_task(title.value, priority=Priority(priority))
        except (TaskLedgerError, ValueError) as error:
            self._message(str(error))
            return
        title.value = ""
        self._message("Task created.")
        self.action_refresh_tasks()

    def _toggle_task(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            return
        try:
            task = self._service.get_task(task_id)
            if task.completed:
                self._service.reopen_task(task_id)
            else:
                self._service.complete_task(task_id)
        except TaskLedgerError as error:
            self._message(str(error))
        self.action_refresh_tasks()

    def _delete_task(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            return
        try:
            self._service.delete_task(task_id)
        except TaskLedgerError as error:
            self._message(str(error))
        self.action_refresh_tasks()


def main() -> None:
    configure_logging()
    TaskLedgerApp(create_service()).run()


if __name__ == "__main__":
    main()
