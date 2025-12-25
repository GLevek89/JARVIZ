from __future__ import annotations

from typing import Dict

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget,
    QStackedWidget, QPushButton, QLineEdit
)

from .theme import THEME, qss
from .settings import load_settings
from .tools_registry import ToolRegistry
from .ui.search_dialog import SearchDialog
from .ui.pages.general import GeneralPage
from .ui.pages.github_zip_page import GithubZipPage
from .ui.pages.settings_page import SettingsPage
from .ui.pages.faq_page import FaqPage
from .ui.pages.capture_page import CapturePage
from .ui.pages.ocr_preview_page import OCRPreviewPage
from .ui.pages.coding_helper_page import CodingHelperPage

class JarvizMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("JARVIZ")
        self.resize(1280, 720)

        s = load_settings()
        if s.start_maximized:
            self.showMaximized()

        self._registry = ToolRegistry()

        self._root = QWidget()
        self._root.setObjectName("AppRoot")
        self.setCentralWidget(self._root)

        self._sidebar = QWidget()
        self._sidebar.setObjectName("Sidebar")
        self._header = QWidget()
        self._header.setObjectName("Header")
        self._content = QWidget()
        self._content.setObjectName("Content")

        self._nav = QListWidget()
        self._nav.setFixedWidth(220)

        self._stack = QStackedWidget()

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search (Ctrl+K)")
        self._search.returnPressed.connect(self._open_search)

        self._btn_help = QPushButton("?")
        self._btn_help.setFixedWidth(44)
        self._btn_help.clicked.connect(lambda: self.open_page("faq"))

        main = QHBoxLayout(self._root)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        side_lay = QVBoxLayout(self._sidebar)
        side_lay.setContentsMargins(10, 12, 10, 12)
        side_lay.setSpacing(10)

        brand = QLabel("JARVIZ")
        brand.setObjectName("H2")
        brand_dim = QLabel("Operator Console")
        brand_dim.setObjectName("Dim")

        side_lay.addWidget(brand)
        side_lay.addWidget(brand_dim)
        side_lay.addWidget(self._nav, 1)

        content_lay = QVBoxLayout(self._content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        header_lay = QHBoxLayout(self._header)
        header_lay.setContentsMargins(14, 10, 14, 10)
        header_lay.setSpacing(10)

        title = QLabel("Control Deck")
        title.setObjectName("H2")

        header_lay.addWidget(title)
        header_lay.addStretch(1)
        header_lay.addWidget(self._search)
        header_lay.addWidget(self._btn_help)

        content_lay.addWidget(self._header, 0)
        content_lay.addWidget(self._stack, 1)

        main.addWidget(self._sidebar, 0)
        main.addWidget(self._content, 1)

        self._pages: Dict[str, QWidget] = {}
        self._search_dialog = SearchDialog(self)
        self._search_dialog.set_provider(self._registry.search)
        self._search_dialog.action_selected.connect(self._on_action_selected)

        self._install_pages()
        self._install_hotkeys()
        self._apply_theme()

        self._nav.currentRowChanged.connect(self._on_nav_changed)
        self._nav.setCurrentRow(0)

    def _install_pages(self):
        general = GeneralPage()
        general.open_github_tool.connect(lambda: self.open_page("github_zip"))
        self._add_page(general)

        github = GithubZipPage()
        self._add_page(github)

        settings = SettingsPage(on_theme_changed=self._apply_theme)
        self._add_page(settings)

        capture = CapturePage()
        self._add_page(capture)

        ocrprev = OCRPreviewPage()
        self._add_page(ocrprev)

        coding = CodingHelperPage()
        self._add_page(coding)

        faq = FaqPage()
        self._add_page(faq)

    def _add_page(self, page):
        self._pages[page.page_id] = page
        self._stack.addWidget(page)
        self._nav.addItem(page.title)
        page.register_actions(self._registry)

    def _install_hotkeys(self):
        act_search = QAction(self)
        act_search.setShortcut(QKeySequence("Ctrl+K"))
        act_search.triggered.connect(self._open_search)
        self.addAction(act_search)

    def _open_search(self):
        self._search_dialog.open_with_focus()

    def _on_action_selected(self, action):
        self.open_page(action.open_page_id)

    def open_page(self, page_id: str):
        if page_id not in self._pages:
            return
        idx = list(self._pages.keys()).index(page_id)
        self._animate_to_index(idx)

    def _on_nav_changed(self, row: int):
        if row < 0:
            return
        self._animate_to_index(row)

    def _animate_to_index(self, idx: int):
        idx = max(0, min(self._stack.count() - 1, idx))
        self._stack.setCurrentIndex(idx)
        new = self._stack.currentWidget()

        new.setWindowOpacity(0.0)
        anim = QPropertyAnimation(new, b"windowOpacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim = anim

    def _apply_theme(self):
        s = load_settings()
        themed = qss(THEME).replace(THEME.accent, s.accent)
        # Apply to the whole app so dialogs and popups match too.
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(themed)
        self.setStyleSheet(themed)
