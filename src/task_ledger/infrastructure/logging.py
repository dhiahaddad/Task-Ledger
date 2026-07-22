"""Standard-library logging configuration shared by executable interfaces."""

import logging
import os


def configure_logging() -> None:
    """Configure predictable console logging without imposing it on library users."""
    level_name = os.environ.get("TASK_LEDGER_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
