"""Interfaces implemented by infrastructure at the edge of the application."""

from typing import Protocol

from task_ledger.domain.models import Task


class TaskRepository(Protocol):
    def list(self) -> list[Task]: ...

    def get(self, task_id: str) -> Task | None: ...

    def save(self, task: Task) -> None: ...

    def delete(self, task_id: str) -> bool: ...
