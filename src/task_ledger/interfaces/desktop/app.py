"""A deliberately thin PySide6 interface over TaskService."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from task_ledger.application.services import TaskService
from task_ledger.domain.errors import TaskLedgerError
from task_ledger.domain.models import Priority
from task_ledger.infrastructure.logging import configure_logging
from task_ledger.interfaces.common import create_service, format_due_date, format_tags


class MainWindow(QMainWindow):
    """Desktop presentation; it delegates all state changes to TaskService."""

    def __init__(self, service: TaskService) -> None:
        super().__init__()
        self._service = service
        self.setWindowTitle("Task Ledger")
        self.resize(900, 560)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What needs doing?")
        self.title_input.returnPressed.connect(self.add_task)

        self.priority_input = QComboBox()
        self.priority_input.addItems([priority.value for priority in Priority])
        self.priority_input.setCurrentText(Priority.MEDIUM.value)

        add_button = QPushButton("Add task")
        add_button.clicked.connect(self.add_task)
        complete_button = QPushButton("Toggle complete")
        complete_button.clicked.connect(self.toggle_complete)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_task)

        controls = QHBoxLayout()
        controls.addWidget(self.title_input, stretch=1)
        controls.addWidget(self.priority_input)
        controls.addWidget(add_button)
        controls.addWidget(complete_button)
        controls.addWidget(delete_button)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Status", "Priority", "Title", "Due", "Tags"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout()
        heading = QLabel("Task Ledger")
        heading.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(heading)
        layout.addLayout(controls)
        layout.addWidget(self.table)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)
        self.refresh()

    def _selected_task_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return None if item is None else item.text()

    def _show_error(self, error: Exception) -> None:
        QMessageBox.warning(self, "Task Ledger", str(error))

    def add_task(self) -> None:
        try:
            self._service.create_task(
                self.title_input.text(),
                priority=Priority(self.priority_input.currentText()),
            )
        except TaskLedgerError as error:
            self._show_error(error)
            return
        self.title_input.clear()
        self.refresh()

    def toggle_complete(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            return
        try:
            task = self._service.get_task(task_id)
            if task.completed:
                self._service.reopen_task(task_id)
            else:
                self._service.complete_task(task_id)
        except TaskLedgerError as error:
            self._show_error(error)
        self.refresh()

    def delete_task(self) -> None:
        task_id = self._selected_task_id()
        if task_id is None:
            return
        answer = QMessageBox.question(self, "Delete task", f"Delete task {task_id}?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self._service.delete_task(task_id)
        except TaskLedgerError as error:
            self._show_error(error)
        self.refresh()

    def refresh(self) -> None:
        tasks = self._service.list_tasks()
        self.table.setRowCount(len(tasks))
        for row, task in enumerate(tasks):
            values = (
                task.id,
                "Done" if task.completed else "Open",
                task.priority.value,
                task.title,
                format_due_date(task.due_date),
                format_tags(task),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if task.completed:
                    item.setForeground(Qt.GlobalColor.gray)
                self.table.setItem(row, column, item)


def main() -> None:
    configure_logging()
    application = QApplication(sys.argv)
    application.setApplicationName("Task Ledger")
    window = MainWindow(create_service())
    window.show()
    raise SystemExit(application.exec())


if __name__ == "__main__":
    main()
