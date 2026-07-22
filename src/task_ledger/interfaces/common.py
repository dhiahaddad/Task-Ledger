"""Small presentation helpers shared by interface adapters."""

from datetime import date

from task_ledger.application.services import TaskService
from task_ledger.domain.models import Task
from task_ledger.infrastructure.json_repository import JsonTaskRepository


def create_service() -> TaskService:
    """Composition root for local interfaces."""
    return TaskService(JsonTaskRepository())


def task_status(task: Task) -> str:
    return "done" if task.completed else "open"


def format_due_date(value: date | None) -> str:
    return value.isoformat() if value else "—"


def format_tags(task: Task) -> str:
    return ", ".join(task.tags) if task.tags else "—"
