"""Domain-specific errors that every interface can present in its own way."""


class TaskLedgerError(Exception):
    """Base class for expected application errors."""


class ValidationError(TaskLedgerError):
    """Raised when a requested state violates a domain rule."""


class TaskNotFoundError(TaskLedgerError):
    """Raised when a task identifier cannot be found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task '{task_id}' was not found.")
        self.task_id = task_id
