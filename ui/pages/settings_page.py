from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit, QPushButton, QMessageBox

from .base import Page
from ...settings import load_settings, save_settings
from ...tools_registry import ToolAction

class SettingsPage(Page):
    page_id = "settings"
    title = "Settings"

    def __init__(self, parent=None, on_theme_changed=None):
        super().__init__(parent)
        self._on_theme_changed = on_theme_changed

        s = load_settings()

        self._accent = QLineEdit()
        self._tesseract = QLineEdit()
        self._accent.setPlaceholderText("#3aa3ff")
        self._accent.setText(s.accent)
        self._tesseract.setText(getattr(s, 'tesseract_path', ''))

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        h = QLabel("Settings")
        h.setObjectName("H1")
        root.addWidget(h)

        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        row = QHBoxLayout()
        row.addWidget(QLabel("Accent color (hex)"), 0)
        row.addWidget(self._accent, 1)

        btn_apply = QPushButton("Apply")
        btn_apply.setObjectName("Primary")
        btn_apply.clicked.connect(self._apply)
        row.addWidget(btn_apply)

        lay.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Tesseract path (optional)"), 0)
        self._tesseract.setPlaceholderText(r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        row2.addWidget(self._tesseract, 1)
        lay.addLayout(row2)


        tip = QLabel("Example: #3aa3ff or #6fdcff. Updates instantly and is saved.")
        tip.setObjectName("Dim")
        lay.addWidget(tip)

        root.addWidget(card)
        root.addStretch(1)

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="settings",
            title="Settings",
            keywords=["accent", "theme", "color", "ui"],
            open_page_id="settings",
        ))

    def _apply(self):
        accent = self._accent.text().strip()
        if not accent.startswith("#") or len(accent) not in (4, 7):
            QMessageBox.warning(self, "Invalid", "Enter a hex color like #3aa3ff.")
            return
        s = load_settings()
        s.accent = accent
        s.tesseract_path = self._tesseract.text().strip()
        save_settings(s)
        if self._on_theme_changed:
            self._on_theme_changed()