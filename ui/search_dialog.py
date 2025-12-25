from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel

class SearchDialog(QDialog):
    action_selected = Signal(object)  # ToolAction

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setObjectName("Card")

        self._query = QLineEdit()
        self._query.setPlaceholderText("Search tools, pages, features...")
        self._list = QListWidget()
        self._hint = QLabel("Type to search. Enter to open.")
        self._hint.setObjectName("Dim")

        lay = QVBoxLayout(self)
        lay.addWidget(self._query)
        lay.addWidget(self._list)
        lay.addWidget(self._hint)

        self._query.textChanged.connect(self._on_query_changed)
        self._query.returnPressed.connect(self._on_enter)
        self._list.itemActivated.connect(self._on_item_activated)

        self._provider = None
        self._actions = []

        self.resize(560, 420)

    def set_provider(self, provider):
        self._provider = provider

    def open_with_focus(self):
        self._query.setText("")
        self._list.clear()
        self._query.setFocus()
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_query_changed(self, text: str):
        self._list.clear()
        self._actions = []
        if not self._provider:
            return
        actions = self._provider(text)
        self._actions = actions
        for a in actions[:30]:
            item = QListWidgetItem(a.title)
            item.setToolTip(", ".join(a.keywords))
            self._list.addItem(item)

    def _emit(self, idx: int):
        if 0 <= idx < len(self._actions):
            self.action_selected.emit(self._actions[idx])
            self.close()

    def _on_enter(self):
        self._emit(0)

    def _on_item_activated(self, item: QListWidgetItem):
        row = self._list.row(item)
        self._emit(row)
