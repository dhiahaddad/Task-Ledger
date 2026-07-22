from datetime import date

import pytest

from task_ledger.application.services import TaskService
from task_ledger.domain.errors import TaskNotFoundError
from task_ledger.domain.models import Priority


def test_create_and_list_tasks(service: TaskService) -> None:
    later = service.create_task("Later", due_date=date(2026, 8, 2), tags=("Home",))
    sooner = service.create_task(
        "Sooner",
        priority=Priority.HIGH,
        due_date=date(2026, 7, 25),
        tags=("Work",),
    )

    assert service.list_tasks() == [sooner, later]
    assert service.list_tasks(tag="WORK") == [sooner]


def test_complete_reopen_edit_and_delete(service: TaskService) -> None:
    task = service.create_task("Draft")

    edited = service.edit_task(task.id, title="Final draft", tags=("Writing",))
    completed = service.complete_task(task.id)
    reopened = service.reopen_task(task.id)
    service.delete_task(task.id)

    assert edited.title == "Final draft"
    assert completed.completed
    assert not reopened.completed
    with pytest.raises(TaskNotFoundError):
        service.get_task(task.id)


def test_missing_task_operations_raise_domain_error(service: TaskService) -> None:
    with pytest.raises(TaskNotFoundError, match="missing"):
        service.complete_task("missing")
    with pytest.raises(TaskNotFoundError, match="missing"):
        service.delete_task("missing")
