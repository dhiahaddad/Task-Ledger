"""Application services orchestrate domain objects and persistence ports."""

from collections.abc import Callable
from datetime import UTC, date, datetime
from uuid import uuid4

from task_ledger.application.ports import TaskRepository
from task_ledger.domain.errors import TaskNotFoundError
from task_ledger.domain.models import Priority, Task

Clock = Callable[[], datetime]
IdFactory = Callable[[], str]


def _utc_now() -> datetime:
    return datetime.now(UTC)


class TaskService:
    """The public use-case API consumed by CLI, desktop, and TUI adapters."""

    def __init__(
        self,
        repository: TaskRepository,
        *,
        clock: Clock = _utc_now,
        id_factory: IdFactory = lambda: uuid4().hex[:8],
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._id_factory = id_factory

    def create_task(
        self,
        title: str,
        *,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        tags: tuple[str, ...] = (),
        due_date: date | None = None,
    ) -> Task:
        task = Task(
            id=self._id_factory(),
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            created_at=self._clock(),
        )
        self._repository.save(task)
        return task

    def list_tasks(
        self,
        *,
        completed: bool | None = None,
        tag: str | None = None,
    ) -> list[Task]:
        tasks = self._repository.list()
        if completed is not None:
            tasks = [task for task in tasks if task.completed is completed]
        if tag:
            normalized_tag = tag.strip().lower()
            tasks = [task for task in tasks if normalized_tag in task.tags]
        return sorted(
            tasks, key=lambda task: (task.completed, task.due_date or date.max, task.created_at)
        )

    def get_task(self, task_id: str) -> Task:
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def edit_task(
        self,
        task_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        tags: tuple[str, ...] | None = None,
        due_date: date | None = None,
        clear_due_date: bool = False,
    ) -> Task:
        task = self.get_task(task_id).edit(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            clear_due_date=clear_due_date,
        )
        self._repository.save(task)
        return task

    def complete_task(self, task_id: str) -> Task:
        task = self.get_task(task_id).complete(at=self._clock())
        self._repository.save(task)
        return task

    def reopen_task(self, task_id: str) -> Task:
        task = self.get_task(task_id).reopen()
        self._repository.save(task)
        return task

    def delete_task(self, task_id: str) -> None:
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)
