from collections.abc import Iterator
from datetime import UTC, datetime

import pytest

from task_ledger.application.services import TaskService
from task_ledger.domain.models import Task


class MemoryTaskRepository:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}

    def list(self) -> list[Task]:
        return list(self.tasks.values())

    def get(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def save(self, task: Task) -> None:
        self.tasks[task.id] = task

    def delete(self, task_id: str) -> bool:
        return self.tasks.pop(task_id, None) is not None


@pytest.fixture
def repository() -> MemoryTaskRepository:
    return MemoryTaskRepository()


@pytest.fixture
def service(repository: MemoryTaskRepository) -> Iterator[TaskService]:
    identifiers = iter(("task-001", "task-002", "task-003"))
    yield TaskService(
        repository,
        clock=lambda: datetime(2026, 7, 22, 12, 0, tzinfo=UTC),
        id_factory=lambda: next(identifiers),
    )
