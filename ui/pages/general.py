from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QGridLayout, QPushButton

from .base import Page
from ...tools_registry import ToolAction

class GeneralPage(Page):
    page_id = "general"
    title = "General"

    open_github_tool = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        h1 = QLabel("JARVIZ")
        h1.setObjectName("H1")
        sub = QLabel("General utilities and coding tools. Sharp, fast, and modular.")
        sub.setObjectName("Dim")

        root.addWidget(h1)
        root.addWidget(sub)

        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(16, 16, 16, 16)
        card_lay.setSpacing(12)

        title = QLabel("Coding Utilities")
        title.setObjectName("H2")
        card_lay.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        btn_github = QPushButton("GitHub: Download repo as ZIP")
        btn_github.setObjectName("Primary")
        btn_github.clicked.connect(self.open_github_tool.emit)

        btn_a = QPushButton("Quick Notes (coming soon)")
        btn_b = QPushButton("Regex Tester (coming soon)")
        btn_c = QPushButton("JSON Formatter (coming soon)")
        btn_d = QPushButton("URL Opener (coming soon)")

        for b in (btn_a, btn_b, btn_c, btn_d):
            b.setEnabled(False)

        grid.addWidget(btn_github, 0, 0)
        grid.addWidget(btn_a, 0, 1)
        grid.addWidget(btn_b, 1, 0)
        grid.addWidget(btn_c, 1, 1)
        grid.addWidget(btn_d, 2, 0)

        card_lay.addLayout(grid)

        tip = QLabel("Tip: Press Ctrl+K to search tools and jump to pages.")
        tip.setObjectName("Dim")
        card_lay.addWidget(tip)

        root.addWidget(card)
        root.addStretch(1)

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="open_github_zip",
            title="GitHub ZIP downloader",
            keywords=["github", "zip", "download", "repo", "coding"],
            open_page_id="github_zip",
        ))
