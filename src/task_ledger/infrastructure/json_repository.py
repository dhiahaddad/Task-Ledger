"""A small, atomic JSON implementation of the task repository port."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from task_ledger.domain.models import Priority, Task
from task_ledger.infrastructure.paths import default_database_path


class JsonTaskRepository:
    """Persist tasks in a human-readable file using atomic replacement."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_database_path()
        self._lock = RLock()

    def list(self) -> list[Task]:
        with self._lock:
            return list(self._read().values())

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            return self._read().get(task_id)

    def save(self, task: Task) -> None:
        with self._lock:
            tasks = self._read()
            tasks[task.id] = task
            self._write(tasks)

    def delete(self, task_id: str) -> bool:
        with self._lock:
            tasks = self._read()
            if task_id not in tasks:
                return False
            del tasks[task_id]
            self._write(tasks)
            return True

    def _read(self) -> dict[str, Task]:
        if not self.path.exists():
            return {}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise ValueError(f"Unsupported Task Ledger data format in {self.path}")
        raw_tasks = payload.get("tasks", [])
        if not isinstance(raw_tasks, list):
            raise ValueError(f"Invalid task list in {self.path}")
        tasks = (self._task_from_dict(item) for item in raw_tasks)
        return {task.id: task for task in tasks}

    def _write(self, tasks: dict[str, Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "tasks": [self._task_to_dict(task) for task in tasks.values()],
        }
        handle, temporary_name = tempfile.mkstemp(
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(payload, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            Path(temporary_name).replace(self.path)
        except BaseException:
            Path(temporary_name).unlink(missing_ok=True)
            raise

    @staticmethod
    def _task_to_dict(task: Task) -> dict[str, Any]:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "tags": list(task.tags),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

    @staticmethod
    def _task_from_dict(value: Any) -> Task:
        if not isinstance(value, dict):
            raise ValueError("A stored task must be a JSON object.")
        due_date = date.fromisoformat(value["due_date"]) if value.get("due_date") else None
        completed_at = (
            datetime.fromisoformat(value["completed_at"]) if value.get("completed_at") else None
        )
        return Task(
            id=str(value["id"]),
            title=str(value["title"]),
            description=str(value.get("description", "")),
            priority=Priority(value.get("priority", Priority.MEDIUM)),
            tags=tuple(value.get("tags", ())),
            due_date=due_date,
            completed=bool(value.get("completed", False)),
            created_at=datetime.fromisoformat(value["created_at"]),
            completed_at=completed_at,
        )
