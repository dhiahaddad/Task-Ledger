import json
from datetime import UTC, date, datetime

import pytest

from task_ledger.domain.models import Priority, Task
from task_ledger.infrastructure.json_repository import JsonTaskRepository


def test_repository_round_trip_and_delete(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "nested" / "tasks.json"
    repository = JsonTaskRepository(path)
    task = Task(
        id="abc123",
        title="Ship release",
        priority=Priority.HIGH,
        tags=("release",),
        due_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 22, tzinfo=UTC),
    )

    repository.save(task)

    assert repository.get(task.id) == task
    assert repository.list() == [task]
    assert repository.delete(task.id)
    assert not repository.delete(task.id)
    assert repository.list() == []


def test_repository_rejects_unknown_format(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({"version": 99, "tasks": []}), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported"):
        JsonTaskRepository(path).list()
