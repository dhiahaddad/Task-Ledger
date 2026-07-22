"""Domain entities and value objects."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import StrEnum

from task_ledger.domain.errors import ValidationError


class Priority(StrEnum):
    """The urgency assigned to a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _clean_title(value: str) -> str:
    title = " ".join(value.split())
    if not title:
        raise ValidationError("A task title cannot be empty.")
    if len(title) > 200:
        raise ValidationError("A task title cannot exceed 200 characters.")
    return title


def _clean_tags(values: tuple[str, ...]) -> tuple[str, ...]:
    tags = tuple(dict.fromkeys(tag.strip().lower() for tag in values if tag.strip()))
    if any(len(tag) > 40 for tag in tags):
        raise ValidationError("A tag cannot exceed 40 characters.")
    return tags


@dataclass(frozen=True, slots=True)
class Task:
    """A task is immutable; state changes return a new validated instance."""

    id: str
    title: str
    created_at: datetime
    description: str = ""
    priority: Priority = Priority.MEDIUM
    tags: tuple[str, ...] = ()
    due_date: date | None = None
    completed: bool = False
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValidationError("A task identifier cannot be empty.")
        object.__setattr__(self, "title", _clean_title(self.title))
        object.__setattr__(self, "description", self.description.strip())
        object.__setattr__(self, "tags", _clean_tags(self.tags))
        if self.completed != (self.completed_at is not None):
            raise ValidationError("Completed tasks must have a completion time.")
        if self.created_at.tzinfo is None:
            raise ValidationError("Creation times must include a timezone.")

    def complete(self, *, at: datetime) -> Task:
        if at.tzinfo is None:
            raise ValidationError("Completion times must include a timezone.")
        if self.completed:
            return self
        return replace(self, completed=True, completed_at=at)

    def reopen(self) -> Task:
        if not self.completed:
            return self
        return replace(self, completed=False, completed_at=None)

    def edit(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        tags: tuple[str, ...] | None = None,
        due_date: date | None = None,
        clear_due_date: bool = False,
    ) -> Task:
        return replace(
            self,
            title=self.title if title is None else title,
            description=self.description if description is None else description,
            priority=self.priority if priority is None else priority,
            tags=self.tags if tags is None else tags,
            due_date=None if clear_due_date else (self.due_date if due_date is None else due_date),
        )
