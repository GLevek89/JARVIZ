from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QTextEdit

from .base import Page
from ...tools_registry import ToolAction

FAQ_TEXT = """JARVIZ FAQ

General
- Ctrl+K opens Search. Type to find tools and pages.
- Left sidebar is navigation. Each section is a page.

GitHub ZIP Downloader
- Paste a repo link like: https://github.com/OWNER/REPO
- Private repos: add a GitHub Personal Access Token with repo read access.
- If a repo uses a different branch: type it in Branch, or paste a /tree/branch link.

Safety
- This app downloads public files and runs local tools only.
- Token is kept in memory only. No token persistence by default.
"""

class FaqPage(Page):
    page_id = "faq"
    title = "FAQ"

    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        h = QLabel("Help / FAQ")
        h.setObjectName("H1")
        root.addWidget(h)

        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(FAQ_TEXT)

        lay.addWidget(txt)
        root.addWidget(card)
        root.addStretch(1)

    def register_actions(self, registry):
        registry.register(ToolAction(
            id="faq",
            title="Help and FAQ",
            keywords=["help", "faq", "hotkeys", "troubleshoot"],
            open_page_id="faq",
        ))
