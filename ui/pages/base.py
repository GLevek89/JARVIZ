from __future__ import annotations

from PySide6.QtWidgets import QWidget

class Page(QWidget):
    page_id: str = "base"
    title: str = "Base"

    def register_actions(self, registry):
        return
