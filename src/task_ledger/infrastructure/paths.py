"""Cross-platform application data paths implemented with the standard library."""

import os
import sys
from pathlib import Path


def user_data_directory(app_name: str = "TaskLedger") -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / app_name


def default_database_path() -> Path:
    override = os.environ.get("TASK_LEDGER_DATA_FILE")
    return Path(override).expanduser() if override else user_data_directory() / "tasks.json"
