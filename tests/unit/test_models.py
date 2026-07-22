from datetime import UTC, datetime

import pytest

from task_ledger.domain.errors import ValidationError
from task_ledger.domain.models import Priority, Task


def make_task(**overrides: object) -> Task:
    values: dict[str, object] = {
        "id": "abc123",
        "title": "Write tests",
        "created_at": datetime(2026, 7, 22, tzinfo=UTC),
    }
    values.update(overrides)
    return Task(**values)  # type: ignore[arg-type]


def test_task_normalizes_title_and_tags() -> None:
    task = make_task(title="  Write   tests ", tags=("Python", " python ", "QA"))

    assert task.title == "Write tests"
    assert task.tags == ("python", "qa")


@pytest.mark.parametrize("title", ["", "   ", "x" * 201])
def test_task_rejects_invalid_title(title: str) -> None:
    with pytest.raises(ValidationError):
        make_task(title=title)


def test_complete_and_reopen_are_immutable() -> None:
    task = make_task(priority=Priority.HIGH)
    completion_time = datetime(2026, 7, 23, tzinfo=UTC)

    completed = task.complete(at=completion_time)
    reopened = completed.reopen()

    assert not task.completed
    assert completed.completed_at == completion_time
    assert not reopened.completed
    assert reopened.completed_at is None


def test_completion_requires_timezone() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        make_task().complete(at=datetime(2026, 7, 23))
